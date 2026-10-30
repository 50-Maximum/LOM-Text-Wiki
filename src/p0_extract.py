# -*- coding: utf-8 -*-
"""P0 全量提取：从 Unity assets 抽出全部简体文本，按类别落盘。

去重规则：同名 TextAsset 取中文字数最多的一份（游戏内存在同名多语言/小副本，
按长度取会被更长的韩文版挤掉）。
"""
import os, re, json, hashlib, shutil, collections

GAME = r"E:\Game\steamapps\common\LegendOfMortal"
DATA = os.path.join(GAME, "Mortal_Data")
OUT = r"D:\LegendOfMortal Wiki\data\raw"

SOURCES = ["sharedassets0.assets", "resources.assets", "sharedassets2.assets"]

CJK = re.compile(r"[\u4e00-\u9fff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
KANA = re.compile(r"[\u3040-\u30ff]")


def lang_of(name, text):
    if name.endswith("_zh-cn"):
        return "zh-cn"
    if name.endswith("_zh-tw"):
        return "zh-tw"
    if name.endswith("_kr"):
        return "kr"
    cjk = len(CJK.findall(text))
    han = len(HANGUL.findall(text))
    kana = len(KANA.findall(text))
    if han > cjk and han > 200:
        return "kr"
    if kana > cjk and kana > 100:
        return "jp"
    if cjk > 50:
        return "zh-cn"
    return "other"


def kind_of(name, src):
    # 其他语种表整份跳过；它们曾经被误当成章节脚本导入，
    # 在场景列表里表现为“有字数、0 句”的空页。
    if name.endswith(("_zh-tw", "_kr", "_en", "_jp")):
        return "skip"
    if name.endswith("_zh-cn"):
        return "system"
    if name.startswith("Story"):
        return "story"
    if src == "resources.assets":
        return "scripts"
    if re.match(r"^[A-Za-z]{0,3}\d", name) or "ch" in name.lower():
        return "scripts"
    return "misc"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    import UnityPy

    for sub in ("story", "system", "scripts", "misc"):
        d = os.path.join(OUT, sub)
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    best = {}
    sources = {}

    for src in SOURCES:
        path = os.path.join(DATA, src)
        sources[src] = {"size": os.path.getsize(path), "sha256": sha(path)}
        env = UnityPy.load(path)
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
            kind = kind_of(name, src)
            if kind == "skip":
                continue
            cjk = len(CJK.findall(s))
            if kind == "scripts":
                # 纯逻辑脚本可能一个汉字都没有（台词全用 key 引用），必须保留
                if cjk == 0 and not any(k in s for k in (
                        "say(", "GetStoryText", "checkpointmanager", "SetFlag", "runblock")):
                    continue
            elif lang_of(name, s) != "zh-cn":
                continue
            key = (name, kind)
            cur = best.get(key)
            # 中文字数优先，其次总长度
            if cur is None or (cjk, len(s)) > (cur["cjk"], len(cur["text"])):
                best[key] = {"name": name, "kind": kind, "src": src,
                             "text": s, "cjk": cjk}

    counts = collections.Counter()
    chars = collections.Counter()
    files = []
    for (name, kind), item in best.items():
        safe = re.sub(r'[\\/:*?"<>|]', "_", name) or "unnamed"
        fp = os.path.join(OUT, kind, safe + ".txt")
        with open(fp, "w", encoding="utf-8", newline="\n") as f:
            f.write(item["text"])
        counts[kind] += 1
        chars[kind] += item["cjk"]
        files.append({"name": name, "kind": kind, "src": item["src"],
                      "path": os.path.relpath(fp, OUT),
                      "chars": len(item["text"]), "cjk": item["cjk"]})

    manifest = {
        "game": GAME,
        "sources": sources,
        "counts": dict(counts),
        "chars": dict(chars),
        "total_cjk": sum(chars.values()),
        "files": sorted(files, key=lambda x: -x["cjk"]),
    }
    with open(r"D:\LegendOfMortal Wiki\data\manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print("files:", manifest["counts"])
    print("cjk  :", manifest["chars"])
    print("total cjk:", manifest["total_cjk"])


if __name__ == "__main__":
    main()
