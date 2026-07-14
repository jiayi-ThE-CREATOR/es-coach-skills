#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""経験インベントリの「使用状況」を批改ログから自動再生成する。

真実の出所は各批改ログの frontmatter `episodes_used`（例: [E1, E2]）一箇所。
このスクリプトが全ログを走査して各エピソードの使用回数・使用先を集計し、
経験インベントリ.md の <!-- AUTO:USAGE:START --> 〜 END マーカー間だけを
書き換える。マーカー上の「核となる経験」定義（手動維持）は一切触らない。

これにより「別ファイルで使用回数を手で数えて更新し忘れる」漂移を根絶する。
es-coach は Phase 4（読込前）と Phase 8（ログ保存後）にこれを呼ぶ。

使い方：
  experience_inventory_sync.py            # 集計して書き換え
  experience_inventory_sync.py --check    # 書き換えず差分の有無だけ報告（終了コード）
"""
import re
import os
import sys
import glob
import argparse

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vault_paths import vault_path  # noqa: E402

START = "<!-- AUTO:USAGE:START -->"
END = "<!-- AUTO:USAGE:END -->"


def load_frontmatter(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return None


def build_section(defs, usage, unknown):
    lines = [
        START,
        "",
        "> `tools/experience_inventory_sync.py` が批改ログの `episodes_used` から自動生成。手で編集しない。",
        "",
    ]
    for eid in sorted(defs, key=lambda x: int(x[1:])):
        uses = usage.get(eid, [])
        lines.append("### %s. %s — 使用 %d 回" % (eid, defs[eid], len(uses)))
        if not uses:
            lines.append("- （未使用）")
        for fm in sorted(uses, key=lambda d: str(d.get("date", ""))):
            comp = fm.get("company_normalized") or fm.get("company") or "?"
            qt = fm.get("question_type") or "?"
            dt = fm.get("date") or "?"
            oc = fm.get("outcome") or "未定"
            ocomp = fm.get("outcome_components")
            tag = "結果:%s" % oc
            if ocomp:
                tag += "（%s）" % ocomp
            lines.append("- %s ／ %s （%s, %s）" % (comp, qt, dt, tag))
        lines.append("")
    if unknown:
        lines.append(
            "> ⚠️ 批改ログが未定義のエピソードIDを参照しています：%s。"
            "「核となる経験」に定義を追加してください。" % ", ".join(sorted(unknown))
        )
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="書き換えず差分有無のみ")
    args = ap.parse_args()

    log_dir = str(vault_path("VAULT_SHUKATSU_HIKAKU_LOG"))
    inv_path = os.path.join(str(vault_path("VAULT_SHUKATSU_SOZAI_SELF")), "経験インベントリ.md")

    if not os.path.exists(inv_path):
        print("経験インベントリが見つかりません: %s" % inv_path, file=sys.stderr)
        sys.exit(1)

    inv_txt = open(inv_path, encoding="utf-8").read()
    if START not in inv_txt or END not in inv_txt:
        print("AUTO マーカーが見つかりません。手で %s / %s を挿入してください。" % (START, END), file=sys.stderr)
        sys.exit(1)

    # 定義セクションから ID→タイトルを拾う（マーカーより前の ### E<n>. 見出しだけ）
    before_auto = inv_txt.split(START)[0]
    defs = dict(re.findall(r"^###\s+(E\d+)\.\s*(.+?)\s*$", before_auto, re.M))

    usage = {}
    unknown = set()
    for f in sorted(glob.glob(os.path.join(log_dir, "*.md"))):
        if f.endswith("_index.md"):
            continue
        fm = load_frontmatter(f)
        if not fm:
            continue
        eps = fm.get("episodes_used") or []
        if isinstance(eps, str):
            eps = [e.strip() for e in re.split(r"[,\s]+", eps) if e.strip()]
        for e in eps:
            e = str(e).strip()
            if not e:
                continue
            usage.setdefault(e, []).append(fm)
            if e not in defs:
                unknown.add(e)

    new_section = build_section(defs, usage, unknown)
    new_txt = re.sub(re.escape(START) + r".*?" + re.escape(END), new_section, inv_txt, flags=re.S)

    if new_txt == inv_txt:
        print("経験インベントリ 使用状況：変更なし")
        sys.exit(0)

    if args.check:
        print("経験インベントリ 使用状況：更新が必要（--check のため書き換えなし）")
        sys.exit(1)

    open(inv_path, "w", encoding="utf-8").write(new_txt)
    total = sum(len(v) for v in usage.values())
    print("経験インベントリ 使用状況を更新しました（%d エピソード / 延べ %d 回）" % (len(defs), total))
    if unknown:
        print("  ⚠️ 未定義ID: %s" % ", ".join(sorted(unknown)))


if __name__ == "__main__":
    main()
