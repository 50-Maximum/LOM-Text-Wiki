# -*- coding: utf-8 -*-
"""P3 本地服务：零依赖 HTTP + SQLite 查询接口。"""
import os, sys, json, sqlite3, urllib.parse, mimetypes, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "wiki.db")
WEB = os.path.join(ROOT, "web")
PORT = int(os.environ.get("LOM_PORT", "8765"))


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
                _l["branch_h"] = _bh.get(script + "\x1f" + _b) or ""
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
        _tmap = {}
        try:
            for r in q("select name,title from pages where type='人物' and title<>''"):
                _tmap[r["name"].split("·")[-1]] = r["title"]
        except Exception:
            _tmap = {}
        return {"scene": s, "lines": lines, "choices": chs,
                "branches": brs, "titles": _tmap,
                "participants": q("SELECT speaker nm, COUNT(*) n FROM lines WHERE script=? AND speaker<>'旁白' GROUP BY speaker ORDER BY n DESC LIMIT 12", (script,)),
                "prereq": [r for c in chs for r in (c.get("requires") or []) + (c.get("cond_text") or [])],
                "flags": q("SELECT seq,flag,value,after_key,branch FROM flags WHERE script=? ORDER BY seq", (script,))}
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
        rows = q("select slug,type,name,mentions,title,substr(lead,1,80) lead from pages where " +
                 " and ".join(where) +
                 " order by mentions desc, name limit ? offset ?", tuple(args) + (limit, offset))
        return {"total": total, "rows": rows, "offset": offset, "limit": limit}

    def search2(self, text):
        text = text.strip()
        if not text:
            return {"pages": [], "scenes": [], "lines": []}
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
        return {"pages": pages_, "scenes": scenes_, "lines": lines_[:60]}

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
