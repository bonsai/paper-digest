#!/usr/bin/env python3
"""Extract page-aware text from permitted research PDFs into a reproducible corpus.

Outputs:
  papers.csv  - one row per PDF, including SHA-256 and extraction status
  chunks.jsonl - one row per extracted page chunk with page provenance

Usage:
  python scripts/literature/ingest_pdfs.py --input data/pdfs --output data/literature/processed

PyMuPDF is required: pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    file_hash = sha256_file(path)
    paper_id = file_hash[:16]
    paper: dict[str, Any] = {
        "paper_id": paper_id,
        "file_name": path.name,
        "sha256": file_hash,
        "file_bytes": path.stat().st_size,
        "page_count": 0,
        "pages_with_text": 0,
        "extraction_status": "pending",
        "error": "",
    }
    chunks: list[dict[str, Any]] = []

    if fitz is None:
        paper["extraction_status"] = "dependency_missing"
        paper["error"] = "PyMuPDF is not installed"
        return chunks, paper

    try:
        with fitz.open(path) as document:
            paper["page_count"] = len(document)
            for page_index, page in enumerate(document):
                text = clean_text(page.get_text("text"))
                if text:
                    paper["pages_with_text"] += 1
                    chunks.append({
                        "chunk_id": f"{paper_id}-p{page_index + 1:04d}",
                        "paper_id": paper_id,
                        "file_name": path.name,
                        "page_start": page_index + 1,
                        "page_end": page_index + 1,
                        "text": text,
                        "text_chars": len(text),
                        "source_sha256": file_hash,
                        "extraction_method": "pymupdf_page_text",
                    })
        if paper["page_count"] == 0:
            paper["extraction_status"] = "empty_pdf"
        elif paper["pages_with_text"] == 0:
            paper["extraction_status"] = "no_text_layer"
        else:
            paper["extraction_status"] = "success"
    except Exception as exc:  # preserve per-file failures instead of aborting the corpus
        paper["extraction_status"] = "error"
        paper["error"] = f"{type(exc).__name__}: {exc}"
        chunks = []

    return chunks, paper


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Directory containing source PDFs")
    parser.add_argument("--output", type=Path, required=True, help="Directory for CSV/JSONL outputs")
    args = parser.parse_args()

    if not args.input.exists() or not args.input.is_dir():
        parser.error(f"Input directory does not exist or is not a directory: {args.input}")

    pdfs = sorted(path for path in args.input.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf")
    args.output.mkdir(parents=True, exist_ok=True)

    all_papers: list[dict[str, Any]] = []
    all_chunks: list[dict[str, Any]] = []
    for path in pdfs:
        chunks, paper = extract_pdf(path)
        all_papers.append(paper)
        all_chunks.extend(chunks)

    papers_path = args.output / "papers.csv"
    fieldnames = [
        "paper_id", "file_name", "sha256", "file_bytes", "page_count",
        "pages_with_text", "extraction_status", "error",
    ]
    with papers_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_papers)

    chunks_path = args.output / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as stream:
        for chunk in all_chunks:
            stream.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    run_info = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(args.input.resolve()),
        "pdf_count": len(pdfs),
        "paper_rows": len(all_papers),
        "chunk_rows": len(all_chunks),
        "python_version": sys.version.split()[0],
        "pymupdf_version": getattr(fitz, "VersionBind", None) if fitz else None,
        "outputs": {"papers_csv": str(papers_path), "chunks_jsonl": str(chunks_path)},
        "status_counts": {},
    }
    for paper in all_papers:
        status = paper["extraction_status"]
        run_info["status_counts"][status] = run_info["status_counts"].get(status, 0) + 1
    (args.output / "run-manifest.json").write_text(
        json.dumps(run_info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "pdf_count": len(pdfs),
        "chunk_count": len(all_chunks),
        "status_counts": run_info["status_counts"],
        "output_dir": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
