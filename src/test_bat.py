# -*- coding: utf-8 -*-
"""单独验证 _bat_apply：只覆盖、校验文件落地（用 notepad 占位重启）。"""
import io, json, os, shutil, sys, time, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
sys.path.insert(0, os.path.join(BASE, "src"))
import updater

SCRATCH = os.path.join(BASE, "_updtest", "bat_root")
shutil.rmtree(SCRATCH, ignore_errors=True)
os.makedirs(os.path.join(SCRATCH, "data"), exist_ok=True)
open(os.path.join(SCRATCH, "version.json"), "w", encoding="utf-8").write('{"version":"0.6"}')

zp = os.path.join(BASE, "_updtest", "bat_pkg.zip")
with zipfile.ZipFile(zp, "w") as z:
    z.writestr("version.json", '{"version":"0.6.1"}')
    z.writestr("data/marker.txt", "ok")

updater.ROOT = SCRATCH
log = os.path.join(os.environ["TEMP"], "lom_update.log")
if os.path.exists(log):
    os.remove(log)
updater._bat_apply(zp, "notepad.exe")
print("已派出批处理，等待覆盖…")
time.sleep(8)
print("version.json:", open(os.path.join(SCRATCH, "version.json"), encoding="utf-8").read())
print("marker:", os.path.exists(os.path.join(SCRATCH, "data", "marker.txt")))
if os.path.exists(log):
    print("--- log ---")
    print(open(log, encoding="gbk", errors="replace").read()[:1200])
