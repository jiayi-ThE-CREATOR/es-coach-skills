# セクション 4「部門・職種マップ」の必須フォーマット（最重要）

セクション 4 は **このレポートの中核**。**X.0 として「全体概観図」を最初に置き**、その後で各部門ごとのサブセクションに展開する。

---

## X.0 部門全体概観図（必ずセクション冒頭に配置）

各部門を **フロント / ミドル / バック** の 3 層に分類した Mermaid ピラミッドを生成する。情報源は **対象企業の公式「Divisions」または「Our Businesses」ページ**を優先（例：GS なら https://www.goldmansachs.com/japan/careers/divisions、MS なら corp.morganstanley.com/careers/divisions）。

JS レンダリングで取得できない場合は、`curl` で生 HTML を取得し、`grep -oE '[ア-ン・ー]+部門[^"<>]*'` 等で部門名と説明を抽出する。

**3 層分類の判定基準**：

| レイヤー | 判定基準 | 代表例 |
|---------|---------|--------|
| フロント | 顧客接点があり、収益を直接生む | IBD、Markets、Research、Asset Management |
| ミドル | リスク・統制・規制対応を担う | Risk、Compliance、Controllers、Legal、Audit |
| バック | 実行・基盤・人事を担う | Operations、Engineering、Finance、HR、Real Estate |

**Mermaid テンプレ**（このまま使用、企業固有部門名のみ差し替え）。プレビュー: [assets/kigyou-report-orgchart-template.svg](../../../assets/kigyou-report-orgchart-template.svg)（GitHub 上でこのコードブロックがライブ Mermaid として描画されない場合があるため、静止画も置いている。Obsidian にコピーする分にはこの下の生テキストをそのまま使う）：

```mermaid
flowchart TB
    C(["顧客<br/>法人 / 機関投資家 / 富裕個人"])

    subgraph L1["▼ フロントオフィス（顧客接点・収益創出）"]
        direction LR
        F1["部門名1<br/>業務"]
        F2["部門名2<br/>業務"]
        F3["..."]
    end

    subgraph L2["▼ ミドルオフィス（リスク・統制）"]
        direction LR
        M1["Risk"]
        M2["Compliance"]
        M3["..."]
    end

    subgraph L3["▼ バックオフィス（業務基盤）"]
        direction LR
        B1["Operations"]
        B2["Engineering"]
        B3["..."]
    end

    C ==>|"取引・運用依頼"| L1
    L1 ==>|"取引承認依頼"| L2
    L2 ==>|"執行指示"| L3
    L3 -.->|"基盤・データ提供"| L1
    L2 -.->|"監督・チェック"| L1

    style L1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style L2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style L3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style C fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

**続けて必須**：
- **部門一覧テーブル**：全 N 部門を「レイヤー / 部門名 / 公式説明 1 行要約」の 3 列で列挙
- **協働シナリオ 3 例**：`> [!example]` で「主要取引（M&A、トレード、新商品開発等）が部門間をどう流れるか」を矢印付き 1-2 行で示す
- **就活生視点 tip**：図全体から読み取れる戦略的示唆を 3-4 点

---

## X.1 以降：各部門サブセクション

X.0 の後で、各部門ごとに **1 つの独立サブセクション**を作り、以下の構造を厳守する：

```markdown
### 4.X 部門名（英略 / 正式英名）

> [!quote] 公式（goldmansachs.com 等の正式ソース）
> **<原文（英語）の主要パラグラフをそのまま引用>**

> [!quote] 公式 — <サブテーマ>（任意：ランキング、業績、サブ部門説明等）
> **<追加引用>**

**業務の本質**（1-2 段落、私の補足解釈）：<業務内容、収益源、組織内位置づけ>

#### サブ業務 / プロダクト領域

| 領域 | 内容 / 公式引用 |
|------|---------------|
| <サブ1> | "<公式短文引用 or 私の説明>" |
| <サブ2> | ... |

**日本拠点の特性**（任意）：<日本特有の事情、リーダー名、最近の組織変動>

> [!tip] 就活生視点
> <この部門を志望するうえでの 1-3 文の助言>
```

## 引用ルール

- **公式引用 ≥ 解説**：1 サブセクション内で **引用ブロックの行数 ≥ 私の解説の行数**
- **原文優先**：英語ソースは英語のまま `**bold**` で引用、日本語意訳は補足としてカッコ書き
- **出典明示**：各 `> [!quote]` の冒頭に「公式（goldmansachs.com / <ページ名>）」と明記
- **改変禁止**：引用文の語句を改変せず、省略する場合は `...` を使う
- **複数ソース**：同じ部門に対し公式・業界紙・社員ブログなど複数ソースがあれば、全て引用ブロックで並列

## 取得すべき公式ページ（例：GS の場合）

```bash
# defuddle で並列取得
defuddle parse "https://www.goldmansachs.com/what-we-do/our-businesses" --md
defuddle parse "https://www.goldmansachs.com/what-we-do/investment-banking" --md
defuddle parse "https://www.goldmansachs.com/careers/our-firm/engineering" --md
defuddle parse "https://www.goldmansachs.com/careers/our-firm/global-investment-research" --md
defuddle parse "https://www.goldmansachs.com/careers/our-firm/operations" --md
# 他、各部門の専用ページ
```

日本語公式ページは JS レンダリングで取得困難な場合がある → **グローバル英語ページを優先**。

## 部門サブセクションの後に必須

- **3.X 部門サマリー比較表**：全部門を 1 つの表で横断比較（顧客 / 収益源 / 新卒倍率 / 数字力 / 英語要求）。**`/es-coach` が志望部門を特定できないときここを読むので、必ず作る**
- **出典コールアウト**：`> [!important] 出典` で「公式英文ページから取得、和訳は補足のため意訳を含む」と明記
