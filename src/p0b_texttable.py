# -*- coding: utf-8 -*-
"""P0b 台词总表：直接扫全部 TextAsset，按行合并 key = value。

比按文件语言猜更可靠：游戏里同名 Story_N 存在多个对象，
按文件去重会漏掉另一份里的 key。
规则：
  - 文件名以 _zh-tw / _kr / _en 结尾 → 整份跳过
  - 单行值里含韩文/日文假名 → 跳过该行
  - 同 key 取中文字数更多的值
"""
import os, re, json, collections

GAME = r"E:\Game\steamapps\common\LegendOfMortal"
DATA = os.path.join(GAME, "Mortal_Data")
OUT = r"D:\LegendOfMortal Wiki\data\build\text.json"

SOURCES = ["sharedassets0.assets", "resources.assets", "sharedassets2.assets",
           "sharedassets6.assets", "globalgamemanagers.assets"]

CJK = re.compile(r"[\u4e00-\u9fff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
KANA = re.compile(r"[\u3040-\u30ff]")
KV = re.compile(r"^(?:Story/)?([A-Za-z]{1,2}_[A-Za-z0-9_]+|[A-Za-z]+_[A-Za-z0-9_]+)\s*=\s(.*)$")


def main():
    import UnityPy
    try:
        from opencc import OpenCC
        cc = OpenCC("t2s")
    except Exception:
        cc = None

    def simp(x):
        return cc.convert(x) if cc else x
    table = {}
    conflict = 0
    stats = collections.Counter()
    skipped_files = collections.Counter()

    for src in SOURCES:
        env = UnityPy.load(os.path.join(DATA, src))
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            try:
                d = obj.read()
                name = getattr(d, "m_Name", "") or ""
                s = d.m_Script
            except Exception:
                continue
            if isinstance(s, bytes):
                s = s.decode("utf-8", "ignore")
            if name.endswith(("_zh-tw", "_kr", "_en", "_jp")):
                skipped_files[name.rsplit("_", 1)[-1]] += 1
                continue
            if len(CJK.findall(s)) < 20 and HANGUL.search(s):
                skipped_files["korean"] += 1
                continue
            for line in s.splitlines():
                m = KV.match(line)
                if not m:
                    continue
                k, v = m.group(1), m.group(2)
                v = simp(v)
                if HANGUL.search(v) or KANA.search(v):
                    continue
                cur = table.get(k)
                if cur is None:
                    table[k] = v
                elif v != cur:
                    conflict += 1
                    if len(CJK.findall(v)) > len(CJK.findall(cur)):
                        table[k] = v

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False)

    pref = collections.Counter(k.split("_")[0] for k in table)
    print("keys:", len(table))
    print("cjk :", sum(len(CJK.findall(v)) for v in table.values()))
    print("conflicts:", conflict, "skipped:", dict(skipped_files))
    print("prefixes:", pref.most_common(8))


if __name__ == "__main__":
    main()
