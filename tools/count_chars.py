#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""ES 字数カウンタ — es-coach の字数判定を LLM の目測から外部化する。

LLM は全角文字を正確に数えられないため、字数チェックはこのスクリプトに委ねる。
標準入力から ES 本文を受け取り、日本語（--ja）か英語（--en）で数える。

日本語 ES の「字数」の数え方は募集要項ごとに揺れる（改行や空白を含める/含めない）。
判定を誤らないよう、複数の定義を同時に出す：
  - total_no_newline : 改行を除いた全文字数（多くの日系ESフォームの実カウントに近い）
  - total_no_space   : 改行＋空白（半角/全角）を除いた文字数（純粋な内容字数）
呼び出し側は、その企業が明示する字数ルールに合う方を採用すること。

英語 ES は語数（whitespace 区切り）を数える。

使い方：
  echo "<ES本文>" | count_chars.py --ja
  pbpaste       | count_chars.py --en
  count_chars.py --ja < draft.txt
"""
import sys
import argparse
import json
import unicodedata


def count_ja(text):
    no_newline = text.replace("\r", "").replace("\n", "")
    total_no_newline = len(no_newline)
    total_no_space = len("".join(ch for ch in no_newline if not ch.isspace()))
    # 参考情報：全角換算（半角文字を 0.5 とみなす一部フォーム向け）
    zen = sum(
        0.5 if unicodedata.east_asian_width(ch) in ("Na", "H") else 1
        for ch in no_newline
        if not ch.isspace()
    )
    return {
        "mode": "ja",
        "total_no_newline": total_no_newline,
        "total_no_space": total_no_space,
        "zenkaku_equiv": round(zen, 1),
    }


def count_en(text):
    words = text.split()
    return {
        "mode": "en",
        "words": len(words),
        "chars_no_space": len("".join(text.split())),
    }


def main():
    ap = argparse.ArgumentParser(description="ES 字数/語数カウンタ")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ja", action="store_true", help="日本語ES（字数）")
    g.add_argument("--en", action="store_true", help="英語ES（語数）")
    ap.add_argument("--json", action="store_true", help="JSON で出力")
    args = ap.parse_args()

    text = sys.stdin.read()
    result = count_ja(text) if args.ja else count_en(text)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif args.ja:
        print(
            "字数（改行除く）: %d ／ 字数（改行・空白除く）: %d ／ 全角換算: %s"
            % (result["total_no_newline"], result["total_no_space"], result["zenkaku_equiv"])
        )
    else:
        print("語数: %d ／ 文字数（空白除く）: %d" % (result["words"], result["chars_no_space"]))


if __name__ == "__main__":
    main()
