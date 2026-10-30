# -*- coding: utf-8 -*-
"""给 updater 加 GitHub Releases 支持：优先读 data/update.json 的 github 配置。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\updater.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

add = '''

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
    return {
        "version": ver,
        "url": pick.get("browser_download_url") or "",
        "size": pick.get("size") or 0,
        "notes": (data.get("body") or "")[:600],
        "date": (data.get("published_at") or "")[:10],
        "source": "github",
    }
'''

if "fetch_github" not in s:
    s = s.replace("def check_and_update(interactive=True):", add.strip("\n") + "\n\n\ndef check_and_update(interactive=True):", 1)

# fetch_remote 增加 GitHub 兜底
old = '''def fetch_remote(timeout=6):
    """取远程清单，返回 dict 或 None（无网络/未配置/出错都返回 None）。"""
    url = manifest_url().strip()
    if not url:
        return None'''
new = '''def fetch_remote(timeout=6):
    """取更新清单：清单直链 → GitHub 最新 release。都没有则 None。"""
    url = manifest_url().strip()
    if not url:
        return fetch_github()
    info = None'''
if old in s:
    s = s.replace(old, new, 1)
    # 补上原函数体的返回值逻辑：在 except 后加 github 兜底
    s = s.replace('''        if isinstance(data, dict) and data.get("version"):
            return data
    except Exception:
        return None
    return None''', '''        if isinstance(data, dict) and data.get("version"):
            return data
    except Exception:
        info = None
    return info or fetch_github()''', 1)

open(p, "w", encoding="utf-8", newline="\n").write(s)
print("updater.py 已加 GitHub Releases 支持")
