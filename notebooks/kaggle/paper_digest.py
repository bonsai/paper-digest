#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Digest MVP — Kaggle one-file pipeline
- PDF -> page-aware chunks
- TF-IDF keywords
- keyword co-occurrence graph (HTML)
- source-grounded RAG retrieval/answers with paper + page citations
- reproducibility manifest and CSV/JSONL artifacts

Kaggle use:
1. Add PDFs as a Kaggle Dataset/input, or place them under /kaggle/working/pdfs.
2. Run this file.
3. Set QUESTIONS below, then rerun to produce RAG answers.
No paid API, GPU, or external LLM is required. Answers are evidence excerpts,
not LLM-generated summaries; this deliberately avoids unsupported synthesis.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import subprocess
import importlib.util
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------- User configuration ----------
PDF_DIRS = [Path("/kaggle/input"), Path("/kaggle/working/pdfs"), Path("./pdfs")]
OUTPUT_DIR = Path("/kaggle/working/paper-digest-output")
# Put questions here. Example:
# QUESTIONS = ["What methods are compared?", "What limitations are reported?"]
QUESTIONS = []
CHUNK_WORDS = 220
CHUNK_OVERLAP_WORDS = 40
TOP_KEYWORDS_PER_PAPER = 12
TOP_KEYWORD_GRAPH_NODES = 80
TOP_RAG_EVIDENCE = 5
MIN_RAG_SCORE = 0.015
RANDOM_SEED = 42

# Kaggle normally has these installed. Install only missing packages if internet is enabled.
_REQUIRED = {
    "fitz": "pymupdf",
    "pandas": "pandas",
    "sklearn": "scikit-learn",
    "plotly": "plotly",
    "networkx": "networkx",
}
_missing = [package for module, package in _REQUIRED.items()
            if importlib.util.find_spec(module) is None]
if _missing:
    print("Installing missing packages:", ", ".join(_missing))
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *_missing])

import fitz  # PyMuPDF
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_id(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", text.strip()).strip("-")
    return value[:100] or "paper"


def find_pdfs() -> list[Path]:
    found: dict[str, Path] = {}
    for root in PDF_DIRS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() == ".pdf":
                # Avoid re-ingesting our own output if it lives below a scanned root.
                if OUTPUT_DIR == path or OUTPUT_DIR in path.parents:
                    continue
                found[str(path.resolve())] = path
    return sorted(found.values(), key=lambda item: str(item).lower())


def split_words(text: str, chunk_words: int, overlap_words: int) -> list[str]:
    words = re.findall(r"\S+", text)
    if not words:
        return []
    step = max(1, chunk_words - overlap_words)
    return [" ".join(words[start:start + chunk_words])
            for start in range(0, len(words), step)]


def extract_pdfs(pdf_paths: list[Path]) -> tuple[list[dict], list[dict], list[dict]]:
    papers, chunks, errors = [], [], []
    for path in pdf_paths:
        paper_id = safe_id(path.stem)
        file_hash = sha256_file(path)
        paper = {
            "paper_id": paper_id,
            "title": path.stem,
            "file_name": path.name,
            "file_path": str(path),
            "sha256": file_hash,
            "page_count": 0,
            "extraction_status": "pending",
        }
        try:
            with fitz.open(path) as pdf:
                paper["page_count"] = len(pdf)
                for page_index, page in enumerate(pdf):
                    page_text = re.sub(r"\s+", " ", page.get_text("text")).strip()
                    if not page_text:
                        continue
                    page_chunks = split_words(page_text, CHUNK_WORDS, CHUNK_OVERLAP_WORDS)
                    for chunk_index, text in enumerate(page_chunks):
                        chunk_id = f"{paper_id}-p{page_index + 1}-c{chunk_index + 1}"
                        chunks.append({
                            "chunk_id": chunk_id,
                            "paper_id": paper_id,
                            "title": path.stem,
                            "page": page_index + 1,
                            "chunk_index": chunk_index + 1,
                            "text": text,
                            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                            "source_file": path.name,
                        })
            paper["extraction_status"] = "ok" if any(c["paper_id"] == paper_id for c in chunks) else "no_text"
        except Exception as exc:
            paper["extraction_status"] = "error"
            errors.append({"file": str(path), "error": f"{type(exc).__name__}: {exc}"})
        papers.append(paper)
        print(f"[PDF] {path.name}: {paper['page_count']} pages, {paper['extraction_status']}")
    return papers, chunks, errors


def extract_keywords(papers: list[dict], chunks: list[dict]) -> tuple[list[dict], dict[str, list[str]]]:
    if not chunks:
        return [], {}
    # Aggregate all extracted text per paper to reduce page-level term noise.
    texts = defaultdict(list)
    for chunk in chunks:
        texts[chunk["paper_id"]].append(chunk["text"])
    paper_ids = list(texts)
    documents = [" ".join(texts[paper_id]) for paper_id in paper_ids]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=12000,
        sublinear_tf=True,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
    )
    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return [], {}
    terms = vectorizer.get_feature_names_out()
    keyword_rows, paper_keywords = [], {}
    for row_index, paper_id in enumerate(paper_ids):
        row = matrix.getrow(row_index)
        ranked = sorted(zip(row.indices, row.data), key=lambda pair: pair[1], reverse=True)
        selected = [(terms[index], float(score)) for index, score in ranked[:TOP_KEYWORDS_PER_PAPER]]
        paper_keywords[paper_id] = [term for term, _ in selected]
        paper_title = next((p["title"] for p in papers if p["paper_id"] == paper_id), paper_id)
        for rank, (term, score) in enumerate(selected, 1):
            keyword_rows.append({
                "paper_id": paper_id, "title": paper_title,
                "keyword": term, "tfidf_score": round(score, 6), "rank": rank,
            })
    return keyword_rows, paper_keywords


