# サンプル出力 — kigyou-report が生成する企業分析レポート（抜粋）

> `/kigyou-report <企業名>` はフルレポートで 12 セクション・2〜4 万字になります。全文を載せると長すぎるため、ここでは構成が伝わる範囲で**架空の企業「サンプル証券株式会社」**を使った抜粋のみを示します。

```markdown
---
company: サンプル証券株式会社
company_en: Sample Securities
tier: A
industry: 外資系金融
country: 米国 / 日本拠点
report_type: 企業分析レポート
target_year: 28卒
generated: 2026-01-10
sources: Web / Vault素材
tags:
  - 就活
  - 金融
  - サンプル証券
---

# サンプル証券株式会社

> [!success] 一言で言うと
> データドリブンな意思決定を掲げる外資系証券。新卒採用ではケース面接よりも「数字で語れるか」を重視する傾向が強い（架空設定）。

## 4. 部門・職種マップ（抜粋）

### 4.0 部門全体概観図

\`\`\`mermaid
flowchart TB
    C(["顧客<br/>法人 / 機関投資家"])
    subgraph L1["▼ フロントオフィス"]
        direction LR
        F1["Investment Banking<br/>資金調達助言"]
        F2["Markets<br/>トレーディング"]
    end
    subgraph L2["▼ ミドルオフィス"]
        direction LR
        M1["Risk"]
    end
    subgraph L3["▼ バックオフィス"]
        direction LR
        B1["Operations"]
    end
    C ==>|"取引依頼"| L1
    L1 ==>|"承認依頼"| L2
    L2 ==>|"執行指示"| L3
\`\`\`

### 4.1 Investment Banking（IBD）

> [!quote] 公式（sample-securities.example.com/careers）
> **"Our Investment Banking professionals advise clients on capital raising and strategic transactions."**（架空の引用）

**業務の本質**：企業の資金調達・M&A を助言する部門。日本拠点では特に製造業クライアントの海外展開案件が多いとされる（架空設定）。

> [!tip] 就活生視点
> IBD 志望なら「なぜ助言業務なのか」「なぜ事業会社の中の人ではなく外から支援する側なのか」を自分の言葉で説明できるようにしておく。

## 6. 企業理念・求める人材像（抜粋）

> [!quote] 公式 — 求める人物像
> **"We look for people who make decisions based on data, not instinct."**（架空の引用）

内定者の共通パターンとして、面接で聞かれた質問に対して感覚的な回答ではなく、必ず数字・根拠を添えて答える傾向がある（蒸留知識より）。
```

## この後どう使われるか

`/es-coach` の Phase 4 は、このレポートの該当部門セクションと「6. 企業理念・求める人材像」だけを `grep`/`Read` の offset で部分読みし、ES がこの企業理念に刺さっているかを判定します。全文フォーマットは [kigyou-report/SKILL.md](../skills/kigyou-report/SKILL.md) の Step 5 を参照。
