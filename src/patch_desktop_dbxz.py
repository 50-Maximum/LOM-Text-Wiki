# -*- coding: utf-8 -*-
"""首次运行解压 data/wiki.db.xz，再启动服务。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\desktop.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

if "def ensure_db" not in s:
    blk = '''def ensure_db():
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


'''
    s = s.replace("def main():", blk + "def main():\n    ensure_db()", 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("desktop.py 已加首次解压")
else:
    print("已有 ensure_db")
