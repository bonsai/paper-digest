# Literature data

Put PDFs that you are legally permitted to process in a local input directory (for example, `data/pdfs/`) or attach them as a Kaggle dataset. Do not commit papers or extracted full text unless the applicable license allows redistribution.

Run the first ingestion step from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/literature/ingest_pdfs.py --input data/pdfs --output data/literature/processed
```

Outputs:
- `papers.csv`: one row per PDF, including SHA-256, page counts, and extraction status.
- `chunks.jsonl`: one record per page with non-empty extracted text, including page provenance and source hash.
- `run-manifest.json`: run timestamp, versions, counts, and status summary.

A PDF with no selectable text is marked `no_text_layer`; OCR is not implemented in this first version. Extraction success does not imply that the extracted text is complete or scientifically valid.
