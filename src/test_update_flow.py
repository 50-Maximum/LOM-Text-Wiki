# -*- coding: utf-8 -*-
"""验证在线更新链路：起本地清单服务 → 触发更新 → 检查是否重启并换版。

只在临时副本上做，不动发布目录。
"""
import io, json, os, shutil, subprocess, sys, time, zipfile, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
SRC = os.path.join(BASE, "dist_build_v06", "活侠传追踪Wiki")
TMP = r"D:\LegendOfMortal Wiki\_updtest"
SRV = os.path.join(TMP, "srv")
APP = os.path.join(TMP, "app")

shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(SRV, exist_ok=True)
if not os.path.isdir(SRC):
    print("发布目录不存在")
    sys.exit(1)
print("复制程序到临时目录…")
shutil.copytree(SRC, APP)

# 造更新包（只含 version.json 与一个标记文件）
pkg = os.path.join(SRV, "pkg.zip")
with zipfile.ZipFile(pkg, "w") as z:
    z.writestr("version.json", json.dumps(
        {"version": "0.6.1", "app": "活侠传追踪Wiki", "built_at": "2026-10-27"},
        ensure_ascii=False, indent=1))
    z.writestr("data/upd_marker.txt", "updated")

json.dump({"version": "0.6.1", "url": "http://127.0.0.1:8899/pkg.zip",
           "notes": "测试更新"},
          open(os.path.join(SRV, "update.json"), "w", encoding="utf-8"), ensure_ascii=False)

# 副本里的清单地址
json.dump({"manifest": "http://127.0.0.1:8899/update.json"},
          open(os.path.join(APP, "data", "update.json"), "w", encoding="utf-8"))

srv = subprocess.Popen([sys.executable, "-m", "http.server", "8899", "--bind", "127.0.0.1"],
                       cwd=SRV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)


def get(path, timeout=6):
    with urllib.request.urlopen("http://127.0.0.1:8765" + path, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


exe = os.path.join(APP, "活侠传追踪Wiki.exe")
p = subprocess.Popen([exe], cwd=APP)
time.sleep(10)
try:
    print("启动版本:", get("/api/appver"))
    print("检查更新:", get("/api/update/check"))
    print("触发更新:", get("/api/update/apply"))
except Exception as e:
    print("接口失败:", e)

# 等它自己重启
for i in range(40):
    time.sleep(2)
    try:
        v = get("/api/appver", timeout=3)
        if v.get("version") == "0.6.1":
            print("更新成功，重启后版本:", v)
            break
    except Exception:
        pass
else:
    print("!! 更新后未检测到新版本")

print("标记文件存在:", os.path.exists(os.path.join(APP, "data", "upd_marker.txt")))
srv.terminate()
for pr in subprocess.run(["tasklist", "/FI", "IMAGENAME eq 活侠传追踪Wiki.exe"],
                         capture_output=True, text=True).stdout.splitlines():
    if "活侠传" in pr:
        pid = pr.split()[-1]
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
print("测试结束")
