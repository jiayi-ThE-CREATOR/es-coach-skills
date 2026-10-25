#!/usr/bin/env python3
"""日本語の文章に紛れ込んだ中国語の字形（簡体字など）と中国語の句読点を見つける。

使い方:
  echo "本文" | python3 check_ja_kanji.py      # 標準入力
  python3 check_ja_kanji.py <file> [<file>...]  # ファイル

判定:
  - 漢字が CP932（日本語の通常の文字集合）に無い → 中国語の字形の疑い（例：责→責、说→説）
    JIS 第3・第4水準（euc_jis_2004）にはある字は「要確認」として出す
  - 中国語の句読点「，；“”」→ 日本語の「、」「。」「「」」に直す
見つかったら終了コード 1、無ければ 0。
"""
import sys

CN_PUNCT = "，；“”"


def check_line(line):
    hits = []
    for ch in line:
        if "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿":
            try:
                ch.encode("cp932")
            except UnicodeEncodeError:
                try:
                    ch.encode("euc_jis_2004")
                    hits.append(f"{ch}（JIS第3/4水準・要確認）")
                except UnicodeEncodeError:
                    hits.append(ch)
        elif ch in CN_PUNCT:
            hits.append(f"句読点{ch}")
    return hits


def main():
    sources = [(p, open(p, encoding="utf-8")) for p in sys.argv[1:]] or [("stdin", sys.stdin)]
    found = False
    for name, f in sources:
        for n, line in enumerate(f, 1):
            hits = check_line(line)
            if hits:
                found = True
                print(f"{name}:{n}: {' '.join(hits)} ｜ {line.strip()[:50]}")
    print("中国語の字形・句読点：あり" if found else "中国語の字形・句読点：なし")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
