# -*- coding: utf-8 -*-
"""把立绘与书物封面接进 wiki.html：人物页右上角立绘，书物页封面。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
H = os.path.join(BASE, "web", "wiki.html")
h = open(H, encoding="utf-8").read()

CSS = '''
.portrait{float:right;width:208px;max-width:32%;margin:0 0 14px 18px;border:1px solid #d8cfbc;
  border-radius:8px;background:#f6f1e5;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.cover{float:right;width:150px;max-width:26%;margin:0 0 12px 16px;border:1px solid #d8cfbc;
  border-radius:6px;background:#f6f1e5}
'''
if ".portrait{" not in h:
    i = h.rindex("</style>")
    h = h[:i] + CSS + h[i:]
    print("已加立绘样式")

JS = r'''
let ART=null;
async function loadArt(){
  if(ART) return ART;
  ART={p:{},c:{}};
  try{ ART.p=await api('/static/portraits.json'); }catch(e){}
  try{ ART.c=await api('/static/covers.json'); }catch(e){}
  return ART;
}

'''
if "async function loadArt(" not in h:
    h = h.replace("async function mapWidget(){", JS + "async function mapWidget(){", 1)
    print("已加 loadArt()")

H1 = "h+=`<h1>${esc(d.name)}</h1><div class=\"sub\"><span class=\"tag\">${esc(d.type)}</span>"
if "loadArt()" in h and "ART.p[slug]" not in h:
    assert H1 in h, "h1 锚点未找到"
    ins = H1 + ("\n  {const _a=await loadArt();"
                "if(d.type==='人物'&&_a.p[slug]) h+=`<img class=\"portrait\" src=\"/static/${_a.p[slug]}\" alt=\"${esc(d.name)}\">`;"
                "if(d.type==='书物'&&_a.c[slug]) h+=`<img class=\"cover\" src=\"/static/${_a.c[slug]}\" alt=\"${esc(d.name)}\">`;}")
    h = h.replace(H1, ins, 1)
    print("renderPage 已插入立绘/封面")

open(H, "w", encoding="utf-8").write(h)

# 统计
p = json.load(open(os.path.join(BASE, "web", "portraits.json"), encoding="utf-8"))
c = json.load(open(os.path.join(BASE, "web", "covers.json"), encoding="utf-8"))
n = len(os.listdir(os.path.join(BASE, "web", "portrait")))
print("立绘文件 %d 张，接上条目 %d 个；书物封面 %d 个" % (n, len(p), len(c)))
