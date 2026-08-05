#!/usr/bin/env bash
# es-coach-skills セットアップ（何度実行しても安全 / idempotent）
#
#   ./setup.sh              セットアップを実行
#   ./setup.sh --check      何も書き換えず、現状の診断だけ出す
#
# やること：
#   1. vault.paths.env を用意（無ければ example からコピーして編集を促す）
#   2. vault 側のフォルダを作成（ここを作らないと初回起動でコケる）
#   3. seed の蒸留知識を配置（知識ファイルが 1 つも無いときだけ）
#   4. ~/.claude/skills へ symlink
#   5. python3 / pyyaml の確認

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
err()  { printf '  \033[31m✗\033[0m %s\n' "$1"; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }

FAILED=0

# ---------------------------------------------------------------- 1. env
step "1. vault.paths.env"

# plugin としてインストールされている場合、リポジトリ本体は更新のたびに差し替わる
# キャッシュディレクトリなので、設定は ~/.config/shukatsu-skills/ に置く（更新で消えない）
case "$REPO_ROOT" in
  */.claude/plugins/cache/*)
    IS_PLUGIN=1
    ENV_FILE="$HOME/.config/shukatsu-skills/vault.paths.env"
    [ "$CHECK_ONLY" = 1 ] || mkdir -p "$(dirname "$ENV_FILE")"
    ;;
  *)
    IS_PLUGIN=0
    ENV_FILE="$REPO_ROOT/vault.paths.env"
    ;;
esac
[ "$IS_PLUGIN" = 1 ] && ok "plugin としてインストール済み（設定は ${ENV_FILE}）"
if [ ! -f "$ENV_FILE" ]; then
  if [ "$CHECK_ONLY" = 1 ]; then
    err "vault.paths.env が未作成（example からコピーが必要）"
    FAILED=1
  else
    cp "$REPO_ROOT/vault.paths.example.env" "$ENV_FILE"
    ok "vault.paths.example.env → vault.paths.env を作成した"
    warn "この後 vault.paths.env を開き、VAULT_ROOT をあなたの Obsidian vault の実パスに書き換えてから、もう一度 setup.sh を実行してください"
    printf '\n  %s\n\n' "\$EDITOR \"$ENV_FILE\""
    exit 0
  fi
else
  ok "vault.paths.env はすでにある"
fi

# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a

if [ ! -d "${VAULT_ROOT:-}" ]; then
  err "VAULT_ROOT が存在しない: ${VAULT_ROOT:-（未設定）}"
  warn "vault.paths.env の VAULT_ROOT を実在する Obsidian vault のパスに直してください"
  exit 1
fi
ok "VAULT_ROOT: $VAULT_ROOT"

# ------------------------------------------------------------ 2. folders
step "2. vault 内フォルダ"

VAULT_KEYS="VAULT_SHUKATSU_DISTILL VAULT_SHUKATSU_SOZAI_YT VAULT_SHUKATSU_SOZAI_WEB VAULT_SHUKATSU_SOZAI_SELF VAULT_SHUKATSU_CHISHIKI VAULT_SHUKATSU_HIKAKU_LOG VAULT_SHUKATSU_ES VAULT_KIGYOU_REPORTS VAULT_MENSETSU_TAISAKU"

for key in $VAULT_KEYS; do
  dir="${!key:-}"
  if [ -z "$dir" ]; then
    err "$key が vault.paths.env に無い（テンプレートを更新してください）"
    FAILED=1
    continue
  fi
  if [ -d "$dir" ]; then
    ok "$key"
  elif [ "$CHECK_ONLY" = 1 ]; then
    warn "$key が未作成: $dir"
    FAILED=1
  else
    mkdir -p "$dir" && ok "$key を作成: ${dir#"$VAULT_ROOT"/}"
  fi
done

# --------------------------------------------------------------- 3. seed
step "3. seed 蒸留知識"

SEED_SRC="$REPO_ROOT/seed/全行業共通.md"
SEED_DST="${VAULT_SHUKATSU_CHISHIKI:-}/全行業共通.md"
existing_md=$(ls "${VAULT_SHUKATSU_CHISHIKI:-/nonexistent}"/*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$existing_md" != "0" ]; then
  ok "蒸留知識がすでに $existing_md 件ある（seed は配置しない）"
elif [ "$CHECK_ONLY" = 1 ]; then
  warn "蒸留知識が 0 件（seed 未配置）"
  FAILED=1
else
  cp "$SEED_SRC" "$SEED_DST" && ok "seed を配置: 全行業共通.md（source_count: 0 の一般論ベース）"
  warn "seed は公開情報だけの初期値です。/shukatsu-distill ingest で素材を入れるほど精度が上がります"
fi

# ------------------------------------------------------------- 4. skills
step "4. ~/.claude/skills への symlink"

if [ "$IS_PLUGIN" = 1 ]; then
  ok "plugin 版なので symlink は不要（skill は plugin として登録済み。/shukatsu:es-coach 等で起動）"
else

SKILLS_DIR="$HOME/.claude/skills"
[ "$CHECK_ONLY" = 1 ] || mkdir -p "$SKILLS_DIR"

for skill in es-coach shukatsu-distill kigyou-report mensetsu-report; do
  src="$REPO_ROOT/skills/$skill"
  dst="$SKILLS_DIR/$skill"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then
      ok "$skill"
    else
      warn "$skill は別の場所を指す symlink（手動で確認してください）: $(readlink "$dst")"
    fi
  elif [ -e "$dst" ]; then
    warn "$skill は symlink ではない実体がある。上書きしないので手動で確認してください: $dst"
  elif [ "$CHECK_ONLY" = 1 ]; then
    warn "$skill が未リンク"
    FAILED=1
  else
    ln -s "$src" "$dst" && ok "$skill をリンクした"
  fi
done

fi

# ------------------------------------------------------------- 5. python
step "5. Python"

if command -v python3 >/dev/null 2>&1; then
  ok "python3: $(python3 --version 2>&1)"
  if python3 -c 'import yaml' 2>/dev/null; then
    ok "pyyaml"
  else
    warn "pyyaml が無い（experience_inventory_sync.py に必要）: pip install pyyaml"
    FAILED=1
  fi
else
  err "python3 が見つからない（count_chars.py / experience_inventory_sync.py に必要）"
  FAILED=1
fi

# --------------------------------------------------------------- 仕上げ
step "結果"

if [ "$CHECK_ONLY" = 1 ]; then
  [ "$FAILED" = 0 ] && ok "問題なし" || warn "上の ! / ✗ を解消してから ./setup.sh を実行してください"
  exit "$FAILED"
fi

if [ "$FAILED" = 0 ]; then
  ok "セットアップ完了"
else
  warn "一部に警告あり（上を確認してください）"
fi

if [ "$IS_PLUGIN" = 1 ]; then PFX="/shukatsu:"; else PFX="/"; fi

cat <<NEXT

  次の一歩：Claude Code で

    ${PFX}shukatsu-distill ingest   内定者の体験談・YouTube・記事を素材として入れる（まずここから）
    ${PFX}kigyou-report <企業名>     志望企業の分析レポートを作る
    ${PFX}es-coach                  ES を添削してもらう
    ${PFX}mensetsu-report <企業名>   面接前の対策レポートを作る

  蒸留知識が seed（source_count: 0）のままだと、添削は一般論ベースになります。
  ingest を数回回すと「内定者の傾向」を根拠にした添削に変わります。

NEXT
