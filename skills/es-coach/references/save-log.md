# Phase 8 — 添削ログへの保存

ユーザーが「はい」または「保存して」と言った場合のみ実行する。

ファイル名：`YYYY-MM-DD_[設問略称]_[志望先略称].md`（`VAULT_SHUKATSU_HIKAKU_LOG` 配下）
例：`2026-05-08_ガクチカ_GS.md`

**保存前に `$SKILLS_ROOT/tools/count_chars.py` で最終字数を確認**し、フロントマターの schema を必ず揃える（横断スキャンが将来数十件でも効くように）：

```markdown
---
date: YYYY-MM-DD
company: [志望先（正式名でよい）]
company_normalized: [横断マッチ用の正規化キー。英語正式名で統一。例：Goldman Sachs / Morgan Stanley。表記揺れ（MS / モルガン…）を吸収する]
question: [設問文]
question_type: [ガクチカ / 自己PR / 志望動機 / 長所短所 / その他]
final_version: [最終バージョン番号]
final_score: [S / A / B / C / D のいずれか1つ。「S相当」等の曖昧表記は使わない]
outcome: 未定   # 選考結果が判明したら 通過 / 落選 / 辞退 に更新（手動回填）
outcome_date:   # outcome が確定した日付
outcome_components: # この選考で ES と一緒に評価されたもの。「ES単独」/「ES + Webテスト」/「ES + 動画」等。ES単独でなければ outcome は ES の成績とは言えない（交絡）
episodes_used: [E1, E2] # このESで使った本人エピソードのID（経験インベントリの E 番号）。sync がここから使用状況を集計する。新エピソードなら先にインベントリへ定義を追加
weaknesses: [初稿〜途中で指摘した主要弱点をキーワードで列挙。次回 Phase 4 の横断スキャン用。例：結論が弱い, 数字がない, 企業理念に触れていない]
---

# ES添削ログ

## 設問
[設問文]

## 修正履歴

### v1（初稿）
[v1のES文]

**添削レポート（v1）要約：**
[v1の総合評価 + 主要改善点]

### v2（あれば）
[v2のES文]

**添削レポート（v2）要約：**
[v2の総合評価 + 改善された点 + 残課題]

...（バージョン数だけ繰り返す）

## 最終版（v[n]）
[最終バージョンのES文]

## コーチ総評
[最終添削レポートの内容]
```

**保存後、使用状況を自動更新する**：ログ frontmatter の `episodes_used` にこのESで使ったエピソードIDを記録し（新しい経験なら先にインベントリの「核となる経験」へ E＋番号で定義を追加）、`$SKILLS_ROOT/tools/experience_inventory_sync.py` を実行する。使用回数・使用先はスクリプトがログから再集計するので、インベントリを手で数えて更新しない（真実の出所は `episodes_used` 一箇所）。

## outcome の回填と交絡（振り返り時の必須ルール）

過去ログの `outcome`（通過/落選）が未回填ならリマインドし、**その際 `outcome_components`（ES と一緒に何が評価されたか）も必ず聞く**。ES単独の選考でなければ、落選＝ESの問題とは言えない（Webテスト・動画等が原因の可能性）。

よって「S判定ESの通過率」を振り返るときは、**`outcome_components` が「ES単独」の案件だけを信号として扱い、Webテスト等が混ざった案件は参考外にする**。この区別をせずに通過率を語らない。
