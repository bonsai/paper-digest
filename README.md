# Research & Engineering Knowledge Factory

A reproducible, source-grounded workspace for turning papers, engineering articles, official blogs, and open-source implementations into reusable software-engineering knowledge.

The goal is to connect source evidence to hypotheses, experiments, architecture decisions, GitHub Issues, and continuous improvement. Four-panel comics are an optional publishing format, not the product's main purpose.

## Project documents

- [Market Requirements Document](docs/mrd-paper-explorer.md)
- [Product Requirements Document](docs/prd-paper-explorer.md)
- [Kaggle notebook scaffold](notebooks/kaggle/paper-digest-mvp.ipynb)
- [Research source list: papers, software-factory articles, and implementation cases](data/sources/paper-list.md)
- [Separate bibliography: prompt-only LLM methods and evaluation](data/sources/prompt-only-llm-evaluation-list.md)
- [Machine-readable JSONL bibliography: prompt-only LLM methods and evaluation](data/sources/prompt-only-llm-evaluation-list.jsonl)
- [Prompt-only LLM research map and experiment protocol](data/sources/prompt-only-llm-evaluation.md)
- [Machine-readable source manifest](data/sources/r2v-papers.yaml)

## MVP workflow

1. Add permitted research PDFs to a local or Kaggle input folder; do not commit copyrighted PDFs unless their license permits redistribution.
2. Extract page-aware text and record extraction errors.
3. Create searchable chunks with paper, page, and chunk identifiers.
4. Explore keywords and relationships with pandas, NumPy, and Plotly.
5. Retrieve evidence for questions and show paper/page/chunk citations.
6. Record candidate insights with supporting evidence, limitations, and counterevidence.

## Current status

The single-file Kaggle pipeline is implemented at [`notebooks/kaggle/paper_digest.py`](notebooks/kaggle/paper_digest.py). It downloads configured PDF URLs, extracts page-aware text, computes TF-IDF keywords, builds a paper-keyword graph, and retrieves source excerpts for configured questions. Its RAG output is retrieval with citations, not an LLM-synthesized answer. Results are generated at runtime; do not treat example outputs or planned metrics as measured results.

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


## GitHub Actions → Kaggle CLI automation

The `.github/workflows/kaggle-paper-digest.yml` workflow submits the single-file pipeline to Kaggle when relevant files are pushed to `main`, waits for the kernel run, downloads its outputs, validates the run manifest, and uploads the results as a GitHub Actions artifact.

### One-time setup

1. In Kaggle, create an API token for the account that should own the kernel.
2. In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**.
3. Add these repository secrets:
   - `KAGGLE_USERNAME`: the Kaggle account username (not an email address).
   - `KAGGLE_KEY`: the API key from the Kaggle token.
4. Ensure the Kaggle account is allowed to run kernels and has accepted any applicable terms for the source material.

The workflow writes credentials to the runner's temporary `~/.kaggle/kaggle.json` with owner-only file permissions. Credentials are not committed to the repository or included in kernel metadata. The kernel is configured as private and internet-enabled because the script downloads configured PDF URLs. The Kaggle account's kernel slug is `paper-digest`.

### Trigger and outputs

- Automatic trigger: pushes to `main` that change `notebooks/kaggle/paper_digest.py`, `data/sources/**`, or the workflow itself.
- Manual trigger: **Actions → Run Paper Digest on Kaggle → Run workflow**.
- Output: open the completed GitHub Actions run and download the `paper-digest-<run number>` artifact. It contains the files returned by Kaggle, including the manifest, paper/chunk data, keyword data, graph, and download/extraction logs.
- The Kaggle kernel is updated and run on each trigger. Concurrent runs in this workflow are not cancelled to avoid interrupting an in-flight Kaggle run.

### Security and operational notes

- Never place Kaggle API keys in source files, kernel metadata, issue text, or logs. Rotate the key if it is exposed.
- This workflow requires both GitHub Actions to be enabled and valid Kaggle API credentials stored as repository secrets.
- Kaggle's internet setting must remain enabled for URL-based PDF ingestion. A failed URL is logged by the Python pipeline; the workflow fails if the run produces no papers or no extracted text chunks.
- PDF availability, licenses, and redistribution rights are not verified by the workflow. Keep copyrighted PDFs out of the repository unless redistribution is permitted.
- Kaggle runs and output downloads have platform limits; the workflow waits up to 45 minutes for a run to finish and stores GitHub artifacts for 14 days.
