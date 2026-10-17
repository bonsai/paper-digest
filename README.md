# Paper Digest

A reproducible, source-grounded workspace for exploring research papers—starting with AI-generated anime/video production.

The first milestone is intentionally small: ingest a user-provided corpus of around 10 PDFs, preserve page-level provenance, explore paper/keyword relationships, and test whether candidate insights are supported by evidence. This is a research tool, not an automatic truth machine.

## Project documents

- [Market Requirements Document](docs/mrd-paper-explorer.md)
- [Product Requirements Document](docs/prd-paper-explorer.md)
- [Kaggle notebook scaffold](notebooks/kaggle/paper-digest-mvp.ipynb)
- [Paper candidate list: AI video, Toyota/organization, human-AI](data/sources/paper-list.md)
- [Machine-readable source manifest](data/sources/r2v-papers.yaml)

## MVP workflow

1. Add permitted research PDFs to a local or Kaggle input folder; do not commit copyrighted PDFs unless their license permits redistribution.
2. Extract page-aware text and record extraction errors.
3. Create searchable chunks with paper, page, and chunk identifiers.
4. Explore keywords and relationships with pandas, NumPy, and Plotly.
5. Retrieve evidence for questions and show paper/page/chunk citations.
6. Record candidate insights with supporting evidence, limitations, and counterevidence.

## Current status

This repository contains planning documents and a notebook skeleton. The ingestion, graph, retrieval, and evaluation pipeline is not implemented yet. Do not treat example outputs or planned metrics as measured results.

## Data and provenance principles

- The source PDF is canonical; extracted text and chunks are derived artifacts.
- Keep paper metadata, page numbers, extraction status, and file hashes.
- Separate keyword co-occurrence, semantic similarity, citation links, dataset usage, and metric usage.
- If the corpus does not support an answer, say so instead of inventing a claim.
- Check copyright and dataset licenses before storing or redistributing papers and extracted text.

## Local setup

The notebook is designed to run in Kaggle or a compatible Python environment. The initial baseline should avoid paid APIs and GPU requirements.

Suggested libraries: pandas, NumPy, Plotly, PyMuPDF (fitz), and SQLite FTS5. Pin and record versions when the pipeline is implemented.

## Scope note

The product is for research exploration. The initial corpus and any findings must not be presented as representative of the entire field without a documented sampling and search protocol.
