# -*- coding: utf-8 -*-
"""把 D:\攻略 的 HTML 转成保留结构的纯文本（标题/表格行/列表）。"""
import os, re, io, sys
from html.parser import HTMLParser

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SRC = r"D:\攻略"
OUT = r"D:\LegendOfMortal Wiki\data\guide"
os.makedirs(OUT, exist_ok=True)

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0
        self.cell = []
        self.row = []
        self.in_table = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag == "table":
            self.in_table += 1
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = []
        elif tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n" + "#" * int(tag[1]) + " ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        elif tag in ("td", "th"):
            self.row.append(" ".join("".join(self.cell).split()))
        elif tag == "tr":
            if any(self.row):
                self.out.append("\n| " + " | ".join(self.row) + " |")
            self.row = []
        elif tag == "table":
            self.in_table = max(0, self.in_table - 1)
            self.out.append("\n")
        elif tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "br"):
            self.out.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        t = data.replace("\u00a0", " ")
        if self.cell is not None and self.in_table:
            self.cell.append(t)
        else:
            if t.strip():
                self.out.append(t)

for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".html"):
        continue
    raw = open(os.path.join(SRC, fn), encoding="utf-8", errors="replace").read()
    p = P()
    p.feed(raw)
    text = "".join(p.out)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    dst = os.path.join(OUT, fn.replace(".html", ".txt"))
    open(dst, "w", encoding="utf-8").write(text)
    print(f"{fn}: {len(raw)} -> {len(text)} 字符")
