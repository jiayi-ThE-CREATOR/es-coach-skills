# es-coach-skills — 日本就活 ES 対話コーチ用 Claude Code Skills

[简体中文](README.zh.md) | **日本語**

日本就活（新卒採用）の ES（エントリーシート）対策を、[Claude Code](https://claude.com/claude-code) の Skill として自動化する3点セット。内定者の経験談から成功パターンを蒸馏（distill）し、それを根拠に ES を批改し、企業分析レポートで理念・求める人物像との適合を突き合わせる。

> これは個人の就活自動化プロジェクトから抽出した Skill 本体です。あなたの ES 内容・企業情報・vault の中身は含まれていません——すべてあなた自身の Obsidian vault に蓄積されます。

## 3つの Skill の関係

```
shukatsu-distill (ingest / grill)   kigyou-report
  内定者の経験談・本人の経験を         企業の理念・部門・求める人物像を
  素材として蓄積                      構造化レポートに整理
        │                                   │
        ▼                                   ▼
shukatsu-distill (distill)  ──────────►  蒸馏知識ファイル
        │                                   │
        └───────────────┬───────────────────┘
                         ▼
                     es-coach
              ES を受け取り、上記2つを根拠に批改
```

| Skill | 役割 |
|-------|------|
| `es-coach` | ES 文を対話的に批改（事実確認 → 評価 → 修正ループ → サインオフ）。蒸馏知識・企業分析レポート・本人の過去エピソードを根拠にする |
| `shukatsu-distill` | `ingest`（内定者体験談の取り込み）/ `distill`（成功パターンの抽出）/ `coach mock`（模擬面接）/ `grill`（逆面接で本人の経験を素材化）の4モード |
| `kigyou-report` | 指定企業を12セクション固定の構造化レポートに整理（部門マップ、企業理念、ES 攻略法など） |

3つとも Obsidian vault にデータを読み書きする前提で、vault 内のパスは `vault.paths.env` という**唯一のレジストリファイル**経由で解決する（vault の再編成をしても Skill 本文を書き換えずに済む設計）。

## 必要なもの

- [Claude Code](https://claude.com/claude-code)（Skills 機能）
- Obsidian（または同等の Markdown vault）
- Python 3（`tools/count_chars.py` と `tools/experience_inventory_sync.py` の実行に必要。`pyyaml` が要る）

## セットアップ

```bash
# 1. クローン
git clone <this-repo-url> es-coach-skills
cd es-coach-skills

# 2. このリポジトリの場所を環境変数として設定する（シェルの起動ファイルに追記）
echo 'export SHUKATSU_SKILLS_ROOT="'"$(pwd)"'"' >> ~/.zshrc
source ~/.zshrc

# 3. vault のパスを設定する
cp vault.paths.example.env vault.paths.env
$EDITOR vault.paths.env   # あなたの Obsidian vault の実際のパスに書き換える

# 4. Skill を Claude Code に認識させる（コピーでもシンボリックリンクでも可）
mkdir -p ~/.claude/skills
ln -s "$SHUKATSU_SKILLS_ROOT/skills/es-coach"        ~/.claude/skills/es-coach
ln -s "$SHUKATSU_SKILLS_ROOT/skills/shukatsu-distill" ~/.claude/skills/shukatsu-distill
ln -s "$SHUKATSU_SKILLS_ROOT/skills/kigyou-report"    ~/.claude/skills/kigyou-report

# 5. Python 依存関係
pip install pyyaml
```

セットアップ後、Claude Code で `/shukatsu-distill ingest` から始めるのがおすすめ（内定者の体験談・YouTube 動画の文字起こし・就活サイト記事などを投入 → 自動で蒸馏 → `/es-coach` で ES 批改、という流れ）。

## 使い方

```
/shukatsu-distill ingest      内定者の体験談・記事を素材として取り込む
/shukatsu-distill distill     素材から成功パターンを抽出・蒸馏知識に反映
/shukatsu-distill grill       逆面接形式であなた自身の経験を掘り起こして素材化
/shukatsu-distill coach mock  模擬面接
/kigyou-report <企業名>        企業分析レポートを生成
/es-coach                     ES を対話的に批改
```

## 蒸馏知識・素材はどこにある?

`vault.paths.env` で指定した vault 内に、あなた自身の就活の進行とともに蓄積されていく。このリポジトリにはロジック（Skill の指示文とヘルパースクリプト）だけが入っており、あなたの企業選考の内容・ES の実データは一切含まれない。

## ライセンス

MIT. `LICENSE` 参照。
