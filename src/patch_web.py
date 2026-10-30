# -*- coding: utf-8 -*-
"""前端补丁：台账名称全局可点，加统一事件委托。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\web\index.html"
s = open(p, encoding="utf-8").read()

old = '<div class="entry"><div class="et">${esc(r.name)}</div><div class="eb">${esc(r.note)}</div><div class="ek">${esc(r.chapter)} · ${esc(r.type)}</div></div>'
new = ('<div class="entry"><div class="et"><span data-wk="${esc(r.name)}" data-wktype="${esc(r.type)}" '
       'style="cursor:pointer">${esc(r.name)}</span></div><div class="eb">${esc(r.note)}</div>'
       '<div class="ek">${esc(r.chapter)} · ${esc(r.type)}</div></div>')
n = s.count(old)
s = s.replace(old, new)

anchor = "document.querySelectorAll('.tabs div').forEach(d=>d.onclick=()=>loadTab(d.dataset.t));"
deleg = ("document.addEventListener('click',e=>{\n"
         "  const w=e.target.closest('[data-wk]');\n"
         "  if(w){ openWiki(w.dataset.wktype||'', w.dataset.wk); }\n"
         "});\n")
if "closest('[data-wk]')" not in s:
    s = s.replace(anchor, deleg + anchor)

open(p, "w", encoding="utf-8").write(s)
print("替换台账条目", n, "处；委托", "已加" if "closest('[data-wk]')" in s else "未加")
