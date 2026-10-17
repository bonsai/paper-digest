# LLMのみのプロンプト手法・評価研究リスト

> 更新日: 2026-10-18  
> 目的: モデルの重み・バージョンを固定し、プロンプト設計と評価手法を比較するための独立した文献リスト。  
> 状態: 調査候補。全文読解・PDF取得・実験再現が完了したことを意味しない。機械処理向けデータは [JSONL版](prompt-only-llm-evaluation-list.jsonl) を参照。

## 選定範囲

- 中心テーマは、プロンプト手法、プロンプトの頑健性、生成結果の評価。
- 基本比較ではモデル・設定・データを固定し、プロンプト要因を比較する。
- ツール、RAG、外部検索、ファインチューニングはプロンプト単独の実験と混ぜない。
- Self-Consistencyや別呼び出しのLLM-as-a-Judgeは、単一呼び出しのプロンプト手法とは分けて比較する。
- 論文URLがあることと、本文を読んだこと・PDFを取得できたことは別。PDFを保存する場合は利用条件を確認する。

## A. プロンプト手法・体系化

| 優先度 | 研究 | 主題・読むポイント | 出典 |
|---|---|---|---|
| P0 | A Survey of Prompt Engineering Methods in Large Language Models for Different NLP Tasks (Vatsal & Dubey, 2024) | プロンプト手法の分類。手法マップの起点 | [arXiv](https://arxiv.org/abs/2407.12994) |
| P0 | A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications (Sahoo et al., 2024) | 技法、用途、長所・限界、未解決課題 | [arXiv](https://arxiv.org/abs/2402.07927) |
| P0 | Large Language Models Are Zero-Shot Reasoners (Kojima et al., NeurIPS 2022) | Zero-shot CoTをプロンプト介入として検討 | [論文](https://papers.neurips.cc/paper_files/paper/2022/hash/8bb0d291acd4acf06ef112099c16f326-Abstract-Conference.html) |
| P0 | Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (Wei et al., 2022) | Few-shotの推論例示とタスク依存の効果 | [arXiv](https://arxiv.org/abs/2201.11903) |
| P1 | Self-Consistency Improves Chain of Thought Reasoning in Language Models (Wang et al., ICLR 2023) | 複数出力の集約。追加呼び出しを使う比較条件として扱う | [Google Research](https://research.google/pubs/self-consistency-improves-chain-of-thought-reasoning-in-language-models/) |
| P0 | PromptRobust: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts (2023) | 言い換え、誤字、小さな変更への頑健性 | [arXiv](https://arxiv.org/abs/2306.04528) |

## B. 生成結果の評価・LLM-as-a-Judge

| 優先度 | 研究・資料 | 主題・読むポイント | 出典 |
|---|---|---|---|
| P0 | G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment (Liu et al., EMNLP 2023) | ルーブリック型評価、人間評価との整合、評価者バイアス | [ACL Anthology](https://aclanthology.org/2023.emnlp-main.153/) · [PDF](https://aclanthology.org/2023.emnlp-main.153.pdf) |
| P0 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (Zheng et al., NeurIPS 2023) | ペア比較、人間との一致、順序・冗長性バイアス | [NeurIPS](https://papers.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html) · [arXiv](https://arxiv.org/abs/2306.05685) |
| P0 | Humans or LLMs as the Judge? A Study on Judgement Bias (Chen et al., EMNLP 2024) | 人間とLLMの評価バイアス比較 | [ACL Anthology](https://aclanthology.org/2024.emnlp-main.474/) |
| P0 | Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge (Shi et al., 2025) | 評価順序を入れ替えたときの一貫性・安定性 | [ACL Anthology](https://aclanthology.org/2025.ijcnlp-long.18/) |
| P1 | A survey on LLM-as-a-judge (2025/2026 publication record) | 評価者の信頼性、一貫性、バイアス分類 | [Open-access article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13237853/) |
| P0 | Evaluation best practices (living technical guidance) | 代表性あるテストデータ、明示的基準、失敗分析、継続評価 | [OpenAI developer guide](https://developers.openai.com/api/docs/guides/evaluation-best-practices) |

## C. このリストから比較する手法

### 単一呼び出し・プロンプト中心

- **P0 最小ベースライン**: タスク指示のみ。
- **P1 明示的指示**: 目的、対象読者、範囲、成功条件を明示。
- **P2 構造化出力**: 必須項目やJSON Schemaなどの形式を指定。
- **P3 Few-shot**: 入出力の例を少数追加。
- **P4 タスク分解**: サブタスクやチェックリストを指定し、最終出力を評価する。
- **P5 ルーブリック／セルフチェック**: 客観的な確認項目を含める。
- **P6 言い換え頑健性**: 意味を保った指示の言い換えで性能の揺れを測る。
- **P7 曖昧さ・例外への対応**: 不明情報の明示、保留、追加確認の基準を指定。

### 別枠にする複数呼び出し手法

- Self-Consistency（複数生成の集約）
- Generate-then-judge / revise（生成後に別呼び出しで評価・修正）
- LLM-as-a-Judge（別の評価プロンプトで採点）

## D. 評価方法の候補

| 方法 | 適用例 | 主な指標 | 注意点 |
|---|---|---|---|
| 正解照合・決定的チェック | 分類、抽出、計算、スキーマ | Accuracy、完全一致、合格率 | 言い換えに厳しすぎる場合がある |
| タスク別ルーブリック | 要約、説明、実装計画 | 基準ごとの合格率・スコア | 基準が曖昧だと評価が揺れる |
| ブラインド二者比較 | 自由形式の回答 | 勝敗・引き分け・選好率 | 提示順と長さのバイアス |
| LLM評価者 | 大量のルーブリック採点 | 基準別スコア、人間との一致 | 人間の抜き取り評価で妥当性確認が必要 |
| 人手レビュー | 主観的・重要な判断 | 一致度、選好、エラー分類 | コストと評価者間の不一致 |
| 頑健性テスト | 言い換え、誤字、境界事例 | 性能低下、分散、一貫性 | 意味まで変えないよう注意 |
| 運用指標 | 実サービス向けプロンプト | 遅延、トークン、成功1件あたりコスト、再試行率 | 安価・高速でも正しいとは限らない |

## E. 最初の実験案

**GitHub Issueをテスト可能な実装計画へ変換する**タスクで、プロンプト条件を比較する。

- データ: 曖昧・不完全な例を含む匿名化Issue 50件。
- 条件: 最小指示、明示的指示、構造化JSON、Few-shot、構造化JSON＋ルーブリック確認。
- 固定条件: 同じモデル／バージョン、同じ生成設定。ツール、RAG、リポジトリ閲覧、ファインチューニングなし。
- 主要指標: 受け入れ条件のテスト可能性、必須項目の網羅率、根拠のない仮定の割合、JSON妥当性。
- 副指標: ブラインド人手選好、遅延、トークン／コスト、言い換え頑健性。
- 評価: 決定的バリデータ＋ルーブリック評価＋層化抽出した20%の人手レビュー。
- 採用基準: 事前に品質閾値を定め、重大な品質・頑健性の悪化がなく、条件を満たす最も単純なプロンプトを選ぶ。

## F. 実験の最低限の記録

モデル名・正確なバージョン、日時、システム指示、温度などの生成設定、プロンプトの版／ハッシュ、データセット版、入力、出力、生の評価、評価者の版、遅延、トークン、コスト、失敗例、採否を記録する。評価ルーブリックは結果を見る前に定義し、LLM評価者だけを唯一の正解としない。

## 次の作業

1. 優先度P0の文献から原文と書誌情報を確認する。
2. 実験用データセットと評価ルーブリックを別ファイルで定義する。
3. モデル・設定を固定してベースラインを実行し、各プロンプト条件を比較する。
4. 成績だけでなく、頑健性・費用・失敗事例も含めて結果を記録する。
