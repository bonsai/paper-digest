# Research & Engineering Knowledge Factory

A reproducible, source-grounded workspace for turning papers, engineering articles, official blogs, and open-source implementations into reusable software-engineering knowledge.

The goal is to connect source evidence to hypotheses, experiments, architecture decisions, GitHub Issues, and continuous improvement. Four-panel comics are an optional publishing format, not the product's main purpose.

## Project documents

- [Market Requirements Document](docs/mrd-paper-explorer.md)
- [Product Requirements Document](docs/prd-paper-explorer.md)
- [Kaggle notebook scaffold](notebooks/kaggle/paper-digest-mvp.ipynb)
- [Research source list: papers, software-factory articles, and implementation cases](data/sources/paper-list.md)
- [Prompt-only LLM methods and evaluation research](data/sources/prompt-only-llm-evaluation.md)
- [Machine-readable source manifest](data/sources/r2v-papers.yaml)

## MVP workflow

1. Add permitted research PDFs to a local or Kaggle input folder; do not commit copyrighted PDFs unless their license permits redistribution.
2. Extract page-aware text and record extraction errors.
3. Create searchable chunks with paper, page, and chunk identifiers.
4. Explore keywords and relationships with pandas, NumPy, and Plotly.
5. Retrieve evidence for questions and show paper/page/chunk citations.
6. Record candidate insights with supporting evidence, limitations, and counterevidence.

## Current status

This repository currently contains planning documents, a source-candidate list, and notebook scaffolding. The ingestion, graph, retrieval, and evaluation pipeline is not implemented yet. Do not treat example outputs or planned metrics as measured results.

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


## Knowledge-to-engineering loop

1. Register a paper, article, documentation page, or repository with source type and usage status.
2. Extract claims and evidence pointers; distinguish author claims, observed facts, interpretation, and unknowns.
3. Turn useful findings into hypotheses or design propositions.
4. Test them through a JEV-style experiment/implementation loop; record metrics and limitations.
5. Export reviewed results as PRDs, ADRs, GitHub Issues, evaluation plans, or articles.
6. Keep generated changes reviewable; do not let a summary alone authorize implementation or merge.

## Initial article sources

- [GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)
- [Microsoft: Transform software development through an agentic platform](https://developer.microsoft.com/blog/learn-from-microsoft-transform-software-development-through-an-agentic-platform/)
- [Elastic AI Software Factory: Welcome to the Agent Factory](https://elastic.github.io/ai-github-actions/blog/welcome-to-the-agent-factory/)
- [Martin Fowler: Humans and Agents in Software Engineering Loops](https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html)
- [Microsoft Research: Why AI Agents Still Need You](https://www.microsoft.com/en-us/research/publication/sharp-tools-how-developers-wield-agentic-ai-in-real-software-engineering-tasks/?lang=ja)

The linked articles are research leads, not independent validation of vendor claims. Verify current status and implementation details before adopting a pattern.
