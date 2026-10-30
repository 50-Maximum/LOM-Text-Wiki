# -*- coding: utf-8 -*-
"""桌面外壳：本地服务 + 独立窗口。

优先用 pywebview（WebView2 内核，真正的应用窗口）；
没装则退化为 Edge --app 模式（无地址栏的独立窗口）；
再不行就用默认浏览器。
"""
import os, sys, threading, subprocess, time, socket

ROOT = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
PORT = int(os.environ.get("LOM_PORT", "8765"))
URL = "http://127.0.0.1:%d" % PORT


def port_open():
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def start_server():
    if port_open():
        return
    import app
    threading.Thread(target=app.serve, daemon=True).start()
    for _ in range(40):
        if port_open():
            return
        time.sleep(0.1)


def run_edge():
    edge = None
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            edge = p
            break
    if not edge:
        return False
    prof = os.path.join(ROOT, "data", "edge-profile")
    subprocess.Popen([edge, "--app=" + URL, "--window-size=1480,940",
                      "--user-data-dir=" + prof, "--no-first-run",
                      "--disable-features=TranslateUI"])
    return True


def _bg_update():
    try:
        import updater
        updater.check_and_update(interactive=True)
    except Exception as e:
        print("更新检查跳过", e)


def ensure_db():
    """data/wiki.db 不存在但有 wiki.db.xz 时，解压一份出来（首次启动）。"""
    db = os.path.join(ROOT, "data", "wiki.db")
    xz = db + ".xz"
    if os.path.exists(db) or not os.path.exists(xz):
        return
    try:
        import lzma, shutil
        tmp = db + ".part"
        with lzma.open(xz, "rb") as f, open(tmp, "wb") as g:
            shutil.copyfileobj(f, g, 1 << 20)
        os.replace(tmp, db)
    except Exception as e:
        print("数据库解压失败", e)


def main():
    ensure_db()
    start_server()
    threading.Thread(target=_bg_update, daemon=True).start()
    try:
        import webview
        win = webview.create_window("活侠传追踪Wiki", URL,
                                    width=1480, height=940,
                                    min_size=(980, 640),
                                    background_color="#141619",
                                    text_select=True)
        webview.start()
        return
    except Exception:
        pass
    if not run_edge():
        import webbrowser
        webbrowser.open(URL)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
