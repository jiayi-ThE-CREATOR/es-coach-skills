#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""es-coach の総合評価（S〜D）が、実際の書類通過と合っているかを集計する。

入力は2つ：
  - 批改ログ（VAULT_SHUKATSU_HIKAKU_LOG/*.md）の frontmatter：final_score / es_file / outcome / outcome_components
  - 選考結果一覧（VAULT_SHUKATSU_SOZAI_SELF/選考結果一覧.md）の表：| [[ES ファイル名]] | 結果 | メモ |

判定（書類の段階だけを見る。面接の結果は ES の良し悪しと別物なので混ぜない）：
  - 結果が `テスト×` `一次×` `二次×` `最終×` `◎` → ES 通過（ES と一緒に受けたテストがあっても、通ったなら ES は足りていた）
  - 結果が `書類×` → ES 落選。ただし outcome_components が「ES単独」でなければ、テスト等との交絡として別に数える
  - 空欄・`待ち`・`辞退`、または一覧に行が無い → 不明（集計しない）
一覧に行が無いログは、ログ自身の outcome（通過 / 落選）で補う。

あわせて、ログ frontmatter の schema 違反（final_score が S〜D でない等）を列挙する。

使い方：
  score_calibration.py          # 表を出す
  score_calibration.py --brief  # 1行サマリーだけ（Phase 7 のサインオフ用）
"""
import re
import os
import sys
import glob
import argparse

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vault_paths import vault_path  # noqa: E402

SCORES = ["S", "A", "B", "C", "D"]
PASS = {"テスト×", "一次×", "二次×", "最終×", "◎"}
REQUIRED = ["date", "company_normalized", "question_type", "final_score", "outcome", "outcome_components", "episodes_used"]


def load_frontmatter(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return None


def load_results(path):
    """選考結果一覧の表を {ES ファイル名: 結果} にする。"""
    res = {}
    if not os.path.exists(path):
        return res
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[0].startswith("[["):
            continue
        name = cells[0].strip("[]")
        res[name] = cells[1]
    return res


def classify(fm, results):
    """→ 'pass' / 'fail' / 'fail_confounded' / None"""
    r = results.get(str(fm.get("es_file") or "").strip("[]"), "")
    clean = str(fm.get("outcome_components") or "").startswith("ES単独")
    if r in PASS:
        return "pass"
    if r == "書類×":
        return "fail" if clean else "fail_confounded"
    if r:
        return None  # 待ち・辞退など
    oc = str(fm.get("outcome") or "")
    if oc.startswith("通過"):
        return "pass"
    if oc.startswith("落選"):
        return "fail" if clean else "fail_confounded"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", action="store_true", help="1行サマリーだけ")
    args = ap.parse_args()

    log_dir = str(vault_path("VAULT_SHUKATSU_HIKAKU_LOG"))
    results = load_results(os.path.join(str(vault_path("VAULT_SHUKATSU_SOZAI_SELF")), "選考結果一覧.md"))

    table = {s: {"pass": 0, "fail": 0, "fail_confounded": 0, None: 0} for s in SCORES}
    errors = []
    for f in sorted(glob.glob(os.path.join(log_dir, "*.md"))):
        name = os.path.basename(f)
        if name.endswith("_index.md"):
            continue
        fm = load_frontmatter(f)
        if fm is None or fm.get("question_type") is None:
            continue  # 面接練習など ES 添削以外のノート
        missing = [k for k in REQUIRED if k not in fm]
        score = str(fm.get("final_score") or "").strip()
        if missing:
            errors.append("%s：項目なし %s" % (name, ", ".join(missing)))
        if score not in SCORES:
            errors.append("%s：final_score が S〜D でない（%r）" % (name, score or None))
            continue
        table[score][classify(fm, results)] += 1

    passed = sum(t["pass"] for s, t in table.items() if s in ("S", "A"))
    failed = sum(t["fail"] for s, t in table.items() if s in ("S", "A"))
    n = passed + failed

    if args.brief:
        if n == 0:
            print("サインオフ（S/A）後の書類結果：まだデータなし")
        else:
            print("サインオフ（S/A）後の書類通過：%d/%d（ES単独で落ちたもののみ分母に入れ、交絡は除外）" % (passed, n))
        return

    print("| 判定 | 書類通過 | 書類落選（ES単独） | 落選（テスト等と交絡） | 不明 |")
    print("|---|---|---|---|---|")
    for s in SCORES:
        t = table[s]
        print("| %s | %d | %d | %d | %d |" % (s, t["pass"], t["fail"], t["fail_confounded"], t[None]))
    if errors:
        print("\nschema 違反（集計から漏れる・ずれる）：")
        for e in errors:
            print("- " + e)


if __name__ == "__main__":
    main()
