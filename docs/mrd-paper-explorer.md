# MRD — Research & Engineering Knowledge Factory

- Status: Draft
- Product: `bonsai/paper-digest`
- Version: 0.2
- Primary audience: AI開発者、ソフトウェアファクトリー設計者、研究者、プロジェクト運営者
- Scope: 論文・技術記事・ブログ・OSSリポジトリ・実践事例を横断し、知識を再利用可能な開発成果物へ変換する。4コマ漫画は任意の出力形式。

## 1. ビジョン

論文や技術記事を単に要約するのではなく、根拠を保持したまま知識を比較・再構成し、PRD、ADR、GitHub Issue、実験計画、技術記事などへ変換するソフトウェアファクトリーを作る。研究知識をJEVの仮説・実験・評価・改善ループにつなぎ、学びを次の実装へ戻す。

**PDFが一次情報、チャンク・グラフ・要約・インサイトはすべて派生物**として扱う。すべての重要な主張は、元論文・ページ・該当箇所まで戻れること。

## 2. 解決する課題

- PDFを個別に読むだけでは、10本を横断した比較や関係の発見に時間がかかる。
- 文章要約だけでは、論文・手法・データセット・評価指標のつながりを探索しにくい。
- RAGの回答が、根拠のない一般知識や誤った引用を混ぜるリスクがある。
- 「インサイト」と「単なるキーワードの共起」「AIが生成した推測」が混同されやすい。
- 論文の読み込み状態や抽出失敗が見えないと、分析結果の信頼性を評価できない。

## 3. 対象ユーザーとジョブ

ユーザーが達成したいこと：

1. 10本のPDFを登録し、正常に読めたページ・失敗したファイルを確認する。
2. 論文ごとの目的、手法、データ、評価指標、限界を比較する。
3. 動的なグラフから、論文・キーワード・手法・データセット・評価指標の関係を探索する。
4. 「この10本では何が共通しているか」「結果が矛盾するのはどこか」などを質問し、引用付きで回答を得る。
5. 根拠・反証・限界を確認しながら、研究上のインサイト候補を選別する。
6. 結果と中間データをCSV/JSONL/HTMLなどで出力し、再現できるようにする。

## 4. MVPの価値と成功基準

### 必須の成果

- 登録したPDF 10本それぞれについて、ファイル名・ハッシュ・ページ数・抽出状態を確認できる。
- 抽出テキストの各チャンクから、元PDFとページへ追跡できる。
- グラフ上のノード選択から、関連論文・根拠チャンクへ移動できる。
- RAG回答に論文名、ページ番号、該当抜粋が表示される。
- 根拠がない質問には「このコーパスからは確認できない」と回答する。
- インサイト候補に、主張・根拠・解釈・限界・反証候補・次の検証質問が記録される。
- 実行ごとにコーパスのハッシュ、依存ライブラリ、抽出状態、実行日時を記録する。

### 初期の評価指標

- PDF処理完了率：10本中、成功・失敗・OCR必要を区別して10本すべての状態を表示できる。
- 引用検証：固定質問セットに対し、人手で根拠箇所と回答の対応を判定する。
- 引用付き回答率：回答可能な質問に出典が付いている割合。
- 不回答の適切さ：コーパスに根拠がない質問を無理に回答しない割合。
- グラフ到達性：選択したノードから関連論文・ページ根拠に到達できるか。
- インサイト採用率：人が確認した候補のうち、根拠が十分で調査継続に値すると判断した割合。

初期の数値は目標値としてPRDの評価計画で定める。実測していない結果を実績として表示しない。

## 5. MVPの機能範囲

### In scope

- PDF 10本の登録・ファイル検証・SHA-256記録
- ページ単位のテキスト抽出と抽出状態表示
- 論文メタデータ、チャンク、キーワードの構造化
- 動的グラフとフィルター
- キーワード・全文検索およびRAG質問
- 引用付き回答と根拠箇所へのナビゲーション
- 共通点・相違点・矛盾候補・研究ギャップ候補の整理
- CSV、JSONL、HTML等のエクスポート
- Kaggleでの再現可能な実行経路

### Out of scope

- 最初から研究分野全体を代表すると主張すること
- 10本だけを根拠に分野全体の比率やトレンドを断定すること
- PDFの著作権・利用条件を無視したアップロードや再配布
- 論文の正しさをAIだけで確定すること
- モデルの学習・ファインチューニング
- 有料API、GPU、常時稼働サーバーを必須にすること
- スキャンPDFへのOCRを初期リリースの必須要件にすること
- グラフ上の近さを因果関係や研究的重要度とみなすこと

## 6. プロダクト原則

1. **出典優先**：主張には検証可能な根拠を付ける。
2. **不確実性を表示**：事実、論文著者の主張、システムの解釈、未確認を区別する。
3. **反証可能性**：インサイトには反証・別解釈・次の検証を含める。
4. **関係の型を区別**：共起、引用、意味的類似、データセット使用、評価指標使用を別のエッジとして扱う。
5. **再現性**：入力ファイルのハッシュと処理設定を記録する。
6. **小さく・無料で始める**：ローカルまたはKaggle、オープンソースを優先する。
7. **人間が最終判断**：AIは発見候補を提案するが、研究上の結論を自動確定しない。

## 7. 前提・リスク

