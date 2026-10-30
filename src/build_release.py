# -*- coding: utf-8 -*-
"""打发布包：压缩 dist_build_v06 目录 → release/，并生成 update.json 清单骨架。"""
import hashlib, io, json, os, shutil, sys, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
SRC = os.path.join(BASE, "dist_build_v07", "活侠传追踪Wiki")
REL = os.path.join(BASE, "release")
VER = str(json.load(open(os.path.join(BASE, "version.json"), encoding="utf-8"))["version"])
_VJ = json.load(open(os.path.join(BASE, "version.json"), encoding="utf-8"))
CFG = {}
try:
    CFG = json.load(open(os.path.join(BASE, "data", "update.json"), encoding="utf-8"))
except Exception:
    CFG = {}
GH = CFG.get("github") or {}
NAME = "活侠传追踪Wiki-%s" % VER
_url = ("https://github.com/%s/%s/releases/download/v%s/%s.zip"
        % (GH.get("owner"), GH.get("repo"), VER, NAME))
if not GH.get("owner") or not GH.get("repo"):
    _url = "https://github.com/OWNER/REPO/releases/download/v%s/%s.zip" % (VER, NAME)

os.makedirs(REL, exist_ok=True)
zp = os.path.join(REL, NAME + ".zip")
if os.path.exists(zp):
    os.remove(zp)

print("压缩中…")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for base, dirs, files in os.walk(SRC):
        for f in files:
            full = os.path.join(base, f)
            rel = os.path.relpath(full, SRC)
            z.write(full, os.path.join(NAME, rel))

size = os.path.getsize(zp)
h = hashlib.sha256()
with open(zp, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)
digest = h.hexdigest()

manifest = {
    "version": VER,
    "url": _url,
    "size": size,
    "sha256": digest,
    "notes": _VJ.get("notes") or ("%s：内容更新。" % VER),
    "date": _VJ.get("built_at") or "",
}
mp = os.path.join(REL, "update.json")
json.dump(manifest, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("发布包:", zp, "%.1f MB" % (size / 1048576))
print("sha256:", digest)
print("清单:", mp)
