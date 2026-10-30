# -*- coding: utf-8 -*-
"""把「大地图」接进百科：建页面 + 前端渲染（底图 + 可点红点 + 标签左右避让）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"

# ---------- 1. build_wiki2.py：加页面 ----------
P = BASE + r"\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()
if "地图/大地图" not in s:
    anchor = "pages = _pp\n"
    assert anchor in s
    add = '''pages = _pp

# 大地图页：图与坐标由 src/export_map.py 生成到 web/map_nodes.json，前端渲染
_MAP_LEAD = ("大地图是游戏中往来各地的行程图：自唐门出发，经眉山、江陵、襄阳一线东行，"
             "西上青城、峨嵋，北上崆峒、大雪山、嵩山，南下点苍。图上红点为可前往之地，"
             "点开即进入该地条目；小点是途程节点，只作路线示意。")
pages.append(("地图/大地图", "地图", "大地图", _MAP_LEAD,
              json.dumps({"底图": "2880 × 2360", "标记点": "13 处"}, ensure_ascii=False),
              "[]", json.dumps(["地图"], ensure_ascii=False), 0, "[]", "", "", 0, "", ""))
'''
    s = s.replace(anchor, add, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("build_wiki2：已加入「地图/大地图」页面")
else:
    print("build_wiki2：已存在，跳过")

# ---------- 2. wiki.html：样式 + 渲染 ----------
H = BASE + r"\web\wiki.html"
h = open(H, encoding="utf-8").read()

CSS = '''
.mapbox{position:relative;margin:12px 0 10px;border:1px solid #d8cfbc;border-radius:8px;
  overflow:hidden;background:#f6f1e5;line-height:0}
.mapbox img{display:block;width:100%;height:auto}
.mnode{position:absolute;width:13px;height:13px;border-radius:50%;background:#b4281e;
  border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.35);
  transform:translate(-50%,-50%);transition:transform .12s ease,background .12s ease}
.mnode:hover{background:#e0341f;transform:translate(-50%,-50%) scale(1.4);z-index:5}
.mlab{position:absolute;line-height:1.15;font-size:13px;padding:2px 6px;white-space:nowrap;
  background:rgba(255,255,255,.92);border:1px solid #d8cfbc;border-radius:4px;
  color:#2a2118;pointer-events:none}
.mway{position:absolute;width:5px;height:5px;border-radius:50%;
  background:rgba(96,64,32,.5);transform:translate(-50%,-50%);line-height:0}
.mapnote{font-size:12px;color:#7a6a55;margin:2px 0 14px}
'''
if ".mapbox{" not in h:
    i = h.rindex("</style>")
    h = h[:i] + CSS + h[i:]
    print("wiki.html：已加地图样式")

JS = r'''
async function mapWidget(){
  let m=null;
  try{ m=await api('/static/map_nodes.json'); }catch(e){}
  if(!m||!m.nodes) return '<div class="empty">地图数据缺失（web/map_nodes.json）</div>';
  let h='<div class="mapbox"><img src="'+m.img+'" alt="大地图">';
  for(const w of (m.ways||[]))
    h+=`<i class="mway" style="left:${w.x}%;top:${w.y}%"></i>`;
  for(const n of m.nodes){
    const pos=n.side==='left'?'transform:translate(-100%,-50%) translateX(-11px);text-align:right'
      :n.side==='up'?'transform:translate(-50%,-100%) translateY(-11px)'
      :n.side==='down'?'transform:translate(-50%,0) translateY(11px)'
      :'transform:translateY(-50%) translateX(11px)';
    h+=`<a class="mnode" href="#/p/${enc(n.slug)}" style="left:${n.x}%;top:${n.y}%" title="${esc(n.name)}"></a>`;
    h+=`<span class="mlab" style="left:${n.x}%;top:${n.y}%;${pos}">${esc(n.name)}</span>`;
  }
  h+='</div><div class="mapnote">底图为游戏内行程地图（'+m.w+'×'+m.h+'）。红点为图中可前往之地，'
    +'小点为途程节点。标签位置按图面避让调整，与方位无关。</div>';
  return h;
}

'''
if "function mapWidget(" not in h:
    anchor = "async function renderPage(slug){"
    assert anchor in h
    h = h.replace(anchor, JS + anchor, 1)
    print("wiki.html：已加 mapWidget()")

LEAD = 'if(d.lead) h+=`<div class="lead">${fnmark(linkify(d.lead))}</div>`;'
if "d.type==='地图'" not in h:
    assert LEAD in h
    h = h.replace(LEAD, LEAD + "\n  if(d.type==='地图') h+=await mapWidget();", 1)
    print("wiki.html：renderPage 已插入地图渲染")

OLD_ORDER = "const order=['人物','势力','地点','事件','剧情段','地图事件','数值','物品','武学','成就','场景','时间线'];"
NEW_ORDER = "const order=['地图','人物','势力','地点','事件','剧情段','地图事件','数值','物品','武学','成就','场景','时间线'];"
if OLD_ORDER in h:
    h = h.replace(OLD_ORDER, NEW_ORDER, 1)
    print("wiki.html：首页分类已含「地图」")

open(H, "w", encoding="utf-8").write(h)
print("wiki.html 写入完成")
