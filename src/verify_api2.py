# -*- coding: utf-8 -*-
"""通过运行中的 exe 验证：事件的触发条件行、场景的门事件菜单。"""
import io, sys, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def page(slug):
    u = "http://127.0.0.1:8765/api/page?slug=" + urllib.parse.quote(slug)
    return json.loads(urllib.request.urlopen(u, timeout=15).read().decode("utf-8"))


d = page("事件/南宫远就任武林盟主")
for s in d.get("sections") or []:
    if s.get("h") == "触发条件":
        for r in s.get("rows") or []:
            print("行:", r.get("note"))

d2 = page("事件/夏侯兰拒赴邀约后出门剿匪")
for s in d2.get("sections") or []:
    if s.get("h") == "触发条件":
        for r in s.get("rows") or []:
            print("门事件:", r.get("note"))
    if s.get("h") == "分支选项":
        for b in s.get("choice_rows") or []:
            print("菜单:", b.get("prompt"), "｜", b.get("scene"))
            for o in (b.get("options") or [])[:6]:
                print("   ", o.get("text"), "| 条件:", (o.get("cond") or "无")[:40], "|", o.get("result"))