- 10本のPDFはユーザーが選定・提供する。具体的なPDFと利用許諾は開始時に確認する。
- PDFからのテキスト抽出は数式・図表・段組み・脚注を完全には復元できない場合がある。
- キーワード抽出は誤検出や同義語の分裂が起きる。
- 生成モデルを使う場合、回答の流暢さは正確性を保証しない。
- 「研究ギャップ」はコーパス内の不足を示す候補であり、研究分野全体に存在しないことを意味しない。

## 8. 初期ユーザーフロー

PDF登録 → 抽出状態を確認 → 論文カードを確認 → グラフで関係を探索 → 質問して根拠を読む → インサイト候補を保存・反証確認 → エクスポート。

## 9. 未決事項

- 実際に使用する10本のPDFとライセンス
- Kaggle Datasetとして保持するか、セッションへアップロードするか
- RAG回答生成に使うモデルと、検索のみで動かすフォールバック
- グラフをノートブック内に置くか、静的HTMLとして共有するか
- OCRを後続版で追加するか


## 10. R2V source corpus and Kaggle ML extension (v0.3)

### Source of seed papers

Use `bonsai/r2v/papers.yaml` as the research catalog of record for seed-paper metadata and research intent, and `bonsai/r2v/rag/papers.yml` as the source of explicit PDF download URLs for the three existing RAG seed papers. Mirror source metadata into `data/sources/r2v-papers.yaml` with the original record URL, canonical paper URL, PDF URL when verified, and download status.

The source manifest now contains **14 candidate records**: 9 mirrored from `bonsai/r2v` and 5 additions spanning Toyota/management, team learning, and human-AI collaboration. This is a candidate list, not a claim that 14 PDFs are downloadable or approved. Direct PDF URLs and license/access status for the five additions remain unverified. Select a balanced set of 10, verify each file and its terms, then report the corpus as complete only after 10 valid PDFs are available.

### Kaggle ML use cases

Kaggle is the experimental environment for CPU-friendly baseline ML on the small corpus, not the canonical data store. The first ML iteration focuses on:

1. **Keywording:** TF-IDF/keyphrase baseline, term normalization, per-paper keyword candidates, and optionally unsupervised grouping. Keep the source chunk and page for every candidate keyword.
2. **Intent classification:** classify research questions/queries into explicit intents such as `summarize`, `compare`, `find_method`, `find_dataset`, `find_metric`, `find_limitations`, `find_evidence`, and `identify_gap`.
3. **Evaluation:** manually review keyword precision and intent labels; compare the ML candidate with a simple lexical baseline.
4. **Human-in-the-loop:** label corrections become the training/evaluation dataset; model outputs are suggestions, not ground truth.

Ten papers are too few to justify a reliable supervised model from paper count alone. Keywording should begin with unsupervised/lexical baselines. Intent classification requires a separately maintained, manually reviewed query-label dataset and must report the small-sample limitation. Never manufacture evaluation scores or treat synthetic examples as real user behavior.


## 11. Software factory and article corpus extension (v0.4)

### Product positioning

This project is a research-to-engineering knowledge factory, not a paper-summary or comic-generation product. Four-panel comics and other accessible explainers are optional publication formats. The primary outcome is reusable, traceable knowledge that can inform software design, implementation, evaluation, and process improvement.

### Supported source types

- Academic papers and preprints
- Engineering articles, technical blogs, and design notes
- Official engineering blogs and product documentation
- Open-source repositories, READMEs, ADRs, and workflow examples
- Case studies about software factories, agent factories, continuous engineering, and organizational learning

Each source record must include a source type, canonical URL, publication/update date when available, author or publisher, access status, license/usage notes, claims, evidence pointers, and review state. A web article is not automatically peer-reviewed evidence. Keep author claims, independently supported facts, project interpretation, and unverified claims distinct.

### Software factory themes

1. Spec-driven development: turning goals into requirements, acceptance criteria, and implementation plans.
2. Agentic software engineering: role-scoped agents, task orchestration, context handoff, and human review.
3. GitHub-native automation: issue triage, documentation maintenance, tests, CI failure investigation, and draft pull requests.
4. Continuous quality: deterministic CI/CD plus agent-assisted work, security boundaries, observability, and evaluation.
5. Knowledge reuse: reusable templates, repository conventions, ADRs, catalogues, and cross-repository learning.
6. Organizational learning: small experiments, psychological safety, feedback, and continuous improvement.

### JEV connection

Treat JEV as the user's own experiment/development loop; do not expand the acronym without an explicit definition. For each useful source, capture:
- hypothesis or design proposition
- experiment or implementation to try
- expected observable outcome
- metric or review method
- result and limitations
- decision: adopt, adapt, reject, or investigate further

A source should not be considered validated merely because it was summarized. Record the link from source → hypothesis → experiment → evidence → decision.

### Output artifacts

- PRD/MRD and acceptance criteria
- ADRs and architecture diagrams (Mermaid/PlantUML)
- GitHub Issues and implementation checklists
- Experiment plans, evaluation rubrics, and result summaries
- Engineering articles, explainers, and optional comics
- Structured JSONL/YAML catalogues for reuse across repositories

### Success criteria additions

- Every extracted claim links to a source URL and, for PDFs, page/chunk evidence where available.
- Articles and peer-reviewed papers are distinguishable in search results and exports.
- At least one source can be traced through a hypothesis or design proposition to a recorded experiment/decision.
- Generated artifacts remain drafts until human review; source collection never automatically authorizes code changes or merges.
