# Research & Engineering Knowledge Factory

**[Open the Paper Digest dashboard](https://bonsai.github.io/paper-digest/)** — browse the latest papers, TF-IDF keywords, retrieval evidence, and run manifest.

A reproducible, source-grounded workspace for turning papers, engineering articles, official blogs, and open-source implementations into reusable software-engineering knowledge.

The goal is to connect source evidence to hypotheses, experiments, architecture decisions, GitHub Issues, and continuous improvement. Four-panel comics are an optional publishing format, not the product's main purpose.

## Project documents

- [Market Requirements Document](dev/mrd-paper-explorer.md)
- [Product Requirements Document](dev/prd-paper-explorer.md)
- [Colab notebook: full pipeline with GitHub publishing](notebooks/colab/paper_digest_colab.ipynb)
- [Colab notebook: MVP scaffold (manifest and hashes)](notebooks/colab/paper_digest_mvp_colab.ipynb)
- [Colab notebook: keyword/intent ML baselines](notebooks/colab/keyword_intent_ml_colab.ipynb)
- [Kaggle notebooks (legacy, optional)](notebooks/kaggle/)
- [Research source list: papers, software-factory articles, and implementation cases](inputs/sources/paper-list.md)
- [Separate bibliography: prompt-only LLM methods and evaluation](inputs/sources/prompt-only-llm-evaluation-list.md)
- [Machine-readable JSONL bibliography: prompt-only LLM methods and evaluation](inputs/sources/prompt-only-llm-evaluation-list.jsonl)
- [Prompt-only LLM research map and experiment protocol](inputs/sources/prompt-only-llm-evaluation.md)
- [Machine-readable source manifest](inputs/sources/r2v-papers.yaml)

## MVP workflow

1. Add permitted research PDFs to a local or Colab input folder (`inputs/literature/`); do not commit copyrighted PDFs unless their license permits redistribution.
2. Extract page-aware text and record extraction errors.
3. Create searchable chunks with paper, page, and chunk identifiers.
4. Explore keywords and relationships with pandas, NumPy, and Plotly.
5. Retrieve evidence for questions and show paper/page/chunk citations.
6. Record candidate insights with supporting evidence, limitations, and counterevidence.

## Current status

The single-file pipeline is implemented at [`notebooks/kaggle/paper_digest.py`](notebooks/kaggle/paper_digest.py). It downloads configured PDF URLs, extracts page-aware text, computes TF-IDF keywords, builds a paper-keyword graph, and retrieves source excerpts for six default Japanese questions using English retrieval-query expansions. RAG evidence includes paper ID, page, chunk, excerpt, and source PDF URL. Its answers are retrieval notices plus cited evidence, not LLM-synthesized summaries. After changing the pipeline, rerun [the Colab notebook](notebooks/colab/paper_digest_colab.ipynb) to regenerate and push `outputs/latest/`; the public dashboard only shows the last published run. Results are generated at runtime; do not treat example outputs or planned metrics as measured results.

## Data and provenance principles

- The source PDF is canonical; extracted text and chunks are derived artifacts.
- Keep paper metadata, page numbers, extraction status, and file hashes.
- Separate keyword co-occurrence, semantic similarity, citation links, dataset usage, and metric usage.
- If the corpus does not support an answer, say so instead of inventing a claim.
- Check copyright and dataset licenses before storing or redistributing papers and extracted text.

## Local setup

The notebooks are designed to run in Google Colab (primary), Kaggle, or any compatible Python environment. The initial baseline should avoid paid APIs and GPU requirements.

Dependencies are managed in [`requirements.txt`](requirements.txt), split by pipeline stage (ingest / compute / interpretation / narration / display). Pin and record versions when the pipeline changes.

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


## Google Colab execution and GitHub output persistence

The primary execution environment is Google Colab. Open [`notebooks/colab/paper_digest_colab.ipynb`](notebooks/colab/paper_digest_colab.ipynb) in Colab and run the cells from top to bottom. The notebook clones this repository, runs the shared pipeline, validates the manifest, then publishes generated artifacts to GitHub.

### One-time setup

1. Open the notebook in Google Colab.
2. Create a GitHub fine-grained personal access token limited to `bonsai/paper-digest` with **Contents: Read and write**.
3. In Colab, open **Secrets** (key icon), add a secret named `GITHUB_TOKEN`, and allow the notebook to access it.
4. Run the notebook cells in order.

Do not paste the token into notebook code or output cells. The notebook reads it from Colab Secrets and uses it only for the push operation.

### Output contract

- `outputs/latest/`: latest validated run artifacts (manifest, CSV, JSONL, and graph HTML).
- `outputs/runs/<run-id>/`: lightweight immutable history containing the manifest, papers table, and keywords table.
- Source PDFs are downloaded at runtime and are not committed.
- The script accepts `PAPER_DIGEST_WORK_DIR`, `PAPER_DIGEST_DOWNLOAD_DIR`, `PAPER_DIGEST_INPUT_DIR`, and `PAPER_DIGEST_OUTPUT_DIR` so it can run in Colab or Kaggle without changing the pipeline logic.

Colab sessions can disconnect and runtime storage is temporary, so publish outputs before ending the session. GitHub is the durable destination. The former Kaggle Actions submission workflow has been retired; Colab runs are currently started manually from the notebook.

## RAG MCP server (`mcp/rag_mcp.py`)

A stdio MCP server (JSON-RPC 2.0, Python stdlib only) that serves retrieval over the committed `outputs/latest/` artifacts. It performs no LLM calls: `ask` returns page-cited evidence excerpts, and generation (turning excerpts into an answer) is left to the calling LLM, which must cite `paper_id` and `page`.

Run interactively or register it with an MCP-capable agent:

```bash
python3 mcp/rag_mcp.py   # stdio server; PAPER_DIGEST_ROOT overrides the repo location
```

opencode registration example:

```jsonc
// ~/.config/opencode/opencode.jsonc  →  "mcp"
"paper-digest-rag": {
  "type": "local",
  "command": ["python3", "/home/sexy/paper-digest/mcp/rag_mcp.py"],
  "enabled": true
}
```

Tools: `list_papers` (ids, resolved titles, chunk counts, top keywords), `search(query, top_k?, paper_id?)` (BM25-style lexical retrieval with phrase bonus; English queries match best because the corpus is English), `ask(question, top_k?)` (evidence excerpts only, never a generated answer), `get_keywords(paper_id)`, `get_chunk(chunk_id)`. The server indexes on startup and fails tool calls with a clear message when `outputs/latest/` has not been generated yet.
