# -*- coding: utf-8 -*-
"""P3 本地服务：零依赖 HTTP + SQLite 查询接口。"""
import os, re, sys, json, sqlite3, urllib.parse, mimetypes, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "wiki.db")
WEB = os.path.join(ROOT, "web")
PORT = int(os.environ.get("LOM_PORT", "8765"))

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from qfilter import build_where, FilterError, FIELDS as FILTER_FIELDS
except Exception:
    build_where = None
    FilterError = Exception
    FILTER_FIELDS = []



def _app_version():
    try:
        return str(json.load(open(os.path.join(ROOT, "version.json"), encoding="utf-8")).get("version") or "0.0.0")
    except Exception:
        return "0.0.0"

CHAPTER_NAMES = {
    "序章": "入门试炼",
    "第0章": "唐门与飞石帮",
    "第1章": "招募弟子",
    "第2章": "上山之路与论战",
    "第3章": "叶云裳与疗伤",
    "第4章": "龙渊与说服",
    "第5章": "逃脱与赌局",
    "第6章": "唐门伤亡",
    "第7章": "出使青城与崆峒",
    "第8章": "刺客与武林盟",
    "支线": "支线",
    "角色线": "角色线",
    "其他": "其他",
}


def conn():
    c = sqlite3.connect(DB, timeout=5)
    c.row_factory = sqlite3.Row
    return c


def q(sql, args=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args)]


def one(sql, args=()):
    r = q(sql, args)
    return r[0] if r else None


_BH_CACHE = None


def branch_human():
    """分支串的人话对照（script\x1f原文 → 人话），第一次用时读入。"""
    global _BH_CACHE
    if _BH_CACHE is None:
        try:
            _BH_CACHE = json.load(open(os.path.join(ROOT, "data", "branch_human.json"), encoding="utf-8"))
        except Exception:
            _BH_CACHE = {}
    return _BH_CACHE


_BL_CACHE = None
_O_RE = re.compile(r"(?<![A-Za-z0-9_])O_[A-Za-z0-9_]+(?![A-Za-z0-9_])")
_NODE_RE = re.compile(r"\b(?:talk|exit|event|move|default)\+([A-Za-z0-9_]+)\+\d+\+\d+")
_COND1 = re.compile(r"条件\s*([A-Za-z0-9_]+)\s*｜\s*")
_COND2 = re.compile(r"【条件\s*([A-Za-z0-9_]+)】\s*")
_COND3 = re.compile(r"（([A-Za-z0-9_]{4,})：")
_BARE_RE = re.compile(r"(?<![^\s>+›（])([A-Za-z_][A-Za-z0-9_]*)\s*｜\s*")
_SWITCH_RE = re.compile(r"switch(\d+)_(\d+)_result=(\d+)")
_PAREN_RE = re.compile(r"\s*\([A-Za-z][A-Za-z0-9_]{4,}\)")
_VARS = [
    (re.compile(r"TalkOption_0*(\d+)"), r"该处选项\1"),
    (re.compile(r"Facility_0*(\d+)"), r"设施\1"),
    (re.compile(r"好感度_([\u4e00-\u9fff]+)"), r"好感度·\1"),
    (re.compile(r"技能_([\u4e00-\u9fff]+)"), r"技能·\1"),
]


def branch_labels():
    """选项代号 → 中文选项名，第一次用时读入。"""
    global _BL_CACHE
    if _BL_CACHE is None:
        try:
            _BL_CACHE = json.load(open(os.path.join(ROOT, "data", "branch_labels.json"), encoding="utf-8"))
        except Exception:
            _BL_CACHE = {}
    return _BL_CACHE


