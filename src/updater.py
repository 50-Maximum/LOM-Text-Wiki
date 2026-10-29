# -*- coding: utf-8 -*-
"""版本更新器：支持「远程清单」与「本地 _update 目录」两种来源。

远程清单（data/update.json 里配 manifest 地址）：
    {"version": "0.7", "url": "https://.../pkg.zip", "notes": "更新说明",
     "sha256": "可选", "size": 123456}

zip 内为要覆盖到程序根目录的文件（保持相对路径），可只含 data/web，也可含整个程序。
更新方式：下载 → 解压到临时目录 → 写一个等待本进程退出的批处理 → 覆盖 → 重启。
"""
import os, sys, json, hashlib, subprocess, tempfile, time, zipfile, shutil

ROOT = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER_FILE = os.path.join(ROOT, "version.json")
CONF_FILE = os.path.join(ROOT, "data", "update.json")
UPD_DIR = os.path.join(ROOT, "_update")

APP_NAME = "活侠传追踪Wiki"
DEFAULT_MANIFEST = ""          # 发布后填：例如 https://xxx/update.json


def local_version():
    try:
        return str(json.load(open(VER_FILE, encoding="utf-8")).get("version") or "0.0.0")
    except Exception:
        return "0.0.0"


def parse(v):
    out = []
    for p in str(v).split("."):
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return (out + [0] * 4)[:4]


def newer(remote, local):
    return parse(remote) > parse(local)


def manifest_url():
    try:
        return str(json.load(open(CONF_FILE, encoding="utf-8")).get("manifest") or DEFAULT_MANIFEST)
    except Exception:
        return DEFAULT_MANIFEST


def fetch_remote(timeout=6):
    """取更新清单：清单直链 → GitHub 最新 release。都没有则 None。"""
    url = manifest_url().strip()
    if not url:
        return fetch_github()
    info = None
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "LoMWiki/%s" % local_version()})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        if isinstance(data, dict) and data.get("version"):
            return data
    except Exception:
        info = None
    return info or fetch_github()


