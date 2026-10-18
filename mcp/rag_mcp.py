#!/usr/bin/env python3
"""paper-digest RAG MCP サーバー（stdio / JSON-RPC 2.0、stdlib のみ）.

outputs/latest/（chunks.jsonl, papers.csv, keywords.csv）の上に語彙検索（BM25 相当 +
フレーズボーナス）を載せ、ページ引用付きの証拠チャンクを返す。

設計方針:
  - LLM を呼ばない（有料 API 禁止の方針に従う）。generation は呼び出し側 LLM に委ねる。
    ask ツールは「証拠抜粋の束」を返すだけで、要約・回答を生成しない。
  - 起動時に全チャンクを索引化（~600 チャンクなのでメモリ内・ミリ秒級）。
  - パスは repo 相対（本体は <repo>/mcp/rag_mcp.py）。PAPER_DIGEST_ROOT で上書き可。

ツール:
  list_papers   論文一覧（解題タイトル・チャンク数・上位キーワード）
  search        語彙検索（top_k / paper_id 絞り込み、ページ引用付き）
  ask           質問 → 証拠抜粋の束（生成はしない・引用必須）
  get_keywords  論文のキーワード一覧（tfidf 順）
  get_chunk     chunk_id の全文取得

登録（opencode）:
  "paper-digest-rag": {"type": "local", "command": ["python3", "<repo>/mcp/rag_mcp.py"], "enabled": true}
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SERVER_NAME = "paper-digest-rag"
SERVER_VERSION = "1.0.0"
PROTOCOL_FALLBACK = "2024-11-05"

# BM25 パラメータ
K1 = 1.5
B = 0.75
PHRASE_BONUS = 3.0
BIGRAM_BONUS = 0.5
DEFAULT_TOP_K = 5
MAX_TOP_K = 20
CLIP_CHARS = 1200  # search 結果のテキスト上限（get_chunk は全文）

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "is", "are", "was", "were", "be", "been", "being", "of",
    "in", "on", "at", "to", "for", "from", "by", "with", "as", "into", "about",
    "it", "its", "we", "our", "us", "you", "your", "they", "their", "i", "me",
    "my", "he", "she", "his", "her", "do", "does", "did", "can", "could", "will",
    "would", "should", "may", "might", "not", "no", "so", "such", "both", "each",
    "via", "per", "up", "out", "over", "also", "have", "has", "had", "there",
    "here", "when", "where", "which", "who", "whom", "how", "what", "why", "all",
    "any", "some", "more", "most", "other", "between", "during", "after", "before",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")


def log(msg: str) -> None:
    print(f"[{SERVER_NAME}] {msg}", file=sys.stderr, flush=True)


def repo_root() -> Path:
    env = os.environ.get("PAPER_DIGEST_ROOT")
    if env:
        return Path(env).expanduser()
    return Path(__file__).resolve().parent.parent


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 1]


def norm_text(text: str) -> str:
    return " ".join(TOKEN_RE.findall(text.lower()))


# --------------------------------------------------------------------------- #
# 索引
# --------------------------------------------------------------------------- #

class Index:
    def __init__(self, root: Path) -> None:
        self.root = root
        latest = root / "outputs" / "latest"
        self.latest = latest
        self.chunks: list[dict[str, Any]] = []
        self.papers: dict[str, dict[str, Any]] = {}
        self.keywords: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.df: dict[str, int] = defaultdict(int)
        self.tf: list[Counter] = []
        self.len: list[int] = []
        self.avg_len: float = 1.0
        self.norm_cache: list[str] = []
        self.titles: dict[str, str] = {}  # paper_id -> 解題タイトル（sources から）
        self._load()

    # -- loading ----------------------------------------------------------- #
    def _load(self) -> None:
        latest = self.latest
        if not (latest / "chunks.jsonl").exists():
            raise FileNotFoundError(
                f"{latest / 'chunks.jsonl'} がありません。先に digest パイプライン（Colab）を実行してください。"
            )

        with io.open(latest / "chunks.jsonl", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                self.chunks.append(rec)

        papers_csv = latest / "papers.csv"
        if papers_csv.exists():
            with io.open(papers_csv, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.papers[row["paper_id"]] = row

        kw_csv = latest / "keywords.csv"
        if kw_csv.exists():
            with io.open(kw_csv, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        row["rank"] = int(row.get("rank") or 0)
                        row["tfidf_score"] = float(row.get("tfidf_score") or 0.0)
                    except ValueError:
                        pass
                    self.keywords[row["paper_id"]].append(row)
        for rows in self.keywords.values():
            rows.sort(key=lambda r: (r.get("rank") or 999))

        self._resolve_titles()

        # 転置索引
        for i, rec in enumerate(self.chunks):
            toks = tokenize(rec.get("text", ""))
            self.tf.append(Counter(toks))
            self.len.append(len(toks))
            self.norm_cache.append(norm_text(rec.get("text", "")))
            for tok in set(toks):
                self.df[tok] += 1
        if self.len:
            self.avg_len = sum(self.len) / len(self.len)

    def _resolve_titles(self) -> None:
        """sources マニフェストのタイトルを paper_id に紐付ける（語の重なりで類推）。"""
        src = self.root / "inputs" / "sources"
        cands: list[dict[str, Any]] = []
        for jf in sorted(src.glob("*.jsonl")) if src.exists() else []:
            with io.open(jf, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if rec.get("title"):
                        cands.append(rec)
        for pid in self.papers or {c["paper_id"] for c in self.chunks}:
            pid_toks = set(tokenize(pid.replace("-", " ")))
            if not pid_toks:
                continue
            best, best_score = None, 0.0
            for rec in cands:
                cand = f"{rec.get('id', '')} {rec.get('title', '')}"
                cand_toks = set(tokenize(cand))
                if not cand_toks:
                    continue
                overlap = len(pid_toks & cand_toks) / len(pid_toks | cand_toks)
                if overlap > best_score:
                    best, best_score = rec, overlap
            if best is not None and best_score >= 0.4:
                self.titles[pid] = best["title"]

    # -- search ------------------------------------------------------------ #
    def _idf(self, token: str) -> float:
        n = len(self.chunks) or 1
        df = self.df.get(token, 0)
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = DEFAULT_TOP_K, paper_id: str | None = None) -> list[dict[str, Any]]:
        q_toks = tokenize(query)
        if not q_toks:
            return []
        candidates: list[int] | range
        if paper_id:
            candidates = [i for i, c in enumerate(self.chunks) if c.get("paper_id") == paper_id]
        else:
            candidates = range(len(self.chunks))
        cands = set(candidates)

        scored: list[tuple[float, int]] = []
        q_norm = norm_text(query)
        q_bigrams = list(zip(q_toks, q_toks[1:]))
        for i in cands:
            tf, ln = self.tf[i], self.len[i]
            if not tf:
                continue
            score = 0.0
            hit = False
            for tok in q_toks:
                f = tf.get(tok, 0)
                if not f:
                    continue
                hit = True
                score += self._idf(tok) * (f * (K1 + 1)) / (f + K1 * (1 - B + B * ln / self.avg_len))
            if not hit:
                continue
            norm = self.norm_cache[i]
            if len(q_toks) > 1 and q_norm in norm:
                score += PHRASE_BONUS
            if q_bigrams and norm:
                score += BIGRAM_BONUS * sum(1 for a, b in q_bigrams if f"{a} {b}" in norm)
            scored.append((score, i))

        scored.sort(key=lambda t: (-t[0], t[1]))
        out = []
        for score, i in scored[: max(1, min(top_k, MAX_TOP_K))]:
            rec = self.chunks[i]
            text = rec.get("text", "")
            out.append(
                {
                    "chunk_id": rec.get("chunk_id"),
                    "paper_id": rec.get("paper_id"),
                    "page": rec.get("page"),
                    "score": round(score, 3),
                    "text": text if len(text) <= CLIP_CHARS else text[:CLIP_CHARS] + " …[末尾は get_chunk で]",
                }
            )
        return out


INDEX: Index | None = None


def get_index() -> Index:
    global INDEX
    if INDEX is None:
        INDEX = Index(repo_root())
    return INDEX


# --------------------------------------------------------------------------- #
# ツール定義
# --------------------------------------------------------------------------- #

TOOLS = [
    {
        "name": "list_papers",
        "description": (
            "digest 済み論文の一覧を返す。paper_id / 解題タイトル / ページ数 / チャンク数 / 上位キーワードを含む。"
            "search や ask の paper_id フィルタに使う id をここで得る。"
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "search",
        "description": (
            "digest チャンクの語彙検索（BM25 相当＋フレーズボーナス）。"
            "結果は必ず page 引用付きの原文抜粋。質問は英語トークンで最も効く（論文本文は英語）。"
            "paper_id を指定するとその論文に絞り込める。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "検索クエリ（英語推奨）"},
                "top_k": {"type": "integer", "description": f"返す件数（既定 {DEFAULT_TOP_K}、最大 {MAX_TOP_K}）"},
                "paper_id": {"type": "string", "description": "論文に絞り込む場合の paper_id"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "ask",
        "description": (
            "質問に対する「証拠抜粋の束」を返す RAG の検索側。"
            "本サーバーは要約・回答を生成しない（方針: 回答は必ず根拠ページ付きの原文である）。"
            "生成（回答の言語化）は呼び出し側 LLM が、返ってきた抜粋と引用だけを材料に行うこと。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "論文群への質問"},
                "top_k": {"type": "integer", "description": "証拠の最大件数（既定 5）"},
            },
            "required": ["question"],
        },
    },
    {
        "name": "get_keywords",
        "description": "指定論文のキーワード一覧（tfidf 順）。テーマ把握・検索語の発見に使う。",
        "inputSchema": {
            "type": "object",
            "properties": {"paper_id": {"type": "string"}},
            "required": ["paper_id"],
        },
    },
    {
        "name": "get_chunk",
        "description": "chunk_id（例: chain-of-thought-prompting-2022-p1-c1）の全文を返す。search の抜粋が途中で切れていたときの追跡取得に使う。",
        "inputSchema": {
            "type": "object",
            "properties": {"chunk_id": {"type": "string"}},
            "required": ["chunk_id"],
        },
    },
]


def tool_list_papers(_: dict[str, Any]) -> dict[str, Any]:
    idx = get_index()
    counts = Counter(c.get("paper_id") for c in idx.chunks)
    out = []
    for pid in sorted(counts):
        meta = idx.papers.get(pid, {})
        kws = [k.get("keyword") for k in idx.keywords.get(pid, [])[:5]]
        out.append(
            {
                "paper_id": pid,
                "title": idx.titles.get(pid) or meta.get("title") or pid,
                "title_source": "sources-manifest" if pid in idx.titles else "paper_id",
                "page_count": meta.get("page_count"),
                "chunk_count": counts[pid],
                "top_keywords": kws,
            }
        )
    return {"papers": out, "total": len(out)}


def tool_search(args: dict[str, Any]) -> dict[str, Any]:
    idx = get_index()
    query = (args.get("query") or "").strip()
    if not query:
        return {"error": "query が空です"}
    if CJK_RE.search(query) and not tokenize(query):
        return {
            "error": "クエリが CJK 文字のみです。digest 本文は英語なので、英語キーワードで検索してください（呼び出し側 LLM が翻訳して再検索するのが最も確実です）。",
            "hint_query": "例: \"chain of thought reasoning\"",
        }
    top_k = int(args.get("top_k") or DEFAULT_TOP_K)
    results = idx.search(query, top_k=top_k, paper_id=args.get("paper_id"))
    return {"query": query, "count": len(results), "results": results}


def tool_ask(args: dict[str, Any]) -> dict[str, Any]:
    idx = get_index()
    question = (args.get("question") or "").strip()
    if not question:
        return {"error": "question が空です"}
    top_k = int(args.get("top_k") or DEFAULT_TOP_K)
    results = idx.search(question, top_k=top_k)
    return {
        "question": question,
        "note": (
            "これは証拠抜粋であり回答ではない。本サーバーは生成を行わない。"
            "呼び出し側 LLM は以下の抜粋のみを材料に回答を組み立て、"
            "主張には必ず paper_id と page を引用すること。抜粋に無い内容を答えない。"
        ),
        "evidence": results,
    }


def tool_get_keywords(args: dict[str, Any]) -> dict[str, Any]:
    idx = get_index()
    pid = (args.get("paper_id") or "").strip()
    rows = idx.keywords.get(pid)
    if rows is None:
        return {"error": f"paper_id '{pid}' が見つかりません。list_papers で id を確認してください。"}
    return {
        "paper_id": pid,
        "keywords": [
            {"keyword": r.get("keyword"), "rank": r.get("rank"), "tfidf_score": r.get("tfidf_score")}
            for r in rows
        ],
    }


def tool_get_chunk(args: dict[str, Any]) -> dict[str, Any]:
    idx = get_index()
    cid = (args.get("chunk_id") or "").strip()
    for rec in idx.chunks:
        if rec.get("chunk_id") == cid:
            return {
                "chunk_id": cid,
                "paper_id": rec.get("paper_id"),
                "page": rec.get("page"),
                "text": rec.get("text", ""),
            }
    return {"error": f"chunk_id '{cid}' が見つかりません"}


DISPATCH = {
    "list_papers": tool_list_papers,
    "search": tool_search,
    "ask": tool_ask,
    "get_keywords": tool_get_keywords,
    "get_chunk": tool_get_chunk,
}


# --------------------------------------------------------------------------- #
# JSON-RPC 2.0 over stdio（改行区切り）
# --------------------------------------------------------------------------- #

def make_result(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle(msg: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method")
    req_id = msg.get("id")

    if method == "initialize":
        client_ver = (msg.get("params") or {}).get("protocolVersion") or PROTOCOL_FALLBACK
        return make_result(
            req_id,
            {
                "protocolVersion": client_ver,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method in ("notifications/initialized", "notifications/cancelled"):
        return None

    if method == "ping":
        return make_result(req_id, {})

    if method == "tools/list":
        return make_result(req_id, {"tools": TOOLS})

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        fn = DISPATCH.get(name)
        if fn is None:
            return make_error(req_id, -32602, f"unknown tool: {name}")
        try:
            result = fn(args)
            is_err = isinstance(result, dict) and "error" in result
            return make_result(
                req_id,
                {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": is_err,
                },
            )
        except FileNotFoundError as e:
            return make_result(
                req_id, {"content": [{"type": "text", "text": str(e)}], "isError": True}
            )
        except Exception as e:  # noqa: BLE001 - サーバは落とさずツールエラーとして返す
            log(f"tool error {name}: {e!r}")
            return make_result(
                req_id,
                {"content": [{"type": "text", "text": f"internal error: {e}"}], "isError": True},
            )

    if req_id is not None:
        return make_error(req_id, -32601, f"method not found: {method}")
    return None


def main() -> None:
    try:
        idx = get_index()
        log(f"indexed {len(idx.chunks)} chunks / {len(set(c.get('paper_id') for c in idx.chunks))} papers "
            f"from {idx.latest}")
    except FileNotFoundError as e:
        log(f"warning: {e}（起動はするが tools/call で isError を返す）")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            resp = make_error(None, -32700, "parse error")
            print(json.dumps(resp, ensure_ascii=False), flush=True)
            continue
        try:
            resp = handle(msg)
        except Exception as e:  # noqa: BLE001
            log(f"handler error: {e!r}")
            resp = make_error(msg.get("id"), -32603, f"internal error: {e}")
        if resp is not None:
            print(json.dumps(resp, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
