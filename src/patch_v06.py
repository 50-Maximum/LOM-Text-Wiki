# -*- coding: utf-8 -*-
"""v0.6：改名活侠传追踪Wiki、加版本号与在线更新入口。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

# ---------- wiki.html ----------
P = os.path.join(BASE, "web", "wiki.html")
s = open(P, encoding="utf-8").read()
s = s.replace("<title>活侠传 · 百科</title>", "<title>活侠传追踪Wiki</title>")
s = s.replace('<a href="#/">活侠传 · 百科</a>', '<a href="#/">活侠传追踪Wiki</a>')
if "updchip" not in s:
    css = (
        "\n#updchip{position:fixed;right:14px;bottom:12px;z-index:60;padding:5px 11px;"
        "border-radius:14px;background:#1b1e23;border:1px solid #282c33;color:#8a93a1;"
        "font-size:12px;cursor:pointer;user-select:none}\n"
        "#updchip:hover{color:#c8a06a;border-color:#c8a06a}\n</style>"
    )
    s = s.replace("</style>", css, 1)
    js = """
<div id="updchip">v<span id="uver">?</span> · 检查更新</div>
<script>
(async function(){
  try{const v=await api('/api/version'); if(v&&v.version) document.getElementById('uver').textContent=v.version;}catch(e){}
  const chip=document.getElementById('updchip');
  if(!chip) return;
  chip.onclick=async function(){
    const old=chip.innerHTML; chip.textContent='检查中…';
    try{
      const d=await api('/api/update/check');
      if(d&&d.newer){
        if(confirm('发现新版本 '+d.version+'（当前 '+d.current+'）\\n\\n'+(d.notes||d.version)+'\\n\\n现在下载并更新？')){
          chip.textContent='正在下载…';
          const r=await api('/api/update/apply');
          chip.textContent=(r&&r.ok)?'更新中，程序会自动重启':'更新失败';
        }else{ chip.innerHTML=old; }
      }else if(d&&d.ok){
        alert('已是最新版本 '+d.current); chip.innerHTML=old;
      }else{
        alert('暂时无法检查更新（未配置清单或网络不通）'); chip.innerHTML=old;
      }
    }catch(e){ alert('检查更新失败：'+e); chip.innerHTML=old; }
  };
})();
</script>
</body>"""
    s = s.replace("</body>", js, 1)
open(P, "w", encoding="utf-8").write(s)
print("wiki.html 已更新")

# ---------- app.py ----------
A = os.path.join(BASE, "src", "app.py")
t = open(A, encoding="utf-8").read()
if "api/version" not in t:
    helper = (
        'PORT = int(os.environ.get("LOM_PORT", "8765"))\n\n\n'
        'def _app_version():\n'
        '    try:\n'
        '        return str(json.load(open(os.path.join(ROOT, "version.json"), encoding="utf-8"))'
        '.get("version") or "0.0.0")\n'
        '    except Exception:\n'
        '        return "0.0.0"'
    )
    t = t.replace('PORT = int(os.environ.get("LOM_PORT", "8765"))', helper, 1)
    routes = (
        '            if p == "/api/version":\n'
        '                return self._json({"name": "活侠传追踪Wiki", "version": _app_version()})\n'
        '            if p == "/api/update/check":\n'
        '                return self._json(update_check())\n'
        '            if p == "/api/update/apply":\n'
        '                return self._json(update_apply())\n'
        '            if p == "/api/search2":'
    )
    t = t.replace('            if p == "/api/search2":', routes, 1)
    funcs = (
        '\ndef update_check():\n'
        '    cur = _app_version()\n'
        '    try:\n'
        '        import updater\n'
        '    except Exception:\n'
        '        return {"ok": False, "current": cur, "reason": "no-updater"}\n'
        '    info = updater.local_package() or updater.fetch_remote()\n'
        '    if not info:\n'
        '        return {"ok": False, "current": cur, "reason": "no-manifest"}\n'
        '    try:\n'
        '        return {"ok": True, "current": cur, "version": str(info.get("version")),\n'
        '                "notes": info.get("notes") or "",\n'
        '                "newer": updater.newer(str(info.get("version")), cur)}\n'
        '    except Exception as e:\n'
        '        return {"ok": False, "current": cur, "reason": str(e)}\n'
        '\n\n'
        'def update_apply():\n'
        '    try:\n'
        '        import updater\n'
        '    except Exception:\n'
        '        return {"ok": False}\n'
        '    info = updater.local_package() or updater.fetch_remote()\n'
        '    if not info:\n'
        '        return {"ok": False}\n'
        '    threading.Thread(target=lambda: updater.apply_update(info), daemon=True).start()\n'
        '    return {"ok": True, "version": info.get("version")}\n'
        '\n\n'
        'def serve():'
    )
    t = t.replace("\ndef serve():", funcs, 1)
open(A, "w", encoding="utf-8").write(t)
print("app.py 已加版本与更新接口")

# ---------- desktop.py ----------
Dp = os.path.join(BASE, "src", "desktop.py")
d = open(Dp, encoding="utf-8").read()
d = d.replace('"活侠传 · 文本库"', '"活侠传追踪Wiki"')
if "_bg_update" not in d:
    d = d.replace("def main():", (
        'def _bg_update():\n'
        '    try:\n'
        '        import updater\n'
        '        updater.check_and_update(interactive=True)\n'
        '    except Exception as e:\n'
        '        print("更新检查跳过", e)\n'
        '\n\n'
        'def main():'), 1)
    old = (
        '    try:\n'
        '        import updater\n'
        '        if updater.check_and_update():\n'
        '            return\n'
        '    except Exception as e:\n'
        '        print("更新检查跳过", e)\n'
        '    start_server()'
    )
    d = d.replace(old, '    start_server()\n    threading.Thread(target=_bg_update, daemon=True).start()', 1)
open(Dp, "w", encoding="utf-8").write(d)
print("desktop.py 已改名并后台检查更新")

# ---------- version.json ----------
json.dump({"version": "0.6", "built_at": "2026-10-27", "app": "活侠传追踪Wiki"},
          open(os.path.join(BASE, "version.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("version.json → 0.6")

# ---------- spec ----------
src = os.path.join(BASE, "活侠传Wiki.spec")
if os.path.exists(src):
    sp = open(src, encoding="utf-8").read().replace("活侠传Wiki", "活侠传追踪Wiki")
    open(os.path.join(BASE, "活侠传追踪Wiki.spec"), "w", encoding="utf-8").write(sp)
    print("spec 已生成")

# ---------- 更新清单占位 ----------
cfg = os.path.join(BASE, "data", "update.json")
if not os.path.exists(cfg):
    json.dump({"manifest": "", "note": "把发布后的 update.json 直链填到 manifest"},
              open(cfg, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("data/update.json 已建（待填清单地址）")
