# Paper Digest outputs

This directory is the repository-side publication target for validated pipeline runs.

## Layout

- `latest/`: files from the most recent successfully validated run.
- `runs/<run-id>/`: immutable snapshot/manifest for a specific run.
- `schema.json`: shared artifact contract for Kaggle and Colab.

## Core artifacts

- `run-manifest.json`: run timestamp, source counts, extraction counts, schema version, and hashes.
- `papers.csv`: one row per paper with source identity and extraction status.
- `chunks.jsonl`: page-aware text chunks with paper/page/chunk IDs.
- `keywords.csv` and `keyword-cooccurrence.csv`: extracted terms and relationships.
- `download-results.jsonl` and `extraction-errors.jsonl`: ingestion diagnostics.
- `keyword-graph.html`: interactive graph when generated.

## Publishing rules

1. Publish only after manifest validation succeeds.
2. Keep a stable schema across Kaggle and Colab.
3. Do not commit original PDFs unless redistribution is explicitly permitted.
4. Never store API keys, credentials, or private tokens in outputs.
5. Keep large/reproducible artifacts out of Git if they exceed the documented repository size budget; publish them as GitHub Actions artifacts or external object storage instead.
6. A run ID must be unique; never silently overwrite historical run snapshots.

The publishing implementation is tracked in [Issue #3](https://github.com/bonsai/paper-digest/issues/3).
