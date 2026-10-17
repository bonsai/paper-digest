# 論文候補リスト

> 更新日: 2026-10-18  
> 目的: 論文を根拠付きで読み、専門用語を日常語に焼き直して4コマ漫画にする。  
> 状態: **候補14本。10本のPDFコーパスは未確定。** URLがあることと、PDFの取得・再配布が許可されていることは別。

## 選定方針

- AI動画生成だけに閉じず、経営学・組織論・人間とAIの協働も扱う。
- 4コマにしやすい「身近な疑問 → 問題 → 研究の工夫/発見 → 意味と限界」を作れる論文を優先。
- すべての説明を原文のページに結びつける。たとえ話と論文の事実は区別する。
- PDF取得時にHTTPステータス、PDFシグネチャ、ファイルサイズ、SHA-256、利用条件を確認する。
- PDF未取得の候補を「読み込み済み」と扱わない。著作権上の確認前にPDFや全文をリポジトリへコミットしない。

## A. R2V・動画生成研究（9本）

| 論文 | 年 | PDF/出典 | 状態 | 4コマの切り口 |
|---|---:|---|---|---|
| Scaling Zero-Shot Reference-to-Video Generation (SABER) | 2025 | [PDF](https://arxiv.org/pdf/2512.06905) · [概要](https://arxiv.org/abs/2512.06905) | URL候補あり・未取得 | 見本の画像から動画を作ると何が難しい？ |
| RefAlign: Representation Alignment for Reference-to-Video Generation | 2026 | [PDF](https://arxiv.org/pdf/2603.25743) · [概要](https://arxiv.org/abs/2603.25743) | URL候補あり・未取得 | 見本と生成動画のズレをどう減らす？ |
| OmniVBench: A Benchmark and Large-Scale Dataset for Omni Reference-to-Video Generation | 2026 | [PDF](https://arxiv.org/pdf/2609.22069) · [概要](https://arxiv.org/abs/2609.22069) | URL候補あり・未取得 | AI動画の出来ばえをどう公平に比べる？ |
| VBench: Comprehensive Benchmark Suite for Video Generative Models | 2024 | [論文ページ](https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html) | 直接PDF URL要確認 | 「きれい」だけで動画AIを評価していい？ |
| EvalCrafter | 2024 | [公式ページ](https://evalcrafter.github.io/) | 直接PDF URL要確認 | AI動画の評価を人の感想だけに頼らない方法 |
| Video-Bench | 2025 | [論文ページ](https://mlanthology.org/cvpr/2025/han2025cvpr-videobench/) | 直接PDF URL要確認 | 動画の良し悪しをどう測る？ |
| Face Consistency Benchmark | 2025 | [PDF](https://arxiv.org/pdf/2505.11425) · [概要](https://arxiv.org/abs/2505.11425) | URL候補あり・未取得 | 動画の途中で顔が変わる問題をどう測る？ |
| OpenS2V-Nexus | 2025 | [論文ページ](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dae77d03bd51a5acfe8519848a3af6c9-Abstract-Datasets_and_Benchmarks_Track.html) | 直接PDF URL要確認 | 1枚の画像から動画を作るとき何が必要？ |
| ControlNeXt | 2024 | [PDF](https://arxiv.org/pdf/2408.06070) · [概要](https://arxiv.org/abs/2408.06070) | URL候補あり・未取得 | AIの生成結果を、どう狙いどおりに動かす？ |

## B. 経営学・組織論・人間とAI（追加5本）

| 論文 | 年 | PDF/出典 | 状態 | 4コマの切り口 |
|---|---:|---|---|---|
| Inter-Organizational Knowledge Sharing and Creation in Toyota Group（トヨタ自主研にみる組織間知識共有・知識創造マネジメント） | 2022 | [PDF](https://www.jstage.jst.go.jp/article/seisankanri/29/1/29_7/_pdf/-char/en) · [論文ページ](https://www.jstage.jst.go.jp/article/seisankanri/29/1/29_7/_article/-char/en) | OA候補・取得/ライセンス要確認 | 会社をまたいで、改善の知恵をどう共有する？ |
| The Evolution of Production Systems: Exploring the Sources of Toyota's Competitiveness | 2012 | [PDF](https://www.jstage.jst.go.jp/article/abas/11/0/11_25/_pdf) · [論文ページ](https://www.jstage.jst.go.jp/article/abas/11/0/11_25/_article/-char/en) | OA候補・取得/ライセンス要確認 | 作る力だけでなく、改善する力も育てる |
| Psychological Safety and Learning Behavior in Work Teams | 1999 | [著者資料候補PDF](https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Organizational_Learning_and_Change/Edmondson_1999_Psychological_safety.pdf) · [Harvard掲載ページ](https://dash.harvard.edu/entities/publication/13a7b031-0fdd-45ec-a7e0-2b80e2bc679f) | PDFアクセス/権利要確認 | 失敗や質問を言えるチームは、どう学ぶ？ |
| The Toyota Way in Services: The Case of Lean Product Development | 2006 | [出版社PDF候補](https://journals.aom.org/doi/pdf/10.5465/amp.2006.20591002) · [論文ページ](https://doi.org/10.5465/amp.2006.20591002) | アクセス制限の可能性・要確認 | 工場の改善方法を、企画やサービスにも活かせる？ |
| Complementarity in human-AI collaboration: concept, sources, and evidence | 2025 | [論文ページ（PDFリンクあり）](https://www.tandfonline.com/doi/full/10.1080/0960085X.2025.2475962) | 直接PDF URL未確定・OA条件要確認 | 人間とAIの得意分野を組み合わせると何が変わる？ |

## 次の作業

1. 候補14本から、テーマの偏りを見て対象10本を選ぶ。
2. PDFを実際に取得できるか確認し、利用条件とSHA-256を記録する。
3. PDFごとにページ付きテキストを抽出し、要約・漫画の各コマを根拠ページに紐づける。
4. まずはトヨタ自主研か心理的安全性の論文で、やさしい言葉の4コマ試作を行う。
