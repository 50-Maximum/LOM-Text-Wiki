# -*- coding: utf-8 -*-
r"""生成江湖夜话的数据包：只放「这个人/这个地方是谁」，不放剧情进展。

规则：
1. 只取 lead 的第一句（到第一个句号），去掉脚注编号
2. 事件类一律不进（剧透风险最高）
3. gate 用该实体在剧情里第一次出现的脚本行号；找不到就不写（宁可漏）
4. 输出 `夜话设定\wiki\pack.txt`，UTF-8 无 BOM
"""
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "wiki.db")

TYPES = ("人物", "地点", "势力", "物品")

FOOT = re.compile(r"（[0-9、，,\s]+）")
TAIL = re.compile(r"[。！？]")


def first_sentence(text):
    if not text:
        return ""
    t = FOOT.sub("", text).strip()
    t = re.sub(r"\s+", "", t)
    if not t:
        return ""
    m = TAIL.search(t)
    if m and m.start() >= 8:
        t = t[:m.start() + 1]
    return t


def key_to_gate(key):
    """D_2_5_1#53 -> D_2_5_1_053"""
    if not key or "#" not in key:
        return ""
    a, b = key.rsplit("#", 1)
    if not b.isdigit():
        return ""
    return "%s_%03d" % (a, int(b))


def main(out=None):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    game = ""
    try:
        r = con.execute("SELECT value FROM meta WHERE key='game'").fetchone()
        game = (r["value"] if r else "") or ""
    except Exception:
        pass
    out_dir = os.path.join(game, "夜话设定", "wiki") if game else ""
    if not out:
        out = (os.path.join(out_dir, "pack.txt") if out_dir else "")
    if not out:
        print("no game dir")
        return 2

    # 说话人 id -> 名字
    name_of = {}
    for r in con.execute("SELECT id, name FROM names"):
        if r["id"]:
            name_of[r["id"]] = r["name"]

    # 每个说话人第一次说话的位置（按场景顺序）
    first_at = {}
    try:
        for r in con.execute(
                "SELECT l.speaker_id AS sid, l.script AS s "
                "FROM lines l JOIN scene_order so ON so.script = l.script "
                "WHERE l.speaker_id IS NOT NULL "
                "ORDER BY so.ord, l.seq"):
            sid = r["sid"]
            if sid not in first_at:
                first_at[sid] = r["s"]
    except Exception as e:
        print("first_at:", e)

    # 场景 → 游戏内部原始脚本键（夜话的 Canon.SeenAt 只认这种）
    scene_key = {}
    try:
        for r in con.execute("SELECT script, first_key FROM scenes WHERE first_key IS NOT NULL"):
            scene_key[r["script"]] = r["first_key"]
    except Exception as e:
        print("scene_key:", e)

    rows = con.execute(
        "SELECT slug, type, name, lead FROM pages "
        "WHERE hidden=0 AND lead IS NOT NULL AND length(lead) > 20 "
        "ORDER BY type, slug").fetchall()

    # 待查实体名（地点/势力/物品没有说话人 id，用正文首次出现兜底）
    want = {}
    for r in rows:
        if r["type"] not in TYPES:
            continue
        nm = (r["name"] or "").split("·")[-1].strip() or r["slug"].split("/")[-1]
        if len(nm) >= 2 and nm not in want:
            want[nm] = r["slug"]

    # 一次扫完台词库，记每个名字最早出现的场景
    seen_at = {}
    remaining = set(want)
    if remaining:
        try:
            for r in con.execute(
                    "SELECT l.script AS s, l.text AS t FROM lines l "
                    "JOIN scene_order so ON so.script = l.script "
                    "WHERE l.text IS NOT NULL "
                    "ORDER BY so.ord, l.seq"):
                t = r["t"]
                hit = [n for n in remaining if n in t]
                for n in hit:
                    seen_at[n] = r["s"]
                    remaining.discard(n)
                if not remaining:
                    break
        except Exception as e:
            print("scan:", e)

    def gate_of(script):
        """场景 → 夜话能识别的 gate（D_/N_/T_ 前缀的原始脚本键）。"""
        k = scene_key.get(script) or ""
        if not k:
            return ""
        if "#" in k:
            k = key_to_gate(k)
        if not re.match(r"^[DNT]_", k):
            return ""
        return k

    def gate_for(nm, sid_candidates):
        for sid in sid_candidates:
            s = first_at.get(sid)
            if s:
                g = gate_of(s)
                if g:
                    return g
        s = seen_at.get(nm)
        if s:
            return gate_of(s)
        return ""

    world = []
    for r in rows:
        typ = r["type"]
        if typ not in TYPES:
            continue
        slug = r["slug"]
        nm = (r["name"] or "").split("·")[-1].strip()
        if not nm:
            nm = slug.split("/")[-1]
        text = first_sentence(r["lead"])
        if len(text) < 12:
            continue
        # 事件/剧透词过滤
        if any(w in text for w in ("后来", "最终", "结局", "死后", "临死", "传位")):
            continue
        gate = ""
        sids = [sid for sid, sname in name_of.items() if sname == nm]
        gate = gate_for(nm, sids)
        if not gate:
            continue
        keys = [nm]
        world.append((gate, keys, text))

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 江湖夜话 · wiki 资料包\n")
        f.write("# 由《活侠传追踪Wiki》生成，请勿手改\n")
        f.write("@world\n")
        for gate, keys, text in world:
            f.write("%s\t%s\t%s\n" % (gate, ",".join(keys), text))
    print("written %s rows=%d bytes=%d" % (out, len(world), os.path.getsize(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