def code_to_label(b):
    """分支串人话化：选项代号→选项名，条件代号→中文条件名，内部开关→分支N。"""
    if not b:
        return ""
    bl = branch_labels()
    t = _NODE_RE.sub(r"\1", b)
    t = _SWITCH_RE.sub(r"分支\3", t)
    t = _COND1.sub("条件 ", t)
    t = _COND2.sub("条件 ", t)
    t = _COND3.sub("（", t)
    t = _O_RE.sub(lambda m: bl.get(m.group(0)) or m.group(0), t)
    t = _BARE_RE.sub("", t)
    for _p, _r in _VARS:
        t = _p.sub(_r, t)
    t = _PAREN_RE.sub("", t)
    t = re.sub(r"\s+>\s+(?![=])", " > ", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()




def phrase(text):
    """把查询拆成单字短语：'布衣' -> '"布 衣"'，实现任意子串匹配。"""
    chars = [c for c in text if not c.isspace() and c not in '"']
    if not chars:
        return None
    return '"' + " ".join(chars) + '"'


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _text(self, s, code=200):
        b = (s or "").encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _file(self, path):
        if not os.path.isfile(path):
            self.send_error(404)
            return
        b = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
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
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                return self._json({"ok": True})
            except Exception as e:
                return self._json({"ok": False, "err": str(e)})
        if u.path == "/api/yehua/install":
            try:
                return self._json(self.yehua_install(urllib.parse.parse_qs(u.query)))
            except Exception as e:
                return self._json({"ok": False, "msg": str(e)})
        return self.send_error(404)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p, qs = u.path, urllib.parse.parse_qs(u.query)
        try:
            if p == "/":
                return self._file(os.path.join(WEB, "wiki.html"))
            if p == "/text":
                return self._file(os.path.join(WEB, "index.html"))
            if p.startswith("/static/"):
                return self._file(os.path.join(WEB, p[len("/static/"):]))
            if p == "/api/meta":
                return self._json(self.meta())
            if p == "/api/search":
                return self._json(self.search(qs.get("q", [""])[0],
                                              int(qs.get("limit", ["60"])[0])))
            if p == "/api/scenes":
                return self._json(self.scenes(qs.get("chapter", [None])[0]))
            if p == "/api/scene":
                return self._json(self.scene(qs.get("script", [""])[0]))
            if p == "/api/ledger":
                return self._json(self.ledger(qs))
            if p == "/api/terms":
                return self._json(self.terms(qs.get("type", [""])[0]))
            if p == "/api/term":
                return self._json(self.term(qs.get("type", [""])[0], qs.get("name", [""])[0]))
            if p == "/api/categories":
                return self._json(self.categories())
            if p == "/api/factions":
                return self._json(self.factions())
            if p == "/api/faction":
                return self._json(self.faction(qs.get("name", [""])[0]))
            if p == "/api/place":
                return self._json(self.place(qs.get("name", [""])[0]))
            if p == "/api/media/portrait":
                return self.portrait(qs.get("id", [""])[0])
            if p == "/api/entity":
                return self._json(self.entity(qs.get("id", [""])[0]))
            if p == "/api/character":
                return self._json(self.character(qs.get("id", [""])[0]))
            if p == "/api/characters":
                return self._json(self.characters(qs.get("q", [""])[0]))
            if p == "/api/timeline":
                return self._json(self.timeline())
            if p == "/api/home":
                return self._json(self.home())
            if p == "/api/events":
                return self._json(self.events(qs))
            if p == "/api/flags":
                return self._json(self.flags(qs.get("q", [""])[0]))
            if p == "/api/flaglist":
                return self._json({"flags": q(
                    "SELECT f.flag, COUNT(*) n, COALESCE(i.label,'') label FROM flags f "
                    "LEFT JOIN flaginfo i ON i.flag=f.flag "
                    "GROUP BY f.flag ORDER BY n DESC, f.flag")})
            if p == "/api/flag":
                f = qs.get("f", [""])[0]
                lab = one("SELECT label FROM flaginfo WHERE flag=?", (f,))
                return self._json({"flag": f, "label": (lab or {}).get("label", ""), "rows": q(
                    "SELECT f.script, f.seq, f.value, f.after_key, l.text, sc.chapter, sc.cjk "
                    "FROM flags f LEFT JOIN lines l ON l.script=f.script AND l.seq=f.seq "
                    "LEFT JOIN scenes sc ON sc.script=f.script "
                    "WHERE f.flag=? ORDER BY f.script, f.seq LIMIT 600", (f,))})
            if p == "/api/kv":
                return self._json(self.kv(qs.get("ns", [""])[0]))
            if p == "/api/wiki/list":
                return self._json(self.wiki_list(qs.get("type", [""])[0],
                                                 qs.get("q", [""])[0]))
            if p == "/api/wiki":
                return self._json(self.wiki(qs.get("type", [""])[0],
                                            qs.get("name", [""])[0]))
            if p == "/api/page":
                return self._json(self.page(qs.get("slug", [""])[0]))
            if p == "/api/filter2":
                return self._json(self.filter_fields(qs))
            if p == "/api/stats":
                return self._json(self.stats())
            if p == "/api/filter":
                return self._json(self.filter_scenes(
                    qs.get("q", [""])[0],
                    int(qs.get("limit", ["300"])[0])))
            if p == "/api/pages":
                return self._json(self.pages_list(qs.get("type", [""])[0],
                                                  qs.get("q", [""])[0],
                                                  int(qs.get("offset", ["0"])[0]),
                                                  int(qs.get("limit", ["80"])[0]),
                                                  qs.get("facet", [""])[0],
                                                  qs.get("facet2", [""])[0]))
            if p == "/api/facets":
                return self._json(self.facets(qs.get("type", [""])[0],
                                              qs.get("dim", ["1"])[0]))
            if p == "/api/types":
                types = q("select type,count(*) n from pages where hidden=0 "
                          "group by type order by n desc")
                try:
                    kp = one("select count(*) n from place_children where slug like '地点/%'")["n"]
                    kf = one("select count(*) n from place_children where slug like '势力/%'")["n"]
                    for t in types:
                        if t["type"] == "地点":
                            t["n"] -= kp
                        elif t["type"] == "势力":
                            t["n"] -= kf
                except Exception:
                    pass
                return self._json({"types": types})
            if p == "/api/appver":
                return self._json({"name": "活侠传追踪Wiki", "version": _app_version()})
            if p == "/api/yehua":
                return self._json(self.yehua(qs))
            if p == "/api/yehua/brief":
                return self._text(self.yehua_brief(qs))
            if p == "/api/update/check":
                return self._json(update_check())
            if p == "/api/update/apply":
                return self._json(update_apply())
            if p == "/api/search2":
                return self._json(self.search2(qs.get("q", [""])[0]))
            if p == "/api/version":
                try:
                    _st = os.stat(os.path.join(ROOT, "data", "wiki.db"))
                    _v = "%d-%d" % (int(_st.st_mtime), _st.st_size)
                except Exception:
                    _v = "0"
                return self._json({"v": _v})
            if p == "/api/nameindex":
                return self._json({"names": q(
                    "select name,slug from ( "
                    "select name,slug from pages where type in "
                    "('势力','地点','书物','物品','武学','装备') "
                    "and length(name) between 2 and 10 "
                    "union all "
                    "select alias as name, slug from aliases "
                    "where length(alias) between 2 and 10 ) "
                    "order by length(name) desc")})
            self.send_error(404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def meta(self):
        m = {r["key"]: r["value"] for r in q("SELECT * FROM meta")}
        return {"meta": m, "counts": {
            "lines": one("SELECT COUNT(*) n FROM lines")["n"],
            "scenes": one("SELECT COUNT(*) n FROM scenes")["n"],
            "speakers": one("SELECT COUNT(DISTINCT speaker) n FROM lines")["n"],
            "flags": one("SELECT COUNT(*) n FROM flags")["n"],
            "choices": one("SELECT COUNT(*) n FROM choices")["n"],
        }}

    def search(self, text, limit=60):
        text = text.strip()
        if not text:
            return {"hits": [], "characters": [], "titles": []}
        ph = phrase(text)
        hits = []
        if ph:
            hits = q("""SELECT l.id, l.script, l.seq, l.speaker, l.text, l.mode
                        FROM lines_fts JOIN lines l ON l.id = lines_fts.rowid
                        WHERE lines_fts MATCH ? ORDER BY rank LIMIT ?""", (ph, limit))
        chars = q("""SELECT DISTINCT speaker, speaker_id FROM lines
                     WHERE speaker LIKE ? LIMIT 20""", ("%" + text + "%",))
        names = q("SELECT id, name FROM names WHERE name LIKE ? LIMIT 20",
                  ("%" + text + "%",))
        titles = q("SELECT script, chapter, line_count FROM scenes "
                   "WHERE (script LIKE ? OR chapter LIKE ?) AND line_count>0 LIMIT 20",
                   ("%" + text + "%", "%" + text + "%"))
        for t in titles:
            t["chapter_name"] = CHAPTER_NAMES.get(t["chapter"], "")
        events = q("SELECT id, title FROM chk WHERE title LIKE ? LIMIT 20",
                   ("%" + text + "%",))
        facs = q("SELECT name FROM factions WHERE name LIKE ? LIMIT 10", ("%" + text + "%",))
        plc = q("SELECT DISTINCT place FROM scenes WHERE place LIKE ? AND place<>'' LIMIT 10",
                ("%" + text + "%",))
        led = q("SELECT chapter,type,name,note FROM ledger WHERE name LIKE ? OR note LIKE ? LIMIT 20",
                ("%" + text + "%", "%" + text + "%"))
        ents = q("""SELECT type,name,mentions FROM entities
                     WHERE name LIKE ? ORDER BY mentions DESC LIMIT 20""", ("%" + text + "%",))
        return {"hits": hits, "characters": chars, "titles": names,
                "scene_titles": titles, "event_titles": events,
                "factions": facs, "places": plc, "ledger": led, "entities": ents}

    def scenes(self, chapter=None):
        if chapter:
            rows = q("SELECT * FROM scenes WHERE chapter=? AND line_count>0 ORDER BY script", (chapter,))
        else:
            rows = q("SELECT * FROM scenes WHERE line_count>0 ORDER BY chapter, script")
        chapters = q("SELECT chapter, COUNT(*) n FROM scenes WHERE line_count>0 GROUP BY chapter ORDER BY chapter")
        for c in chapters:
            c["name"] = CHAPTER_NAMES.get(c["chapter"], "")
        return {"scenes": rows, "chapters": chapters}

    def timeline(self):
        cols = "script,title,place,chapter,line_count,time_from,time_to,tkey,battles"
        timed = q("SELECT " + cols + " FROM scenes WHERE tkey>0 AND line_count>0 ORDER BY tkey, script")
        untimed = q("SELECT " + cols + " FROM scenes WHERE tkey=0 AND line_count>0 ORDER BY chapter, script")
        return {"timed": timed, "untimed": untimed}

    def home(self):
        counts = {
            "lines": one("SELECT COUNT(*) n FROM lines")["n"],
            "scenes": one("SELECT COUNT(*) n FROM scenes WHERE line_count>0")["n"],
            "speakers": one("SELECT COUNT(DISTINCT speaker) n FROM lines")["n"],
            "choices": one("SELECT COUNT(*) n FROM choices")["n"],
            "flags": one("SELECT COUNT(*) n FROM flags")["n"],
            "battles": one("SELECT COUNT(*) n FROM scenes WHERE battles>0")["n"],
        }
        places = q("SELECT place, COUNT(*) n FROM scenes WHERE place<>'' GROUP BY place ORDER BY n DESC LIMIT 12")
        chapters = q("SELECT chapter, COUNT(*) n, SUM(line_count) l FROM scenes WHERE line_count>0 GROUP BY chapter ORDER BY chapter")
        for c in chapters:
            c["name"] = CHAPTER_NAMES.get(c["chapter"], "")
        t = one("SELECT time_from, time_to FROM scenes WHERE tkey>0 ORDER BY tkey LIMIT 1")
        t2 = one("SELECT time_from, time_to, tkey FROM scenes WHERE tkey>0 ORDER BY tkey DESC LIMIT 1")
        return {"counts": counts, "places": places, "chapters": chapters,
                "earliest": (t or {}).get("time_from") or (t or {}).get("time_to", ""),
                "latest": (t2 or {}).get("time_to") or (t2 or {}).get("time_from", "")}

    def events(self, qs):
        place = qs.get("place", [""])[0]
        trait = qs.get("trait", [""])[0]
        battle = qs.get("battle", [""])[0]
        tiers = qs.get("tier", [""])[0]
        chapter = qs.get("chapter", [""])[0]
        where, args = ["line_count>0"], []
        if chapter:
            where.append("chapter=?")
            args.append(chapter)
        if place:
            where.append("place=?")
            args.append(place)
        if trait:
            where.append("traits LIKE ?")
            args.append("%" + trait + "%")
        if battle:
            where.append("battles>0")
        for tk in [x for x in tiers.split(",") if x]:
            where.append("tiers LIKE ?")
            args.append("%" + tk + "%")
        rows = q("SELECT * FROM scenes WHERE " + " AND ".join(where) +
                 " ORDER BY chapter, script", tuple(args))
        places = q("SELECT place, COUNT(*) n FROM scenes WHERE place<>'' AND line_count>0 "
                   "GROUP BY place ORDER BY n DESC")
        roots = q("SELECT root, COUNT(*) n FROM scenes WHERE root<>'' AND line_count>0 "
                  "GROUP BY root ORDER BY n DESC")
        return {"scenes": rows, "places": places, "roots": roots}

    def scene(self, script):
        s = one("SELECT * FROM scenes WHERE script=?", (script,))
        if not s:
            return {"error": "not found"}
        lines = q("SELECT seq,key,text,speaker,speaker_id,mode,branch FROM lines "
                  "WHERE script=? ORDER BY seq", (script,))
        _bh = branch_human()
        for _l in lines:
            _b = _l.get("branch") or ""
            if _b:
                _l["branch_h"] = code_to_label(_bh.get(script + "\x1f" + _b) or _b)
        brs = {r["branch"]: json.loads(r["effects"]) for r in
               q("SELECT branch, effects FROM branches WHERE script=?", (script,))}
        chs = q("SELECT seq,checkpoint,options FROM choices WHERE script=? ORDER BY seq", (script,))
        conds = {c["id"]: json.loads(c["attrs"]) for c in
                 q("SELECT id, attrs FROM cond")} if any(c["checkpoint"] for c in chs) else {}
        for c in chs:
            c["options"] = json.loads(c["options"])
            c["requires"] = conds.get(c["checkpoint"], [])
            row = one("SELECT title FROM chk WHERE id=?", (c["checkpoint"],))
            c["title"] = (row or {}).get("title", "")
            row2 = one("SELECT attrs FROM cond WHERE id=?", (c["checkpoint"] + "@cond",))
            c["cond_text"] = json.loads(row2["attrs"]) if row2 else []
        _STAT = {"money": "银两", "life": "体力", "stamina": "内力", "dexterity": "轻功",
                 "charisma": "魅力", "literacy": "学问", "mental": "心相", "fate": "命运",
                 "disposition": "性情", "behaviour": "处世", "training": "修养", "karma": "道德",
                 "talking": "嘴力", "fame": "名声", "people": "门人", "team": "向心",
                 "faction": "门派规模", "weapon": "锻造", "poison": "炼丹", "contribution": "贡献度",
                 "internal": "阴阳", "change-heart": "变心", "action": "行动次数", "action2": "行动",
                 "poison-resistance": "抗毒", "paralysis-resistance": "抗麻",
                 "martial-point": "武学", "assets": "门派资产",
                 "cook": "厨艺", "m-sword": "刀剑", "m-projectile": "暗器", "m-fist": "拳掌",
                 "m-leg": "腿法", "m-odd": "奇门", "m-soft": "软兵器", "m-stick": "枪棍",
                 "m-internal": "内功", "default-battle-hp": "门人血量", "relationship": "好感度",
                 "battle-people": "门人数量", "lover": "心上人"}
        _fx = {}
        try:
            for r in q("SELECT seq, idx, flags, stats FROM branch_nodes WHERE script=?", (script,)):
                if not r["idx"]:
                    continue
                try:
                    fl = json.loads(r["flags"] or "[]")
                except Exception:
                    fl = []
                try:
                    st = json.loads(r["stats"] or "[]")
                except Exception:
                    st = []
                _fx[(r["seq"], r["idx"])] = (fl, st)
        except Exception:
            _fx = {}
        try:
            for r in q("SELECT seq, idx, flags, stats FROM choice_fx WHERE script=?", (script,)):
                if not r["idx"]:
                    continue
                try:
                    fl2 = json.loads(r["flags"] or "[]")
                except Exception:
                    fl2 = []
                try:
                    st2 = json.loads(r["stats"] or "[]")
                except Exception:
                    st2 = []
                if st2 or fl2:
                    _fx[(r["seq"], r["idx"])] = (fl2, st2)
        except Exception:
            pass
        _CH = {}
        try:
            for r in q("SELECT DISTINCT speaker_id, speaker FROM lines "
                       "WHERE coalesce(speaker_id,'')<>'' AND coalesce(speaker,'')<>''"):
                _CH[r["speaker_id"]] = r["speaker"]
        except Exception:
            _CH = {}
        for c in chs:
            for _i, o in enumerate(c["options"], 1):
                got = _fx.get((c["seq"], _i))
                if not got:
                    continue
                fl, st = got
                agg = {}
                for x in st:
                    nm = (x.get("s") or "").strip()
                    if not nm:
                        continue
                    nm = _STAT.get(nm, nm)
                    if nm.startswith("好感·"):
                        nm = "好感·" + _CH.get(nm[3:], nm[3:])
                    try:
                        agg[nm] = agg.get(nm, 0.0) + float(x.get("v") or 0)
                    except Exception:
                        pass
                o["stat_delta"] = [{"s": k, "v": v} for k, v in agg.items() if v]
                o["flag_delta"] = [{"f": (x.get("f") or ""), "v": x.get("v")}
                                   for x in fl if x.get("f")]
        _tmap = {}
        try:
            for r in q("select name,title from pages where type='人物' and title<>''"):
                _tmap[r["name"].split("·")[-1]] = r["title"]
        except Exception:
            _tmap = {}
        # ---- 选项与判定的去处（正文内跳转用）----
        _jumps = {}
        _next = []
        try:
            _ENGINE = {"Free": "自由行动", "Combat": "战斗", "Battle": "战斗",
                       "Title": "标题画面", "GameOver": "游戏结束", "Story": "主线", "Ending": "结局"}

            def _jump_target(dst):
                if dst in _ENGINE:
                    return {"script": dst, "slug": "", "name": _ENGINE[dst], "kind": "engine"}
                _r = q("SELECT title FROM scenes WHERE script=?", (dst,))
                _t = (_r[0]["title"] if _r and _r[0]["title"] else "")
                _p = q("SELECT name FROM pages WHERE slug=?", ("场景/" + dst,))
                _nm = _t or (_p[0]["name"] if _p else dst)
                return {"script": dst, "slug": "场景/" + dst, "name": _nm, "kind": "scene"}

            _nodes = q("SELECT seq,kind,idx,text FROM branch_nodes "
                       "WHERE script=? AND kind IN ('dice','choose') ORDER BY seq,idx", (script,))
            _seqs, _lab = [], {}
            for _r in _nodes:
                _s0 = _r["seq"]
                if _s0 not in _seqs:
                    _seqs.append(_s0)
                _lab.setdefault(_s0, {})[_r["idx"]] = (_r["text"] or "").strip()
            _varmap = {}
            for _r in q("SELECT dst,cond FROM scene_edges WHERE src=?", (script,)):
                _cond = (_r["cond"] or "").strip()
                if not _cond.startswith("choice"):
                    continue
                _first = _cond.split("/")[0].strip()
                if "==" not in _first:
                    continue
                _var, _, _num = _first.partition("==")
                _var = _var.strip()
                try:
                    _k = int(_num.strip())
                except Exception:
                    continue
                _dst = (_r["dst"] or "").strip()
                if not _dst:
                    continue
                _varmap.setdefault(_var, {}).setdefault(_k, [])
                if _dst not in _varmap[_var][_k]:
                    _varmap[_var][_k].append(_dst)
            for _var, _rm in _varmap.items():
                _m = re.search(r"choice_[a-z]+(\d+)", _var)
                _n = int(_m.group(1)) if _m else 1
                if not (1 <= _n <= len(_seqs)):
                    continue
                _labs = _lab.get(_seqs[_n - 1], {})
                for _k, _dsts in _rm.items():
                    _lb = _labs.get(_k)
                    if not _lb:
                        continue
                    _arr = _jumps.setdefault(_lb, [])
                    for _d in _dsts:
                        _t = _jump_target(_d)
                        if _t and _t["name"] not in [_x["name"] for _x in _arr]:
                            _arr.append(_t)
            for _r in q("SELECT dst FROM scene_edges WHERE src=? AND type IN ('story','branch') "
                       "AND coalesce(cond,'')=''", (script,)):
                _t = _jump_target(_r["dst"])
                if _t and _t["name"] not in [_x["name"] for _x in _next]:
                    _next.append(_t)
        except Exception:
            _jumps = {}
        return {"scene": s, "lines": lines, "choices": chs,
                "branches": brs, "titles": _tmap, "jumps": _jumps, "next": _next,
                "participants": q("SELECT speaker nm, COUNT(*) n FROM lines WHERE script=? AND speaker<>'旁白' GROUP BY speaker ORDER BY n DESC LIMIT 12", (script,)),
                "prereq": [r for c in chs for r in (c.get("requires") or []) + (c.get("cond_text") or [])],
                "flags": q("SELECT f.seq,f.flag,f.value,f.after_key,f.branch,COALESCE(i.label,'') AS flag_cn FROM flags f LEFT JOIN flaginfo i ON i.flag=f.flag WHERE f.script=? ORDER BY f.seq", (script,))}
    def ledger(self, qs):
        ch = qs.get("chapter", [""])[0]
        ty = qs.get("type", [""])[0]
        where, args = [], []
        if ch:
            where.append("chapter=?")
            args.append(ch)
        if ty:
            where.append("type=?")
            args.append(ty)
        sql = "SELECT chapter,type,name,note,evidence FROM ledger"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY chapter,type,name"
        rows = q(sql, tuple(args))
        chapters = q("SELECT chapter,COUNT(*) n FROM ledger GROUP BY chapter ORDER BY chapter")
        types = q("SELECT type,COUNT(*) n FROM ledger GROUP BY type ORDER BY n DESC")
        return {"rows": rows, "chapters": chapters, "types": types}

    def terms(self, t):
        if t:
            rows = q("SELECT name,n FROM terms WHERE type=? ORDER BY n DESC", (t,))
        else:
            rows = q("SELECT type, COUNT(*) n FROM terms GROUP BY type")
        return {"type": t, "rows": rows}

    def term(self, t, name):
        rows = q("SELECT script,seq,speaker,text FROM lines WHERE text LIKE ? LIMIT 120",
                 ("%" + name + "%",))
        return {"type": t, "name": name, "rows": rows}

    def categories(self):
        groups = [("物品", ["ItemBook_zh-cn", "ItemSpecial_zh-cn", "ItemMisc_zh-cn", "Equipment_zh-cn"]),
                  ("武学", ["BattleSkill_zh-cn"]),
                  ("天赋", ["Talent_zh-cn"]),
                  ("成就与结局", ["Library_zh-cn"]),
                  ("战斗效果", ["CombatEffects_zh-cn"])]
        out = []
        for g, nss in groups:
            n = 0
            for x in nss:
                r = one("SELECT COUNT(*) n FROM entries WHERE ns=?", (x,))
                n += (r or {}).get("n", 0)
            out.append({"group": g, "count": n, "ns": nss})
        return {"groups": out}

    def factions(self):
        rows = q("""SELECT f.name,f.kind,f.desc,COUNT(cf.char_id) n
                      FROM factions f LEFT JOIN char_faction cf ON cf.faction=f.name
                      GROUP BY f.name ORDER BY n DESC""")
        return {"factions": rows}

    def faction(self, name):
        f = one("SELECT * FROM factions WHERE name=?", (name,))
        if not f:
            return {"error": "not found"}
        members = q("""SELECT cf.char_id id, n.name nm, cf.score, cf.method, COUNT(l.id) lines
                       FROM char_faction cf LEFT JOIN names n ON n.id=cf.char_id
                       LEFT JOIN lines l ON l.speaker_id=cf.char_id
                       WHERE cf.faction=? GROUP BY cf.char_id ORDER BY lines DESC""", (name,))
        events = q("""SELECT s.script,s.title,s.place,s.chapter,COUNT(l.id) n
                      FROM char_faction cf JOIN lines l ON l.speaker_id=cf.char_id
                      JOIN scenes s ON s.script=l.script
                      WHERE cf.faction=? GROUP BY s.script ORDER BY n DESC LIMIT 20""", (name,))
        places = q("""SELECT s.place, COUNT(*) n FROM char_faction cf
                      JOIN lines l ON l.speaker_id=cf.char_id
                      JOIN scenes s ON s.script=l.script
                      WHERE cf.faction=? AND s.place<>'' GROUP BY s.place ORDER BY n DESC LIMIT 10""", (name,))
        return {"faction": f, "members": members, "events": events, "places": places}

    def place(self, name):
        info = one("SELECT * FROM scenes WHERE place=? AND line_count>0 LIMIT 1", (name,))
        subs = q("""SELECT place, COUNT(*) n FROM scenes WHERE place LIKE ? AND line_count>0
                   GROUP BY place ORDER BY n DESC""", (name + "-%",))
        chars = q("""SELECT l.speaker nm, l.speaker_id id, COUNT(*) n FROM lines l JOIN scenes s ON s.script=l.script
                     WHERE s.place LIKE ? AND l.speaker<>'旁白' GROUP BY l.speaker ORDER BY n DESC LIMIT 20""", (name + "%",))
        events = q("""SELECT script,title,time_from,time_to,line_count,battles FROM scenes
                     WHERE place LIKE ? AND line_count>0 ORDER BY line_count DESC LIMIT 30""", (name + "%",))
        desc = one("SELECT value FROM kv WHERE ns='Position_zh-cn' AND key=?", ("Name/" + name.split("-")[-1],))
        return {"name": name, "desc": (desc or {}).get("value", ""), "subs": subs,
                "characters": chars, "events": events, "info": info}

    def portrait(self, cid):
        n = one("SELECT name FROM names WHERE id=?", (cid,))
        name = (n or {}).get("name", "")
        pdir = os.path.join(ROOT, "data", "portraits")
        idxp = os.path.join(ROOT, "data", "portrait_index.json")
        if os.path.isdir(pdir) and os.path.exists(idxp):
            try:
                idx = json.load(open(idxp, encoding="utf-8"))
            except Exception:
                idx = {}
            fp = idx.get((cid or "").lower())
            if fp and os.path.exists(os.path.join(pdir, fp)):
                return self._file(os.path.join(pdir, fp))
        try:
            from opencc import OpenCC
            cc = OpenCC("t2s")
        except Exception:
            cc = None

        def norm(s):
            return (cc.convert(s) if cc else s).lower()

        target_name = norm(name)
        target_id = (cid or "").lower()
        base_dirs = [os.path.join(r"E:\Game\steamapps\common\LegendOfMortal\Dagui", d)
                     for d in ("Characters", os.path.join("Output", "Characters"))]
        for root in base_dirs:
            if not os.path.isdir(root):
                continue
            for folder in os.listdir(root):
                fn = norm(folder)
                hit = False
                if target_id and (fn.startswith(target_id) or ("_" + target_id) in fn):
                    hit = True
                if not hit and target_name and target_name in fn:
                    hit = True
                if not hit:
                    continue
                fp = os.path.join(root, folder)
                if not os.path.isdir(fp):
                    continue
                if os.path.exists(os.path.join(fp, "normal.png")):
                    return self._file(os.path.join(fp, "normal.png"))
                pngs = [x for x in os.listdir(fp) if x.endswith(".png")]
                if pngs:
                    return self._file(os.path.join(fp, pngs[0]))
        return self._json({"error": "no portrait"}, 404)

    def entity(self, cid):
        n = one("SELECT name FROM names WHERE id=?", (cid,))
        name = (n or {}).get("name", cid)
        intro = q("SELECT eid,title,body FROM entries WHERE ns='CharacterIntro_zh-cn' AND eid=?", (cid,))
        stat = one("SELECT COUNT(*) n, MIN(script) a, MAX(script) b FROM lines WHERE speaker_id=?", (cid,))
        places = q("""SELECT s.place, COUNT(*) n FROM lines l JOIN scenes s ON s.script=l.script
                      WHERE l.speaker_id=? AND s.place<>'' GROUP BY s.place ORDER BY n DESC LIMIT 8""", (cid,))
        events = q("""SELECT s.script, s.title, s.chapter, s.place, COUNT(*) n
                      FROM lines l JOIN scenes s ON s.script=l.script
                      WHERE l.speaker_id=? GROUP BY s.script ORDER BY n DESC LIMIT 15""", (cid,))
        related = q("""SELECT l2.speaker name, l2.speaker_id id, COUNT(*) n
                        FROM lines l1 JOIN lines l2 ON l1.script=l2.script
                        WHERE l1.speaker_id=? AND l2.speaker<>l1.speaker AND l2.speaker<>'旁白'
                        GROUP BY l2.speaker ORDER BY n DESC LIMIT 12""", (cid,))
        return {"id": cid, "name": name, "intro": intro,
                "lines": (stat or {}).get("n", 0),
                "first": (stat or {}).get("a", ""), "last": (stat or {}).get("b", ""),
                "places": places, "events": events, "related": related,
                "ledger": q("SELECT chapter,type,name,note,evidence FROM ledger WHERE name=? OR note LIKE ? LIMIT 30", (name, "%" + name + "%"))}

    def character(self, cid):
        n = one("SELECT name FROM names WHERE id=?", (cid,))
        rows = q("""SELECT script, seq, key, text, mode FROM lines
                    WHERE speaker_id=? ORDER BY script, seq LIMIT 3000""", (cid,))
        scripts = sorted({r["script"] for r in rows})
        return {"id": cid, "name": (n or {}).get("name", cid), "count": len(rows),
                "lines": rows, "scenes": scripts}

    def characters(self, text):
        if text:
            return {"characters": q(
                "SELECT speaker name, speaker_id id, COUNT(*) n FROM lines "
                "WHERE speaker LIKE ? GROUP BY speaker ORDER BY n DESC LIMIT 200",
                ("%" + text + "%",))}
        return {"characters": q(
            "SELECT speaker name, speaker_id id, COUNT(*) n FROM lines "
            "GROUP BY speaker ORDER BY n DESC")}

    def yehua(self, qs):
        """江湖夜话（MortalTalk）状态与存档摘要。只读，不改动游戏目录。"""
        import glob
        import datetime
        game = (qs.get("game", [""])[0] or "").strip().strip('"')
        if not game:
            try:
                r = one("SELECT value FROM meta WHERE key='game'")
                game = (r or {}).get("value") or ""
            except Exception:
                pass
        out = {"game": game, "installed": False, "version": "", "plugin": "",
               "config": False, "config_path": "", "saves_dir": "", "saves": [],
               "bridge": False, "error": ""}
        if not game or not os.path.isdir(game):
            out["error"] = "no-game-dir"
            return out
        plug = os.path.join(game, "BepInEx", "plugins", "MortalTalk")
        out["plugin"] = plug
        out["installed"] = os.path.exists(os.path.join(plug, "MortalTalk.dll"))
        out["bridge"] = os.path.exists(os.path.join(game, "BepInEx", "plugins", "MortalTalk.WikiBridge.dll"))
        vt = os.path.join(plug, "version.txt")
        if os.path.exists(vt):
            try:
                out["version"] = open(vt, encoding="utf-8-sig").read().strip()
            except Exception:
                pass
        cfg = os.path.join(game, "BepInEx", "config", "yumina.mortal.yehua.cfg")
        out["config"] = os.path.exists(cfg)
        out["config_path"] = cfg
        sdir = os.path.join(game, "BepInEx", "config", "JianghuYehua")
        out["saves_dir"] = sdir
        names = {}
        try:
            names = {r["id"]: r["name"] for r in q("SELECT id, name FROM names")}
        except Exception:
            pass

        def rt(rd):
            if not rd or rd < 1:
                return ""
            y = (rd - 1) // 36 + 1
            m = (rd - 1) % 36 // 3 + 1
            x = (rd - 1) % 3 + 1
            return "第%d年%d月%s" % (y, m, ("", "上旬", "中旬", "下旬")[x])

        # 游戏自己的存档槽位：用落盘时间把插件的随机档号对到 Save_XXX.dat
        slot_root = ""
        try:
            _ll = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Obb Studio", "Mortal")
            _best = ("", 0)
            for _d in glob.glob(os.path.join(_ll, "*")):
                if os.path.isdir(_d):
                    _n = len(glob.glob(os.path.join(_d, "Save_*.dat")))
                    if _n > _best[1]:
                        _best = (_d, _n)
            slot_root = _best[0]
        except Exception:
            slot_root = ""

        def slot_of(tsv):
            if not slot_root:
                return ""
            best = None
            for sp in glob.glob(os.path.join(slot_root, "Save_*.dat")):
                nm = os.path.basename(sp)
                if nm.startswith("Save_universe"):
                    continue
                dt = abs(os.path.getmtime(sp) - tsv)
                if best is None or dt < best[0]:
                    best = (dt, nm)
            if not best or best[0] > 120:
                return ""
            nm = best[1]
            m = re.match(r"Save_(\d{3})\.dat$", nm)
            if m:
                return "存档 " + m.group(1)
            m = re.match(r"Save_auto_battle_?(\d*)\.dat$", nm)
            if m:
                return "战斗自动" + (m.group(1) or "")
            m = re.match(r"Save_auto_free_?(\d*)\.dat$", nm)
            if m:
                return "自由自动" + (m.group(1) or "")
            m = re.match(r"Save_auto_?(\d*)\.dat$", nm)
            if m:
                return "自动" + (m.group(1) or "")
            if nm == "Save_replay.dat":
                return "回放"
            return ""

        for fp in sorted(glob.glob(os.path.join(sdir, "save_*.json"))):
            base = os.path.basename(fp)
            ts = os.path.getmtime(fp)
            try:
                d = json.load(open(fp, encoding="utf-8-sig"))
            except Exception as e:
                out["saves"].append({"file": base, "error": str(e)})
                continue
            ents = d.get("Entries") or []
            ppl = {}
            miles = []
            kinds = {}
            rounds = []
            for e in ents:
                who = e.get("Who") or ""
                k = e.get("Kind") or ""
                kinds[k] = kinds.get(k, 0) + 1
                rd = e.get("Round") or 0
                if rd:
                    rounds.append(rd)
                if not who:
                    continue
                p = ppl.setdefault(who, {"id": who, "name": names.get(who, who),
                                         "n": 0, "last": "", "milestones": 0})
                p["n"] += 1
                if rd and (not p["last"] or rd > 0):
                    p["last"] = rt(rd)
                txt = (e.get("Text") or "").strip()
                if k == "milestone" and txt:
                    p["milestones"] += 1
                    miles.append({"who": p["name"], "when": rt(rd), "text": txt[:140]})
            sid = base[len("save_"):-len(".json")]
            out["saves"].append({
                "file": base,
                "id": sid,
                "slot": slot_of(ts),
                "bytes": os.path.getsize(fp),
                "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M"),
                "entries": len(ents),
                "kinds": kinds,
                "people": sorted(ppl.values(), key=lambda x: -x["n"]),
                "milestones": miles[-40:],
                "from": rt(min(rounds)) if rounds else "",
                "to": rt(max(rounds)) if rounds else "",
                "version": d.get("Version"),
            })
        return out

    def yehua_brief(self, qs):
        """给某个角色一份「他见过的人」清单（纯文本，插件直接读）。"""
        cid = (qs.get("char", [""])[0] or "").strip()
        if not cid:
            return ""
        try:
            import yehua_pack as yp
            fs = yp.first_sentence
        except Exception:
            fs = lambda t: (str(t or "").strip()[:120])
        row = one("SELECT name FROM names WHERE id=?", (cid,))
        name = (row or {}).get("name") or cid
        out = ["#" + name]
        seen = {name}
        generic = set(["少侠", "众人", "弟子", "少女", "妇人", "老丈", "汉子", "掌柜", "小贖",
                       "侍女", "路人", "乞丐", "官兵", "客人", "少年", "孩童", "老头", "大汉",
                       "唐门弟子", "唐门女弟子", "宋兵", "镖师", "贼人",
                       "掌门", "弟子们", "女侠", "女弟子", "师兄", "师弟", "师姐", "师妹",
                       "长老", "帮主", "教主", "掌门人", "主上", "大人", "姑娘", "女子", "男子",
                       "百姓", "村民", "商贩", "大侠", "黑衣人", "蒙面人", "小贩", "侍女们",
                       "先生", "山贼", "僧人", "道人", "官员", "将军"])
        BAD = ("后来", "最终", "结局", "死后", "临死", "传位", "上述", "补的发言", "游戏里名字显示")

        def ok_entry(nm, t):
            if not nm or len(nm) < 2 or nm in seen or nm in generic:
                return False
            t = t or ""
            if len(t) < 8:
                return False
            return not any(w in t for w in BAD)

        self_row = one("SELECT lead FROM pages WHERE slug=? AND lead IS NOT NULL", ("人物/" + name,))
        if self_row and self_row.get("lead"):
            t = fs(self_row["lead"])
            if t:
                out.append("SELF\t" + t)
        try:
            peers = q("SELECT peer, n FROM char_peers WHERE sid=? ORDER BY n DESC LIMIT 30", (cid,))
        except Exception:
            peers = []
        for p in peers:
            pid = p["peer"]
            if not pid or pid == "player":
                continue
            nr = one("SELECT name FROM names WHERE id=?", (pid,))
            pname = (nr or {}).get("name") or pid
            pr = one("SELECT lead FROM pages WHERE slug=? AND lead IS NOT NULL", ("人物/" + pname,))
            if not pr or not pr.get("lead"):
                continue
            t = fs(pr["lead"])
            if not ok_entry(pname, t):
                continue
            out.append(pname + "\t" + t)
            seen.add(pname)
        try:
            famous = q("SELECT name, mentions, selfdef FROM char_fame WHERE mentions>=3 ORDER BY mentions DESC LIMIT 80")
        except Exception:
            famous = []
        added = 0
        for f in famous:
            nm = f["name"]
            t = fs(f["selfdef"])
            if not ok_entry(nm, t):
                continue
            out.append(nm + "\t" + t)
            seen.add(nm)
            added += 1
            if added >= 20:
                break
        return "\n".join(out)

    def yehua_install(self, qs):
        """把 wiki 读取器装进夜话：复制插件、生成数据包。只写这两个位置。"""
        import shutil
        game = (qs.get("game", [""])[0] or "").strip().strip('"')
        if not game:
            try:
                r = one("SELECT value FROM meta WHERE key='game'")
                game = (r or {}).get("value") or ""
            except Exception:
                pass
        out = {"ok": False, "dll": "", "pack": "", "rows": 0, "msg": ""}
        if not game or not os.path.isdir(game):
            out["msg"] = "找不到游戏目录"
            return out
        src = os.path.join(ROOT, "assets", "yehua", "MortalTalk.WikiBridge.dll")
        if not os.path.exists(src):
            out["msg"] = "缺少读取器文件 MortalTalk.WikiBridge.dll"
            return out
        dst = os.path.join(game, "BepInEx", "plugins", "MortalTalk.WikiBridge.dll")
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        except Exception as e:
            out["msg"] = "插件复制失败：" + str(e)
            return out
        out["dll"] = dst
        pack = os.path.join(game, "夜话设定", "wiki", "pack.txt")
        try:
            os.makedirs(os.path.dirname(pack), exist_ok=True)
            import yehua_pack
            yehua_pack.main(pack)
        except Exception as e:
            out["msg"] = "数据包生成失败：" + str(e)
            return out
        rows = 0
        try:
            with open(pack, encoding="utf-8") as f:
                for line in f:
                    if line and not line.startswith("#") and not line.startswith("@"):
                        rows += 1
        except Exception:
            pass
        out["pack"] = pack
        out["rows"] = rows
        out["ok"] = True
        out["msg"] = "已装好，下次进游戏生效"
        return out

    def flags(self, text):
        if text:
            return {"flags": q("SELECT * FROM flags WHERE flag LIKE ? ORDER BY flag LIMIT 500",
                               ("%" + text + "%",))}
        return {"flags": q("SELECT flag, COUNT(*) n FROM flags GROUP BY flag ORDER BY n DESC LIMIT 300")}

    def wiki_list(self, typ, text):
        where, args = [], []
        if typ:
            where.append("type=?")
            args.append(typ)
        if text:
            where.append("name LIKE ?")
            args.append("%" + text + "%")
        sql = "SELECT type,name,mentions,first_chapter FROM entities"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY mentions DESC, name"
        return {"types": q("SELECT type,COUNT(*) n FROM entities GROUP BY type ORDER BY n DESC"),
                "rows": q(sql, tuple(args))}

    def wiki(self, typ, name):
        e = one("SELECT * FROM entities WHERE type=? AND name=?", (typ, name)) if typ else None
        if not e:
            e = one("SELECT * FROM entities WHERE name=? ORDER BY mentions DESC LIMIT 1", (name,))
        if not e:
            return {"error": "not found"}
        name, typ = e["name"], e["type"]
        seen, mentions = set(), []
        for m in q("SELECT chapter,note,evidence FROM ledger WHERE type=? AND name=? ORDER BY rowid",
                   (typ, name)):
            if m["note"] in seen:
                continue
            seen.add(m["note"])
            mentions.append(m)
        rels = q("""SELECT name,note,chapter FROM ledger
                     WHERE type='关系' AND (name LIKE ? OR name LIKE ?)
                     ORDER BY rowid LIMIT 200""", (name + "—%", "%—" + name))
        rel_seen, rel_out = set(), []
        for r in rels:
            if r["name"] in rel_seen:
                continue
            rel_seen.add(r["name"])
            parts = r["name"].split("—")
            other = parts[1] if parts[0] == name and len(parts) > 1 else parts[0]
            rel_out.append({"name": r["name"], "other": other,
                            "note": r["note"], "chapter": r["chapter"]})
        scenes = []
        if typ == "人物":
            nrow = one("SELECT id FROM names WHERE name=? LIMIT 1", (name,))
            if nrow:
                scenes = q("""SELECT s.script,s.title,s.chapter,s.place,COUNT(*) n
                              FROM lines l JOIN scenes s ON s.script=l.script
                              WHERE l.speaker_id=? GROUP BY s.script
                              ORDER BY n DESC LIMIT 20""", (nrow["id"],))
        elif typ == "地点":
            scenes = q("""SELECT script,title,chapter,place,line_count n FROM scenes
                          WHERE place=? OR place LIKE ? ORDER BY line_count DESC LIMIT 20""",
                       (name, name + "-%"))
        if not scenes:
            scenes = q("""SELECT s.script,s.title,s.chapter,s.place,COUNT(*) n
                          FROM lines l JOIN scenes s ON s.script=l.script
                          WHERE l.text LIKE ? GROUP BY s.script
                          ORDER BY n DESC LIMIT 20""", ("%" + name + "%",))
        members = []
        if typ == "势力":
            members = q("""SELECT name,mentions FROM entities
                            WHERE type='人物' AND faction=?
                            ORDER BY mentions DESC LIMIT 40""", (name,))
        char_id = ""
        if typ == "人物":
            nrow = one("SELECT id FROM names WHERE name=? ORDER BY id LIMIT 1", (name,))
            char_id = (nrow or {}).get("id", "")
        return {"entity": e, "mentions": mentions, "relations": rel_out,
                "scenes": scenes, "members": members, "char_id": char_id}

    def page(self, slug):
        slug = slug.strip()
        row = one("select * from pages where slug=?", (slug,))
        if not row:
            r = one("select slug from redirects where alias=?", (slug.split("/")[-1],))
            if r:
                row = one("select * from pages where slug=?", (r["slug"],))
        if not row:
            cand = q("select slug from pages where name=? order by mentions desc limit 1",
                     (slug.split("/")[-1],))
            if cand:
                row = one("select * from pages where slug=?", (cand[0]["slug"],))
        if not row:
            return {"error": "not found", "slug": slug}
        out = dict(row)
        for k in ("sections", "infobox", "cats", "chapters"):
            try:
                out[k] = json.loads(out.get(k) or "[]")
            except Exception:
                out[k] = [] if k != "infobox" else {}
        out["links"] = q("""select l.dst,l.kind,l.label,p.name,p.type
                            from links l left join pages p on p.slug=l.dst
                            where l.src=? order by l.kind,l.label""", (row["slug"],))
        out["backlinks"] = q("""select l.src,l.kind,l.label,p.name,p.type
                               from links l left join pages p on p.slug=l.src
                               where l.dst=? order by l.kind,l.label limit 300""", (row["slug"],))
        if row["type"] == "人物":
            st = one("""select count(*) n from lines l where l.speaker in
                         (select name from names where id in (select id from names where name=?))""",
                     (row["name"],))
            out["line_count"] = (st or {}).get("n", 0)
        return out

    def facets(self, typ, dim="1"):
        if not typ:
            return {"facets": [], "total": 0}
        col = "facet2" if str(dim) == "2" else "facet"
        where = ["type=?", "hidden=0", "%s<>''" % col]
        args = [typ]
        # 与列表口径一致：有上级的地点/势力不进列表，也不能计入筛选档
        if typ in ("地点", "势力"):
            where.append("slug not in (select slug from place_children)")
        rows = q("select %s v, count(*) n from pages where " % col + " and ".join(where) +
                " group by 1 order by 2 desc, 1", tuple(args))
        return {"facets": rows, "total": sum(r["n"] for r in rows)}

    def filter_fields(self, qs):
        """表单式筛选：多个字段各一个值，按 all/any 组合。"""
        def g(k):
            return (qs.get(k, [""])[0] or "").strip()

        conds = []
        params = []
        mapping = [
            ("speaker", "script IN (SELECT script FROM lines WHERE speaker LIKE ?)"),
            ("text", "script IN (SELECT script FROM lines WHERE text LIKE ?)"),
            ("flag", "script IN (SELECT script FROM flags WHERE flag LIKE ?)"),
            ("opt", "script IN (SELECT script FROM choices WHERE options LIKE ?)"),
            ("place", "place LIKE ?"),
            ("chapter", "chapter LIKE ?"),
            ("title", "title LIKE ?"),
            ("arc", "'场景/' || script IN (SELECT slug FROM pages WHERE type='场景' AND coalesce(facet,'') LIKE ?)"),
            ("id", "script LIKE ?"),
        ]
        used = {}
        for key, sql in mapping:
            v = g(key)
            if v:
                conds.append(sql)
                params.append("%" + v + "%")
                used[key] = v
        if not conds:
            return {"error": "至少填一个条件", "rows": [], "count": 0, "used": used}
        joiner = " OR " if g("match").lower() == "any" else " AND "
        where = "(" + joiner.join(conds) + ")" if len(conds) > 1 else conds[0]
        limit = int(qs.get("limit", ["300"])[0] or 300)
        sql = "select script,title,chapter,place,line_count from scenes where " + where
        sql += " order by chapter, script limit ?"
        try:
            rows = q(sql, tuple(params) + (limit,))
        except Exception as e:
            return {"error": "查询失败: %s" % e, "rows": [], "count": 0, "used": used}
        return {"rows": rows, "count": len(rows), "used": used,
                "match": "any" if g("match").lower() == "any" else "all",
                "limited": len(rows) >= limit}

    def stats(self):
        """按章节、按剧情阶段统计场景数与文本量。"""
        by_chapter = q(
            "select chapter, count(*) n, sum(line_count) lines, sum(cjk) cjk "
            "from scenes where line_count>0 group by chapter order by chapter")
        by_arc = q(
            "select coalesce(p.facet,'(未分阶段)') arc, count(*) n, "
            "sum(s.line_count) lines, sum(s.cjk) cjk "
            "from scenes s join pages p on p.slug='场景/'||s.script "
            "group by arc order by cjk desc")
        tot = q("select count(*) n, sum(line_count) lines, sum(cjk) cjk "
                "from scenes where line_count>0")[0]
        try:
            pages_n = q("select count(*) n from pages where hidden=0")[0]["n"]
        except Exception:
            pages_n = 0
        return {"total": tot, "chapters": by_chapter, "arcs": by_arc, "pages": pages_n}

    def filter_scenes(self, expr, limit=300):
        """布尔表达式筛选场景。"""
        if build_where is None:
            return {"error": "筛选模块未加载", "rows": [], "count": 0}
        try:
            where, params = build_where(expr)
        except FilterError as e:
            return {"error": str(e), "rows": [], "count": 0, "fields": FILTER_FIELDS,
                    "expr": expr}
        sql = "select script,title,chapter,place,line_count from scenes"
        if where:
            sql += " where " + where
        sql += " order by chapter, script limit ?"
        try:
            rows = q(sql, tuple(params) + (limit,))
        except Exception as e:
            return {"error": "查询失败: %s" % e, "rows": [], "count": 0, "expr": expr}
        return {"rows": rows, "count": len(rows), "expr": expr,
                "fields": FILTER_FIELDS, "limited": len(rows) >= limit}

    def pages_list(self, typ, text, offset=0, limit=80, facet="", facet2=""):
        where, args = ["hidden=0"], []
        if typ:
            where.append("type=?")
            args.append(typ)
        if facet:
            where.append("facet=?")
            args.append(facet)
        if facet2:
            where.append("facet2=?")
            args.append(facet2)
        if typ in ("地点", "势力"):
            where.append("slug not in (select slug from place_children)")
        if text:
            where.append("(name LIKE ? OR lead LIKE ? OR slug in "
                         "(select slug from aliases where alias LIKE ?))")
            args += ["%" + text + "%", "%" + text + "%", "%" + text + "%"]
        w = (" where " + " and ".join(where)) if where else ""
        total = one("select count(*) n from pages where " + " and ".join(where), tuple(args))["n"]
        rows = q("select slug,type,name,mentions,title,coalesce(facet,'') facet,"
                 "coalesce(facet2,'') facet2,substr(lead,1,80) lead from pages where " +
                 " and ".join(where) +
                 " order by mentions desc, name limit ? offset ?", tuple(args) + (limit, offset))
        return {"total": total, "rows": rows, "offset": offset, "limit": limit}

    def search2(self, text):
        text = text.strip()
        if not text:
            return {"pages": [], "scenes": [], "lines": [], "flags": []}
        pages_ = q("""select slug,type,name,mentions,title from pages
                      where hidden=0 and (name LIKE ? or lead LIKE ?
                         or slug in (select slug from aliases where alias LIKE ?))
                      order by (name=?) desc, mentions desc limit 50""",
                   ("%" + text + "%", "%" + text + "%", "%" + text + "%", text))
        scenes_ = q("""select script,title,chapter,line_count from scenes
                       where title LIKE ? and line_count>0 order by line_count desc limit 20""",
                    ("%" + text + "%",))
        toks = [t for t in text.split() if t]
        phs = [phrase(t) for t in toks]
        fts = " AND ".join([p for p in phs if p]) or None
        lines_ = []
        if fts:
            try:
                lines_ = q("""select l.script,l.seq,l.speaker,l.text from lines_fts
                            join lines l on l.id=lines_fts.rowid
                            where lines_fts match ? order by rank limit 40""", (fts,))
            except Exception:
                lines_ = []
        if len(lines_) < 10:
            like = "%" + "%".join(toks) + "%"
            rows = q("""select script,seq,speaker,text from lines where text like ?
                        limit 40""", (like,))
            seen = {(x["script"], x["seq"]) for x in lines_}
            for r in rows:
                if (r["script"], r["seq"]) not in seen:
                    lines_.append(r)
        flags_ = []
        try:
            flags_ = q("""select d.flag, d.label,
                                (select count(*) from pages p
                                 where p.type='事件' and p.sections LIKE '%'||d.flag||'%') n
                          from flag_dict d
                          where d.flag LIKE ? or d.label LIKE ? or d.label_tw LIKE ?
                          order by n desc, d.flag limit 30""",
                        ("%" + text + "%", "%" + text + "%", "%" + text + "%"))
            if not flags_:
                flags_ = q("""select f.flag, f.label, 0 n from flaginfo f
                              where f.flag LIKE ? or f.label LIKE ? limit 30""",
                            ("%" + text + "%", "%" + text + "%"))
        except Exception:
            flags_ = []
        return {"pages": pages_, "scenes": scenes_, "lines": lines_[:60], "flags": flags_}

    def kv(self, ns):
        if not ns:
            return {"namespaces": q("SELECT ns, COUNT(*) n FROM kv GROUP BY ns ORDER BY ns")}
        ents = q("SELECT eid,title,body FROM entries WHERE ns=? ORDER BY eid", (ns,))
        items = q("SELECT key, value FROM kv WHERE ns=? AND key NOT LIKE '%/%' ORDER BY key", (ns,))
        return {"ns": ns, "entries": ents, "items": items}


def update_check():
    cur = _app_version()
    try:
        import updater
    except Exception:
        return {"ok": False, "current": cur, "reason": "no-updater"}
    info = updater.local_package() or updater.fetch_remote()
    if not info:
        return {"ok": False, "current": cur, "reason": "no-manifest"}
    try:
        return {"ok": True, "current": cur, "version": str(info.get("version")),
                "notes": info.get("notes") or "",
                "newer": updater.newer(str(info.get("version")), cur)}
    except Exception as e:
        return {"ok": False, "current": cur, "reason": str(e)}


def update_apply():
    try:
        import updater
    except Exception:
        return {"ok": False}
    info = updater.local_package() or updater.fetch_remote()
    if not info:
        return {"ok": False}
    threading.Thread(target=lambda: updater.apply_update(info), daemon=True).start()
    return {"ok": True, "version": info.get("version")}


def serve():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    srv.serve_forever()


def main():
    threading.Thread(target=serve, daemon=True).start()
    url = "http://127.0.0.1:%d" % PORT
    print("serving", url)
    webbrowser.open(url)
    try:
        while True:
            threading.Event().wait(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
