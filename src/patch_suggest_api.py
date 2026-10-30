# -*- coding: utf-8 -*-
"""① app.py 增加 POST /api/suggest 落盘；② 前端：关于页跳首页、记录版本号。"""
import io, os, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

A = os.path.join(BASE, "src", "app.py")
t = open(A, encoding="utf-8").read()
if "def do_POST" not in t:
    code = '''    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        if u.path == "/api/suggest":
            try:
                d = json.loads(raw.decode("utf-8"))
            except Exception:
                return self._json({"ok": False, "err": "bad json"})
            import datetime
            rec = {"t": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "page": str(d.get("page") or "")[:300],
                   "title": str(d.get("title") or "")[:200],
                   "text": str(d.get("text") or "")[:4000],
                   "version": _app_version()}
            try:
                p = os.path.join(ROOT, "data", "suggestions.jsonl")
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\\n")
                return self._json({"ok": True})
            except Exception as e:
                return self._json({"ok": False, "err": str(e)})
        return self.send_error(404)

    def do_GET(self):'''
    assert "    def do_GET(self):" in t
    t = t.replace("    def do_GET(self):", code, 1)
    open(A, "w", encoding="utf-8").write(t)
    py_compile.compile(A, doraise=True)
    print("app.py POST /api/suggest 已加")
else:
    print("app.py 已有 do_POST")

# 前端：关于页跳首页 + 版本缓存
P = os.path.join(BASE, "web", "wiki.html")
s = open(P, encoding="utf-8").read()
if "关于本站'" not in s:
    s = s.replace("    else if(kind==='p') await renderPage(arg);",
                  "    else if(kind==='p' && arg==='关于本站') await home();\n"
                  "    else if(kind==='p') await renderPage(arg);", 1)
if "window.__VER" not in s:
    s = s.replace("try{const v=await api('/api/appver'); if(v&&v.version) document.getElementById('uver').textContent=v.version;}catch(e){}",
                  "try{const v=await api('/api/appver'); if(v&&v.version){ document.getElementById('uver').textContent=v.version; window.__VER=v.version; }}catch(e){}", 1)
open(P, "w", encoding="utf-8").write(s)
print("前端已改：关于页跳首页、版本缓存")
