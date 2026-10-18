# Prompt-only LLM: prompting methods and evaluation research

- Status: research map / not yet experimentally validated
- Scope: improve and evaluate outputs by changing prompts only, with model weights fixed and no fine-tuning.
- Exclusions for the core experiment: tools, retrieval/RAG, external search, model routing, and training. These can be later comparison arms, but must not be mixed into the prompt-only baseline.
- Goal: identify prompt methods, evaluation methods, and a reproducible experiment protocol for the Research & Engineering Knowledge Factory.

## 1. Working definition

**Prompt-only** means that the model/version and weights are fixed and only the input instruction, examples, formatting constraints, and prompt-time sampling/selection procedure vary. Record sampling/decoding settings separately. For a strict "single-call prompt-only" baseline, disable tools, retrieval, memory, external context, and multi-call self-consistency. Multi-call methods are useful comparison arms, but they consume more inference budget.

Do not use "prompt engineering improved performance" as a general conclusion unless the task, model, prompt variants, dataset, settings, and evaluation procedure are specified.

## 2. Core research reading list

| Priority | Work | What to learn | Source |
|---|---|---|---|
| P0 | A Survey of Prompt Engineering Methods in Large Language Models for Different NLP Tasks (Vatsal & Dubey, 2024) | Taxonomy of 39 prompt methods across 29 NLP tasks; use as the first method map | [arXiv](https://arxiv.org/abs/2407.12994) |
| P0 | A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications (Sahoo et al., 2024) | Broader taxonomy, use cases, strengths, limitations, open questions | [arXiv](https://arxiv.org/abs/2402.07927) |
| P0 | Large Language Models Are Zero-Shot Reasoners (Kojima et al., NeurIPS 2022) | Zero-shot CoT: minimal reasoning instruction as a prompt intervention | [Paper](https://papers.neurips.cc/paper_files/paper/2022/hash/8bb0d291acd4acf06ef112099c16f326-Abstract-Conference.html) |
| P0 | Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (Wei et al., 2022) | Few-shot reasoning demonstrations and task-dependent effects | [arXiv](https://arxiv.org/abs/2201.11903) |
| P1 | Self-Consistency Improves Chain of Thought Reasoning in Language Models (Wang et al., ICLR 2023) | Sample multiple reasoning paths and select the most consistent answer; compare as a multi-call arm, not as single-prompt-only | [Google Research](https://research.google/pubs/self-consistency-improves-chain-of-thought-reasoning-in-language-models/) |
| P0 | PromptRobust: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts (Zhu et al., 2023) | Test whether typos, paraphrases, and small semantic-preserving changes alter outcomes | [arXiv](https://arxiv.org/abs/2306.04528) |
| P0 | G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment (Liu et al., EMNLP 2023) | Rubric/form-based LLM evaluation and comparison with human judgments; also discusses judge bias | [ACL Anthology](https://aclanthology.org/2023.emnlp-main.153/) · [PDF](https://aclanthology.org/2023.emnlp-main.153.pdf) |
| P0 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (Zheng et al., NeurIPS 2023) | Pairwise/turn-based evaluation, human agreement, position and verbosity bias | [NeurIPS](https://papers.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html) · [arXiv](https://arxiv.org/abs/2306.05685) |
| P0 | Humans or LLMs as the Judge? A Study on Judgement Bias (Chen et al., EMNLP 2024) | Compare human and LLM evaluator biases; do not assume either is unbiased | [ACL Anthology](https://aclanthology.org/2024.emnlp-main.474/) |
| P0 | Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge (Shi et al., 2025) | Position consistency, repetition stability, and preference fairness | [ACL Anthology](https://aclanthology.org/2025.ijcnlp-long.18/) |
| P1 | A survey on LLM-as-a-judge (2025/2026 publication record) | Reliability, judge consistency, bias taxonomy, and meta-evaluation | [Open-access article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13237853/) |
| P0 | Evaluation best practices (living technical guidance) | Build representative test data, use explicit criteria, inspect failures, and run evaluations continuously | [OpenAI developer guide](https://developers.openai.com/api/docs/guides/evaluation-best-practices) |

**Reading note:** the list is a source map, not a claim that every paper has been downloaded or fully read. Verify bibliographic details and access terms before mirroring PDFs. Some works investigate inference-time sampling or LLM judges rather than prompt text alone; those belong in clearly labeled comparison arms.

## 3. Prompt method taxonomy for controlled comparison

### Single-call prompt-only arms

1. **P0 — Minimal baseline:** task request only, with no examples.
2. **P1 — Explicit instruction:** state goal, audience, scope, and what counts as success.
3. **P2 — Structured output:** define fields/schema, required sections, and output constraints.
4. **P3 — Few-shot examples:** add a small number of curated input/output demonstrations.
5. **P4 — Decomposition:** ask for named sub-tasks or a checklist before producing the final response. Do not require disclosure of private chain-of-thought; evaluate the final answer and any concise, verifiable rationale.
6. **P5 — Rubric/self-check:** include a short checklist of objective requirements, then request a final answer that meets them.
7. **P6 — Robustness paraphrases:** test equivalent variants of the user instruction; this is a test condition, not automatically a better prompt.
8. **P7 — Negative/edge-case guidance:** specify abstention, ambiguity handling, and how to report missing information.

### Multi-call comparison arms (not strict single-call prompt-only)

- **Self-consistency:** sample multiple outputs and vote/aggregate.
- **Generate-then-judge / revise:** one call generates, another evaluates or revises.
- **LLM-as-a-judge:** a separate judging prompt grades outputs against a rubric.

These arms can improve outcomes but add calls, latency, cost, and potential correlated errors. Report them separately from single-call prompt interventions.

## 4. Evaluation methods

| Method | Best fit | Main metric | Main failure mode |
|---|---|---|---|
| Exact match / deterministic code | Extraction, classification, schema values, calculations with known answer | Accuracy, exact-match, pass rate | Too strict for valid paraphrases |
| Task-specific rubric | Writing, summaries, explanations, plans | Criterion-level pass rate and score | Vague criteria lead to unstable grades |
| Blind pairwise comparison | Open-ended outputs where ranking is easier than absolute scoring | Win/tie/loss, preference rate | Position and length bias |
| LLM-as-a-judge | High-volume rubric grading | Per-criterion score and judge-human agreement | Position, verbosity, style, self-preference, evaluator drift |
| Human review | Subjective or high-impact decisions | Agreement, preference, error taxonomy | Expensive; annotator disagreement |
| Robustness tests | Prompt paraphrases, typos, reordered instructions, edge cases | Performance drop, variance, consistency | Test perturbations may unintentionally change task meaning |
| Operational measurement | Any production-oriented prompt | Tokens, latency, cost per successful task, retry rate | Cheap/fast output may be wrong |
| Calibration / abstention | Tasks where uncertainty or missing evidence matters | Error among answered cases, abstention precision/recall | Confident-sounding unsupported answers |

For judge validation, sample a blinded human-reviewed subset and report agreement (for example, Cohen's kappa for categorical labels or Spearman correlation for ordinal ratings where appropriate). Do not rely on an LLM judge as the sole ground truth. Randomize candidate order and, for pairwise tests, repeat a subset with swapped order.

## 5. Minimal experiment protocol

1. **Define one task.** Example: turn a GitHub Issue into acceptance criteria, summarize an article with source links, or classify a user request into a fixed taxonomy.
2. **Create a frozen dataset.** Start with 30–100 representative cases if feasible; include ordinary, ambiguous, edge, and adversarial cases. Keep a held-out test set that is not used to write prompts.
3. **Write the rubric before comparing prompts.** Each criterion must be observable, e.g. required fields present, unsupported claims absent, links preserved, acceptance criteria testable.
4. **Freeze the model settings.** Record provider, exact model/version, date, system prompt, temperature, top-p, output limit, seed if supported, and any API defaults. Use identical settings across prompt arms.
5. **Change one factor at a time first.** Compare P0 vs P1, then P1 vs P2, etc. After the first pass, run selected combinations as a factorial/ablation study.
6. **Repeat stochastic runs.** Use multiple runs or samples when outputs vary; report sample size and uncertainty rather than only the best result.
7. **Evaluate blindly.** Use code for deterministic checks; use a rubric judge for scale; human-review a stratified subset and disagreements.
8. **Run robustness checks.** Paraphrase the user instruction, reorder examples, omit optional context, and add realistic edge cases without changing the intended task.
9. **Report trade-offs.** Quality, task success, unsupported-claim rate, format validity, latency, token usage, cost, and retry rate.
10. **Save artifacts.** Prompt version/hash, dataset version, raw outputs, evaluator prompt/version, judgments, metrics, failure cases, and decision.
11. **Decide with a predeclared rule.** Adopt a prompt only if it improves the target metric without unacceptable regressions in safety, robustness, cost, or latency.

### Suggested data schema

```json
{
  "case_id": "example-001",
  "task_id": "issue-to-acceptance-criteria",
  "input": "Frozen input text",
  "expected": null,
  "rubric_version": "v1",
  "prompt_variant": "P2-structured-output",
  "model_id": "exact-model-version",
  "run_id": "run-001",
  "output": "Raw model output",
  "deterministic_checks": {},
  "judge_scores": {},
  "human_review": null,
  "latency_ms": null,
  "input_tokens": null,
  "output_tokens": null,
  "cost": null
}
```

## 6. Recommended first experiment

Use a practical software-factory task: **convert an Issue into a testable implementation plan**.

- Dataset: 50 anonymized Issues, including incomplete/ambiguous examples.
- Prompt arms: minimal baseline, explicit instruction, structured JSON output, few-shot, structured + rubric self-check.
- Fixed: same model/version and generation settings; no tools, RAG, repository browsing, or fine-tuning.
- Primary metrics: acceptance-criteria testability, required-field completeness, unsupported-assumption rate, and valid JSON rate.
- Secondary metrics: human preference, latency, tokens/cost, and prompt-paraphrase robustness.
- Evaluation: deterministic schema validator + rubric judge + blind human review of a stratified 20% sample.
- Decision: choose the simplest prompt that clears quality thresholds; do not automatically choose the longest or highest-scoring single run.

## 7. Risks and open questions

- Prompt effects may not transfer across model versions or tasks.
- Few-shot examples can leak answers or overfit to the evaluation set.
- LLM judges may reward style/verbosity rather than correctness and may prefer outputs resembling their own.
- Repeated sampling can inflate costs and make comparisons unfair unless inference budgets are matched or reported.
- Benchmark contamination and data leakage can create misleading gains.
- A prompt that improves average score may worsen rare but important failures.
- "LLM-only" must be operationally defined in each experiment; tools, memory, retrieval, and hidden system instructions can change the treatment.

## 8. Sources to verify next

- Prompt surveys: [Vatsal & Dubey (2024)](https://arxiv.org/abs/2407.12994), [Sahoo et al. (2024)](https://arxiv.org/abs/2402.07927)
- Prompt robustness: [PromptRobust (2023)](https://arxiv.org/abs/2306.04528)
- Reasoning prompts: [Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916), [Chain-of-Thought](https://arxiv.org/abs/2201.11903), [Self-Consistency](https://arxiv.org/abs/2203.11171)
- LLM judges: [G-Eval](https://aclanthology.org/2023.emnlp-main.153/), [MT-Bench / Chatbot Arena](https://arxiv.org/abs/2306.05685), [Human vs LLM judges](https://aclanthology.org/2024.emnlp-main.474/), [Position bias study](https://aclanthology.org/2025.ijcnlp-long.18/)
- Evaluation practice: [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