def build_keyword_graph(papers: list[dict], paper_keywords: dict[str, list[str]], output_path: Path) -> dict:
    # Bipartite graph: paper nodes connect to keyword nodes. Keyword co-occurrence
    # is also exported separately so the relationship is inspectable.
    graph = nx.Graph()
    paper_lookup = {p["paper_id"]: p for p in papers}
    keyword_frequency = Counter(k for kws in paper_keywords.values() for k in kws)
    keep_keywords = {k for k, _ in keyword_frequency.most_common(TOP_KEYWORD_GRAPH_NODES)}
    cooccurrence = Counter()
    for paper_id, keywords in paper_keywords.items():
        paper = paper_lookup.get(paper_id, {})
        graph.add_node(paper_id, node_type="paper", label=paper.get("title", paper_id))
        selected = [k for k in keywords if k in keep_keywords]
        for keyword in selected:
            graph.add_node("kw:" + keyword, node_type="keyword", label=keyword)
            graph.add_edge(paper_id, "kw:" + keyword, relation="contains_keyword")
        for i, first in enumerate(selected):
            for second in selected[i + 1:]:
                pair = tuple(sorted((first, second)))
                cooccurrence[pair] += 1

    edge_rows = [{"keyword_a": a, "keyword_b": b, "shared_papers": count}
                 for (a, b), count in cooccurrence.most_common()]
    pd.DataFrame(edge_rows).to_csv(OUTPUT_DIR / "keyword-cooccurrence.csv", index=False)

    if graph.number_of_nodes() == 0:
        return {"nodes": 0, "edges": 0, "html": None}
    positions = nx.spring_layout(graph, seed=RANDOM_SEED, k=0.8)
    edge_x, edge_y = [], []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line={"width": 0.6, "color": "#9ca3af"},
        hoverinfo="none", name="paper-keyword links",
    )
    node_x, node_y, node_text, node_hover, node_color, node_size = [], [], [], [], [], []
    for node, attrs in graph.nodes(data=True):
        x, y = positions[node]
        is_keyword = attrs.get("node_type") == "keyword"
        label = attrs.get("label", node)
        node_x.append(x); node_y.append(y)
        node_text.append(label[:42])
        node_hover.append(f"{attrs.get('node_type')}: {label}")
        node_color.append("#0f766e" if is_keyword else "#2563eb")
        node_size.append(9 if is_keyword else 16)
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_text, textposition="top center",
        hovertext=node_hover, hoverinfo="text",
        marker={"size": node_size, "color": node_color, "line": {"width": 0.5, "color": "white"}},
        name="papers / keywords",
    )
    figure = go.Figure(data=[edge_trace, node_trace])
    figure.update_layout(
        title="Paper Digest — Paper / Keyword Graph",
        showlegend=False, hovermode="closest",
        margin={"b": 20, "l": 10, "r": 10, "t": 55},
        xaxis={"visible": False}, yaxis={"visible": False},
    )
    figure.write_html(str(output_path), include_plotlyjs=True)
    return {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "html": str(output_path)}


