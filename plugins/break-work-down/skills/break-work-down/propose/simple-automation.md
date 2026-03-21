# シンプルな自動化

リテラシー・コスト制限のある現場向けの自動化提案。

- **チーム/組織の場合**: 会社・チーム単位での業務改善に焦点を当てる。ワークフロー全体の最適化、ツール間連携、承認フローの簡素化等を検討する
- **フリーランス/個人事業主の場合**: 個人のワークフロー最適化に焦点を切り替える。チーム向けツール（Slack連携、チームプラン前提のSaaS等）ではなく、個人向けの自動化（IFTTT、テンプレート活用、予約投稿、バッチ処理等）を優先的に検索する

`config.json` の `analysis_scope` で判定する。

## 提案プロセス

1. Web検索で事例・手法を収集する — 対象業務のキーワードで検索し、下記の信頼性の高い専門メディアのドメインを優先的に参照する。ボトルネック業務が複数ある場合は、業務ごとにサブエージェントを割り当てて並行検索する（目安: 2〜3エージェント）
2. 収集した情報をもとに、対象業務に適した自動化手法を選定する
3. 提案としてまとめる
4. 提案の出力時に、参照したWebページのURLを情報源として添付する

---

## 情報源ドメイン

検索時に以下の専門メディアを優先的に参照する。一次情報よりも、情報が体系的にまとまった専門メディアを重視。

### DX・デジタル化

| ドメイン | メディア名 |
|---------|-----------|
| `itmedia.co.jp` | ITmedia ビジネスオンライン |
| `sbbit.jp` | ビジネス+IT |
| `brainpad.co.jp/doors/` | DOORS DX |
| `xtech.nikkei.com` | 日経クロステック |
| `japan.zdnet.com` | ZDNET Japan |
| `enterprisezine.jp` | EnterpriseZine |
| `dx-navigator.com` | DX Navigator |

### コンサル・経営視点

| ドメイン | メディア名 |
|---------|-----------|
| `mirai-works.co.jp` | freeconsultant.jp for Business |
| `nomura-system.co.jp` | Digital Library（NRI系） |
| `toyokeizai.net` | 東洋経済オンライン |
| `diamond.jp` | ダイヤモンド・オンライン |
| `tanabeconsulting.co.jp` | タナベコンサルティング |

### 業務自動化・ノーコード・RPA

| ドメイン | メディア名 |
|---------|-----------|
| `nocoderi.co.jp` | ノーコード総合研究所 |
| `dx-pro.resocia.jp` | DX-Pro |
| `rpatimes.jp` | RPA TIMES |
| `media-rpa.com` | RPA MEDIA |
| `bizx.chatwork.com` | ビズクロ |
| `liskul.com` | LISKUL |
| `dx.biztex.co.jp` | DXhacker |
| `rpa-technologies.com` | BizRobo! Insights |
| `ncpa.info` | ノーコード推進協会（NCPA） |

### ワークフロー・業務プロセス

| ドメイン | メディア名 |
|---------|-----------|
| `atled.jp/wfl/` | ワークフロー総研 |
| `intra-mart.jp/im-press` | IM-Press |

### GAS・VBA・スクリプト活用

| ドメイン | メディア名 |
|---------|-----------|
| `tonari-it.com` | いつも隣にITのお仕事 |
| `powerplatformknowledge.com` | Power Platform Knowledge |

### SaaS比較・レビュー

| ドメイン | メディア名 |
|---------|-----------|
| `boxil.jp` | BOXIL（ボクシル） |
| `itreview.jp` | ITreview |
| `it-trend.jp` | ITトレンド |
| `kigyolog.com` | 起業LOG SaaS |
| `saas.imitsu.jp` | PRONIアイミツ SaaS |

### 中小企業・実践事例

| ドメイン | メディア名 |
|---------|-----------|
| `bizhint.jp` | BizHint |
| `ai-kenkyujo.com` | DX/AI研究所 |
| `union-company.jp/media/` | Union Media |
| `012cloud.jp` | Wiz cloud |
| `tebiki.jp/genba/` | 現場改善ラボ |
| `chusho-dx.bcnretail.com` | 中小企業×DX |
| `sogyotecho.jp` | 創業手帳 |

### バックオフィス・人事労務・経理

| ドメイン | メディア名 |
|---------|-----------|
| `hrnote.jp` | HR NOTE |
| `officenomikata.jp` | オフィスのミカタ |
| `manegy.com` | Manegy |
| `obc.co.jp/360` | OBC360° |
| `g-soumu.com` | 月刊総務オンライン |
| `romsearch.officestation.jp` | 労務SEARCH |

### シンクタンク・定量調査

| ドメイン | メディア名 |
|---------|-----------|
| `mri.co.jp` | 三菱総合研究所 |
| `nri.com/jp/knowledge` | NRI ナレッジ |

### 公的機関・業界団体

| ドメイン | メディア名 |
|---------|-----------|
| `meti.go.jp` | 経産省 DXセレクション |
| `ipa.go.jp/digital/dx/` | IPA DX事例情報提供サイト |
| `tokyo-cci.or.jp/digital-support` | 東商デジタルシフト・DXポータル |
| `ittools.smrj.go.jp` | ここからアプリ（中小機構） |

---

## 提案前の確認事項

新ツール導入を提案する前に、以下を順にチェックする。既存環境で解決できるならそちらを優先し、提案のコスト・摩擦を最小化する。

| # | チェック項目 | 具体例 |
|---|---|---|
| 1 | **既存ツールの未活用機能はないか** | 会計ソフト（freee等）のレポート自動生成・API連携が未使用、Salesforceのワークフロールールが未設定 等 |
| 2 | **GAS等の追加費用ゼロの手段で実現可能か** | Google Workspace環境ならGAS、Microsoft環境ならPower Automate（無料枠） |
| 3 | **対象ツールの公式マーケットプレイスに連携ソリューションがあるか** | Shopifyアプリストア、kintoneプラグイン、Slack App Directory 等 |
| 4 | **NPO/非営利の場合、無償プランがあるか** | Google for Nonprofits、Microsoft Nonprofits、Canva for Teams、Slack Pro 等 |

---

## よくある判断ミス

### 1. 権限設定の壁

「Slackワークフローで自動化」と提案しても、現場に設定権限がないケースが多い。提案時にセットアップの責任者（ユーザー自身/情シス/外部委託）を明確にし、「ユーザー自身で今日からできること」と「情シスへの依頼事項」を分離する。大企業環境では承認プロセスと所要期間を注記する。

### 2. テンプレート化は例外ケースで破綻しやすい

通常ケース90%で効果が出る前提で見積もる。「100%削減」は避ける。

### 3. 「試す気力」の見積もり

ノーコードツールが「簡単」なのはリテラシー中程度以上の場合。低リテラシーではサポート体制とセットで提案する。

### 4. 業界固有システムの情報源不足

製造業（CAQ、SPC）、物流（WMS）、教育（学務システム）等では、汎用SaaS比較サイトでは情報が不足する。業界特化メディアやIPA/経産省のDX事例を優先的に検索する。
