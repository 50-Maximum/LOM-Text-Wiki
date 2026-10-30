# -*- coding: utf-8 -*-
"""前端：脚本编号支持部分匹配（输入片段即可命中）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\web\wiki.html"
s = open(P, encoding="utf-8").read()

if "脚本编号包含" in s:
    print("已存在，跳过")
else:
    a = """    }catch(e){}
  }
  if(d.pages&&d.pages.length){"""
    assert a in s, "锚点缺失"
    add = """    }catch(e){}
  }
  if(qq && qq.length>=2 && /[0-9_]/.test(qq)){
    const ql=qq.toLowerCase();
    const ks=Object.keys(SM).filter(k=>k.toLowerCase()!==ql && k.toLowerCase().includes(ql)).slice(0,30);
    if(ks.length){
      h+=`<h2>脚本编号包含「${esc(qq)}」</h2>`;
      for(const k of ks){const s=SM[k]||{};
        h+=`<div class="hit" onclick="go('#/scene/${enc(k)}')">
            <div class="h">${esc(s.chapter||'')} · ${s.line_count||0} 句${s.place?' · '+esc(s.place):''}</div>
            <div><b>${esc(s.title||k)}</b>　<span class="mt">${esc(k)}</span></div></div>`;}
    }
  }
  if(d.pages&&d.pages.length){"""
    s = s.replace(a, add, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已插入脚本编号部分匹配")

# 语法校验
import subprocess
r = subprocess.run(["node", "--check", P.replace(".html", ".js")], capture_output=True)
print("（跳过 node 校验）")
