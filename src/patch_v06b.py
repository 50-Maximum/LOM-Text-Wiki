# -*- coding: utf-8 -*-
"""补丁：app.py 的增加接口（/api/version 已被占用，改用 /api/appver）。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

A = os.path.join(BASE, "src", "app.py")
t = open(A, encoding="utf-8").read()

if "_app_version" not in t:
    helper = (
        'PORT = int(os.environ.get("LOM_PORT", "8765"))\n\n\n'
        'def _app_version():\n'
        '    try:\n'
        '        return str(json.load(open(os.path.join(ROOT, "version.json"), encoding="utf-8"))'
        '.get("version") or "0.0.0")\n'
        '    except Exception:\n'
        '        return "0.0.0"'
    )
    assert 'PORT = int(os.environ.get("LOM_PORT", "8765"))' in t
    t = t.replace('PORT = int(os.environ.get("LOM_PORT", "8765"))', helper, 1)

if "/api/appver" not in t:
    routes = (
        '            if p == "/api/appver":\n'
        '                return self._json({"name": "活侠传追踪Wiki", "version": _app_version()})\n'
        '            if p == "/api/update/check":\n'
        '                return self._json(update_check())\n'
        '            if p == "/api/update/apply":\n'
        '                return self._json(update_apply())\n'
        '            if p == "/api/search2":'
    )
    t = t.replace('            if p == "/api/search2":', routes, 1)

if "def update_check()" not in t:
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
    assert "\ndef serve():" in t
    t = t.replace("\ndef serve():", funcs, 1)

open(A, "w", encoding="utf-8").write(t)
print("app.py 接口已补（/api/appver, /api/update/*）")

# 前端改调用 /api/appver
P = os.path.join(BASE, "web", "wiki.html")
s = open(P, encoding="utf-8").read()
s = s.replace("await api('/api/version')", "await api('/api/appver')")
open(P, "w", encoding="utf-8").write(s)
print("wiki.html 已指向 /api/appver")