class RAGEngine:
    """Local TF-IDF retrieval with extractive, source-cited answers."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.vectorizer = None
        self.matrix = None
        if chunks:
            self.vectorizer = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), sublinear_tf=True,
                token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
            )
            try:
                self.matrix = self.vectorizer.fit_transform([c["text"] for c in chunks])
            except ValueError:
                self.matrix = None

    def answer(self, question: str, top_k: int = TOP_RAG_EVIDENCE) -> dict:
        question = question.strip()
        if not question:
            return {"question": question, "answer": "質問が空です。", "evidence": []}
        if self.matrix is None or self.vectorizer is None:
            return {"question": question, "answer": "検索対象の本文がありません。PDFの配置と文字抽出結果を確認してください。", "evidence": []}
        query = self.vectorizer.transform([question])
        scores = cosine_similarity(query, self.matrix).ravel()
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        evidence = []
        for index, score in ranked:
            if score < MIN_RAG_SCORE or len(evidence) >= top_k:
                break
            chunk = self.chunks[index]
            evidence.append({
                "rank": len(evidence) + 1,
                "score": round(float(score), 5),
                "paper_id": chunk["paper_id"],
                "title": chunk["title"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "excerpt": chunk["text"][:1200],
            })
        if not evidence:
            answer_text = (
                "登録文献から質問に十分関連する根拠を検索できませんでした。"
                "質問を言い換えるか、関連するPDFが登録されているか確認してください。"
            )
        else:
            answer_text = (
                f"検索で関連する根拠を {len(evidence)} 件取得しました。"
                "以下の抜粋を根拠として確認してください。これは抽出型RAGの回答であり、"
                "抜粋に書かれていない結論は推測していません。"
            )
        return {"question": question, "answer": answer_text, "evidence": evidence}


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_paths = find_pdfs()
    print(f"Found {len(pdf_paths)} PDF(s). Output: {OUTPUT_DIR}")
    papers, chunks, errors = extract_pdfs(pdf_paths)

    pd.DataFrame(papers).to_csv(OUTPUT_DIR / "papers.csv", index=False)
    write_jsonl(OUTPUT_DIR / "chunks.jsonl", chunks)
    write_jsonl(OUTPUT_DIR / "extraction-errors.jsonl", errors)

    keyword_rows, paper_keywords = extract_keywords(papers, chunks)
    pd.DataFrame(keyword_rows).to_csv(OUTPUT_DIR / "keywords.csv", index=False)
    graph_summary = build_keyword_graph(
        papers, paper_keywords, OUTPUT_DIR / "keyword-graph.html"
    )

    rag = RAGEngine(chunks)
    rag_answers = [rag.answer(question) for question in QUESTIONS]
    write_jsonl(OUTPUT_DIR / "rag-answers.jsonl", rag_answers)

    manifest = {
        "pipeline": "paper-digest-kaggle-single-file",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "input_pdf_count": len(pdf_paths),
        "paper_count": len(papers),
        "page_aware_chunk_count": len(chunks),
        "keyword_row_count": len(keyword_rows),
        "rag_question_count": len(QUESTIONS),
        "extraction_error_count": len(errors),
        "graph": graph_summary,
        "configuration": {
            "chunk_words": CHUNK_WORDS,
            "chunk_overlap_words": CHUNK_OVERLAP_WORDS,
            "top_keywords_per_paper": TOP_KEYWORDS_PER_PAPER,
            "top_rag_evidence": TOP_RAG_EVIDENCE,
            "min_rag_score": MIN_RAG_SCORE,
        },
        "limitations": [
            "Keywords are TF-IDF terms, not validated scientific concepts.",
            "Graph edges represent paper-keyword membership and keyword co-occurrence, not causality.",
            "RAG uses TF-IDF retrieval and cited excerpts; it does not generate a synthesized LLM answer.",
            "Scanned PDFs without an OCR text layer may yield no text.",
        ],
    }
    (OUTPUT_DIR / "run-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n=== PAPER DIGEST COMPLETE ===")
    print(f"Papers: {len(papers)} | chunks: {len(chunks)} | keywords: {len(keyword_rows)}")
    print(f"Graph: {graph_summary['nodes']} nodes / {graph_summary['edges']} edges")
    print("Artifacts:")
    for path in sorted(OUTPUT_DIR.iterdir()):
        print(f" - {path.name} ({path.stat().st_size:,} bytes)")
    if QUESTIONS:
        print("\n=== RAG ANSWERS ===")
        for item in rag_answers:
            print(f"\nQ: {item['question']}\nA: {item['answer']}")
            for ev in item["evidence"]:
                print(f"  [{ev['rank']}] {ev['title']} p.{ev['page']} "
                      f"(score={ev['score']}) — {ev['excerpt'][:240]}...")


if __name__ == "__main__":
    main()
