# -*- coding: utf-8 -*-
"""标注 Demo 版限定内容（练功塔），并修正赵活简介里只靠该内容支撑的说法。

依据（逐条可查）：
  1) 参考 wiki docs/event/badends/index.md 生死簿 No.23 备注：「Demo版練功塔相關事件，目前無法觸發。」
  2) 参考 wiki docs/other/news/20240607-01-demoUpdate.md：「模式：新增練功塔模式(Demo版本限定)」
  3) 参考 wiki docs/other/qna/202411.md：问唐门是否还有其他没出现过的设施（如 demo 版的练功塔）→「沒有了。」
  4) 参考 wiki docs/people/factions/tang-men.md：「現版本除了練功塔外，沒有其他未出現的設施了。」
  5) 剧本层面：act1 没有任何剧本引用它，act2_1/act3_1 由 act1 引，其余顺着 act1 串成一条封闭链。
"""
import io, sys, os, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

SCN = [r[0] for r in c.execute("select script from scenes where script like 'act%' order by script")]

# 这些场里出现的事件——只标注「全部场景都在 act* 链上」的事件，避免误伤正式剧情也出现的事件
events = set()
for sc in SCN:
    for (nm,) in c.execute("select distinct name from notes where script=? and type='事件'", (sc,)):
        if not nm:
            continue
        scripts = {r[0] for r in c.execute(
            "select distinct script from notes where name=? and type='事件'", (nm,))}
        if scripts and scripts <= set(SCN):
            events.add(nm)
        else:
            print("  跳过（另有正式剧情场景）：", nm, sorted(scripts - set(SCN))[:3])

pages = ["场景/" + s for s in SCN] + ["事件/" + e for e in sorted(events)]
for slug in ("地点/唐门-练功塔", "设施/练功塔"):
    if c.execute("select count(*) from pages where slug=?", (slug,)).fetchone()[0]:
        pages.append(slug)

# 含这些场的剧情段
try:
    SG = json.load(open(os.path.join(B, "data", "story_segments.json"), encoding="utf-8"))
    segs = []
    for s in SG.get("segments") or []:
        scs = s.get("scenes") or []
        if scs and all(x in SCN for x in scs):
            segs.append("剧情段/" + s["id"])
    pages += segs
except Exception as e:
    print("剧情段读取失败", e)

note = ("本页内容属于 Demo 版限定的「练功塔」模式：正式版没有入口，正常游玩看不到。"
        "依据有三——参考 wiki 生死簿 No.23 的备注写明「Demo版練功塔相關事件，目前無法觸發」；"
        "2024-06-07 更新日志把练功塔列为「Demo版本限定」；"
        "官方问答里提到「demo 版的練功塔」时说唐门已无其他未出现的设施。"
        "剧本层面也一致：act1 没有任何剧本跳转指向它，后续各场都由 act1 串出，是一条封闭链。")

out = {"scenes": SCN, "events": sorted(events), "pages": pages, "note": note}
json.dump(out, open(os.path.join(B, "data", "demo_only.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("场景 %d、事件 %d、页面合计 %d" % (len(SCN), len(events), len(pages)))
print("事件：", "、".join(sorted(events)))
print("剧情段：", [p for p in pages if p.startswith("剧情段/")])

# 赵活简介：把只靠 Demo 内容支撑的「守练功塔的杂役」改成正式剧情可证的「门中杂役」
P = os.path.join(B, "data", "intros_char.json")
d = json.load(open(P, encoding="utf-8"))
e = d.get("人物/赵活")
if e:
    old = "他命硬、抗揍，从守练功塔的杂役一路做成唐门栋梁。"
    new = "他命硬、抗揍，在门中担任杂役，一路做成唐门栋梁。"
    if old in e["text"]:
        e["text"] = e["text"].replace(old, new)
        e.setdefault("footnotes", []).append({
            "n": 3 + 100, "text": "", "script": "", "quote": ""})
        e["footnotes"] = [x for x in e["footnotes"] if x.get("text")]
        json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\n赵活简介已改：", new)
    else:
        print("\n赵活简介未命中旧句，未改")
