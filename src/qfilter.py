# -*- coding: utf-8 -*-
"""布尔筛选表达式 → SQL WHERE（作用于 scenes 表）。

支持：
  speaker:郁竹 AND flag:E00017
  (speaker:郁竹 OR speaker:唐布衣) AND NOT arc:不限时间
  title:献策           裸词 = 多字段模糊匹配
  text:"一口气"        引号内可含空格

字段：
  speaker 说话人   text 台词   flag 旗标   check 判定
  place 地点      chapter 章节  title 场景名
  arc 剧情阶段     id 场景编号  opt 选项文字
"""


class FilterError(Exception):
    pass


PREFIX = {
    "speaker": "script IN (SELECT script FROM lines WHERE speaker LIKE ?)",
    "text": "script IN (SELECT script FROM lines WHERE text LIKE ?)",
    "flag": "script IN (SELECT script FROM flags WHERE flag LIKE ?)",
    "opt": "script IN (SELECT script FROM choices WHERE options LIKE ?)",
    "check": "script IN (SELECT script FROM choices WHERE checkpoint LIKE ?)",
    "place": "place LIKE ?",
    "chapter": "chapter LIKE ?",
    "title": "title LIKE ?",
    "arc": "'场景/' || script IN (SELECT slug FROM pages WHERE type='场景' AND coalesce(facet,'') LIKE ?)",
    "id": "script LIKE ?",
}

FIELDS = list(PREFIX)


def tokenize(s):
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            out.append((ch, ch))
            i += 1
            continue
        # 读取一段（到空白或括号）
        j = i
        buf = []
        while j < n and not s[j].isspace() and s[j] not in "()":
            if s[j] == '"':
                j += 1
                while j < n and s[j] != '"':
                    buf.append(s[j])
                    j += 1
                j += 1
                continue
            buf.append(s[j])
            j += 1
        tok = "".join(buf)
        i = j
        up = tok.upper()
        if up in ("AND", "OR", "NOT"):
            out.append((up, up))
        elif ":" in tok:
            k, v = tok.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            if not v:
                raise FilterError("字段 %s 后面没有值" % k)
            if k not in PREFIX:
                raise FilterError("未知字段 %s，可用：%s" % (k, "、".join(FIELDS)))
            out.append(("ATOM", (k, v)))
        elif tok:
            out.append(("ATOM", ("word", tok)))
    return out


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i][0] if self.i < len(self.t) else None

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def parse(self):
        if not self.t:
            return None
        node = self.expr()
        if self.i < len(self.t):
            raise FilterError("表达式有多余内容，检查括号是否配对")
        return node

    def expr(self):
        node = self.term()
        while self.peek() == "OR":
            self.take()
            node = ("OR", node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.peek() == "AND":
            self.take()
            node = ("AND", node, self.factor())
        return node

    def factor(self):
        p = self.peek()
        if p == "NOT":
            self.take()
            return ("NOT", self.factor())
        if p == "(":
            self.take()
            node = self.expr()
            if self.peek() != ")":
                raise FilterError("括号没有闭合")
            self.take()
            return node
        if p == "ATOM":
            return ("LEAF", self.take()[1])
        raise FilterError("表达式不完整")


def compile_node(node, params):
    if node is None:
        return ""
    kind = node[0]
    if kind == "AND":
        a, b = compile_node(node[1], params), compile_node(node[2], params)
        return "(%s AND %s)" % (a, b)
    if kind == "OR":
        a, b = compile_node(node[1], params), compile_node(node[2], params)
        return "(%s OR %s)" % (a, b)
    if kind == "NOT":
        return "NOT (%s)" % compile_node(node[1], params)
    # LEAF
    field, val = node[1]
    like = "%" + val + "%"
    if field == "word":
        parts = []
        for f in ("title", "speaker", "text"):
            parts.append(PREFIX[f])
            params.append(like)
        return "(" + " OR ".join(parts) + ")"
    params.append(like)
    return PREFIX[field]


def build_where(expr):
    """返回 (sql_where, params)。空表达式返回 ('', [])。"""
    expr = (expr or "").strip()
    if not expr:
        return "", []
    node = Parser(tokenize(expr)).parse()
    params = []
    where = compile_node(node, params)
    return where, params


if __name__ == "__main__":
    tests = [
        "speaker:郁竹 AND flag:E00017",
        "(speaker:郁竹 OR speaker:唐布衣) AND NOT arc:不限时间",
        "title:献策",
        'text:"一口气" OR id:ch7_3',
        "speaker:郁竹 AND",
        "foo:bar",
    ]
    for t in tests:
        try:
            w, p = build_where(t)
            print("OK  ", t)
            print("    ", w)
            print("    ", p)
        except FilterError as e:
            print("ERR ", t, "->", e)
        print()
