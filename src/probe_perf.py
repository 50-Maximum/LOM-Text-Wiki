# -*- coding: utf-8 -*-
import io, sys, time, json, urllib.parse, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = "http://127.0.0.1:8765"
def t(path):
    u = BASE + path
    s = time.time()
    raw = urllib.request.urlopen(u, timeout=20).read()
    ms = (time.time() - s) * 1000
    return len(raw), ms
for slug in ["人物/赵活", "事件/三人处理匪类尸身", "场景/ch8_8_1", "数值/道德", "地图事件/索引",
             "时间线/按年月", "世界观/总览", "关于本站"]:
    n, ms = t("/api/page?slug=" + urllib.parse.quote(slug))
    print("%-22s %7d 字节 %6.0f ms" % (slug, n, ms))
n, ms = t("/api/search2?q=" + urllib.parse.quote("唐门"))
print("%-22s %7d 字节 %6.0f ms" % ("搜索 唐门", n, ms))
n, ms = t("/api/pages?type=" + urllib.parse.quote("事件") + "&limit=100")
print("%-22s %7d 字节 %6.0f ms" % ("事件列表", n, ms))
