# -*- coding: utf-8 -*-
"""单独验证 updater.fetch_remote 在副本目录下能否取到清单。"""
import io, importlib, json, os, subprocess, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
TMP = os.path.join(BASE, "_updtest")
SRV = os.path.join(TMP, "srv")
APP = os.path.join(TMP, "app")
sys.path.insert(0, os.path.join(BASE, "src"))
import updater

updater.ROOT = APP
updater.CONF_FILE = os.path.join(APP, "data", "update.json")
updater.VER_FILE = os.path.join(APP, "version.json")

srv = subprocess.Popen([sys.executable, "-m", "http.server", "8899", "--bind", "127.0.0.1"],
                       cwd=SRV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
print("清单地址:", updater.manifest_url())
print("本地版本:", updater.local_version())
try:
    print("远程清单:", updater.fetch_remote())
except Exception as e:
    print("异常:", type(e).__name__, e)
import urllib.request
try:
    print("直连:", urllib.request.urlopen("http://127.0.0.1:8899/update.json", timeout=5).read()[:80])
except Exception as e:
    print("直连失败:", type(e).__name__, e)
print("环境代理:", {k: v for k, v in os.environ.items() if "PROXY" in k.upper()})
srv.terminate()