def download(url, dest, sha256="", timeout=60):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "LoMWiki/%s" % local_version()})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    if sha256:
        h = hashlib.sha256()
        with open(dest, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        if h.hexdigest().lower() != sha256.strip().lower():
            raise ValueError("校验失败：文件不完整")
    return dest


def _bat_apply(zip_path, exe_name):
    """解压到临时目录，写批处理：等本进程退出→覆盖→重启。批处理纯 ASCII，路径走环境变量。"""
    stage = os.path.join(tempfile.gettempdir(), "lom_stage_%d" % int(time.time()))
    if os.path.isdir(stage):
        shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(stage)

    # 安装包内通常套着「活侠传追踪Wiki-X.Y.Z」一层目录，覆盖时要以它为源，
    # 否则会把整包塞进旧目录里、旧文件一个也不会被替换。
    _ents = [x for x in os.listdir(stage) if not x.startswith(".")]
    if len(_ents) == 1 and os.path.isdir(os.path.join(stage, _ents[0])):
        stage = os.path.join(stage, _ents[0])

    log = os.path.join(tempfile.gettempdir(), "lom_update.log")
    bat = os.path.join(tempfile.gettempdir(), "lom_update_%d.bat" % int(time.time()))
    lines = [
        "@echo off",
        "setlocal",
        'echo [start] %DATE% %TIME% >> "%LOM_LOG%"',
        'if not "%LOM_PID%"=="" powershell -NoProfile -WindowStyle Hidden '
        '-Command "Wait-Process -Id %LOM_PID% -ErrorAction SilentlyContinue"',
        "timeout /t 2 /nobreak >nul",
        'echo [copy] %LOM_STAGE% -^> %LOM_ROOT% >> "%LOM_LOG%"',
        'robocopy "%LOM_STAGE%" "%LOM_ROOT%" /E /IS /IT /R:2 /W:1 >> "%LOM_LOG%" 2>&1',
        'if errorlevel 8 xcopy /y /e /i "%LOM_STAGE%\\*" "%LOM_ROOT%\\" >> "%LOM_LOG%" 2>&1',
        'echo [restart] %LOM_EXE% >> "%LOM_LOG%"',
        'start "" "%LOM_ROOT%\\%LOM_EXE%"',
        'rd /s /q "%LOM_STAGE%"',
        'del "%~f0"',
    ]
    with open(bat, "w", encoding="ascii", errors="replace", newline="\n") as f:
        f.write("\n".join(lines))
    env = os.environ.copy()
    env.update({"LOM_ROOT": ROOT, "LOM_STAGE": stage,
                "LOM_EXE": exe_name, "LOM_LOG": log, "LOM_PID": str(os.getpid())})
    subprocess.Popen(["cmd", "/c", bat], cwd=tempfile.gettempdir(), env=env,
                     creationflags=0x00000008 | 0x00000200)  # DETACHED | NO_WINDOW
    return bat


def exe_name():
    return os.path.basename(sys.executable) if getattr(sys, "frozen", False) else APP_NAME + ".exe"


def apply_update(info):
    """下载/取包 + 排定覆盖 + 退出本进程。成功返回 True。"""
    url = str(info.get("url") or "").strip()
    if not url:
        return False
    tmpzip = os.path.join(tempfile.gettempdir(), "lom_update_%d.zip" % int(time.time()))
    download(url, tmpzip, info.get("sha256") or "")
    _bat_apply(tmpzip, exe_name())
    time.sleep(0.6)
    os._exit(0)


def ask(title, msg):
    try:
        r = __import__("ctypes").windll.user32.MessageBoxW(None, msg, title, 0x04 | 0x20)
        return r == 6
    except Exception:
        return False


def local_package():
    """本地 _update/update.json（离线更新包），没有则 None。"""
    p = os.path.join(UPD_DIR, "update.json")
    if not os.path.exists(p):
        return None
    try:
        m = json.load(open(p, encoding="utf-8"))
        if m.get("version"):
            zp = os.path.join(UPD_DIR, m.get("zip") or "app.zip")
            if os.path.exists(zp):
                m["url"] = "file:///" + zp.replace("\\", "/")
                return m
    except Exception:
        pass
    return None


# ---------- GitHub Releases ----------
def github_repo():
    """从 data/update.json 读 {"github": {"owner": "...", "repo": "..."}}。"""
    try:
        cfg = json.load(open(CONF_FILE, encoding="utf-8"))
        g = cfg.get("github") or {}
        o, r = (g.get("owner") or "").strip(), (g.get("repo") or "").strip()
        if o and r:
            return o, r
    except Exception:
        pass
    return "", ""


def fetch_github(timeout=8):
    """查 GitHub 最新 release，返回与 fetch_remote 相同的清单结构。"""
    owner, repo = github_repo()
    if not owner or not repo:
        return None
    import urllib.request
    api = "https://api.github.com/repos/%s/%s/releases/latest" % (owner, repo)
    try:
        req = urllib.request.Request(api, headers={
            "User-Agent": "LoMWiki/%s" % local_version(),
            "Accept": "application/vnd.github+json",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return None
    tag = str(data.get("tag_name") or data.get("name") or "").strip()
    ver = tag.lstrip("vV")
    if not ver:
        return None
    assets = data.get("assets") or []
    pick = None
    for a in assets:
        nm = str(a.get("name") or "")
        if nm.lower().endswith(".zip"):
            pick = a
            if "wiki" in nm.lower() or APP_NAME in nm:
                break
    if not pick:
        return None
    _dg = str(pick.get("digest") or "").strip()
    _sha = _dg.split(":", 1)[1].strip() if _dg.lower().startswith("sha256:") else ""
    return {
        "version": ver,
        "url": pick.get("browser_download_url") or "",
        "size": pick.get("size") or 0,
        "sha256": _sha,
        "notes": (data.get("body") or "")[:600],
        "date": (data.get("published_at") or "")[:10],
        "source": "github",
    }


def check_and_update(interactive=True):
    """启动时调用：有新版→询问→更新→退出。返回是否已进入更新流程。"""
    info = local_package()
    if info is None:
        info = fetch_remote()
    if not info or not newer(str(info.get("version")), local_version()):
        return False
    if interactive:
        notes = (info.get("notes") or "").strip()
        msg = "发现新版本 %s（当前 %s）\n\n%s\n\n现在更新吗？" % (
            info.get("version"), local_version(), notes[:400] if notes else "无更新说明")
        if not ask("%s 更新" % APP_NAME, msg):
            return False
    url = str(info.get("url") or "")
    if url.startswith("file:///"):
        zp = url[8:].replace("/", "\\")
        _bat_apply(zp, exe_name())
        os._exit(0)
    return apply_update(info)


if __name__ == "__main__":
    print("当前版本", local_version())
    print("清单地址", manifest_url() or "（未配置）")
    r = fetch_remote()
    print("远程清单", r)
