# -*- coding: utf-8 -*-
"""用逐场景笔记（notes）重建 wiki 页面，取代旧的按章节块抽取的 ledger。

页面：人物 / 势力 / 地点 / 书物 / 事件 / 场景 / 路线
每条笔记都带场景与逐字引文，可回溯到原文那一句。
"""
import sqlite3, sys, io, json, re, collections, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
DB = os.path.join(BASE, "data", "wiki.db")
if "--db" in sys.argv:
    DB = sys.argv[sys.argv.index("--db") + 1]
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

# 标题统一转简中（游戏资源里部分条目名是繁中）
try:
    from opencc import OpenCC as _OCC
    _CC = _OCC("t2s")
    def _t2s(s):
        return _CC.convert(s) if s else s
except Exception:
    def _t2s(s):
        return s

# 梦境/幻境场景（人工根据叙述框架确认）
DREAM = {}
try:
    _dp = os.path.join(BASE, "data", "dream_scenes.json")
    if os.path.exists(_dp):
        DREAM = json.load(open(_dp, encoding="utf-8"))
except Exception:
    DREAM = {}

# 分支选项（选项 → 结果），需在早期加载：chain_rows 要用它反查选项文案
CB = {}
try:
    _cbp0 = os.path.join(BASE, "data", "choice_branch.json")
    if os.path.exists(_cbp0):
        CB = json.load(open(_cbp0, encoding="utf-8"))
except Exception:
    CB = {}

# 对话菜单（talk[]）：带解锁条件的选项 + 去向
TM = {}
try:
    _tmp = os.path.join(BASE, "data", "talk_menus.json")
    if os.path.exists(_tmp):
        TM = json.load(open(_tmp, encoding="utf-8"))
except Exception:
    TM = {}

# O_xxx 键 → 文案 / 解锁条件 / 去向
# O_xxx 键 → 文案 / 解锁条件 / 去向
OPTXT = {}
try:
    _optp = os.path.join(BASE, "data", "optkey_text.json")
    if os.path.exists(_optp):
        OPTXT = json.load(open(_optp, encoding="utf-8"))
except Exception:
    OPTXT = {}

# Demo 版限定内容（练功塔），页面需要挂提示
DEMO = {}
try:
    _dmp = os.path.join(BASE, "data", "demo_only.json")
    if os.path.exists(_dmp):
        DEMO = json.load(open(_dmp, encoding="utf-8"))
except Exception:
    DEMO = {}
_DEMO_PAGES = set(DEMO.get("pages") or [])
_DEMO_NOTE = DEMO.get("note") or ""

OPTIDX = {}
# 选项键 → 出现在哪个剧本第几句
OPTPOS = {}
try:
    _posp = os.path.join(BASE, "data", "optkey_pos.json")
    if os.path.exists(_posp):
        OPTPOS = json.load(open(_posp, encoding="utf-8"))
except Exception:
    OPTPOS = {}
for _sc, _blks in TM.items():
    for _b in _blks:
        for _o in _b.get("options") or []:
            _k = _o.get("key") or ""
            if not _k:
                continue
            OPTIDX[_k] = {"text": _o.get("text") or "",
                          "cond": _o.get("cond") or "",
                          "next": _o.get("next") or "",
                          "script": _sc}
for _sc, _blks in CB.items():
    for _b in _blks:
        for _o in _b.get("options") or []:
            _k = _o.get("key") or ""
            if _k and _k not in OPTIDX:
                OPTIDX[_k] = {"text": _o.get("text") or "", "cond": "",
                              "next": _o.get("next") or "", "script": _sc}

# ---------- 规范名 ----------
CANON = {
    ("势力", "崆峒"): "崆峒派", ("势力", "青城"): "青城派", ("势力", "点苍"): "点苍派",
    ("势力", "南宫家"): "南宫世家", ("势力", "全真"): "全真派", ("势力", "峨嵋"): "峨嵋派",
    ("势力", "嵩山"): "嵩山派", ("势力", "上官家"): "上官世家", ("势力", "极乐教"): "极乐教",
    ("人物", "小梅"): "虞小梅", ("人物", "云裳"): "叶云裳", ("人物", "小师妹"): "唐默铃",
    ("人物", "小竹"): "郁竹", ("人物", "小兰"): "夏侯兰", ("人物", "小菊"): "魏菊",
    ("人物", "大师兄"): "唐布衣", ("人物", "三师兄"): "唐惟元",
    ("地点", "唐门"): "唐门", ("地点", "江陵府"): "江陵", ("地点", "崆峒山"): "崆峒山",
}

# 人工定稿的导语（有则优先于自动挑选）
INTROS = {}
for _fn in ("intros_char.json", "intros_world.json"):
    _p = os.path.join(BASE, "data", _fn)
    if os.path.exists(_p):
        try:
            INTROS.update(json.load(open(_p, encoding="utf-8")))
        except Exception:
            pass

def intro_of(slug):
    v = INTROS.get(slug)
    if isinstance(v, str):
        return {"text": v, "sources": []}
    return v or None

# 时间线序号：场景 → ord
ORDER = {}
try:
    for sc, od in c.execute("select script,ord from scene_order"):
        ORDER[sc] = od
except Exception:
    pass

# 地点归并/层级/导语
P_FIX = {}
_pf = os.path.join(BASE, "data", "places_fix.json")
if os.path.exists(_pf):
    P_FIX = json.load(open(_pf, encoding="utf-8"))
PMERGE = P_FIX.get("merge", {})
PDELETE = set(P_FIX.get("delete", []))
PPARENT = P_FIX.get("parent", {})
PINTRO = P_FIX.get("intro", {})
DELETE_TO = {"蜀中": "唐门", "蜀地": "唐门", "四川蜀中": "唐门",
             "岳阳": "风雨山", "洞庭": "锦香宫", "洞庭湖": "锦香宫"}

# 人工地点改订（data/place_edits.json）：改名、删项、上级、区域、补注、新地点
try:
    PE = json.load(open(os.path.join(BASE, "data", "place_edits.json"), encoding="utf-8"))
except Exception:
    PE = {}
for _o, _n2 in (PE.get("rename") or {}).items():
    PMERGE[_o] = _n2
for _d2 in (PE.get("delete") or []):
    PDELETE.add(_d2)
for _k2, _v2 in (PE.get("parent") or {}).items():
    PPARENT[_k2] = _v2
for _t3 in (PE.get("top_level") or []):
    PPARENT.pop(_t3, None)
PE_REGION = PE.get("region") or {}
PE_TIP = PE.get("tips") or {}
PE_NEW = PE.get("new_places") or []
PE_HIDE = set(PE.get("hide") or [])
PE_TOP = PE.get("top_level") or []
PE_RENAME = PE.get("region_rename") or {}
PE_TYPE = PE.get("type") or {}

# 编号规律推断（src/infer_by_id.py 生成）
PLACE_INFER2 = {}
try:
    _pi2 = os.path.join(BASE, "data", "place_infer2.json")
    if os.path.exists(_pi2):
        PLACE_INFER2 = json.load(open(_pi2, encoding="utf-8"))
except Exception:
    PLACE_INFER2 = {}
PE_INTRO = PE.get("intro") or {}
PLACE_INFER3 = {}
try:
    _pi3 = os.path.join(BASE, "data", "place_infer3.json")
    if os.path.exists(_pi3):
        PLACE_INFER3 = json.load(open(_pi3, encoding="utf-8"))
except Exception:
    PLACE_INFER3 = {}

PLACE_INFER4 = {}
try:
    _pi4 = os.path.join(BASE, "data", "place_infer4.json")
    if os.path.exists(_pi4):
        PLACE_INFER4 = json.load(open(_pi4, encoding="utf-8"))
except Exception:
    PLACE_INFER4 = {}

PLACE_INFER5 = {}
try:
    _pi5 = os.path.join(BASE, "data", "place_infer5.json")
    if os.path.exists(_pi5):
        PLACE_INFER5 = json.load(open(_pi5, encoding="utf-8"))
except Exception:
    PLACE_INFER5 = {}

PLACE_INFER6 = {}
try:
    _pi6 = os.path.join(BASE, "data", "place_infer6.json")
    if os.path.exists(_pi6):
        PLACE_INFER6 = json.load(open(_pi6, encoding="utf-8"))
except Exception:
    PLACE_INFER6 = {}

PLACE_INFER7 = {}
try:
    _p7 = os.path.join(BASE, "data", "place_infer7.json")
    if os.path.exists(_p7):
        PLACE_INFER7 = json.load(open(_p7, encoding="utf-8"))
except Exception:
    PLACE_INFER7 = {}

PLACE_AUDIT2 = {}
try:
    _pa2 = os.path.join(BASE, "data", "place_audit2.json")
    if os.path.exists(_pa2):
        PLACE_AUDIT2 = json.load(open(_pa2, encoding="utf-8"))
except Exception:
    PLACE_AUDIT2 = {}

PLACE_AUDIT = {}
try:
    _pap = os.path.join(BASE, "data", "place_audit.json")
    if os.path.exists(_pap):
        PLACE_AUDIT = json.load(open(_pap, encoding="utf-8"))
except Exception:
    PLACE_AUDIT = {}

COND_LIB = {}
try:
    _clp = os.path.join(BASE, "data", "cond_lib.json")
    if os.path.exists(_clp):
        COND_LIB = json.load(open(_clp, encoding="utf-8"))
except Exception:
    COND_LIB = {}

COND_USED = {}
try:
    _cup = os.path.join(BASE, "data", "cond_used.json")
    if os.path.exists(_cup):
        COND_USED = json.load(open(_cup, encoding="utf-8"))
except Exception:
    COND_USED = {}

CLUSTERS = []
CLUSTER_BY_ID = {}
CLUSTER_MAP = {}
try:
    _clp2 = os.path.join(BASE, "data", "scene_clusters.json")
    if os.path.exists(_clp2):
        CLUSTERS = json.load(open(_clp2, encoding="utf-8"))
        CLUSTER_BY_ID = {x["id"]: x for x in CLUSTERS}
    _cmp = os.path.join(BASE, "data", "scene_cluster_map.json")
    if os.path.exists(_cmp):
        CLUSTER_MAP = json.load(open(_cmp, encoding="utf-8"))
except Exception:
    CLUSTERS = []

SCENE_BG = {}
try:
    _bgp = os.path.join(BASE, "data", "scene_bg.json")
    if os.path.exists(_bgp):
        SCENE_BG = json.load(open(_bgp, encoding="utf-8"))
except Exception:
    SCENE_BG = {}

# 势力归并/层级/导语
F_FIX = {}
_ff = os.path.join(BASE, "data", "factions_fix.json")
if os.path.exists(_ff):
    F_FIX = json.load(open(_ff, encoding="utf-8"))

# 人物别名归并
C_FIX = {}
_cf = os.path.join(BASE, "data", "chars_fix.json")
if os.path.exists(_cf):
    C_FIX = json.load(open(_cf, encoding="utf-8"))
CMERGE = C_FIX.get("merge", {})
CDELETE = set(C_FIX.get("delete", []))

# 游戏内称号（对话名字上方的身份）
char_title = {}
_ct = os.path.join(BASE, "data", "chars_title.json")
if os.path.exists(_ct):
    try:
        char_title = json.load(open(_ct, encoding="utf-8"))
    except Exception:
        char_title = {}

# 无名群像（不进人物列表，但页面与链接保留）
CHAR_HIDDEN = set()
_ch = os.path.join(BASE, "data", "chars_hidden.json")
if os.path.exists(_ch):
    try:
        CHAR_HIDDEN = set(json.load(open(_ch, encoding="utf-8")))
    except Exception:
        CHAR_HIDDEN = set()

# 事件时间的逻辑推导（人工核定）
EVT = {}
_evp = os.path.join(BASE, "data", "event_time.json")
if os.path.exists(_evp):
    try:
        EVT = json.load(open(_evp, encoding="utf-8"))
    except Exception:
        EVT = {}

# 自动推导的时间（人工条目优先）
_evap = os.path.join(BASE, "data", "event_time_auto.json")
if os.path.exists(_evap):
    try:
        _auto = json.load(open(_evap, encoding="utf-8"))
        for _k, _v in _auto.items():
            EVT.setdefault(_k, _v)
    except Exception:
        pass

# 事件触发条件（攻略原文分句）
ECOND = {}
_ecp = os.path.join(BASE, "data", "event_cond.json")
if os.path.exists(_ecp):
    try:
        ECOND = json.load(open(_ecp, encoding="utf-8"))
    except Exception:
        ECOND = {}

# 场景进入条件边（谁在什么条件下跳进来）
EDGES = {}
_edp = os.path.join(BASE, "data", "entry_edges.json")
if os.path.exists(_edp):
    try:
        EDGES = json.load(open(_edp, encoding="utf-8"))
    except Exception:
        EDGES = {}

# 地图位置事件条件（PositionEventData）
POS = {}
POSEV = []
_pp = os.path.join(BASE, "data", "position_events.json")
_pm = os.path.join(BASE, "data", "position_script_map.json")
if os.path.exists(_pp) and os.path.exists(_pm):
    try:
        _pe = json.load(open(_pp, encoding="utf-8"))
        POSEV = _pe
        _pmap = json.load(open(_pm, encoding="utf-8"))
        _bynm = {d["name"]: d for d in _pe}
        for _nm, _sc in _pmap.items():
            d = _bynm.get(_nm)
            if not d:
                continue
            POS.setdefault(_sc, []).append(d)
    except Exception:
        POS = {}

# 场景判定汇总（编号 → 可读要求）
SCONDS = {}
_scp = os.path.join(BASE, "data", "scene_conds.json")

# 场景衔接（SetNextScript / 条件分支）
NXT = {}
_nxp = os.path.join(BASE, "data", "scene_next.json")
if os.path.exists(_nxp):
    try:
        NXT = json.load(open(_nxp, encoding="utf-8"))
    except Exception:
        NXT = {}
REV = {}
for _s, _d in NXT.items():
    _t = (_d or {}).get("next")
    if _t:
        REV.setdefault(_t, []).append(_s)

# 剧情段（无条件接续合段）
SEGS = []
SEGOF = {}
ROUTEOF = {}
SP = os.path.join(BASE, "data", "story_segments.json")
if os.path.exists(SP):
    try:
        _sg = json.load(open(SP, encoding="utf-8"))
        SEGS = _sg.get("segments") or []
        SEGOF = _sg.get("seg_of") or {}
        ROUTEOF = _sg.get("route_of") or {}
    except Exception:
        SEGS, SEGOF, ROUTEOF = [], {}, {}
SEGMAP = {s["id"]: s for s in SEGS}

# 剧情单元（阶段 → 单元 → 剧情段 → 场景）：data/blocks_map.json
BLOCKS = []
BLOCK_OF = {}
try:
    _bp = os.path.join(BASE, "data", "blocks_map.json")
    if os.path.exists(_bp):
        _bm = json.load(open(_bp, encoding="utf-8"))
        BLOCKS = _bm.get("blocks") or []
        BLOCK_OF = _bm.get("of") or {}
except Exception as _e:
    print("剧情单元跳过:", _e)

# 叙事角色：主线（必然）/ 路线（互斥）/ 支线（可选）/ 日常
STORY_ROLE = {}
BLOCK_ROLE = {}
SCENE_ROLE = {}
SCENE_ROLE_NOTE = {}
try:
    _srp = os.path.join(BASE, "data", "story_role.json")
    if os.path.exists(_srp):
        _sr = json.load(open(_srp, encoding="utf-8"))
        BLOCK_ROLE = _sr.get("block_role") or {}
        SCENE_ROLE = _sr.get("scene_role") or {}
        SCENE_ROLE_NOTE = _sr.get("scene_note") or {}
except Exception as _e:
    print("叙事角色跳过:", _e)


def role_of(script):
    """主线（必然）/ 路线 / 支线 / 日常；场景覆写优先于单元。"""
    _r = SCENE_ROLE.get(script)
    if _r:
        return _r
    _b = BLOCK_OF.get(script) or ""
    _r0 = BLOCK_ROLE.get(_b) or UNIT_ROLE.get(_b)
    if _r0:
        return _r0
    if _b.startswith("其他"):
        return "日常"
    if _b.startswith("支线") or _b.startswith("杂项"):
        return "支线"
    return "其他"

# 攻略年表标注的主/支线（优先级高于脚本推导，用于事件页）
GUIDE_ROUTE = {}
try:
    _gp = os.path.join(BASE, "data", "route_guide.json")
    if os.path.exists(_gp):
        GUIDE_ROUTE = json.load(open(_gp, encoding="utf-8"))
except Exception:
    GUIDE_ROUTE = {}
if os.path.exists(_scp):
    try:
        SCONDS = json.load(open(_scp, encoding="utf-8"))
    except Exception:
        SCONDS = {}

# 场内分支判定（Switch）里出现的攻略旗标只是台词变体，不等于「本场属于该路线」
_VAR_FLAGS = {}
try:
    for _sc, _items in SCONDS.items():
        _set = set()
        for _it in _items or []:
            _info = COND_LIB.get(_it.get("id") or "") or {}
            if (_info.get("kind") or "") != "switch":
                continue
            for _a in (_info.get("attrs") or []):
                for _m in re.findall(r"G\d{5}", str(_a)):
                    _set.add(_m)
        if _set:
            _VAR_FLAGS[_sc] = _set
except Exception:
    _VAR_FLAGS = {}

# 场景开场判定（无进入边时的兜底）
GATES = {}
_gp = os.path.join(BASE, "data", "scene_gates.json")
if os.path.exists(_gp):
    try:
        GATES = json.load(open(_gp, encoding="utf-8"))
    except Exception:
        GATES = {}
FMERGE = F_FIX.get("merge", {})
FPARENT = F_FIX.get("parent", {})
FDELETE = set(F_FIX.get("delete", []))
FINTRO = F_FIX.get("intro", {})

def fcanon(name):
    n = (name or "").strip()
    if not n:
        return ""
    n = FMERGE.get(n, n)
    if n in FDELETE:
        return ""
    return n

# 与势力同名的「人物」页（飞石帮、南宫世家等）：归到势力，不列人物
_FACNAMES = set()
for (_n,) in c.execute("select distinct name from notes where type='势力'"):
    _c = fcanon(_n)
    if _c:
        _FACNAMES.add(_c)

def pcanon(name):
    """地点规范名；删除项返回空串或折叠目标。"""
    n = (name or "").strip()
    if not n:
        return ""
    n = PCANON2.get(n, n)
    n = PMERGE.get(n, n)
    if n.startswith("崆峒山-"):      # 页面实际用「崆峒-X」，别写「崆峒山-X」
        n = "崆峒-" + n[len("崆峒山-"):]
    if n in PDELETE:
        return DELETE_TO.get(n, "")
    return n


# 剧本里存的是短名，页面要用全名
PCANON2 = {
    "崆峒": "崆峒山", "青城": "青城山", "夺魄": "崆峒山-夺魄森林",
    "练功场": "唐门-练功场", "大门": "唐门-大门", "正心堂": "唐门-正心堂",
    "炼丹房": "唐门-炼丹房", "伙房": "唐门-伙房", "锻冶场": "唐门-锻冶场",
    "讲经堂": "唐门-讲经堂", "后山": "唐门-后山", "外堡": "唐门-外堡",
    "男弟子房": "唐门-弟子房", "女弟子房": "唐门-弟子房",
    "义田": "唐门-义田", "茶肆": "唐门-茶肆", "药铺": "唐门-药铺",
    "闹市": "唐门-闹市", "温泉": "唐门-温泉",
}

# 同剧情段内唯一地点的推断结果（build_place_infer.py 生成）
PLACE_INFER = {}
try:
    _pip = os.path.join(BASE, "data", "scene_place_infer.json")
    if os.path.exists(_pip):
        PLACE_INFER = json.load(open(_pip, encoding="utf-8"))
except Exception:
    PLACE_INFER = {}

# 人工核定：逐场看过原文的地点修正（data/place_override.json）
PLACE_OVERRIDE = {}
try:
    _pov = os.path.join(BASE, "data", "place_override.json")
    if os.path.exists(_pov):
        PLACE_OVERRIDE = json.load(open(_pov, encoding="utf-8"))
except Exception:
    PLACE_OVERRIDE = {}


# 脚本编号能直接对应地点的前缀（这类是确定的）
PLACE_PREFIX_KEYS = ("alchemy", "forge", "kitchen", "door", "backmountain", "study",
                     "center", "room1", "room2", "mall", "downtown", "secret",
                     "section_01_01", "section_01_02", "section_01_03", "section_01_04",
                     "section_01_05", "section_01_06", "section_02_01", "section_02_02",
                     "section_02_03")


# 前后剧情走位推导（build_place_logic.py 生成）
PLACE_LOGIC = {}
try:
    _plp = os.path.join(BASE, "data", "place_logic.json")
    if os.path.exists(_plp):
        PLACE_LOGIC = json.load(open(_plp, encoding="utf-8"))
except Exception:
    PLACE_LOGIC = {}


# 人工逐场指定的地点（data/place_manual.json）
PLACE_MANUAL = {}
PLACE_NOTE = {}
try:
    _pmp = os.path.join(BASE, "data", "place_manual.json")
    if os.path.exists(_pmp):
        PLACE_MANUAL = json.load(open(_pmp, encoding="utf-8"))
    _pfp = os.path.join(BASE, "data", "place_fix_stage.json")
    if os.path.exists(_pfp):
        for _kf, _vf in json.load(open(_pfp, encoding="utf-8")).items():
            PLACE_MANUAL[_kf] = {"place": _vf, "src": "人工指定"}
        for _k9, _v9 in PLACE_MANUAL.items():
            if _v9.get("note"):
                PLACE_NOTE[_k9] = _v9["note"]
except Exception:
    PLACE_MANUAL = {}

# 场景标题覆盖（data/title_override.json）
TITLE_OVR = {}
try:
    _top9 = os.path.join(BASE, "data", "title_override.json")
    if os.path.exists(_top9):
        TITLE_OVR = json.load(open(_top9, encoding="utf-8"))
    _tfp = os.path.join(BASE, "data", "title_fix2.json")
    if os.path.exists(_tfp):
        TITLE_OVR.update(json.load(open(_tfp, encoding="utf-8")))
except Exception:
    TITLE_OVR = {}

# 人工核定的前置触发（data/event_pre.json）
EVENT_PRE = {}
try:
    _epp = os.path.join(BASE, "data", "event_pre.json")
    if os.path.exists(_epp):
        EVENT_PRE = json.load(open(_epp, encoding="utf-8"))
except Exception:
    EVENT_PRE = {}

# 已封锁/不可达内容（data/locked.json）
LOCKED = {}
try:
    _lkp = os.path.join(BASE, "data", "locked.json")
    if os.path.exists(_lkp):
        LOCKED = json.load(open(_lkp, encoding="utf-8"))
except Exception:
    LOCKED = {}

# 人工读完后写的单元概要与阶段（data/unit_notes.json）
UNIT_NOTES = {}
try:
    _unp = os.path.join(BASE, "data", "unit_notes.json")
    if os.path.exists(_unp):
        UNIT_NOTES = json.load(open(_unp, encoding="utf-8"))
except Exception:
    UNIT_NOTES = {}

# 内容单元的叙事角色（data/unit_plan.json 里的 role）
UNIT_ROLE = {}
try:
    _upp = os.path.join(BASE, "data", "unit_plan.json")
    if os.path.exists(_upp):
        for _u in (json.load(open(_upp, encoding="utf-8")).get("units") or []):
            UNIT_ROLE[_u.get("name") or ""] = _u.get("role") or ""
except Exception:
    UNIT_ROLE = {}


def place_of(script):
    _mn = PLACE_MANUAL.get(script)
    if _mn is not None:
        if _mn.get("note"):
            return "", ""
        _pv9 = pcanon(_mn.get("place") or "")
        return _pv9, ("人工指定" if _pv9 else "")
    _ov = PLACE_OVERRIDE.get(script)
    if _ov is not None:
        _pls = _ov.get("places")
        if _pls:
            _pv = "／".join(pcanon(x) for x in _pls if pcanon(x))
            return _pv, ("人工核定" if _pv else "证据不足")
        _pv = pcanon(_ov.get("place") or "")
        return _pv, ("人工核定" if _pv else "证据不足")
    """返回 (地点, 依据)。依据：脚本编号 / 场景标题 / 正文线索 / 承前场 / 途中 / 文中提及。"""
    p = pcanon((scenes.get(script) or {}).get("place") or "")
    if p:
        _low = script.lower()
        if any(_low.startswith(k) for k in PLACE_PREFIX_KEYS):
            return p, "脚本编号"
    inf = PLACE_INFER.get(script) or {}
    if inf.get("place"):
        return pcanon(inf["place"]), "场景标题"
    lg = PLACE_LOGIC.get(script) or {}
    if lg.get("place"):
        src = lg.get("src") or "正文线索"
        if src == "承前场":
            return pcanon(lg["place"]), "承前场（推断）"
        if src == "动身无目的地":
            return "途中（未明说地点）", "动身无目的地"
        return pcanon(lg["place"]), src
    _i6 = PLACE_INFER6.get(script) or {}
    if _i6.get("place"):
        return pcanon(_i6["place"]), "正文地名（推断）"
    _i5 = PLACE_INFER5.get(script) or {}
    if _i5.get("place"):
        return pcanon(_i5["place"]), "背景资源（推断）"
    _i4 = PLACE_INFER4.get(script) or {}
    if _i4.get("place"):
        return pcanon(_i4["place"]), (_i4.get("src") or "事件链顺延（推断）")
    _i3 = PLACE_INFER3.get(script) or {}
    if _i3.get("place"):
        return pcanon(_i3["place"]), (_i3.get("src") or "承前场（推断）")
    _i2 = PLACE_INFER2.get(script) or {}
    if _i2.get("place"):
        return pcanon(_i2["place"]), "编号规律（推断）"
    _i7 = PLACE_INFER7.get(script) or {}
    if _i7.get("place"):
        return pcanon(_i7["place"]), (_i7.get("src") or "承前场（推断）")
    if p:
        _au = PLACE_AUDIT.get(script) or {}
        _v = _au.get("verdict")
        if _v == "here":
            return p, "正文在场"
        if _v == "away":
            return "", "证据不足（原文说的是他处）"
        if _v == "doubt":
            return p, "文中提及（存疑）"
        _a2 = PLACE_AUDIT2.get(script) or {}
        if _a2.get("label"):
            _lb = _a2["label"].replace("驻地（未细分）", "驻地（场所未指明）")
            return (_a2.get("place") or p), _lb
        return p, "文中提及"
    return "", ""

BATTLE_LV = {}
try:
    _blv = os.path.join(BASE, "data", "battle_level_map.json")
    if os.path.exists(_blv):
        BATTLE_LV = json.load(open(_blv, encoding="utf-8"))
except Exception:
    BATTLE_LV = {}

BATTLE_RESULTS = {}
try:
    _brp = os.path.join(BASE, "data", "battle_results.json")
    if os.path.exists(_brp):
        BATTLE_RESULTS = json.load(open(_brp, encoding="utf-8"))
except Exception:
    BATTLE_RESULTS = {}


def battle_label(sw, res, script=""):
    """胜负只按剧本结构判定（重打/GameOver=败，推进剧情=胜），查不到就不给标签。"""
    if not sw or not script:
        return ""
    mp = (BATTLE_RESULTS.get(script) or {}).get(sw) or {}
    lb = mp.get(str(res)) or ""
    if lb == "胜":
        return "战斗胜利"
    if lb == "败":
        return "战斗失败"
    return ""


def pretty_cond(t):
    """把「条件 X｜需=1 > 条件 Y｜需<10」展开成一句能读的话。"""
    if not t:
        return t
    def _rep(m):
        cid = m.group(1)
        info = COND_LIB.get(cid) or {}
        attrs = [a for a in (info.get("attrs") or []) if a]
        if attrs:
            shown = "／".join(attrs[:5])
            if len(attrs) > 5:
                shown += " 等 %d 条" % len(attrs)
            return "判定 %s（%s）" % (cid, shown)
        return "判定 %s" % cid
    t = re.sub(r"条件\s+([A-Za-z][A-Za-z0-9_]{2,})\s*｜[^>]*", _rep, t)
    t = t.replace(" > ", " 且 ")
    return t.strip()


CH_ORDER = {"序章": 0, "第0章": 1, "第1章": 2}


def chap_key(ch):
    ch = (ch or "").strip()
    if ch in CH_ORDER:
        return (CH_ORDER[ch], 0)
    m = re.match(r"第(\d+)章", ch)
    if m:
        return (10 + int(m.group(1)), 0)
    if ch.startswith("支线"):
        return (100, 0)
    if ch == "角色线":
        return (200, 0)
    if ch.startswith("其他"):
        return (300, 0)
    return (400, 0)

scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3], "place": r[4]}
          for r in c.execute("select script,title,chapter,line_count,place from scenes")}
for _k8, _v8 in TITLE_OVR.items():
    if _k8 in scenes:
        scenes[_k8]["title"] = _v8

# 地点 → 场景（按 place_of 反查，供地点页「发生场景」栏）
SCENES_BY_PLACE = {}
for _s7 in list(scenes):
    try:
        _p7, _e7 = place_of(_s7)
    except Exception:
        continue
    if _p7:
        SCENES_BY_PLACE.setdefault(_p7, []).append(_s7)
print("地点-场景索引", len(SCENES_BY_PLACE), "个地点 /",
      sum(len(v) for v in SCENES_BY_PLACE.values()), "场")
try:
    json.dump(SCENES_BY_PLACE, open(os.path.join(BASE, "data", "scenes_by_place.json"), "w",
                                    encoding="utf-8"), ensure_ascii=False)
except Exception as _e:
    print("地点场景索引导出失败", _e)

# ---------- 剧情阶段（七段）----------
ARC = {}
try:
    _arc = json.load(open(os.path.join(BASE, "data", "arcs.json"), encoding="utf-8"))
    ARC = _arc
except Exception:
    ARC = {}
ARC_ORDER = ARC.get("arcs") or []
ARC_CH = ARC.get("chapter_map") or {}
ARC_KW = [(re.compile(k), v) for k, v in (ARC.get("keywords") or [])]
ARC_SC = ARC.get("scene") or {}
try:
    _asf = os.path.join(BASE, "data", "arc_scene_fix.json")
    if os.path.exists(_asf):
        for _kf, _vf in json.load(open(_asf, encoding="utf-8")).items():
            if _kf not in ARC_SC:
                ARC_SC[_kf] = _vf
except Exception as _e:
    print("阶段补充跳过:", _e)

# 攻略给的游戏时间（脚本 → 年/月/旬/事件）
STIME = {}
try:
    for _sc, _y, _mo, _x, _ev, _sec in c.execute(
            "select script,year,month,xun,event,sec from scene_time"):
        STIME[_sc] = (_y, _mo, _x, _ev, _sec)
except Exception:
    STIME = {}

# 攻略年表推算出的时间（参考 wiki，已转简中）
REFTIME = {}
try:
    _rt = os.path.join(BASE, "data", "scene_time_ref.json")
    if os.path.exists(_rt):
        _CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
               "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}
        for _sc, _v in json.load(open(_rt, encoding="utf-8")).items():
            _y = _v.get("year") or ""
            _m = _v.get("month") or ""
            _yy = 0
            _mm = 0
            _ym = re.search(r"第([\u4e00-\u9fa5]+)年", _y)
            if _ym:
                _yy = _CN.get(_ym.group(1), 0)
            _mm2 = re.search(r"([\u4e00-\u9fa5]+)月", _m)
            if _mm2:
                _mm = _CN.get(_mm2.group(1), 0)
            if _yy and _mm:
                REFTIME[_sc] = (_yy, _mm, _v.get("xun") or "")
except Exception:
    REFTIME = {}

# 年表多条选项逐字命中时，以年表时间为准（覆盖攻略索引推导的 scene_time）
try:
    _ov = os.path.join(BASE, "data", "time_override.json")
    if os.path.exists(_ov):
        for _sc in json.load(open(_ov, encoding="utf-8")):
            if _sc in REFTIME:
                STIME.pop(_sc, None)
except Exception:
    pass

def arc_of_date(y, mo):
    if not y or not mo:
        return ""
    if (y, mo) <= (1, 11):
        return "外姓弟子"
    if (y, mo) <= (2, 8):
        return "南宫寿宴"
    if (y, mo) <= (2, 10):
        return "江陵围城"
    if (y, mo) <= (3, 4):
        return "唐门衰败"
    if (y, mo) <= (3, 7):
        return "比武招亲"
    if (y, mo) <= (3, 11):
        return "武林大会"
    return "武林盟进攻唐门"

def time_label(script):
    st = STIME.get(script)
    if not st or not st[0]:
        rf = REFTIME.get(script)
        if rf:
            return "%d年%d月%s旬（据攻略年表）" % (rf[0], rf[1], rf[2] or "")
        return ""
    return f"{st[0]}年{st[1]}月{st[2] or ''}"

# ---------- 阶段特征：只取「高度集中」的地点与人物（占比≥60%） ----------
ARC_PLACE = {}
ARC_PERSON = {}
try:
    _pc = collections.defaultdict(collections.Counter)
    _uc = collections.defaultdict(collections.Counter)
    for _sc0, _info0 in scenes.items():
        _ch0 = _info0.get("chapter") or ""
        if _ch0 in ("支线", "其他", "角色线"):
            continue
        _a0 = ARC_CH.get(_ch0)
        if not _a0:
            continue
        _pl0 = _info0.get("place") or ""
        if _pl0:
            _pc[_pl0][_a0] += 1
    for _sc0, _sp0, _n0 in c.execute(
            "select script,speaker,count(*) from lines where speaker<>'' group by script,speaker"):
        _ch0 = (scenes.get(_sc0) or {}).get("chapter") or ""
        if _ch0 in ("支线", "其他", "角色线"):
            continue
        _a0 = ARC_CH.get(_ch0)
        if not _a0:
            continue
        _uc[_sp0][_a0] += _n0

    for _pl0, _cc in _pc.items():
        _tot = sum(_cc.values())
        _top, _n = _cc.most_common(1)[0]
        if _tot >= 3 and _n / _tot >= 0.6:
            ARC_PLACE.setdefault(_top, set()).add(_pl0)
    for _sp0, _cc in _uc.items():
        _tot = sum(_cc.values())
        _top, _n = _cc.most_common(1)[0]
        if _tot >= 4 and _n / _tot >= 0.6:
            ARC_PERSON.setdefault(_top, set()).add(_sp0)
    print("阶段指纹（集中度≥60%%）：地点 %d 条，人物 %d 条"
          % (sum(len(v) for v in ARC_PLACE.values()), sum(len(v) for v in ARC_PERSON.values())))
except Exception as _e:
    print("阶段指纹跳过:", _e)


def arc_vote(script):
    """投票已停用：阶段改由人工表、章节、旗标条件与原文判定。"""
    return ""


def arc_of(script):
    # 1) 人工指定
    if script in ARC_SC:
        return ARC_SC[script]
    _ch0 = (scenes.get(script) or {}).get("chapter") or ""
    # 2) 正章：章节即归属
    if _ch0 in ARC_CH and ARC_CH[_ch0] and _ch0 not in ("支线", "其他", "角色线"):
        return ARC_CH[_ch0]
    # 3) 支线/其他：先投票（地点/人物/情节）
    _v = arc_vote(script)
    if _v:
        return _v
    # 4) 攻略日期
    st = STIME.get(script)
    if st and st[0] and st[1]:
        a = arc_of_date(st[0], st[1])
        if a:
            return a
    rf = REFTIME.get(script)
    if rf:
        a = arc_of_date(rf[0], rf[1])
        if a:
            return a
    return "不限时间"


for _s, _v in scenes.items():
    _v["arc"] = arc_of(_s)

# 场景 → 路线旗标（进入条件里带 G11/M20008 等）
try:
    sf = json.load(open(os.path.join(BASE, "data", "scene_flags.json"), encoding="utf-8"))
except Exception:
    sf = {}
ROUTE_LABEL = {"G11000": "小师妹线", "G11001": "上官萤线", "G11002": "叶云裳线",
               "G11003": "龙湘线", "G11004": "小梅线", "G11005": "小兰线",
               "G11006": "小竹线", "G11007": "小菊线",
               "M20008": "留学线", "M20028": "离家出走线", "M40036": "卧云岗线",
               "M60016": "武林大会线", "M70052": "顽抗线"}
def routes_of(script):
    info = sf.get(script) or {}
    _skip = _VAR_FLAGS.get(script) or set()
    out = []
    for rq in info.get("requires", []) or []:
        _fl = str((rq or {}).get("flag") or "") if isinstance(rq, dict) else str(rq)
        if _fl and _fl in _skip:
            continue
        for k, lab in ROUTE_LABEL.items():
            if k in str(rq) and lab not in out:
                out.append(lab)
    return out

notes = c.execute("""select script,seq_from,seq_to,type,name,note,quote from notes
                     order by script,seq_from""").fetchall()
print("笔记", len(notes))

# 人工笔记覆盖（data/notes_patch.json）
NOTE_PATCH = {}
try:
    _npp = os.path.join(BASE, "data", "notes_patch.json")
    if os.path.exists(_npp):
        NOTE_PATCH = json.load(open(_npp, encoding="utf-8"))
except Exception as _e:
    print("笔记补丁跳过:", _e)
if NOTE_PATCH:
    _n2 = []
    for _row in notes:
        _sc, _a, _b, _t, _nm, _no, _q = _row
        _pv = (NOTE_PATCH.get(_sc) or {}).get(_nm)
        if _pv:
            if _pv.get("drop"):
                continue
            _no = _pv.get("note", _no)
            if _pv.get("name"):
                _nm = _pv["name"]
        _n2.append((_sc, _a, _b, _t, _nm, _no, _q))
    notes = _n2
    print("笔记补丁后", len(notes))


# ---------- 聚合 ----------
byname = collections.defaultdict(list)
for s, a, b, t, n, note, q in notes:
    if not n:
        continue
    t2 = t if t in ("人物", "势力", "地点", "书物", "事件", "关系") else "人物"
    n2 = CANON.get((t2, n), n)
    if t2 == "地点":
        n2 = pcanon(n2)
        if not n2:
            continue
    if t2 == "人物":
        n2 = CMERGE.get(n2, n2)
        if n2 in CDELETE or n2 in _FACNAMES:
            continue
    if t2 == "势力":
        n2 = fcanon(n2)
        if not n2:
            continue
    byname[(t2, n2)].append({"script": s, "a": a, "b": b, "note": note, "quote": q})

# 势力清单（判定归属链接是否存在）
# 额外势力（正文明确出现、但笔记未立条的势力）
EXTRA_FAC = {}
try:
    _ef = os.path.join(BASE, "data", "extra_factions.json")
    if os.path.exists(_ef):
        EXTRA_FAC = json.load(open(_ef, encoding="utf-8"))
except Exception as _e:
    print("额外势力跳过:", _e)

EXTRA_PE = {}
try:
    _ep2 = os.path.join(BASE, "data", "extra_persons.json")
    if os.path.exists(_ep2):
        EXTRA_PE = json.load(open(_ep2, encoding="utf-8"))
except Exception as _e:
    print("额外人物跳过:", _e)

facset = {n for (t, n) in byname if t == "势力"}
facset |= set(EXTRA_FAC)
placeset = {n for (t, n) in byname if t == "地点"}
charset = {n for (t, n) in byname if t == "人物"}

# 人物归属（char_faction 表：char_id → names.id）
faction_of = {}
try:
    for nm, fc in c.execute("""select n.name, cf.faction
            from char_faction cf join names n on n.id=cf.char_id
            where cf.faction<>'' order by cf.score desc"""):
        faction_of.setdefault(nm, fc)
except Exception as e:
    print("归属表跳过:", e)

# ---------- 人物名前缀（表明门派/身份） ----------
PREFIX_FIX = {}
_pf = os.path.join(BASE, "data", "chars_prefix.json")
if os.path.exists(_pf):
    try:
        PREFIX_FIX = json.load(open(_pf, encoding="utf-8"))
    except Exception:
        PREFIX_FIX = {}

# 参考 wiki（已转简中）的人物资料：性别/生日/年龄
REFC = {}
_rc = os.path.join(BASE, "data", "ref_wiki", "characters.json")
if os.path.exists(_rc):
    try:
        for _c in json.load(open(_rc, encoding="utf-8")):
            _nm = _c.get("name") or _c.get("title") or ""
            if _nm:
                REFC.setdefault(_nm, _c)
    except Exception:
        REFC = {}

SECT_SHORT = {
    "唐门": "唐门", "泥教": "泥教", "崆峒派": "崆峒派", "南宫世家": "南宫世家",
    "铁拳门": "铁拳门", "锦香宫": "锦香宫", "千灯楼": "千灯楼", "青城派": "青城派",
    "雪山派": "雪山派", "丐帮": "丐帮", "点苍派": "点苍派", "夺魄门": "夺魄门",
    "朝廷": "朝廷", "峨嵋派": "峨嵋派", "宋军": "朝廷", "叶家": "叶家",
    "上官世家": "上官世家", "飞石帮": "飞石帮", "飞天门": "飞天门",
    "金国": "金国", "火炎山剑阁": "火炎山剑阁", "嵩山派": "嵩山派",
    "嵩山寺": "嵩山寺", "大理段氏": "大理段氏", "大理内戒营": "大理内戒营",
    "吕氏商会": "吕氏商会", "华山派": "华山派", "全真派": "全真派",
    "饿鬼道": "饿鬼道", "地狱道": "地狱道", "天道": "天道", "沧帮": "沧帮",
    "巫灵教": "巫灵教", "岭南派": "岭南派", "孤云山派": "孤云山派",
    "极乐教": "极乐教", "玄功门": "玄功门", "飞天教": "飞天门",
    "宋军": "朝廷", "官方": "朝廷",
}

# 名字自带门禁前缀的泛称（唐门弟子、青城长老……）
_SIGNS = [("唐家", "唐门"), ("唐门", "唐门"), ("南宫家", "南宫世家"),
          ("上官家", "上官世家"), ("青城", "青城派"), ("峨嵋", "峨嵋派"),
          ("崆峒", "崆峒派"), ("点苍", "点苍派"), ("全真", "全真派"),
          ("嵩山", "嵩山派"), ("锦香", "锦香宫"), ("夺魄", "夺魄门"),
          ("铁拳", "铁拳门"), ("玄功", "玄功门"), ("飞天", "飞天门"),
          ("泥教", "泥教"), ("极乐", "极乐教"), ("雪山", "雪山派"),
          ("华山", "华山派"), ("丐帮", "丐帮"), ("沧帮", "沧帮"),
          ("飞石", "飞石帮"), ("千灯", "千灯楼"), ("吕氏", "吕氏商会")]
_ROLEWORDS = {"弟子", "女弟子", "男弟子", "长老", "掌门", "帮主", "门主",
              "家丁", "妇人", "护法", "舵主", "护卫", "老人", "老太爷",
              "家主", "汉子", "侍女", "婶女", "管家", "家将", "门人"}

HIST_PEOPLE = {"岳飞", "秦桧", "赵扩", "完颜珣", "术虎高琪", "仆散安贞",
               "成吉思汗", "松赞干布", "文成公主", "赤尊公主", "赤松德赞",
               "寂护", "莲花生大士", "释迦牟尼佛", "丘处机", "尹志平",
               "马钰", "郝大通", "重阳真人", "纯阳真人", "李清照", "陈操",
               "苏辙", "范文正公", "陆机", "左思", "岳珂", "苏颂",
               "朱亥", "侯嬴", "诸葛丞相", "鲁班", "欧冶子", "太宗皇帝",
               "赵法王", "天道法王", "道法将军", "刘过", "觉慧方丈"}
_OFFICIAL = {"知县", "通判", "县太爷", "官兵", "捕快", "宋大人", "赵制置使",
             "赵老将军", "县主", "枣阳孟县主", "孟县主", "上官大人"}

# 姓氏 / 名号自带的门禁
SURNAME_SECT = [("南宫", "南宫世家"), ("上官", "上官世家"), ("唐", "唐门"),
                ("段", "大理段氏"), ("申屠", "崆峒"), ("铁拳", "铁拳门"),
                ("夺魄", "夺魄门"), ("极乐", "极乐教"), ("崆峒", "崆峒"),
                ("魏", "玄功门")]

TOWN_FOLK = {"店小二", "掌柜", "妇人", "少女", "少年", "男童", "乞丐", "老乞丐",
             "山贼", "海盗", "官兵", "铁匠", "说书先生", "武师", "刁民",
             "捕快", "先生", "大妈", "何大妈", "朱碘", "孙碘", "孙娘子",
             "费娘子", "乐娘子", "乐屏娘子", "铜人", "鬼卒", "牛头", "马面",
             "鹦鹉", "狗鸡", "狂犬", "女鬼", "女飞贼", "迷魂大盗",
             "胸口碎大石", "帮主夫人", "管帐先生", "四爷", "赵某", "不知名",
             "少侠", "公子侠", "女侠", "路人侠", "阿金", "阿牛", "秀秀",
             "雉儿", "小卉", "老陈", "老孟", "柳叔", "督老兄", "何兄",
             "冯兄", "白兄", "杜兄", "全师兄弟"}


# 前缀与既有势力页对齐（避免筛选里出现没有势力条的归属）
FAC_NORM = {
    "岭南剑派": "岭南派",
    "大理段氏": "大理",
    "饿鬼道": "泥教",
    "吕氏商会": "市井",
    "崆峒": "崆峒派",
    "嵩山寺": "嵩山派",
    "孤云山": "孤云山派",
    "巫灵教": "苗疆巫灵教",
    "教化司": "执明司",
}


# 分支选项（data/branch_options.json）
BRANCH_OPT = {}
try:
    _bop = os.path.join(BASE, "data", "branch_options.json")
    if os.path.exists(_bop):
        BRANCH_OPT = json.load(open(_bop, encoding="utf-8"))
except Exception as _e:
    print("分支选项跳过:", _e)


# 人工分段（data/char_sections.json）
CHAR_SECTIONS = {}
try:
    _csp = os.path.join(BASE, "data", "char_sections.json")
    if os.path.exists(_csp):
        CHAR_SECTIONS = json.load(open(_csp, encoding="utf-8"))
except Exception as _e:
    print("人工分段跳过:", _e)


# 参数中文名（data/stat_names.json）
STAT_NAMES = {}
try:
    _snp = os.path.join(BASE, "data", "stat_names.json")
    if os.path.exists(_snp):
        STAT_NAMES = json.load(open(_snp, encoding="utf-8"))
except Exception:
    STAT_NAMES = {}


def stat_cn(txt):
    if not txt:
        return txt
    out = txt
    for k, v in STAT_NAMES.items():
        out = out.replace(k, v)
    return out


def char_prefix(nm):
    """返回（前缀，显示名）；无前缀时前缀为空。"""
    if "·" in nm:
        _p0, _d0 = nm.split("·", 1)
        return FAC_NORM.get(_p0, _p0), _d0
    if nm in PREFIX_FIX:
        pf = PREFIX_FIX[nm]
        pf = FAC_NORM.get(pf, pf) if pf else pf
        return (pf, nm) if pf else ("", nm)
    # 1) 名字自带的泛称：唐门弟子 → 唐门·弟子
    for sign, pre in _SIGNS:
        if nm.startswith(sign) and len(nm) > len(sign):
            rest = nm[len(sign):]
            if rest in _ROLEWORDS:
                return FAC_NORM.get(pre, pre), rest
            break
    # 2) 已审定的门派归属
    fc = faction_of.get(nm)
    if fc:
        fc = FAC_NORM.get(fc, fc)
        return SECT_SHORT.get(fc, fc), nm
    if nm in HIST_PEOPLE:
        return "史实", nm
    if nm in _OFFICIAL:
        return "朝廷", nm
    # 3) 姓氏自带门禁
    for sign, pre in SURNAME_SECT:
        if nm.startswith(sign) and len(nm) >= 2:
            return FAC_NORM.get(pre, pre), nm
    # 4) 市井 vs 江湖
    if nm in TOWN_FOLK:
        return "市井", nm
    return "江湖", nm

c.executescript("""
DROP TABLE IF EXISTS pages;
DROP TABLE IF EXISTS links;
DROP TABLE IF EXISTS redirects;
CREATE TABLE pages(slug TEXT PRIMARY KEY, type TEXT, name TEXT, lead TEXT,
                   infobox TEXT, sections TEXT, cats TEXT, mentions INT,
                   chapters TEXT, sort_key TEXT, title TEXT, hidden INT, facet TEXT,
                   facet2 TEXT);
CREATE TABLE links(src TEXT, dst TEXT, kind TEXT, label TEXT);
CREATE TABLE redirects(alias TEXT PRIMARY KEY, slug TEXT);
DROP TABLE IF EXISTS aliases;
CREATE TABLE aliases(alias TEXT PRIMARY KEY, slug TEXT);
CREATE INDEX idx_aliases_slug ON aliases(slug);
DROP TABLE IF EXISTS place_children;
CREATE TABLE place_children(slug TEXT PRIMARY KEY);
CREATE INDEX idx_pages_type ON pages(type);
CREATE INDEX idx_links_dst ON links(dst);
CREATE INDEX idx_links_src ON links(src);
""")

pages, links, redirects = [], [], []

def pick_lead(items):
    """挑一句最像身份说明的笔记；没有就用第一条。"""
    if not items:
        return ""
    pat = ("是", "乃", "身为", "自称", "人称", "身份", "出身", "弟子", "掌门", "帮主",
           "长老", "少主", "公子", "姑娘", "为")
    best, score = items[0]["note"], -1
    for it in items:
        sc = sum(1 for p in pat if p in it["note"])
        if sc > score:
            best, score = it["note"], sc
    return best

def sections_for(items, type_name):
    """按剧情阶段分组，每组列笔记 + 引文 + 场景。"""
    groups = collections.OrderedDict()
    for it in sorted(items, key=lambda x: (ORDER.get(x["script"], 99999), x["a"])):
        ch = scenes.get(it["script"], {}).get("arc") or "不限时间"
        groups.setdefault(ch, []).append(it)
    secs = []
    for ch, arr in groups.items():
        rows = []
        for it in arr[:40]:
            sc = scenes.get(it["script"], {})
            rows.append({"note": it["note"], "quote": it["quote"],
                         "script": it["script"], "title": sc.get("title") or it["script"],
                         "seq": it["a"], "routes": routes_of(it["script"])})
        secs.append({"h": ch, "rows": rows})
    return secs

def chapters_of(items):
    chs = []
    for it in items:
        ch = scenes.get(it["script"], {}).get("arc")
        if ch and ch not in chs:
            chs.append(ch)
    return sorted(chs, key=lambda x: ARC_ORDER.index(x) if x in ARC_ORDER else 99)

def noz(s):
    """事件/剧情段标题去掉默认主语「赵活」，并补回删词后的动宾断尾。"""
    if not s:
        return s
    t = s
    for _a, _b in (("救赵活", "相救"), ("护赵活", "相护"), ("斥赵活", "斥责"),
                   ("问赵活", "问"), ("劝赵活", "劝"), ("陪赵活", "作陪"),
                   ("寻赵活", "寻人"), ("遇赵活", "相遇"), ("找赵活", "寻"),
                   ("为赵活", "为"), ("与赵活", "与"), ("和赵活", "和")):
        t = t.replace(_a, _b)
    t = t.replace("给赵活", "").replace("向赵活", "")
    t = t.replace("赵活", "")
    t = re.sub(r"^[，、·]+", "", t.strip())
    while t and t[-1] in "给为与和向对替帮":
        t = t[:-1].rstrip("，、")
    return t or s


def add_page(slug, typ, name, lead, inf, secs, cats, mentions, chapters, sort_key="",
             title="", hidden=0, facet="", facet2=""):
    name, title = _t2s(name), _t2s(title)
    pages.append((slug, typ, name, lead or "", json.dumps(inf, ensure_ascii=False),
                  json.dumps(secs, ensure_ascii=False), json.dumps(cats, ensure_ascii=False),
                  mentions, json.dumps(chapters, ensure_ascii=False), sort_key,
                  title or "", hidden, facet or "", facet2 or ""))

def source_rows(srcs):
    out = []
    for s in srcs or []:
        sc = s.get("script") or ""
        out.append({"note": s.get("note") or (scenes.get(sc, {}).get("title") or ""),
                    "quote": s.get("quote") or "", "script": sc,
                    "title": scenes.get(sc, {}).get("title") or sc,
                    "seq": find_seq(sc, s.get("quote") or ""), "routes": []})
    return out


def opt_text(script, idx):
    """根据 choice_option_00N = k 反查该选项文案。"""
    for blk in (CB.get(script) or []):
        for o in (blk.get("options") or []):
            if int(o.get("idx") or 0) == int(idx):
                return o.get("text") or ""
    return ""


_TGT_LBL = {"Free": "回养成地图（自由行动）", "Combat": "战斗", "Battle": "战役",
            "Title": "回标题画面", "GameOver": "结局", "Story": "剧情", "End": "结束",
            "section_01_free_start_01": "第一章养成段入口", "section_02_free_start_01": "第二章养成段入口"}


def _tgt_name(t):
    return scenes.get(t, {}).get("title") or _TGT_LBL.get(t) or t


def _tgt_scr(t):
    return t if t in scenes else ""


def chain_rows(script):
    """上一场 / 紧接着 / 分支去向（来自剧本 SetNextScript）。"""
    rows = []
    _edge_groups = {}
    for src in REV.get(script, [])[:3]:
        rows.append({"note": "前一场：" + _tgt_name(src),
                     "quote": "", "script": _tgt_scr(src),
                     "title": _tgt_name(src), "seq": 0, "routes": []})
    d = NXT.get(script) or {}
    nx = d.get("next")
    if nx:
        rows.append({"note": "紧接着：" + _tgt_name(nx),
                     "quote": "", "script": _tgt_scr(nx),
                     "title": _tgt_name(nx), "seq": 0, "routes": []})
    for e in (d.get("edges") or []):
        t = e.get("target") or ""
        if not t or t == nx or t not in scenes:
            continue
        _g = _edge_groups.setdefault(t, [])
        _cc = (e.get("cond") or "").strip()
        if _cc and _cc not in _g:
            _g.append(_cc)
    for t, _conds in list(_edge_groups.items())[:6]:
        _parts, _opts = [], []
        for cc in _conds:
            cc2 = cc.replace("==", "=").replace("switch", "判定")
            if cc2 and cc2 not in _parts:
                _parts.append(cc2)
            for _nm in re.findall(r"choice_option_?\w*\s*=\s*(\d+)", cc2):
                _tx = opt_text(script, int(_nm))
                if _tx and _tx not in _opts:
                    _opts.append(_tx)
        _tag = ("选项" + "、".join("「%s」" % x for x in _opts)) if _opts else ""
        _note = "分支：" + (scenes.get(t, {}).get("title") or t)
        _suffix = "；".join([x for x in (_tag, " 或 ".join(_parts)) if x])
        if _suffix:
            _note += "（" + _suffix + "）"
        rows.append({"note": _note,
                     "quote": "", "script": t,
                     "title": scenes.get(t, {}).get("title") or t, "seq": 0, "routes": []})
        if len(rows) >= 10:
            break
    # 分支点（*_break_*）本身没有台词，把它的去向也接上，免得叙事断在这里
    _seen = {r.get("script") for r in rows}
    for r in list(rows):
        _t2 = r.get("script") or ""
        if "_break" not in _t2.lower():
            continue
        _d2 = NXT.get(_t2) or {}
        _cands = [(_d2.get("next") or "")] + [x.get("target") or "" for x in (_d2.get("edges") or [])]
        for _nx2 in _cands:
            if not _nx2 or _nx2 in _seen or _nx2 not in scenes or "_break" in _nx2.lower():
                continue
            _seen.add(_nx2)
            rows.append({"note": "经分支点 → " + (scenes.get(_nx2, {}).get("title") or _nx2),
                         "quote": "", "script": _nx2,
                         "title": scenes.get(_nx2, {}).get("title") or _nx2, "seq": 0, "routes": []})
            if len(rows) >= 13:
                break
    return rows

def pick_event(sc, quote, text):
    """在场景里挑一条对得上的事件名。引文优先，场景标题次之，仅唯一事件时兜底。"""
    try:
        rows = c.execute("select name,quote from notes where script=? and type='事件'", (sc,)).fetchall()
    except Exception:
        rows = []
    q = (quote or "")[:16]
    if q:
        for name, qq in rows:
            if qq and (q in qq or (len(qq) >= 10 and qq[:10] in (quote or ""))):
                return name
    st = scenes.get(sc, {}).get("title") or ""
    for name, qq in rows:
        if name and len(name) >= 6 and name[:6] in st:
            return name
    return ""

def find_seq(sc, quote):
    """在场景里找引文所在的句序（去空白后包含匹配）。"""
    qn = "".join((quote or "").split())
    if not sc or not qn:
        return 0
    try:
        for seq, tx in c.execute("select seq,text from lines where script=? order by seq", (sc,)):
            if qn in "".join((tx or "").split()):
                return seq
    except Exception:
        pass
    return 0

def footnote_rows(slug, ai):
    rows = []
    for fn in (ai or {}).get("footnotes") or []:
        sc = fn.get("script") or ""
        ev = fn.get("event") or ""
        if not ev and sc:
            nm = pick_event(sc, fn.get("quote") or "", fn.get("text") or "")
            ev = ("事件/" + nm) if nm else ""
        note = f'{fn.get("n")}. ' + ((ev.split("/")[-1] + "：") if ev else "") + fn.get("text", "")
        rows.append({"note": note, "quote": fn.get("quote") or "",
                     "script": sc, "title": scenes.get(sc, {}).get("title") or sc,
                     "seq": find_seq(sc, fn.get("quote") or ""), "routes": []})
        if ev:
            links.append((slug, ev, "脚注", str(fn.get("n"))))
    return rows

# ---------- 实体页 ----------
NAME_ALIAS = []
_SCENE_EVENTS = {}
for (_t0, _n0), _i0 in byname.items():
    if _t0 != "事件":
        continue
    for _it in _i0:
        _SCENE_EVENTS.setdefault(_it["script"], []).append(_n0)
for (typ, name), items in byname.items():
    if typ == "关系":
        continue
    slug = f"{typ}/{name}"
    disp = name
    if typ == "事件":
        disp = noz(disp)
    if typ == "人物":
        _pfx, _dn = char_prefix(name)
        disp = (_pfx + "·" + _dn) if _pfx else _dn
        NAME_ALIAS.append((name, slug))
    ai = intro_of(slug)

    if typ == "地点":
        lead = (ai or {}).get("text") or PINTRO.get(name) or (
            (f"位于{PPARENT[name]}一带。" if name in PPARENT else "")
            + f"原文中出现 {len(items)} 处，未给出成段的地理说明。")
        scs = sorted({it["script"] for it in items}, key=lambda s: ORDER.get(s, 99999))
        rows = [{"note": (scenes.get(sc, {}).get("title") or sc),
                 "quote": "", "script": sc,
                 "title": scenes.get(sc, {}).get("title") or sc,
                 "seq": 0, "routes": routes_of(sc)} for sc in scs[:12]]
        inf = {"类型": "地点", "场景": f"{len(scs)} 场"}
        if name in PPARENT:
            inf["上级"] = PPARENT[name]
        kids = [k for k, v in PPARENT.items() if v == name]
        if kids:
            inf["下辖"] = f"{len(kids)} 处"
        secs = []
        if not ((ai or {}).get("text") or PINTRO.get(name)):
            _ex, _seen = [], set()
            for it in items:
                q = (it.get("quote") or "").strip()
                if not q or q in _seen:
                    continue
                _seen.add(q)
                _ex.append({"note": q[:110], "quote": "", "script": it["script"],
                            "title": scenes.get(it["script"], {}).get("title") or it["script"],
                            "seq": it.get("seq_from") or 0, "routes": []})
                if len(_ex) >= 6:
                    break
            if _ex:
                secs.append({"h": "原文摘录", "rows": _ex})
        srcs = []
        if isinstance(PINTRO.get(name), dict):
            srcs = PINTRO[name].get("sources") or []
        if not srcs and ai:
            srcs = ai.get("sources") or []
        if srcs:
            secs.append({"h": "考据来源", "rows": source_rows(srcs)})
        elif ai and ai.get("footnotes"):
            secs.append({"h": "脚注", "rows": footnote_rows(slug, ai)})
        if not any(s["h"] in ("考据来源", "脚注") for s in secs):
            picks = [it for it in items if it.get("quote")][:3]
            if picks:
                secs.append({"h": "考据来源", "rows": [
                    {"note": it["note"], "quote": it["quote"], "script": it["script"],
                     "title": scenes.get(it["script"], {}).get("title") or it["script"],
                     "seq": it["a"], "routes": []} for it in picks]})
        kids = [k for k, v in PPARENT.items() if v == name]
        if kids:
            krows = []
            for k in kids:
                kl = (intro_of(f"地点/{k}") or {}).get("text") or PINTRO.get(k) or ""
                krows.append({"note": k + (("｜" + kl[:44]) if kl else ""),
                              "quote": "", "script": "", "title": k,
                              "slug": f"地点/{k}",
                              "seq": 0, "routes": []})
            secs.append({"h": "下辖地点", "rows": krows})
        _SC_AT = sorted(SCENES_BY_PLACE.get(name, []), key=lambda x: ORDER.get(x, 99999))
        if _SC_AT:
            secs.append({"h": "发生场景", "rows": [
                {"note": scenes.get(_x, {}).get("title") or _x, "quote": "",
                 "script": _x, "title": scenes.get(_x, {}).get("title") or _x,
                 "seq": 0, "routes": []} for _x in _SC_AT[:60]]})
        _root = name
        _seen_r = set()
        while PPARENT.get(_root) and _root not in _seen_r:
            _seen_r.add(_root)
            _root = PPARENT[_root]
        _has_kids = any(v == name for v in PPARENT.values())
        _facet_pl = (_root if PPARENT.get(name)
                     else (name if _has_kids else "其他"))
        add_page(slug, "地点", name, lead, inf, secs, ["地点"], len(items), [],
                 facet=_facet_pl)
        if name in PPARENT and f"地点/{PPARENT[name]}" in {f"地点/{k}" for k in byname if k[0] == "地点"}:
            links.append((slug, f"地点/{PPARENT[name]}", "上级", ""))
            links.append((f"地点/{PPARENT[name]}", slug, "下级", name))
        continue

    if typ == "势力":
        fi = FINTRO.get(slug) or ai
        lead = (fi or {}).get("text") or f"{name}，原文中出现 {len(items)} 处。"
        secs = []
        if not (fi or {}).get("text"):
            _ex = []
            _seen = set()
            for it in items:
                q = (it.get("quote") or "").strip()
                if not q or q in _seen:
                    continue
                _seen.add(q)
                _ex.append({"note": q[:110], "quote": "", "script": it["script"],
                            "title": scenes.get(it["script"], {}).get("title") or it["script"],
                            "seq": it.get("seq_from") or 0, "routes": []})
                if len(_ex) >= 6:
                    break
            if _ex:
                secs.append({"h": "原文摘录", "rows": _ex})
        if fi and fi.get("footnotes"):
            secs.append({"h": "脚注", "rows": footnote_rows(slug, fi)})
        elif fi and fi.get("sources"):
            secs.append({"h": "考据来源", "rows": source_rows(fi["sources"])})
        for _s in (fi or {}).get("sections") or []:
            secs.append({"h": _s.get("h") or "", "html": _s.get("html") or ""})
        kids = [k for k, v in FPARENT.items() if v == name]
        _par = FPARENT.get(name)
        if _par:
            _pl2 = (FINTRO.get(f"势力/{_par}") or {}).get("text") or ""
            secs.append({"h": "上级势力", "rows": [
                {"note": _par + (("｜" + _pl2[:60]) if _pl2 else ""),
                 "quote": "", "script": "", "title": _par, "seq": 0, "routes": []}]})
        if kids:
            krows = []
            for k in kids:
                kl = (FINTRO.get(f"势力/{k}") or {}).get("text") or ""
                krows.append({"note": k + (("｜" + kl[:60]) if kl else ""),
                              "quote": "", "script": "", "title": k,
                              "seq": 0, "routes": []})
            secs.append({"h": "下辖势力（%d 个）" % len(kids), "rows": krows})
        _mem = []
        _seen = set()
        _cand = [n for (t, n) in byname if t == "人物"]
        _cand += [k.split("/", 1)[1] for k in INTROS if k.startswith("人物/")]
        _cand += list(EXTRA_PE)
        for _n in _cand:
            if _n in _seen:
                continue
            _pfx3, _dn3 = char_prefix(_n)
            if not _pfx3 or FAC_NORM.get(_pfx3, _pfx3) != name:
                continue
            if _dn3 in _ROLEWORDS:
                continue
            if _dn3.endswith(("弟子", "道兄", "师兄", "师弟", "师姐", "师妹",
                              "长老", "掌门", "护法", "帮众", "门人", "师兄们")) and len(_dn3) <= 7:
                continue
            _seen.add(_n)
            _d2 = char_title.get(_n) or ""
            _mem.append((_n, (("「" + _d2 + "」") if _d2 else "")))
        if _mem:
            _mem.sort()
            secs.append({"h": "本派成员（%d 人）" % len(_mem), "rows": [
                {"note": (_dn2 + ("｜" + _ni)) if _ni else _dn2, "quote": "",
                 "script": "", "title": _dn2, "seq": 0, "routes": []}
                for (_dn2, _ni) in _mem]})
        inf = {"类型": "势力", "提及": f"{len(items)} 条"}
        if name in FPARENT:
            inf["上级"] = FPARENT[name]
        if kids:
            inf["下辖"] = f"{len(kids)} 个"
        if _mem:
            inf["成员"] = f"{len(_mem)} 人"
        add_page(slug, "势力", name, lead, inf, secs, ["势力"], len(items), [],
                 facet=(FPARENT.get(name) or "顶层"))
        if name in FPARENT:
            links.append((slug, f"势力/{FPARENT[name]}", "上级", ""))
            links.append((f"势力/{FPARENT[name]}", slug, "下级", name))
        continue

    if ai:
        lead = ai.get("text") or pick_lead(items)
        secs = []
        for _s in ai.get("sections") or []:
            secs.append({"h": _s.get("h") or "", "html": _s.get("html") or ""})
        if ai.get("footnotes"):
            secs.append({"h": "脚注", "rows": footnote_rows(slug, ai)})
        elif ai.get("sources"):
            secs.append({"h": "考据来源", "rows": source_rows(ai["sources"])})
    else:
        lead = pick_lead(items)
        if typ == "势力":
            lead = f"{name}，原文中出现 {len(items)} 处。"
        secs = sections_for(items, typ)
        total = 0
        kept = []
        for s in secs:
            if total >= 8:
                continue
            s["rows"] = (s.get("rows") or [])[:8 - total]
            total += len(s["rows"])
            if s["rows"]:
                kept.append(s)
        secs = kept

    inf = {"类型": typ, "笔记": f"{len(items)} 条"}
    if typ == "事件":
        _pl, _tm = [], []
        for it in items:
            pv, _ev = place_of(it["script"])
            if pv and pv not in _pl:
                _pl.append(pv)
            tl = time_label(it["script"])
            if tl and tl not in _tm:
                _tm.append(tl)
        if _pl:
            inf["发生地"] = "、".join(_pl[:5])
        if _tm:
            inf["时间"] = "、".join(sorted(_tm)[:3])
        et = EVT.get(slug)
        if et:
            inf["推断时间"] = (et.get("earliest") or "") + ((" ～ " + et.get("latest")) if et.get("latest") else "")
            secs.insert(0, {"h": "时间推导", "html": et.get("basis") or ""})
        ec = ECOND.get(name) or []
        crows = []
        for r in ec:
            txt = (r.get("text") or "").strip()
            if not txt:
                continue
            crows.append({"note": r.get("kind", "条件") + "：" + txt, "quote": "",
                           "script": "", "title": "", "seq": 0, "routes": []})
        # 进入条件边：谁在什么判定/选项下跳进这个场景
        seen_e = set()
        erows = []
        for it in items:
            _edges = EDGES.get(it["script"], [])
            _specific = len(_edges) <= 2          # 入口越少，条件越属于本场
            _judged = 0
            for r in _edges:
                tx = (r.get("text") or "").strip()
                kind = r.get("kind") or ""
                if kind == "判定" or kind == "条件":
                    if not _specific:
                        continue
                    _judged += 1
                    if _judged > 2:
                        continue
                if kind != "接续" and (not tx or re.match(r"^(选项|第)\d", tx)):
                    continue
                key = (kind, tx)
                if key in seen_e:
                    continue
                seen_e.add(key)
                _rsc = r.get("src") or ""
                _rseq = 0
                _rtitle = ""
                if kind == "选择":
                    # 边的文案可能是 "exit+O_xxx+0+0" 这种写法，先把真 key 抽出来
                    _km = re.search(r"O_[A-Za-z0-9_]+", tx)
                    _key = _km.group(0) if _km else ""
                    _meta = OPTIDX.get(_key) or {}
                    _t2 = _meta.get("text") or ""
                    _lab = _t2 or _key or tx
                    # 索引指向「这个选项所在的那一场」，而不是选中后去的那一场
                    _pos = OPTPOS.get(_key) or {}
                    if _pos.get("script"):
                        _rsc = _pos["script"]
                    _rseq = int(_pos.get("seq") or 0)
                    _rtitle = scenes.get(_rsc, {}).get("title") or _rsc
                    note, pri = "选择后进入", 0
                    _c2 = _meta.get("cond") or ""
                    _n2 = _meta.get("next") or ""
                    note = "在「%s」%s选择" % (
                        _rtitle, ("第 %d 句" % _rseq) if _rseq else "开头")
                    if _c2:
                        note += "；解锁条件：" + _c2
                    if _n2 and _n2 in scenes:
                        note += "；选中后去「%s」" % (scenes.get(_n2, {}).get("title") or _n2)
                    # 行首链接直接指向「这个选项」本身，不再指向场景或目的地
                    if _lab:
                        _rtitle = _lab
                elif kind == "判定":
                    note, pri = "入境判定：" + tx, 1
                    _rtitle = scenes.get(_rsc, {}).get("title") or _rsc
                elif kind == "接续":
                    note, pri = "上场直接接续", 3
                    _rtitle = scenes.get(_rsc, {}).get("title") or _rsc
                else:
                    note, pri = "前置条件：" + tx, 2
                    _rtitle = scenes.get(_rsc, {}).get("title") or _rsc
                erows.append((pri, {"note": note, "quote": "", "script": _rsc,
                                    "title": _rtitle, "seq": _rseq, "routes": []}))
        erows.sort(key=lambda x: x[0])
        crows += [r for _p, r in erows]
        # 没有任何进入边时，用场景开场判定兜底
        if not any(p < 3 for p, _ in erows):
            seen_g = set()
            for it in items:
                for tx in GATES.get(it["script"], []):
                    if tx in seen_g:
                        continue
                    seen_g.add(tx)
                    crows.append({"note": "开场判定：" + tx, "quote": "", "script": it["script"],
                                   "title": "", "seq": 0, "routes": []})
                    if len(seen_g) >= 4:
                        break
                if len(seen_g) >= 4:
                    break
        # 地图位置事件（PositionEventData）自带的条件
        seen_p = set()
        for it in items:
            for d in POS.get(it["script"], []):
                nm = d.get("dev") or d.get("name")
                if nm in seen_p:
                    continue
                seen_p.add(nm)
                cs = [c for c in (d.get("cond") or []) if c]
                txt = "；".join(cs[:4])
                note = "地图事件「" + nm + "」" + ("：" + txt if txt else "") + \
                       ("（基础概率 %s%%）" % d["rate"] if d.get("rate") is not None else "")
                crows.insert(0, {"note": note, "quote": "", "script": it["script"],
                                 "title": "", "seq": 0, "routes": []})
        if crows:
            _seen_note, _crow2 = set(), []
            for _r in crows:
                _k = (_r.get("note") or "").strip()
                if _k and _k in _seen_note:
                    continue
                _seen_note.add(_k)
                _crow2.append(_r)
            _a0 = arc_of(items[0]["script"]) if items else ""
            _fidx = ARC_ORDER.index(_a0) if _a0 in ARC_ORDER else 99
            _late = ARC_ORDER.index("武林盟进攻唐门") if "武林盟进攻唐门" in ARC_ORDER else 6
            _crow2 = [r for r in _crow2
                      if not re.match(r"^\s*备注[:：]", (r.get("note") or ""))
                      and "差分" not in (r.get("note") or "")
                      and "第三年" not in (r.get("note") or "")
                      and not (_fidx < _late and ("武林盟" in (r.get("note") or "")
                                                  or "西武林" in (r.get("note") or "")))
                      and not (_fidx != 0 and "游戏开始自动触发" in (r.get("note") or ""))]
            if _crow2:
                secs.insert(0, {"h": "触发条件", "rows": _crow2[:16]})
        seen_sc, srows = set(), []
        for it in sorted(items, key=lambda x: (ORDER.get(x["script"], 99999), x["a"])):
            if it["script"] in seen_sc:
                continue
            seen_sc.add(it["script"])
            sc = scenes.get(it["script"], {})
            pv, _ev = place_of(it["script"])
            tl = time_label(it["script"])
            note = ((sc.get("title") or it["script"])
                    + (f"｜{pv}（{_ev}）" if pv else "")
                    + (f"｜{tl}" if tl else ""))
            srows.append({"note": note, "quote": "", "script": it["script"],
                          "title": sc.get("title") or it["script"], "seq": it["a"], "routes": []})
        if srows:
            secs.append({"h": "发生场景", "rows": srows[:30]})
        _last = max(items, key=lambda x: (ORDER.get(x["script"], 99999), x["a"])) if items else None
        _cr = chain_rows(_last["script"]) if _last else []
        _segid = SEGOF.get(_last["script"]) if _last else ""
        if _segid:
            _crows2 = [{"note": "", "title": "剧情段 %s：%s" % (_segid, (SEGMAP.get(_segid, {}) or {}).get("title", "")),
                        "slug": "剧情段/" + _segid, "quote": "", "script": "", "seq": 0, "routes": []}]
            _nseg = (SEGMAP.get(_segid, {}) or {}).get("next_seg")
            if _nseg:
                _crows2.append({"note": "", "title": "本段结束后 → %s：%s" % (
                                    _nseg, (SEGMAP.get(_nseg, {}) or {}).get("title", "")),
                                "slug": "剧情段/" + _nseg, "quote": "", "script": "",
                                "seq": 0, "routes": []})
            else:
                for _b in ((SEGMAP.get(_segid, {}) or {}).get("branches") or [])[:5]:
                    _bs = SEGMAP.get(_b.get("seg")) or {}
                    _crows2.append({"note": "", "title": "接下一段 → %s：%s" % (
                                        _b.get("seg"), _bs.get("title", "")),
                                    "slug": "剧情段/" + _b["seg"], "quote": "", "script": "",
                                    "seq": 0, "routes": []})
            _cr = _crows2 + _cr
        if _cr:
            secs.append({"h": "剧情衔接", "rows": _cr})

    chs = chapters_of(items)
    if typ == "事件" and items:
        _b0 = BLOCK_OF.get(items[0]["script"])
        if _b0:
            inf["剧情单元"] = _b0
        _uset = []
        for _it in items:
            _u = BLOCK_OF.get(_it["script"])
            if _u and _u not in _uset:
                _uset.append(_u)
        if len(_uset) > 1:
            inf["跨单元"] = "、".join(_uset[:4])
    if chs:
        inf["出现阶段"] = "、".join(chs[:8])
    if typ == "人物" and faction_of.get(name):
        inf["门派/归属"] = faction_of[name]
    if typ == "人物" and name in REFC:
        for _k in ("性别", "生日", "年龄"):
            _v = (REFC[name].get("info") or {}).get(_k)
            if _v and _v not in ("-", "？", "?"):
                inf[_k] = _v
    cats = [typ] + (chs[:6] if chs else [])
    if typ == "人物":
        _fc = disp.split("·")[0]
    elif typ == "地点":
        _fc = inf.get("上级") or "顶层"
    elif typ == "势力":
        _fc = FPARENT.get(name) or "顶层"
    elif typ == "事件":
        _fc = arc_of(items[0]["script"]) if items else ""
    else:
        _fc = chs[0] if chs else ""
    if typ == "人物" and name in CHAR_SECTIONS:
        for _cs in CHAR_SECTIONS[name]:
            _rows3 = []
            if _cs.get("text"):
                _rows3.append({"note": _cs["text"], "quote": "", "script": "",
                               "title": "", "seq": 0, "routes": []})
            for _sc3 in _cs.get("scripts") or []:
                _rows3.append({"note": "", "quote": "", "script": _sc3,
                               "title": (scenes.get(_sc3) or {}).get("title") or _sc3,
                               "seq": 0, "routes": []})
            secs.append({"h": _cs["h"], "rows": _rows3})

    add_page(slug, typ, disp, lead, inf, secs, cats, len(items), chs,
             title=(char_title.get(name, "") if typ == "人物" else ""),
             hidden=(1 if (typ == "人物" and name in CHAR_HIDDEN) else 0),
             facet=_fc,
             facet2=(role_of(max(items, key=lambda x: (ORDER.get(x["script"], 99999), x["a"]))["script"])
                     if typ == "事件" and items else ""))
    if typ == "人物" and faction_of.get(name) in facset:
        links.append((slug, f"势力/{faction_of[name]}", "归属", ""))
        links.append((f"势力/{faction_of[name]}", slug, "成员", ""))

# ---------- 额外势力页 ----------
for _fn, _fm in EXTRA_FAC.items():
    if ("势力", _fn) in byname:
        continue
    _fslug = f"势力/{_fn}"
    _fpar = _fm.get("parent") or ""
    if _fpar:
        FPARENT.setdefault(_fn, _fpar)
    _finf = {"类型": "势力", "提及": "0 条"}
    if _fpar:
        _finf["上级"] = _fpar
    _fsecs = []
    _fmem = []
    for _cn in list(EXTRA_PE) + [k.split("/", 1)[1] for k in INTROS if k.startswith("人物/")]:
        _pf, _dn = char_prefix(_cn)
        if not _pf or FAC_NORM.get(_pf, _pf) != _fn:
            continue
        if _dn in _ROLEWORDS:
            continue
        _tt = char_title.get(_cn) or ""
        _fmem.append((_cn, ("「" + _tt + "」") if _tt else ""))
    if _fpar:
        _fsecs.append({"h": "上级势力", "rows": [
            {"note": _fpar, "quote": "", "script": "", "title": _fpar, "seq": 0, "routes": []}]})
    if _fmem:
        _fmem.sort()
        _finf["成员"] = f"{len(_fmem)} 人"
        _fsecs.append({"h": "本派成员（%d 人）" % len(_fmem), "rows": [
            {"note": (_a + ("｜" + _b)) if _b else _a, "quote": "", "script": "",
             "title": _a, "seq": 0, "routes": []} for _a, _b in _fmem]})
    add_page(_fslug, "势力", _fn, _fm.get("text") or "", _finf, _fsecs, ["势力"], 0, [],
             facet=(_fpar or "顶层"))
    if _fpar:
        links.append((_fslug, f"势力/{_fpar}", "上级", ""))
        links.append((f"势力/{_fpar}", _fslug, "下级", _fn))

# ---------- 补充人物页（原文有名字、成段叙述缺失） ----------
try:
    _ep = os.path.join(BASE, "data", "extra_persons.json")
    if os.path.exists(_ep):
        for _nm, _meta in json.load(open(_ep, encoding="utf-8")).items():
            _slug = f"人物/{_nm}"
            if any(p[0] == _slug for p in pages):
                continue
            _tot = c.execute("select count(*) from lines where text like ?",
                             ("%" + _nm + "%",)).fetchone()[0]
            _rows = []
            for _sc, _sq, _sp, _tx in c.execute(
                    "select script,seq,speaker,text from lines where text like ? order by id limit 8",
                    ("%" + _nm + "%",)):
                _rows.append({"note": "（%s）%s" % (_sp or "旁白", (_tx or "")[:110]),
                              "quote": "", "script": _sc,
                              "title": scenes.get(_sc, {}).get("title") or _sc,
                              "seq": _sq, "routes": []})
            _fac = _meta.get("faction") or "江湖"
            _fac = FAC_NORM.get(_fac, _fac)
            _disp = (_fac + "·" + _nm)
            _sub = _meta.get("sub")
            _lead = ((intro_of(_slug) or {}).get("text")
                     or "%s，原文中出现 %d 处。" % (_nm, _tot))
            _inf = {"类型": "人物", "门派/归属": _fac + (("（" + _sub + "）") if _sub else "")}
            add_page(_slug, "人物", _disp, _lead, _inf,
                     [{"h": "原文摘录", "rows": _rows}], ["人物"], _tot, [],
                     facet=_fac)
            NAME_ALIAS.append((_nm, _slug))
except Exception as _e:
    print("补充人物跳过:", _e)

# ---------- 剧情段页 ----------
SEGBR = {}
try:
    _sbp = os.path.join(BASE, "data", "seg_branch.json")
    if os.path.exists(_sbp):
        SEGBR = json.load(open(_sbp, encoding="utf-8"))
except Exception:
    SEGBR = {}

# 段内跨段岔口索引（没人工写过的段，自动列出走向）
_SOF = {}
for _s0 in SEGS:
    for _sc0 in (_s0.get("scenes") or []):
        _SOF[_sc0] = _s0["id"]
_BRK = {}
try:
    for _a, _b, _sw, _rs in c.execute(
            "select src,dst,switch,result from scene_edges where type='branch'"):
        _BRK.setdefault(_a, []).append((_b, _sw, _rs))
except Exception:
    _BRK = {}

for _sg in SEGS:
    _sid = _sg["id"]
    _scs = _sg.get("scenes") or []
    if not _scs:
        continue
    _slug = f"剧情段/{_sid}"
    _first, _lastsc = _scs[0], _scs[-1]
    _rows = [{"note": "%d. %s" % (i + 1, scenes.get(s, {}).get("title") or s),
              "quote": "", "script": s,
              "title": scenes.get(s, {}).get("title") or s, "seq": 0, "routes": []}
             for i, s in enumerate(_scs[:40])]
    _evs = []
    for s in _scs:
        for nm in _SCENE_EVENTS.get(s, []):
            if nm not in _evs:
                _evs.append(nm)
    _erows = [{"note": "", "title": nm, "slug": "事件/" + nm, "quote": "",
               "script": "", "seq": 0, "routes": []} for nm in _evs[:30]]
    _crows = []
    if _sg.get("next_seg"):
        _nx = SEGMAP.get(_sg["next_seg"]) or {}
        _crows.append({"note": "", "title": "下一段 %s：%s" % (_sg["next_seg"], _nx.get("title") or ""),
                       "slug": "剧情段/" + _sg["next_seg"], "quote": "", "script": "",
                       "seq": 0, "routes": []})
    for b in (_sg.get("branches") or [])[:8]:
        _bs = SEGMAP.get(b.get("seg")) or {}
        _crows.append({"note": "", "title": "分支 %s：%s" % (b.get("seg"), _bs.get("title") or ""),
                       "slug": "剧情段/" + b["seg"], "quote": "", "script": "",
                       "seq": 0, "routes": []})
        _to = b.get("to") or ""
        if _to in scenes:
            _crows.append({"note": "",
                           "title": "　→ " + (scenes.get(_to, {}).get("title") or _to),
                           "slug": "", "quote": "", "script": _to,
                           "seq": 0, "routes": []})
    _secs = [{"h": "场景顺序", "rows": _rows}]
    if _erows:
        _secs.append({"h": "本段事件", "rows": _erows})
    if not _crows and len(_scs) == 1:
        # 没有剧本出口时，用时间线顺序给出下一场（标明是推断）
        _ord = sorted((ORDER.get(s, 99999), s) for s in scenes)
        _pos = {s: i for i, (_o, s) in enumerate(_ord)}
        _i = _pos.get(_scs[0])
        if _i is not None and _i + 1 < len(_ord):
            _nx2 = _ord[_i + 1][1]
            _crows.append({"note": "",
                           "title": "按时间线，下一场：%s" % (scenes.get(_nx2, {}).get("title") or _nx2),
                           "quote": "", "script": _nx2,
                           "title": scenes.get(_nx2, {}).get("title") or _nx2,
                           "seq": 0, "routes": []})
    if _crows:
        _secs.append({"h": "剧情衔接", "rows": _crows})
    _ttl = noz(_sg.get("title") or _sid)
    _lead = ("本段共 %d 场，自「%s」起" % (len(_scs), scenes.get(_first, {}).get("title") or _first)
             + (("，接「%s」" % (scenes.get(_lastsc, {}).get("title") or _lastsc)) if len(_scs) > 1 else "")
             + (("，下一段接「%s」" % (SEGMAP.get(_sg["next_seg"], {}) or {}).get("title", "")) if _sg.get("next_seg") else "，此处为分支点")
             + "。")
    _sbr = SEGBR.get(_sid) or []
    if not _sbr:
        _auto = []
        _seen = set()
        for _sc0 in _scs:
            for _b0, _sw0, _rs0 in _BRK.get(_sc0, []):
                _t0 = _SOF.get(_b0)
                if not _t0 or _t0 == _sid or (_sc0, _t0) in _seen:
                    continue
                _seen.add((_sc0, _t0))
                _lab = ("判定 %s 结果 %s" % (_sw0, _rs0)) if _sw0 else "选择"
                _auto.append(["在「%s」%s" % (scenes.get(_sc0, {}).get("title") or _sc0, _lab),
                              "→「%s」" % ((SEGMAP.get(_t0, {}) or {}).get("title") or _t0)])
        _sbr = _auto[:10]
        _autoflag = bool(_sbr)
    else:
        _autoflag = False
    if _sbr:
        _sbr_rows = [{"note": "【%s】%s" % (a, b), "quote": "", "script": "",
                      "title": "", "seq": 0, "routes": []} for a, b in _sbr]
        if _autoflag:
            _sbr_rows.insert(0, {
                "note": "本节由剧本自动归纳，列出本段通向哪些段；尚未逐条改写成说明。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
        if len(_sbr) == 1:
            _sbr_rows.append({
                "note": "本段只有一处条件出口：条件成立才转入下一段，不成立则本段到此为止。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
        else:
            _sbr_rows.append({
                "note": "本段是一个岔口：以上各条互斥，一次只走其中一条，其余不成立。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
        _secs.append({"h": ("本段出口（条件接续）" if len(_sbr) == 1
                            else "本段分岔（择一，%d 条）" % len(_sbr)), "rows": _sbr_rows})
    add_page(_slug, "剧情段", _ttl, _lead,
             {"类型": "剧情段", "场数": str(len(_scs)), "阶段": arc_of(_first),
              "剧情单元": BLOCK_OF.get(_first, ""),
              "主线/支线": _sg.get("route") or "支线"},
             _secs, ["剧情段", arc_of(_first)], len(_scs), [],
             facet=arc_of(_first), facet2=role_of(_first))
    for s in _scs:
        links.append((_slug, f"场景/{s}", "场景", ""))
    for nm in _evs[:30]:
        links.append((_slug, f"事件/{nm}", "事件", ""))

# ---------- 剧情单元页（阶段 → 单元 → 剧情段 → 场景） ----------
_BR_SRC = {}
_IN_SRC = {}
try:
    for _s0, _d0, _t0, _cd0, _sw0, _rs0 in c.execute(
            "select src,dst,type,cond,switch,result from scene_edges"):
        if _t0 == "branch":
            _BR_SRC.setdefault(_s0, []).append((_d0, _cd0, _sw0, _rs0))
        _IN_SRC.setdefault(_d0, []).append((_s0, _t0))
except Exception as _e:
    print("分支索引跳过:", _e)

for _bk in BLOCKS:
    _bn = _bk.get("name") or ""
    _bscs = _bk.get("scenes") or []
    if not _bn or not _bscs:
        continue
    _bslug = "剧情单元/" + _bn
    _bscs = ([_s for _s in _bscs if (scenes.get(_s, {}).get("lines") or 0) > 0]
             + [_s for _s in _bscs if (scenes.get(_s, {}).get("lines") or 0) <= 0])
    # 择一分支：本单元内由分支边进入的场景，不算主线
    _bset = set(_bscs)
    _child = {}
    for _p0, _lst0 in _BR_SRC.items():
        if _p0 not in _bset:
            continue
        for _d0, _cd0, _sw0, _rs0 in _lst0:
            if _d0 in _bset and _d0 != _p0 and _d0 not in _child:
                _child[_d0] = (_p0, _sw0, _rs0, _cd0)
    _main = [_s for _s in _bscs if _s not in _child]
    _rows = []
    for _i, _s in enumerate(_main[:300]):
        _bpl, _ = place_of(_s)
        _bt = scenes.get(_s, {}).get("title") or _s
        _mark = "（此处分支 ↓）" if _BR_SRC.get(_s) else ""
        _rows.append({"note": "%d. %s%s%s" % (_i + 1, _bt, ("｜" + _bpl) if _bpl else "", _mark),
                      "quote": "", "script": _s, "title": _bt, "seq": 0, "routes": []})
    _brows = []
    _bauto = []
    _bgrp = collections.OrderedDict()
    for _p0 in _main:
        for _d0, _cd0, _sw0, _rs0 in (_BR_SRC.get(_p0) or []):
            if _d0 not in _bset:
                continue
            if _sw0:
                _lab = "判定 %s 结果 %s" % (_sw0, _rs0)
            elif _cd0:
                _lab = _cd0.replace("switch", "判定").replace("_result==", " 结果=")
            else:
                _lab = "选项分支"
            _bgrp.setdefault((_p0, _d0), []).append(_lab)
    for (_p0, _d0), _labs in _bgrp.items():
        _bt0 = scenes.get(_p0, {}).get("title") or _p0
        _bt1 = scenes.get(_d0, {}).get("title") or _d0
        _uniq = []
        for _x in _labs:
            if _x not in _uniq:
                _uniq.append(_x)
        _brows.append({"note": "在「%s」：%s →\u3000%s" % (_bt0, "；".join(_uniq), _bt1),
                       "quote": "", "script": _d0, "title": _bt1, "seq": 0, "routes": []})
        _bauto.append({"when": "在「%s」：%s" % (_bt0, "；".join(_uniq)),
                       "then": "→「%s」" % _bt1})
    _segids = []
    for _s in _bscs:
        _g = SEGOF.get(_s)
        if _g and _g not in _segids:
            _segids.append(_g)
    _secs = []
    _un = UNIT_NOTES.get(_bn)
    if _un:
        _ubr = _un.get("branches") or _bauto
        _hasbr = bool(_brows) or bool(_ubr)
        _urows = []
        if _hasbr:
            _urows.append({
                "note": "本单元含互斥走向：同一轮游玩只会走其中一条，不会全部发生。下面是各分支共同的进程；各分支各自的结局，另列在「互斥分支」中。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
        _urows.append({"note": _un.get("summary") or "", "quote": "", "script": "",
                       "title": "", "seq": 0, "routes": []})
        for _ph in (_un.get("phases") or []):
            _urows.append({"note": "阶段：" + _ph, "quote": "", "script": "",
                           "title": "", "seq": 0, "routes": []})
        _secs.append({"h": ("内容概要（主线）" if _hasbr else "内容概要"), "rows": _urows})
        if _ubr:
            _ubrows = []
            for _it in _ubr:
                _ubrows.append({
                    "note": "【%s】%s" % (_it.get("when") or "分支", _it.get("then") or ""),
                    "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
            _ubrows.append({
                "note": "以上 %d 条按主要走向合并；本单元剧本中共有 %d 处分支入口，逐条列于下方「择一分支」。"
                        % (len(_ubr), len(_brows)),
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
            _ubrows.append({
                "note": "以上各条互斥：一轮游玩发生其中一条，其余不成立；下面「择一分支」列出它们在剧本里的实际入口与条件。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
            _secs.append({"h": "互斥分支（择一发生，%d 条）" % len(_ubr), "rows": _ubrows})
    if _rows:
        _secs.append({"h": "主线进程（%d 场，按时间线）" % len(_main), "rows": _rows})
    if _brows:
        _secs.append({"h": "择一分支（%d 条，只会发生其中一条）" % len(_brows), "rows": _brows[:80]})
    if _segids:
        _secs.append({"h": "本单元剧情段（%d 段）" % len(_segids), "rows": [
            {"note": "", "title": "%s：%s" % (_g, (SEGMAP.get(_g, {}) or {}).get("title", "")),
             "slug": "剧情段/" + _g, "quote": "", "script": "", "seq": 0, "routes": []}
            for _g in _segids[:60]]})
    _blead = ("%s阶段的剧情单元，共 %d 场" % (_bk.get("arc") or "", len(_bscs))
              + (("，主要发生在%s" % _bk["place"]) if _bk.get("place") else "")
              + "。下面按剧情先后排列，点场景可读原文。")
    add_page(_bslug, "剧情单元", _bn, _blead,
             {"类型": "剧情单元", "阶段": _bk.get("arc") or "",
              "叙事角色": BLOCK_ROLE.get(_bn) or UNIT_ROLE.get(_bn) or ("日常" if _bn.startswith("其他") else "其他"),
              "地点": _bk.get("place") or "未指定", "场数": str(len(_bscs))},
             _secs, ["剧情单元", _bk.get("arc") or ""], len(_bscs), [],
             facet=(BLOCK_ROLE.get(_bn) or UNIT_ROLE.get(_bn) or ("日常" if _bn.startswith("其他") else "其他")),
             facet2=_bk.get("arc") or "")
    for _s in _bscs[:300]:
        links.append((_bslug, "场景/" + _s, "场景", ""))

# ---------- 地图事件（PositionEventData） ----------
MAP_PLACE = {
    "Alchemy": "唐门-炼丹房", "Back": "唐门-后山", "Door": "唐门-大门",
    "Mall": "唐门-正心堂", "Craft": "唐门-锻冶场", "Forge": "唐门-锻冶场",
    "Center": "唐门-练功场", "Kitchen": "唐门-伙房", "Fortress": "唐门-外堡",
    "Pharmacy": "唐门-药房", "Casino": "崆峒-无色广场赌坊", "Teashop": "唐门-茶室",
    "Room": "唐门-男弟子房", "GirlRoom": "唐门-女弟子房", "Spa": "唐门-温泉",
    "Chess": "唐门-棋室", "Study": "唐门-讲经堂",
    "Travel": "赶路途中", "Section": "章节随机", "Ch": "章节剧情",
}
_pem = {}
if os.path.exists(_pm):
    try:
        _pem = json.load(open(_pm, encoding="utf-8"))
    except Exception:
        _pem = {}
_scr_by_name = {v: k for k, v in _pem.items()}
# 不唯一对应剧本的地图事件（赶路/章节随机事件按路线复用同一套结果剧本）
_FAMPOS = {}
try:
    _fp = os.path.join(BASE, "data", "position_script_family.json")
    if os.path.exists(_fp):
        _FAMPOS = json.load(open(_fp, encoding="utf-8"))
except Exception:
    _FAMPOS = {}
MAP_EVT_PLACE = {}
try:
    _mp = os.path.join(BASE, "data", "map_event_place.json")
    if os.path.exists(_mp):
        MAP_EVT_PLACE = json.load(open(_mp, encoding="utf-8"))
except Exception:
    MAP_EVT_PLACE = {}

MAP_EVT_NAME = {}
try:
    _mn = os.path.join(BASE, "data", "map_event_names.json")
    if os.path.exists(_mn):
        MAP_EVT_NAME = json.load(open(_mn, encoding="utf-8"))
except Exception:
    MAP_EVT_NAME = {}

_EVT_TITLE = {}
for _nm, _sc in (_pem or {}).items():
    if not isinstance(_sc, str):
        continue
    try:
        _r = c.execute("select title from scenes where script=?", (_sc,)).fetchone()
    except Exception:
        _r = None
    if _r and _r[0]:
        _EVT_TITLE[_nm] = _t2s(_r[0])

_pe_seen = {}
for d in POSEV:
    nm = d.get("name") or ""
    pre = nm.split("_")[0] if nm else ""
    place = MAP_EVT_PLACE.get(nm) or MAP_PLACE.get(pre, "")
    if not nm:
        nm = "未命名_" + str(POSEV.index(d) + 1).zfill(3)
    _pe_seen[nm] = _pe_seen.get(nm, 0) + 1
    slug = "地图事件/" + nm + ("_%d" % _pe_seen[nm] if _pe_seen[nm] > 1 else "")
    title = _t2s((d.get("dev") or "").strip())
    title_src = "原生标题" if title else ""
    if not title and MAP_EVT_NAME.get(nm):
        title = _t2s(MAP_EVT_NAME[nm])
        title_src = "整理命名"
    if not title:
        _st = _EVT_TITLE.get(nm) or ""
        if _st and len(_st) >= 4 and not re.search(r"（\d+）$|・工作$|・自由行动$|^转场", _st):
            title = _st
            title_src = "取自剧本标题"
    if not title:
        _k = _t2s((d.get("key") or "").replace("_", " ").strip())
        if place and _k:
            title = place + "・" + _k
        else:
            title = place or _k or nm
        title_src = "地点＋结果"
    else:
        if place and place not in title:
            title = place + "・" + title
    title = noz(title)
    if _pe_seen[nm] > 1:
        title += "（%s）" % (d.get("value") or _pe_seen[nm])
    conds = [c for c in (d.get("cond") or []) if c]
    lead = (f"{place}的地图事件" if place else "地图事件") + f"，基础概率 {d.get('rate')}%。"
    if conds:
        lead += "触发条件：" + "；".join(conds) + "。"
    inf = {"类型": "地图事件", "事件编号": nm}
    if title_src and title_src != "原生标题":
        inf["名称来源"] = title_src
    if place:
        inf["地点"] = place
    if d.get("key"):
        inf["配置"] = f"{d['key']}→{d.get('value', '')}"
    inf["基础概率"] = f"{d.get('rate')}%"
    if d.get("start") or d.get("end"):
        inf["时间窗"] = (d.get("start") or "不限") + " ～ " + (d.get("end") or "不限")
    secs = []
    if conds:
        secs.append({"h": "触发条件", "rows": [
            {"note": c, "quote": "", "script": "", "title": "", "seq": 0, "routes": []}
            for c in conds]})
    rl = [r for r in (d.get("rates") or []) if r.get("cond")]
    if rl:
        secs.append({"h": "概率分支", "rows": [
            {"note": "%d%%：%s" % (r.get("rate") or 0, "；".join(r["cond"])), "quote": "",
             "script": "", "title": "", "seq": 0, "routes": []} for r in rl[:8]]})
    sc = _pem.get(nm)
    if sc and sc in scenes:
        inf["对应剧本"] = scenes[sc].get("title") or sc
        secs.append({"h": "对应剧情", "rows": [
            {"note": scenes[sc].get("title") or sc, "quote": "", "script": sc,
             "title": scenes[sc].get("title") or sc, "seq": 0, "routes": []}]})
    elif _FAMPOS.get(nm):
        _fam = [s for s in _FAMPOS[nm] if s in scenes]
        inf["对应剧情"] = "按路线共 %d 条" % len(_fam)
        secs.append({"h": "同型剧情", "rows": [
            {"note": (scenes[s].get("title") or s) + "（" + s + "）", "quote": "",
             "script": s, "title": scenes[s].get("title") or s, "seq": 0, "routes": []}
            for s in _fam]})
        lead += "这类事件不绑定单独一场戏，同一结果码在不同路线各自播出，下方列出同码剧本。"
    else:
        inf["对应剧情"] = "无专属剧本"
        lead += "游戏里该结果只弹提示文本，没有对应剧本。"
    add_page(slug, "地图事件", title, lead, inf, secs,
             ["地图事件"] + ([place] if place else []), 0, [],
             facet=(place or "其他地点"))
    if place and f"地点/{place}" in placeset:
        links.append((f"地点/{place}", slug, "地图事件", ""))
        links.append((slug, f"地点/{place}", "发生地", place))
    if sc and f"场景/{sc}" in {p[0] for p in pages}:
        links.append((slug, f"场景/{sc}", "剧本", ""))
    for _fs in (_FAMPOS.get(nm) or [])[:6]:
        if f"场景/{_fs}" in {p[0] for p in pages}:
            links.append((slug, f"场景/{_fs}", "同型剧情", ""))

# ---------- 地图事件索引（按地点分组） ----------
if POSEV:
    _grp = {}
    for d in POSEV:
        _pre = (d.get("name") or "").split("_")[0]
        _pl = MAP_PLACE.get(_pre) or "其他地点"
        _grp.setdefault(_pl, []).append(d)
    _secs = []
    for _pl, _lst in sorted(_grp.items(), key=lambda x: -len(x[1])):
        _rows = []
        for d in sorted(_lst, key=lambda x: (x.get("start_key") or 999999, x.get("name") or "")):
            _t = (d.get("dev") or d.get("name") or "").strip()
            _w = ""
            if d.get("start") or d.get("end"):
                _w = "｜%s ～ %s" % (d.get("start") or "不限", d.get("end") or "不限")
            _rows.append({"note": "%s（%s%%）%s" % (_t, d.get("rate"), _w), "quote": "",
                          "script": _pem.get(d.get("name") or "") or "", "title": "", "seq": 0, "routes": []})
        _secs.append({"h": "%s（%d）" % (_pl, len(_lst)), "rows": _rows})
    add_page("地图事件/索引", "地图事件索引", "地图事件索引",
             "养成地图上会随机刷出的 %d 个事件，按地点分组。括号内为基础概率，有明确时间窗的标在后面；能对上剧本的，事件名可点进原文。" % len(POSEV),
             {"类型": "地图事件索引", "条目": str(len(POSEV))}, _secs, ["地图事件"], 0, [])

# 地点父子（无笔记的父级也建链接）
for ch, pa in PPARENT.items():
    if f"地点/{ch}" in {p[0] for p in pages} and f"地点/{pa}" in {p[0] for p in pages}:
        links.append((f"地点/{ch}", f"地点/{pa}", "上级", pa))
        links.append((f"地点/{pa}", f"地点/{ch}", "下级", ch))

# ---------- 关系页 ----------
relnames = collections.defaultdict(list)
for (typ, name), items in byname.items():
    if typ != "关系":
        continue
    parts = [p.strip() for p in re.split(r"[—－\-–]", name) if p.strip()]
    if len(parts) != 2:
        continue
    a, b = CANON.get(("人物", parts[0]), parts[0]), CANON.get(("人物", parts[1]), parts[1])
    if a not in charset or b not in charset:
        continue
    relnames[name] = items
    slug = f"关系/{a}—{b}"
    lead = pick_lead(items)
    inf = {"类型": "关系", "双方": f"{a}、{b}", "笔记": f"{len(items)} 条"}
    add_page(slug, "关系", f"{a}—{b}", lead, inf, sections_for(items, "人物"),
             ["关系", a, b], len(items), chapters_of(items),
             facet="人物关系", facet2="双方关系")
    links.append((slug, f"人物/{a}", "当事", ""))
    links.append((slug, f"人物/{b}", "当事", ""))

# ---------- 事件编号：同名事件合并 ----------
# 已在上面按 (事件,name) 合并，事件重名极少，保留即可。

# ---------- 场景页 ----------
_TL = {"main": "继续", "branch": "分支", "ending": "结局", "map": "回地图",
       "story": "转段", "travel": "赶路", "temp": "临时", "scene": "转场"}
for script, sc in scenes.items():
    if (sc.get("lines") or 0) <= 0:
        _slug = f"场景/{script}"
        _nxt, _rows = [], []
        try:
            for _d, _ty in c.execute("select dst,type from scene_edges where src=? order by type, dst", (script,)):
                _t = scenes.get(_d, {}).get("title") or _d
                _rows.append({"note": _TL.get(_ty, _ty) + "：" + _t, "quote": "",
                              "script": _d if _d in scenes else "", "title": _t,
                              "seq": 0, "routes": []})
                if not _nxt and _d in scenes and (scenes[_d].get("lines") or 0) > 0:
                    _nxt.append(_t)
        except Exception:
            pass
        _in = []
        try:
            for (_s0,) in c.execute("select src from scene_edges where dst=? order by src", (script,)):
                _t = scenes.get(_s0, {}).get("title") or _s0
                _in.append({"note": _t, "quote": "", "script": _s0 if _s0 in scenes else "",
                            "title": _t, "seq": 0, "routes": []})
        except Exception:
            pass
        if _nxt and re.match(r'^转场[：:]?\s*(?:接)?\s*[A-Za-z0-9_]+$', _nxt[0]):
            _nxt[0] = "下一程"
        if _nxt:
            _nm = "转场节点·接「%s」" % _nxt[0]
        elif _in:
            _inm = _in[0]["title"] or ""
            if re.match(r'^转场[：:]?\s*(?:接)?\s*[A-Za-z0-9_]+$', _inm):
                _inm = "上一程"
            _nm = "转场节点·「%s」之后" % _inm
        else:
            _nm = "转场节点 " + script
        _secs = [{"h": "场景信息",
                  "html": "转场节点（本场无台词，不涉及场所）。" + arc_of(script) + "。"}]
        if _rows:
            _secs.append({"h": "接下来", "rows": _rows})
        if _in:
            _secs.append({"h": "被指向", "rows": _in})
        _lk0 = LOCKED.get(script)
        if _lk0:
            _secs.append({"h": "不可达内容（已封锁）", "rows": [
                {"note": "%s「%s」：%s" % (_it.get("kind") or "内容", _it.get("text") or "",
                                         _it.get("reason") or ""),
                 "quote": _it.get("evidence") or "", "script": "", "title": "",
                 "seq": 0, "routes": []} for _it in _lk0]})
        add_page(_slug, "场景", _nm,
                 "本场没有台词，是剧本之间的转场与判定节点，只做跳转与开关设置。",
                 {"脚本": script, "阶段": arc_of(script), "类型": "转场节点",
                  "剧情单元": BLOCK_OF.get(script, "")},
                 _secs, ["场景", arc_of(script)], 0, [arc_of(script)],
                 sort_key=script, facet=arc_of(script), facet2=role_of(script))
        continue
    slug = f"场景/{script}"
    rows = c.execute("select seq,speaker,text from lines where script=? order by seq", (script,)).fetchall()
    parts = collections.Counter()
    for seq, sp, tx in rows:
        if sp and sp != "旁白":
            parts[sp] += 1
    br = c.execute("""select seq,kind,idx,text,cond,flags,scenes from branch_nodes
                      where script=? order by seq,idx""", (script,)).fetchall()
    choices = []
    _seen_ch = set()
    for seq, kind, idx, text, cond, fl, scn in br:
        _ck = (seq, (text or "").strip(), idx)
        if _ck in _seen_ch:
            continue
        _seen_ch.add(_ck)
        choices.append({"seq": seq, "kind": kind, "idx": idx, "text": text,
                        "cond": pretty_cond(cond), "flags": json.loads(fl or "[]"),
                        "scenes": json.loads(scn or "[]")})
    pv, _pv_ev = place_of(script)
    if pv and pv not in placeset:
        pv = pv + "（势力驻地）"
    secs = [{"h": "场景信息",
             "html": f"{arc_of(script)}"
                     + (f"（{time_label(script)}）" if time_label(script) else "")
                     + f"，共 {sc.get('lines')} 句。"
                     + (f"地点：{pv}" + (f"（依据：{_pv_ev}）" if _pv_ev else "") + "。"
                        if pv else ("地点：转场节点（本场无台词，不涉及场所）。"
                                    if (sc.get("lines") or 0) <= 0
                                    else "地点：未证（正文未指明具体场所）。"))}]
    if PLACE_NOTE.get(script):
        secs[0]["html"] += f"场景性质：{PLACE_NOTE[script]}。"
    if parts:
        secs.append({"h": "出场人物", "people": [{"name": p, "n": n} for p, n in parts.most_common(14)]})
    if choices:
        secs.append({"h": "分支与后果", "choices": choices})
    scond = SCONDS.get(script) or []
    if scond:
        _sw_rows, _one_rows = [], []
        for x in scond:
            _cid = x.get("id") or ""
            _info = COND_LIB.get(_cid) or {}
            _attrs = [a for a in (_info.get("attrs") or []) if a]
            if (_info.get("kind") or "") == "switch" and len(_attrs) > 1:
                _sw_rows.append({
                    "note": "分支判定 %s（按结果走不同剧情，只会发生其中一条）：%s"
                            % (_cid, "；".join("%d）%s" % (i + 1, a) for i, a in enumerate(_attrs))),
                    "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
            else:
                _one_rows.append({
                    "note": (x.get("text") or "") + "　（" + _cid + "）",
                    "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
        _rows_sc = []
        if _sw_rows:
            _rows_sc.append({
                "note": "以下「分支判定」是本场内部的岔口：按战斗或选择的结果分走不同剧情，"
                        "并非要求全部条件同时成立；主线不因它改变，只替换对应的台词与出场人物。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
            _rows_sc += _sw_rows
        if _one_rows:
            _rows_sc.append({
                "note": "以下单条判定只影响场内个别台词或小分支，无法逐条对应到具体句子，仅作存档与复盘参考。",
                "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
            _rows_sc += _one_rows
        secs.append({"h": "本场判定", "rows": _rows_sc})
    _pre0 = EVENT_PRE.get(script)
    if _pre0:
        secs.append({"h": "前置触发", "rows": [
            {"note": _pre0.get("text") or "", "quote": _pre0.get("basis") or "",
             "script": "", "title": "", "seq": 0, "routes": []}]})
    _lk = LOCKED.get(script)
    if _lk:
        _lrows = []
        for _it in _lk:
            _lrows.append({
                "note": "%s「%s」：%s" % (_it.get("kind") or "内容", _it.get("text") or "",
                                     _it.get("reason") or ""),
                "quote": _it.get("evidence") or "", "script": "", "title": "",
                "seq": 0, "routes": []})
        secs.append({"h": "不可达内容（已封锁）", "rows": _lrows})
    _cr = chain_rows(script)
    _segid = SEGOF.get(script) or ""
    if _segid:
        _cr = [{"note": "", "title": "剧情段 %s：%s" % (_segid, (SEGMAP.get(_segid, {}) or {}).get("title", "")),
                "slug": "剧情段/" + _segid, "quote": "", "script": "", "seq": 0, "routes": []}] + _cr
    if _cr:
        secs.append({"h": "剧情衔接", "rows": _cr})
    _jrows = []
    _seen_dst = set()
    _TYPE_LABEL = {"main": "继续", "branch": "分支", "ending": "结局", "map": "回地图",
                   "story": "转段", "travel": "赶路", "temp": "临时"}
    try:
        for _r in c.execute("""select dst,type,cond,switch,result,site,line from scene_edges
                               where src=? order by type, site, result""", (script,)):
            _dst, _ty, _cond, _sw, _res, _site, _ln = _r
            if _ty in ("main", "branch") and _dst not in scenes:
                continue
            _key = (_ty, _dst)
            if _key in _seen_dst:
                continue
            _seen_dst.add(_key)
            _title = scenes.get(_dst, {}).get("title") or ""
            _bl0 = "" if _dst.startswith(("Combat", "Battle")) else battle_label(_sw, _res, script)
            if _bl0:
                _lab = _bl0 + "：" + (_title or _dst)
            elif _ty == "ending":
                _lab = "结局：GameOver（战败或剧情终止）"
            elif _ty == "map":
                _lab = "回地图（养成界面）"
            elif _dst.startswith(("Combat", "Battle")):
                _blv2 = BATTLE_LV.get("%s|%s" % (script, _ln)) or {}
                _lab = "战斗：" + (_blv2.get("desc") or (("关卡 " + _blv2["id"]) if _blv2.get("id") else _dst))
            elif _dst == "Free":
                _lab = "回养成地图（自由行动）"
            elif _ty in ("main", "branch", "story", "travel", "temp", "scene"):
                _lab = _TYPE_LABEL.get(_ty, _ty) + "：" + (_title or _dst)
                if _ty == "branch":
                    _bl = battle_label(_sw, _res, script)
                    if _bl:
                        _lab = _bl + "：" + (_title or _dst)
                if _ty == "branch" and not battle_label(_sw, _res, script):
                    _bits = []
                    if _sw:
                        _bits.append("判定 %s 结果 %s" % (_sw, _res))
                    if _cond:
                        _bits.append(_cond.replace("switch", "判定")
                                     .replace("_result==", " 结果=")[:80])
                    if _bits:
                        _lab += "（" + "；".join(_bits) + "）"
            else:
                _lab = _ty + "：" + (_title or _dst)
            _jrows.append({"note": _lab, "quote": "",
                           "script": _dst if _dst in scenes else "",
                           "title": _title, "seq": 0, "routes": []})
            if len(_jrows) >= 12:
                break
    except Exception as _e:
        pass
    if not _jrows:
        _jrows.append({"note": "本场没有出向转场，结束后由上层事件或地图接续。",
                       "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
    secs.append({"h": "接下来", "rows": _jrows})
    _cl = CLUSTER_MAP.get(script)
    if _cl:
        _mem = _cl.get("all") or [{"cluster": _cl.get("cluster"), "alt": _cl.get("alt"),
                                   "n": _cl.get("n"), "results": _cl.get("results")}]
        _rows_c = []
        _pre = {}
        for _m in _mem:
            _cc = CLUSTER_BY_ID.get(_m.get("cluster")) or {}
            if not _cc:
                continue
            _s0 = (_cc.get("switch") or "", _m.get("alt"), len(_cc.get("alts") or []))
            _pre[_s0] = _pre.get(_s0, 0) + 1
        _sig_seen = set()
        for _k, _m in enumerate(_mem):
            _c = CLUSTER_BY_ID.get(_m.get("cluster")) or {}
            if not _c:
                continue
            _sig = (_c.get("switch") or "", _m.get("alt"), len(_c.get("alts") or []))
            if _sig in _sig_seen:
                continue
            _sig_seen.add(_sig)
            _dup = _pre.get(_sig, 1) - 1
            _st = scenes.get(_c.get("src"), {}).get("title") or _c.get("src") or ""
            _head = ("本场属于「%s」判定 %s 的第 %s 路（结果 %s），与下列路线互斥，一次只走一条。"
                     % (_st, _c.get("switch") or "", _m.get("alt"),
                        "/".join(_m.get("results") or [])))
            if _k > 0 or _dup > 0:
                _head = "其中还嵌套一组分支：「%s」判定 %s，本场在第 %s 路（结果 %s）。" % (
                    _st, _c.get("switch") or "", _m.get("alt"), "/".join(_m.get("results") or []))
                if _dup > 0:
                    _head += "另有 %d 处同型分支点也指向这条路（来自不同前场）。" % _dup
            _rows_c.append({"note": _head, "quote": "", "script": "", "title": "",
                            "seq": 0, "routes": []})
            for _i, _alt in enumerate(_c.get("alts") or [], 1):
                if _i == _m.get("alt"):
                    continue
                _t = scenes.get(_alt.get("entry"), {}).get("title") or _alt.get("entry")
                _tail = "（该路超长，仅列到 400 场）" if _alt.get("truncated") else ""
                _rows_c.append({"note": "另一路（结果 %s）：%s　共 %d 场%s"
                                        % ("/".join(_alt.get("results") or []), _t,
                                           len(_alt.get("scenes") or []), _tail),
                                "quote": "", "script": _alt.get("entry"), "title": _t,
                                "seq": 0, "routes": []})
        if _rows_c:
            secs.append({"h": "择一分支", "rows": _rows_c})
    routes = routes_of(script)
    inf = {"脚本": script, "阶段": arc_of(script)}
    if BLOCK_OF.get(script):
        inf["剧情单元"] = BLOCK_OF[script]
    _tl = time_label(script)
    if _tl:
        st = STIME.get(script) or ()
        inf["时间"] = _tl + ((f"（{st[3]}）" if len(st) > 3 and st[3] else ""))
    _vf = _VAR_FLAGS.get(script) or set()
    _vlab = [ROUTE_LABEL[k] for k in ROUTE_LABEL if k in _vf]
    if routes:
        if script in _VAR_FLAGS and _vlab:
            inf["路线变体"] = "、".join(_vlab) + "（本场台词按攻略对象替换，主线不变）"
        else:
            inf["所属路线"] = "、".join(routes)
    elif _vlab:
        inf["路线变体"] = "、".join(_vlab) + "（本场台词按攻略对象替换，主线不变）"
    _lead = ("%s阶段%s的剧情场景，共 %d 句" % (arc_of(script), ("、位于" + pv if pv else ""), sc.get("lines") or 0))
    if arc_of(script) == "不限时间":
        _lead = "时间不限%s的剧情场景，共 %d 句" % (("、位于" + pv) if pv else "", sc.get("lines") or 0)
    if parts:
        _top = [p for p, _n in parts.most_common(3)]
        _lead += "，出场：" + "、".join(_top)
    _lead += "。"
    if not (sc.get("lines") or 0):
        _lead = "本场是转场脚本（切镜、地图移动或存档），没有台词。" + _lead
    if script in DREAM:
        _dm = DREAM[script] or {}
        inf["性质"] = "梦境"
        _lead = "本场是梦境，不是现实中发生的事。" + _lead
        secs.insert(0, {"h": "梦境提示",
                        "html": "原文依据：「%s」" % (_dm.get("quote") or "")})
    _bo = BRANCH_OPT.get(script)
    if _bo:
        _brows = []
        for _g in _bo.get("groups") or []:
            if _g.get("prompt"):
                _brows.append({"note": "【本题】" + _g["prompt"][:110], "quote": "",
                               "script": "", "title": "", "seq": 0, "routes": []})
            for _o in _g.get("options") or []:
                _tgt = _o.get("next") or ""
                _note = "「%s」" % _o["text"]
                if _o.get("cond"):
                    _note += "　条件：" + _o["cond"]
                if _o.get("effects"):
                    _note += "　影响：" + stat_cn("、".join(_o["effects"]))
                if _o.get("note"):
                    _note += "　" + _o["note"]
                if not _tgt:
                    _note += "　（去向未定）"
                _brows.append({"note": _note, "quote": "",
                               "script": _tgt,
                               "title": ((scenes.get(_tgt) or {}).get("title") or _tgt) if _tgt else "",
                               "seq": 0, "routes": []})
        if _brows:
            secs.append({"h": "分支选项", "rows": _brows})

    add_page(slug, "场景", noz(sc.get("title") or script), _lead, inf, secs,
             ["场景", arc_of(script)],
             sc.get("lines") or 0, [arc_of(script)],
             sort_key=script, facet=arc_of(script), facet2=role_of(script))
    for p, n in parts.most_common(14):
        if p in charset:
            links.append((slug, f"人物/{p}", "出场", str(n)))
            links.append((f"人物/{p}", slug, "出场场景", noz(sc.get("title") or script)))

# ---------- 路线页 ----------
try:
    for rid, key, kind, flag, val, summary, entry, beats, fates, gcount, gated, sets in \
            c.execute("""select id,key,kind,flag,value,summary,entry,beats,fates,
                                gated_count,gated,set_points from routes"""):
        slug = f"路线/{key}"
        inf = {"类型": kind}
        if flag:
            inf["旗标"] = flag + (f" = {val}" if val is not None else "")
        inf["专属场景"] = f"{gcount} 场"
        secs = [{"h": "路线概述", "html": summary},
                {"h": "进入条件", "html": entry}]
        beats_l = json.loads(beats or "[]")
        if beats_l:
            secs.append({"h": "关键节点", "rows": [{"note": b, "quote": "", "script": "",
                                                    "title": "", "seq": 0, "routes": []}
                                                   for b in beats_l]})
        fates_l = json.loads(fates or "[]")
        if fates_l:
            secs.append({"h": "角色去向", "rows": [{"note": f, "quote": "", "script": "",
                                                    "title": "", "seq": 0, "routes": []}
                                                   for f in fates_l]})
        g = json.loads(gated or "[]")
        if g:
            secs.append({"h": "这条线才有的场景", "rows": [
                {"note": f"{arc_of(x['script'])}｜{x['title']}", "quote": "", "script": x["script"],
                 "title": x["title"], "seq": 0, "routes": []} for x in g]})
        add_page(slug, "路线", key, summary, inf, secs, ["路线", kind], gcount, [],
                 facet="路线", facet2=kind)
        if kind == "感情线":
            links.append((slug, f"人物/{key}", "路线主角", ""))
        for x in g[:8]:
            links.append((slug, f"场景/{x['script']}", "专属场景", x["title"]))
except Exception as e:
    print("路线页跳过:", e)

# ---------- 结局页：终章按条件拼尾声 ----------
try:
    ends = c.execute("select condition,chain,n,seq,sample,text from endings order by seq").fetchall()
    if ends:
        rows = []
        for cond, chain, n, seq, sample, text in ends:
            if n < 2:
                continue
            sm = json.loads(sample or "[]")
            first = sm[0]["text"] if sm else ""
            rows.append({"note": f"条件：{cond[:70]}", "quote": first[:90],
                         "script": "ch8_8_1", "title": "终章", "seq": seq, "routes": []})
        secs = [{"h": "结局怎么构成",
                 "html": "本作没有独立的结局场景。终章《小竹的愿望》是一场 347 句的长尾声，"
                         "用条件判断把几十段后话拼在一起：谁活着、谁死了、赵活娶了谁、"
                         "唐门是否还在、瑞笙是敌是友，各自对应不同的段落。"
                         "所以下面每一条都是「在什么条件下，故事会这样收尾」，"
                         "而不是同时发生的多段剧情。"},
                {"h": "按条件分段的尾声", "rows": rows}]
        add_page("结局/终章", "结局", "终章",
                 "东西武林决战眉山之后，各人的后话按旗标分段落展开。",
                 {"类型": "结局", "段落": f"{len(rows)} 段", "场景": "ch8_8_1"},
                 secs, ["结局", "第8章"], len(rows), ["第8章"], sort_key="ch8_8_1")
        links.append(("结局/终章", "场景/ch8_8_1", "正文", "终章原文"))
except Exception as e:
    print("结局页跳过:", e)

# ---------- 词条页：物品 / 武学 / 装备 / 天赋 / 成就 / 设施 / 战斗角色 / 战斗效果 ----------
NS_TYPE = {"ItemBook_zh-cn": "武学", "ItemSpecial_zh-cn": "物品", "ItemMisc_zh-cn": "物品",
           "Equipment_zh-cn": "装备", "BattleSkill_zh-cn": "战技", "Talent_zh-cn": "天赋",
           "Library_zh-cn": "成就", "CombatEffects_zh-cn": "战斗效果",
           "Facility_zh-cn": "设施", "CombatCharacter_zh-cn": "战斗角色"}
try:
    existing = {p[0] for p in pages}
    for ns, eid, title, body in c.execute("select ns,eid,title,body from entries"):
        typ = NS_TYPE.get(ns)
        if not typ or not title:
            continue
        # 格式串残名（如「+{0:0}两」）不是真实词条，跳过
        if "{" in title:
            continue
        slug = f"{typ}/{title}"
        if slug in existing:
            continue
        txt = (body or "").replace("\\n", "\n").strip()
        if txt == title:
            txt = ""
        lead = ""
        if txt:
            _ls = [x.strip() for x in txt.split("\n") if x.strip()]
            _tag = ""
            if _ls and _ls[0].startswith("[") and _ls[0].endswith("]"):
                _tag = _ls[0]
                _ls = _ls[1:]
            _b0 = _ls[0] if _ls else ""
            # 说明常被 <br> 拆成多行，拼到够长为止，避免导语断在顿号上
            _acc = _b0
            _k0 = 1
            while len(_acc) < 30 and _k0 < len(_ls):
                _acc += _ls[_k0]
                _k0 += 1
            lead = (("%s %s" % (_tag, _acc)).strip() if _acc else _tag) or title
            lead = lead[:78]
        secs = [{"h": "说明", "html": txt.replace("\n", "<br>") if txt else "（游戏内无说明）"}]
        if not txt:
            _ex = []
            try:
                for _s, _sp, _tx in c.execute(
                        "select script,coalesce(speaker,''),text from lines where text like ? limit 20",
                        ("%" + title + "%",)):
                    _ex.append({"note": (_tx or "")[:100], "quote": "", "script": _s,
                                "title": scenes.get(_s, {}).get("title") or _s, "seq": 0, "routes": []})
                    if len(_ex) >= 5:
                        break
            except Exception:
                _ex = []
            if _ex:
                secs.append({"h": "原文摘录", "rows": _ex})
                lead = "游戏内未给出说明的%s，原文中提到 %d 处，具体见原文摘录。" % (typ, len(_ex))
            else:
                lead = "游戏内未给出说明的%s词条。" % typ
        add_page(slug, typ, title, lead, {"类型": typ, "编号": eid}, secs, [typ], 0, [],
                 facet=("有说明" if txt else "只有原文"))
        existing.add(slug)
        if typ == "武学":
            links.append((slug, "分类/武学", "分类", ""))
except Exception as e:
    print("词条页跳过:", e)

# ---------- 时间线页 ----------
try:
    tl_rows = c.execute("""select script,ord,bucket,chapter,time_label,title
                          from scene_order order by ord""").fetchall()
    by_ch = collections.OrderedDict()
    for script, od, b, ch, tl, title in tl_rows:
        by_ch.setdefault(arc_of(script), []).append(
            {"script": script, "ord": od, "time": tl or "", "title": title or script})
    by_ch = collections.OrderedDict(
        (k, by_ch[k]) for k in sorted(by_ch, key=lambda x: ARC_ORDER.index(x) if x in ARC_ORDER else 99))

    def first_note(script):
        r = c.execute("""select note from notes where script=? and type='事件'
                        order by seq_from limit 1""", (script,)).fetchone()
        return (r[0] if r else "")[:80]

    ov = []
    for ch, arr in by_ch.items():
        slug = f"时间线/{ch}"
        rows = [{"note": it["title"] + (f"（{it['time']}）" if it["time"] else ""),
                 "quote": first_note(it["script"]), "script": it["script"],
                 "title": it["title"], "seq": 0,
                 "routes": routes_of(it["script"])} for it in arr]
        add_page(slug, "时间线", ch,
                 f"{ch}按剧情先后排的 {len(arr)} 场。",
                 {"类型": "时间线", "场景": f"{len(arr)} 场"},
                 [{"h": f"{ch}·场景顺序", "rows": rows}],
                 ["时间线", ch], len(arr), [ch],
                 sort_key=f"{arr[0]['ord']:06d}", facet="时间线", facet2=ch)
        for it in arr[:60]:
            links.append((slug, f"场景/{it['script']}", "场景", it["title"]))
        ov.append({"note": f"{ch}（{len(arr)} 场）",
                   "quote": "　".join(x["title"] for x in arr[:5]),
                   "script": arr[0]["script"], "title": f"{ch}时间线", "seq": 0,
                   "routes": []})
    add_page("时间线/总览", "时间线", "总览",
             "全部 2,146 场按剧情阶段分块、块内按旗标依赖与脚本序排出的先后。",
             {"类型": "时间线", "阶段": f"{len(by_ch)} 段"},
             [{"h": "阶段", "rows": ov}], ["时间线"], len(by_ch), [],
             facet="时间线", facet2="总览")
    for ch in by_ch:
        links.append(("时间线/总览", f"时间线/{ch}", "阶段", ch))

    # 按年月汇总（攻略标注了时间的场景）
    _ym = collections.defaultdict(list)
    _xord = {"上旬": 0, "中旬": 1, "下旬": 2}
    for s, y, m, x in c.execute("select script,year,month,xun from scene_time"):
        if y and m and x:
            _ym[(int(y), int(m))].append((_xord.get(x, 3), x, s))
    if _ym:
        _secs = []
        for (y, m) in sorted(_ym):
            _rows = []
            for _o, x, s in sorted(_ym[(y, m)]):
                t = scenes.get(s, {}).get("title") or s
                _rows.append({"note": "%s｜%s" % (x, t), "quote": "", "script": s,
                              "title": t, "seq": 0, "routes": []})
            _secs.append({"h": "第%d年%d月" % (y, m), "rows": _rows})
        add_page("时间线/按年月", "时间线", "按年月",
                 "把攻略标注了年月的 %d 场剧情按月排开，看得到每个月发生了哪些事。" %
                 sum(len(v) for v in _ym.values()),
                 {"类型": "时间线", "月份": f"{len(_ym)} 个月"}, _secs, ["时间线"], 0, [],
                 facet="时间线", facet2="按年月")
        links.append(("时间线/总览", "时间线/按年月", "另一种看法", "按年月"))
except Exception as e:
    print("时间线页跳过:", e)

# ---------- 攻略年表（参考 wiki，已转简中） ----------
try:
    _cp = os.path.join(BASE, "data", "ref_wiki", "calendar.json")
    _CAL = json.load(open(_cp, encoding="utf-8")) if os.path.exists(_cp) else []
    if _CAL:
        _valid = {p[0] for p in pages}
        _bys = {}
        for _e in _CAL:
            _bys.setdefault(_e.get("year") or "未分年", {}).setdefault(_e.get("month") or "", []).append(_e)
        _secs = []
        for _y, _ms in _bys.items():
            _rows = []
            for _m, _es in _ms.items():
                for _e in _es:
                    _nm = _e.get("name") or ""
                    _hit = ("事件/" + _nm) in _valid
                    _rows.append({"note": "%s%s旬：%s%s" % (
                                    _m, _e.get("xun") or "", _nm,
                                    "" if _hit else "（参考条目，本库无同名事件）"),
                                  "quote": "", "script": "",
                                  "title": (_nm if _hit else ""),
                                  "slug": (("事件/" + _nm) if _hit else ""),
                                  "seq": 0, "routes": []})
            _secs.append({"h": _y, "rows": _rows})
        add_page("时间线/攻略年表", "时间线", "攻略年表（参考）",
                 "攻略资料整理的主支线日程，按年、月、旬排列，共 %d 条；繁体原文已转成简体。" % len(_CAL),
                 {"类型": "时间线", "条目": str(len(_CAL))}, _secs, ["时间线"], len(_CAL), [])
        links.append(("时间线/总览", "时间线/攻略年表", "另一种看法", "攻略年表"))
except Exception as e:
    print("攻略年表跳过:", e)

# ---------- 世界观总览（主页） ----------
try:
    wv = json.load(open(os.path.join(BASE, "data", "worldview.json"), encoding="utf-8"))
    slug = "世界观/总览"
    lead = wv.get("text") or ""
    secs = [{"h": s["h"], "html": s.get("html") or ""} for s in (wv.get("sections") or [])]
    if wv.get("footnotes"):
        secs.append({"h": "脚注", "rows": footnote_rows(slug, wv)})
    add_page(slug, "世界观", "世界观总览", lead, {"类型": "世界观"}, secs, ["世界观"], 0, [])
except Exception as e:
    print("世界观页跳过:", e)

# ---------- 写库 ----------
for _a, _t in CMERGE.items():
    redirects.append((f"人物/{_a}", f"人物/{_t}"))
    redirects.append((_a, f"人物/{_t}"))
for _n in _FACNAMES:
    redirects.append((f"人物/{_n}", f"势力/{_n}"))
    redirects.append((_n, f"势力/{_n}"))
for _a, _t in FMERGE.items():
    redirects.append((f"势力/{_a}", f"势力/{_t}"))
    redirects.append((_a, f"势力/{_t}"))
for _a, _t in PMERGE.items():
    redirects.append((f"地点/{_a}", f"地点/{_t}"))
    redirects.append((_a, f"地点/{_t}"))
# ---------- 数值页（属性判定阈值） ----------
try:
    _stp = os.path.join(BASE, "data", "stats.json")
    if os.path.exists(_stp):
        _st = json.load(open(_stp, encoding="utf-8"))
        def _disp(nm):
            if nm.startswith("好感度_"):
                return nm[4:] + "好感"
            if nm.startswith("技能_"):
                return nm[3:]
            if nm.startswith("数值_"):
                return nm[3:]
            return nm
        _rows_sum = []
        def _nice(tx):
            tx = re.sub(r"好感度_([^\s≤≥＜＞=<>]+)", r"\1好感", tx)
            tx = re.sub(r"技能_([^\s≤≥＜＞=<>]+)", r"\1", tx)
            tx = re.sub(r"数值_([^\s≤≥＜＞=<>]+)", r"\1", tx)
            return tx
        for _nm, _lst in sorted(_st.items(), key=lambda x: -len(x[1])):
            _dispnm = _disp(_nm)
            _reqs = collections.Counter(_nice(x["req"]) for x in _lst)
            _titles = {}
            for x in _lst:
                if x["script"] and x["script"] not in _titles:
                    _titles[x["script"]] = scenes.get(x["script"], {}).get("title") or x["script"]
            _top = [{"note": "%s（%d 处）" % (r, n), "quote": "", "script": "",
                     "title": "", "seq": 0, "routes": []} for r, n in _reqs.most_common(10)]
            _secs = [{"h": "常见判定门槛", "rows": _top}]
            _ex = [{"note": t, "quote": "", "script": s, "title": t, "seq": 0, "routes": []}
                   for s, t in list(_titles.items())[:10]]
            if _ex:
                _secs.append({"h": "出现在哪些场景", "rows": _ex})
            add_page("数值/" + _nm, "数值", _dispnm,
                     "%s在剧本中共有 %d 处判定，最常见的门槛是%s。" % (
                         _dispnm, len(_lst), "、".join(r for r, _ in _reqs.most_common(3))),
                     {"类型": "数值", "判定处数": str(len(_lst))}, _secs,
                     ["数值"], len(_lst), [],
                     facet=("好感" if _nm.startswith("好感度_") else
                            "技能" if _nm.startswith("技能_") else "属性"))
            if _nm.startswith("好感度_"):
                _cp = "人物/" + _nm[4:]
                if any(p[0] == _cp for p in pages):
                    links.append(("数值/" + _nm, _cp, "关联人物", ""))
                    links.append((_cp, "数值/" + _nm, "好感判定", ""))
            _rows_sum.append({"note": "%s（%d 处）" % (_dispnm, len(_lst)), "quote": "",
                              "script": "", "title": "", "seq": 0, "routes": []})
        if _rows_sum:
            add_page("数值/总览", "数值", "数值总览",
                     "剧本里被用作判定的全部数值与技能，按判定次数排序。",
                     {"类型": "数值总览", "条目": str(len(_rows_sum))},
                     [{"h": "全部数值", "rows": _rows_sum}], ["数值"], len(_rows_sum), [])
            links.append(("数值/总览", "数值/道德", "示例", ""))
except Exception as e:
    print("数值页跳过:", e)

# ---------- 关于本站 ----------
try:
    _cnt = collections.Counter(p[1] for p in pages)
    _order = ["人物", "势力", "地点", "事件", "地图事件", "场景", "书物", "物品", "武学", "装备", "天赋", "成就", "战技", "战斗角色", "战斗效果", "设施", "路线", "时间线", "结局"]
    _rows = [{"note": "%s：%d 条" % (k, _cnt[k]), "quote": "", "script": "", "title": "", "seq": 0, "routes": []}
             for k in _order if _cnt.get(k)]
    _secs = [
        {"h": "这个站是什么",
         "html": "把《活侠传》的游戏原文拆成可查的条目：人物、势力、地点、事件、武学、物品与场景。"
                 "每条叙述都能点回具体场景，原文按句保留，不做转述改写。"},
        {"h": "收录规模", "rows": _rows},
        {"h": "数据从哪来",
         "html": "一、游戏本体：Unity 资源包里的剧本与文本资产，逐句解出，带入场景、人物、分支。"
                 "二、攻略资料：整理年月旬、触发条件、角色与事件脉络，作为游戏数据之外的第二来源。"
                 "三、判定库：咖啡伴侣（BepInEx 插件）内置的判定表，只用来把「Ch_6_2_1_003」这类编号"
                 "翻成「宋悲好感≥20」这样能读的要求，不参与任何剧情叙述。"},
        {"h": "页面上的标注怎么读",
         "html": "「时间」是攻略标注的剧情时间；「推断时间」是由上一场或地图事件时间窗推出来的，"
                 "条目里会写明依据。\n"
                 "「入境判定」是从上一场跳进来时必须满足的判定；「开场判定」是本场在台词开始前的检查。\n"
                 "「地图事件」是养成地图上随机刷出的事件，条件与基础概率取自游戏资源。\n"
                 "「原文摘录」是资源库里提到该条的句子，未经改写。"},
        {"h": "已知局限",
         "html": "一、地图事件只有 12 条带明确起始时间、25 条带结束时间，其余靠旗标控制，时间窗口无法给出。\n"
                 "二、25 个地图事件不唯一对应某场戏（赶路、章节随机、大门这类族），游戏里同一结果码按路线各自播出，"
                 "页面上改为列出同码剧本；其中 5 个正常结果只有提示文本、没有剧本。\n"
                 "三、「关闭条件」（哪个事件之后不再发生）仍在核验，未发布，避免误导。\n"
                 "四、地点 25 条、势力 15 条的简介仍写作「原文中出现 N 处」，因原文没有成段地理或组织描述，"
                 "暂保留原样，不用推测文字凑数。"},
    ]
    add_page("关于本站", "关于", "关于本站",
             "收录范围、数据来源、页面标注含义与已知局限。",
             {"类型": "关于", "页面": str(len(pages))}, _secs, ["关于"], 0, [])
except Exception as e:
    print("关于页跳过:", e)

# ---------- 分支选项（选项 → 结果） ----------
CB = CB or {}


# ---------- 梦境/幻境场景 ----------
# 选项文案 → 去向（补足 choice_branch 里缺失的 next）
BOPT_MAP = {}
try:
    for _bs, _bv in (BRANCH_OPT or {}).items():
        for _bg in _bv.get("groups") or []:
            for _bo in _bg.get("options") or []:
                if _bo.get("next"):
                    BOPT_MAP[(_bs, (_bo.get("text") or "").strip())] = _bo["next"]
except Exception as _e:
    print("选项去向表跳过:", _e)



SYS_NEXT_CN = {
    "Free": "养成地图（自由行动）",
    "Title": "标题画面",
    "Battle": "战斗",
    "Combat": "战斗",
    "End": "终章",
    "Story": "正篇",
    "GameOver": "游戏结束",
}


def next_cn(nx):
    return SYS_NEXT_CN.get(nx or "", (scenes.get(nx or "", {}) or {}).get("title") or (nx or ""))

def choice_rows(scs):
    out = []
    _seen_blk = set()
    for s in scs[:6]:
        _tm_blocks = TM.get(s) or []
        _tm_vars = {b.get("var") for b in _tm_blocks}
        _cbp = {b.get("var"): (b.get("prompt") or "") for b in (CB.get(s) or [])}
        for blk in (CB.get(s) or []):
            # 对话菜单交给下面的 TM 块（那边有解锁条件），不要重复列
            if blk.get("var") == "talk" and "talk" in _tm_vars:
                continue
            _bk = (s, blk.get("prompt") or "")
            if _bk in _seen_blk:
                continue
            _seen_blk.add(_bk)
            opts = []
            _ncond = 0
            for o in blk.get("options") or []:
                res = []
                if o.get("effects"):
                    res.append(stat_cn("、".join(o["effects"])))
                if o.get("result"):
                    pass
                if o.get("lines"):
                    res.append("「%s」" % (o["lines"][0].replace("\\n", " ")[:44]))
                _meta = OPTIDX.get(o.get("key") or "") or {}
                _nx = o.get("next") or _meta.get("next") or ""
                if not _nx:
                    _nx = BOPT_MAP.get((s, (o.get("text") or "").strip())) or ""
                _cd = (o.get("cond") or "").strip() or (_meta.get("cond") or "")
                if _nx in SYS_NEXT_CN:
                    res.append("选择后转往" + SYS_NEXT_CN[_nx])
                elif _nx:
                    _tail = "接着演「%s」" % (scenes.get(_nx, {}).get("title") or _nx)
                    if _nx == (NXT.get(s) or {}).get("next"):
                        _tail += "（接下一段）"
                    res.append(_tail)
                if _cd:
                    _ncond += 1
                opts.append({"text": o.get("text") or "",
                             "cond": _cd,
                             "result": stat_cn("；".join(res) or "—"),
                             "next": _nx,
                             "terminal": 1 if (_nx and _nx not in scenes) else 0,
                             "next_title": next_cn(_nx) if _nx else ""})
            if opts:
                out.append({"prompt": (blk.get("prompt") or "").replace("\\n", "\n"),
                            "script": s,
                            "scene": scenes.get(s, {}).get("title") or s,
                            "free": 0 if _ncond else 1,
                            "options": opts})
        # 对话/门事件/移动菜单：选项按条件出现，选中后有旗标变动与去向
        for blk in _tm_blocks:
            _v = blk.get("var") or ""
            if _v.startswith("option_"):
                continue          # choose(option_xxx) 已由 CB 富表渲染
            _bk = (s, _v)
            if _bk in _seen_blk:
                continue
            _seen_blk.add(_bk)
            opts = []
            _ncond = 0
            for o in blk.get("options") or []:
                res = []
                if o.get("effects"):
                    res.append("、".join(o["effects"]))
                _nx = o.get("next") or ""
                if _nx == "Title":
                    res.append("结束本段，回到标题")
                elif _nx and _nx == s:
                    res.append("选后回到本场")
                elif _nx:
                    _tail = "接着演「%s」" % (scenes.get(_nx, {}).get("title") or _nx)
                    if _nx == (NXT.get(s) or {}).get("next"):
                        _tail += "（接下一段）"
                    res.append(_tail)
                if o.get("cond"):
                    _ncond += 1
                opts.append({"text": o.get("text") or "",
                             "cond": o.get("cond") or "",
                             "result": "；".join(res) or "—",
                             "next": _nx,
                             "terminal": 1 if (_nx and _nx not in scenes) else 0,
                             "next_title": (("结束本段（回标题）" if _nx == "Title"
                                             else scenes.get(_nx, {}).get("title") or _nx)
                                            if _nx else "")})
            if opts:
                _lab = blk.get("label") or "菜单"
                if _lab in ("菜单", "对话菜单", "门事件菜单"):
                    _pos = blk.get("pos")
                    _up = (_cbp.get(_v) or "").replace("\\n", " ").strip()
                    _lab = ("上文「%s」→ " % _up[:42]) if _up else ""
                    _lab += "对话选项（%s%d 项可选%s，编号仅本场有效）" % (
                        ("本场第 %s 句，" % _pos) if _pos else "", len(opts),
                        ("，其中 %d 项需条件" % _ncond) if _ncond else "")
                out.append({"prompt": _lab,
                            "script": s,
                            "scene": scenes.get(s, {}).get("title") or s,
                            "free": 0 if _ncond else 1,
                            "options": opts})
    return out


if CB or DREAM or TM:
    _DREAM_EVENTS = set()
    for _dsc in (DREAM or {}):
        for _ev in (_SCENE_EVENTS.get(_dsc) or []):
            _DREAM_EVENTS.add(_ev)
    _np = []
    for _p in pages:
        (_slug, _typ, _nm, _lead, _inf, _secs, _cats, _mts, _ch, _sk, _ttl, _hid, _f1, _f2) = _p
        if _typ in ("事件", "场景"):
            try:
                _secs_l = json.loads(_secs)
            except Exception:
                _secs_l = []
            if _secs_l:
                _scs = []
                if _typ == "场景":
                    _own = _slug.split("/")[-1]
                    if _own in CB or _own in TM:
                        _scs = [_own]
                else:
                    # 事件页只取「发生场景」里的场，避免把整个事件集的所有选项都搬过来
                    _prim = []
                    for _s in _secs_l:
                        if _s.get("h") == "发生场景":
                            for _r in (_s.get("rows") or []):
                                _sc = _r.get("script") or ""
                                if _sc and _sc not in _prim:
                                    _prim.append(_sc)
                    if not _prim:
                        for _s in _secs_l[:2]:
                            for _r in (_s.get("rows") or []):
                                _sc = _r.get("script") or ""
                                if _sc and _sc not in _prim:
                                    _prim.append(_sc)
                    _scs = [x for x in _prim if (x in CB or x in TM)][:3]
                _cr = choice_rows(_scs)
                if _cr:
                    _secs_l.append({"h": "分支选项", "choice_rows": _cr})
                    # 选项已在「分支选项」表里逐条展开，旧的「分支与后果」只留掷骰行
                    for _s3 in _secs_l:
                        if _s3.get("h") == "分支与后果":
                            _s3["choices"] = [x for x in (_s3.get("choices") or [])
                                              if x.get("kind") != "choose"]
                    _secs_l = [x for x in _secs_l
                               if not (x.get("h") == "分支与后果" and not x.get("choices"))]
                    _secs = json.dumps(_secs_l, ensure_ascii=False)
            if _typ == "事件":
                _evn = _slug.split("/", 1)[-1]
                _secs_l = json.loads(_secs)
                if _evn in _DREAM_EVENTS:
                    _secs_l.insert(0, {"h": "梦境提示",
                                       "html": "本条事件发生在梦境/幻境里，不是现实中发生的事。"})
                _main = ""
                for _s in _secs_l:
                    for _r in (_s.get("rows") or []):
                        _sc2 = _r.get("script") or ""
                        if _sc2 in scenes and "_break" not in _sc2.lower():
                            _main = _sc2
                            break
                    if _main:
                        break
                if _main and not any(x.get("h") == "剧情衔接" for x in _secs_l):
                    _rows2 = chain_rows(_main)
                    if _rows2:
                        _secs_l.append({"h": "剧情衔接", "rows": _rows2})
                _secs = json.dumps(_secs_l, ensure_ascii=False)
        _np.append((_slug, _typ, _nm, _lead, _inf, _secs, _cats, _mts, _ch, _sk, _ttl, _hid, _f1, _f2))
    pages = _np

# 残留选项编号统一换成文案（结局页等处仍会引用 O_xxx）
OPTIDX.update({k: {"text": v, "cond": "", "next": "", "script": ""}
               for k, v in OPTXT.items() if k not in OPTIDX})

_RE_OKEY = re.compile(r"O_[A-Za-z0-9_]{4,}")


def _fix_keys(s):
    if not s or "O_" not in s:
        return s

    def _rep(m):
        k = m.group(0)
        return (OPTIDX.get(k) or {}).get("text") or k
    return _RE_OKEY.sub(_rep, s)


def _place_type(nm, lead):
    """地点类型：给筛选用的真实分类，不涉层级。"""
    t = (nm or "") + " " + (lead or "")
    if any(k in t for k in ("门派", "帮派", "世家", "分舵", "驻地")):
        return "势力驻地"
    if any(k in (nm or "") for k in ("山", "峰", "岭", "崖", "洞", "湖", "江", "河",
                                     "溪", "林", "谷", "泉", "池", "沙洲", "峡")):
        return "山川"
    if any(k in (nm or "") for k in ("寺", "观", "宫", "庙", "庵", "祠", "殿", "堂",
                                     "阁", "楼", "院", "斋", "轩", "亭", "塔")):
        return "寺院宫观"
    if any(k in (nm or "") for k in ("镇", "城", "村", "县", "州", "府", "市", "关",
                                     "渡", "铺", "街", "巷", "驿", "寨")):
        return "城镇"
    if any(k in (nm or "") for k in ("客栈", "酒家", "铺", "摊", "店", "医馆", "药堂",
                                     "作坊", "磨坊")):
        return "店铺"
    return "其他"


REGION_MAP = {'成都': '川蜀', '眉山': '川蜀', '绵州': '川蜀', '绵阳': '川蜀', '梓州': '川蜀', '乐山': '川蜀', '青城山': '川蜀', '峨嵋山': '川蜀', '剑门关': '川蜀', '昭化': '川蜀', '唐门': '川蜀', '岷江': '川蜀', '渡口': '川蜀', '泸沽湖': '川蜀', '大雪山': '川蜀', '剑庐': '川蜀', '剑圣故居': '川蜀', '夔州': '巴渝', '夔门': '巴渝', '白帝城遗迹': '巴渝', '朝天门': '巴渝', '江陵': '荆湖', '荆州': '荆湖', '襄阳': '荆湖', '枣阳': '荆湖', '岳阳': '荆湖', '长沙雨花亭': '荆湖', '静江': '荆湖', '风雨山': '荆湖', '锦香宫': '荆湖', '临安': '两浙淮南', '建康': '两浙淮南', '宣州孤云山': '两浙淮南', '宁国府': '两浙淮南', '安济坊': '两浙淮南', '汴京': '中原', '朱仙镇': '中原', '嵩山': '中原', '南嵩山寺': '中原', '南阳': '中原', '新野': '中原', '南阳杏花林': '中原', '华山': '关中陇右', '终南山': '关中陇右', '平凉': '关中陇右', '崆峒山': '关中陇右', '秦州': '关中陇右', '兴元府': '关中陇右', '西和州': '关中陇右', '大理': '西南夷', '点苍山': '西南夷', '天龙寺': '西南夷', '矩州': '西南夷', '福州': '闽越', '阴山': '塞外', '天山': '塞外', '长白山': '塞外', '金国': '塞外', '东瀛': '海外'}
PREFIX_REGION = (('唐门', '川蜀'), ('青城', '川蜀'), ('崆峒', '关中陇右'), ('江陵', '荆湖'), ('锦香宫', '荆湖'))

REGION_MAP.update({'川蜀': '川蜀', '山神龛': '川蜀', '石灰沱': '川蜀', '夔州巫山县衙大牢': '巴渝', '黄龙泉': '巴渝', '六道峡': '荆湖', '春雨楼': '荆湖', '谭州腾云山': '荆湖', '腾云寨': '荆湖', '锦绣轩': '荆湖', '香露池': '荆湖', '孟章厢房': '关中陇右', '监兵厢房': '关中陇右', '陵光厢房': '关中陇右', '插香台': '关中陇右', '朽木桥': '关中陇右', '般若院': '中原', '红岭': '中原', '梁家医馆': '中原', '松烟阁': '西南夷'})


def _region_of0(nm):
    """自身没登记就沿上级链回溯；都江客栈→青城山镇→青城山→川蜀。"""
    n = nm or ""
    seen = set()
    while n and n not in seen:
        seen.add(n)
        if n in REGION_MAP:
            return REGION_MAP[n]
        for pre, reg in PREFIX_REGION:
            if n.startswith(pre):
                return reg
        n = PPARENT.get(n) or ""
    return "其他"



def _region_of(nm):
    r = _region_of0(nm)
    if r == "巴渝":          # 巴渝并入川蜀
        r = "川蜀"
    r = PE_RENAME.get(r, r)
    return PE_REGION.get(nm, r)


CITY_NAMES = {"临安", "建康", "汴京", "江陵", "襄阳", "南阳", "平凉", "大理",
              "昭化", "枣阳", "新野", "成都", "绵州", "夔州", "兴元府", "眉山",
              "长沙", "岳阳", "静江", "岳州", "鄂州", "潭州"}


def _place_type2(nm, lead="", parent=""):
    """地点类型：城池 / 山川 / 街市店肆 / 寺院宫观 / 遗迹 / 牢狱 / 其他。"""
    n = nm or ""
    base = n.split("-")[-1]
    if base in PE_TYPE:
        return PE_TYPE[base]
    if base.endswith(("遗迹", "故居", "旧址", "遗址")):
        return "遗迹"
    if base.endswith(("大牢", "牢房", "狱", "牢")):
        return "牢狱"
    if base.endswith(("寺", "观", "庵", "祠", "庙")):
        return "寺院宫观"
    if base in CITY_NAMES or base.endswith(("府", "州", "县", "城", "郡", "镇")):
        return "城池"
    if base.endswith(("山", "峰", "岭", "河", "江", "湖", "泉", "池", "峡", "洞",
                      "谷", "溪", "林", "森林", "崖", "滩", "岗", "坡", "岛",
                      "沱", "洲", "潭", "原", "关", "渡", "口")):
        return "山川"
    if base.endswith(("楼", "铺", "舖", "摊", "巷", "阁", "肆", "客栈", "栈",
                      "市", "集", "店", "馆", "堂", "坊")):
        return "街市店肆"
    return "其他"

def _faction_type(nm):
    n = nm or ""
    if n.endswith("世家"):
        return "世家"
    if n.endswith("帮"):
        return "帮派"
    if n.endswith("分舵"):
        return "帮派"
    if n.endswith("教"):
        return "教门"
    if n.endswith("道") and not n.endswith("街道"):
        return "教门"
    if n.endswith(("派", "门", "剑阁", "阁", "楼", "宫", "寺", "观")):
        return "门派"
    if n.endswith(("盟", "会", "寨", "堡", "堂")):
        return "联盟组织"
    if n.endswith(("国", "朝")) or "朝廷" in n:
        return "政权"
    if n.endswith(("军", "部队", "义从", "厢军")):
        return "军镇"
    if n.endswith(("家", "氏", "宗")):
        return "世家"
    for _k in ("嵇山", "少林", "全真", "崆峒", "青城", "点苍", "峧嵋", "峧眉",
               "华山", "丐帮", "唐门", "锦香宫", "雪山"):
        if _k in n:
            return "门派"
    if n.endswith(("苑", "局", "司", "斋", "院", "社", "铺", "舖")):
        return "联盟组织"
    return "其他"


# 缺页的上级地点（岳阳/川蜀这类）补成条目，否则子级无处可挂
_valid_pl = {p[2] for p in pages if p[1] == "地点"}
_new_parents = []
for _k, _v in PPARENT.items():
    if _v and _v not in _valid_pl and _v not in _new_parents:
        _new_parents.append(_v)
for _nm2 in _new_parents:
    _kids = [k for k, v in PPARENT.items() if v == _nm2]
    _rows = [{"note": k, "quote": "", "script": "", "title": k, "seq": 0,
              "routes": []} for k in _kids]
    add_page(f"地点/{_nm2}", "地点", _nm2,
             f"{_nm2}，下辖：{'、'.join(_kids[:10])}。",
             {"类型": "地点", "下辖": f"{len(_kids)} 处"},
             [{"h": "下辖地点", "rows": _rows}], ["地点"], len(_kids), [],
             facet=(PPARENT.get(_nm2) or "其他"))
    _valid_pl.add(_nm2)

# 人工补建的地点（places_fix.json 的 extra：{"无羡居": {"parent": "江陵", "text": "..."}}）
for _pn, _pv in (P_FIX.get("extra") or {}).items():
    if f"地点/{_pn}" in {f"地点/{k}" for k in _valid_pl}:
        continue
    _pp2 = (_pv or {}).get("parent") or ""
    if _pp2:
        PPARENT.setdefault(_pn, _pp2)
    _pinf = {"类型": "地点"}
    if _pp2:
        _pinf["上级"] = _pp2
    _psecs = []
    if _pp2:
        _psecs.append({"h": "上级地点", "rows": [
            {"note": _pp2, "quote": "", "script": "", "title": _pp2, "seq": 0, "routes": []}]})
    add_page(f"地点/{_pn}", "地点", _pn, (_pv or {}).get("text") or "", _pinf, _psecs,
             ["地点"], 0, [], facet=(_pp2 or "其他"))
    _valid_pl.add(_pn)
    if _pp2:
        links.append((f"地点/{_pn}", f"地点/{_pp2}", "上级", ""))
        links.append((f"地点/{_pp2}", f"地点/{_pn}", "下级", _pn))

_pp = []
for _p in pages:
    (_slug, _typ, _nm, _lead, _inf, _secs, _cats, _mts, _ch, _sk, _ttl, _hid, _f1, _f2) = _p
    if "O_" in (_lead or "") or "O_" in (_secs or "") or _slug in _DEMO_PAGES or _typ in ("地点", "势力"):
        try:
            _S = json.loads(_secs or "[]")
        except Exception:
            _S = []
        for _s in _S:
            for _r in (_s.get("rows") or []):
                _r["note"] = _fix_keys(_r.get("note") or "")
            for _r in (_s.get("choices") or []):
                _r["text"] = _fix_keys(_r.get("text") or "")
        _lead = _fix_keys(_lead or "")
        if _typ == "势力":
            _f1 = _faction_type(_nm)
        if _typ == "地点":
            _kids2 = [k for k, v in PPARENT.items() if v == _nm]
            if _kids2 and "下辖：" not in _lead:
                _lead = (_lead + "　" if _lead else "") + "下辖：" + "、".join(_kids2[:10]) + "。"
            _par2 = PPARENT.get(_nm) or ""
            _rt2 = _nm
            _seen2 = set()
            while PPARENT.get(_rt2) and _rt2 not in _seen2:
                _seen2.add(_rt2)
                _rt2 = PPARENT[_rt2]
            _f1 = _region_of(_nm)
            _f2 = _place_type2(_nm, _lead, PPARENT.get(_nm))
            try:
                _in2 = json.loads(_inf or "{}")
            except Exception:
                _in2 = {}
            if _kids2:
                _in2["下辖"] = f"{len(_kids2)} 处"
            _inf = json.dumps(_in2, ensure_ascii=False)
        if _slug in _DEMO_PAGES and _DEMO_NOTE:
            if not any(_s.get("h") == "内容状态" for _s in _S):
                _S.insert(0, {"h": "内容状态", "html": _DEMO_NOTE})
            try:
                _cl = json.loads(_cats or "[]")
            except Exception:
                _cl = []
            if "Demo限定" not in _cl:
                _cl.append("Demo限定")
            _cats = json.dumps(_cl, ensure_ascii=False)
            try:
                _in = json.loads(_inf or "{}")
            except Exception:
                _in = {}
            _in["内容状态"] = "Demo 版限定（正式版无法触发）"
            _inf = json.dumps(_in, ensure_ascii=False)
        _p = (_slug, _typ, _nm, _lead, _inf, json.dumps(_S, ensure_ascii=False),
              _cats, _mts, _ch, _sk, _ttl, _hid, _f1, _f2)
    _pp.append(_p)
pages = _pp

# 大地图页：图与坐标由 src/export_map.py 生成到 web/map_nodes.json，前端渲染
_MAP_LEAD = ("大地图是游戏中往来各地的行程图：自唐门出发，经眉山、江陵、襄阳一线东行，"
             "西上青城、峨嵋，北上崆峒、大雪山、嵩山，南下点苍。图上红点为可前往之地，"
             "点开即进入该地条目；小点是途程节点，只作路线示意。")
pages.append(("地图/大地图", "地图", "大地图", _MAP_LEAD,
              json.dumps({"底图": "2880 × 2360", "标记点": "13 处"}, ensure_ascii=False),
              "[]", json.dumps(["地图"], ensure_ascii=False), 0, "[]", "", "", 0, "", ""))


# ===== 收尾：并义（同名地点/势力共用内容）+ 补指定子地点 =====
_MERGE_EQ = []


def _pj(v, d):
    try:
        return json.loads(v or d)
    except Exception:
        return json.loads(d)


_idx = {p[0]: i for i, p in enumerate(pages)}
for _p in list(pages):
    if _p[1] != "地点":
        continue
    _b = f"势力/{_p[2]}"
    if _b in _idx:
        _a = _p[0]
        _pa, _pb = pages[_idx[_a]], pages[_idx[_b]]
        _sa, _sb = _pj(_pa[5], "[]"), _pj(_pb[5], "[]")
        _have = {x.get("h") for x in _sa}
        _merged = _sa + [x for x in _sb if x.get("h") not in _have]
        _ia, _ib = _pj(_pa[4], "{}"), _pj(_pb[4], "{}")
        for _k2, _v2 in _ib.items():
            _ia.setdefault(_k2, _v2)
        _ia["性质"] = "兼为地点与势力"
        _cats = sorted(set(_pj(_pa[6], "[]")) | set(_pj(_pb[6], "[]")))
        _mj = json.dumps(_merged, ensure_ascii=False)
        _ij = json.dumps(_ia, ensure_ascii=False)
        _cj = json.dumps(_cats, ensure_ascii=False)
        _mt = max(_pa[7] or 0, _pb[7] or 0)
        for _i in (_idx[_a], _idx[_b]):
            _q = pages[_i]
            pages[_i] = (_q[0], _q[1], _q[2], _q[3], _ij, _mj, _cj, _mt,
                         _q[8], _q[9], _q[10], _q[11], _q[12], _q[13])
        links.append((_a, _b, "同义", ""))
        links.append((_b, _a, "同义", ""))
        _MERGE_EQ.append(_a.split("/")[-1])
print("并义条目", len(_MERGE_EQ), "：", "、".join(_MERGE_EQ[:12]))

# 导语补注（校订/tips）与隐藏区域页
if PE_TIP or PE_HIDE:
    for _i2, _q2 in enumerate(pages):
        _nm4 = _q2[2]
        if _q2[1] != "地点":
            continue
        _lead4 = _q2[3] or ""
        _tip4 = PE_TIP.get(_nm4)
        if _tip4 and _tip4 not in _lead4:
            _lead4 = (_lead4 + "\n\n" if _lead4 else "") + _tip4
        _hid4 = 1 if _nm4 in PE_HIDE else _q2[11]
        if _lead4 != (_q2[3] or "") or _hid4 != _q2[11]:
            pages[_i2] = (_q2[0], _q2[1], _q2[2], _lead4, _q2[4], _q2[5], _q2[6],
                          _q2[7], _q2[8], _q2[9], _q2[10], _hid4, _q2[12], _q2[13])
    print("导语补注", len(PE_TIP), "处；隐藏", len(PE_HIDE), "个区域页")

# 子级页面补齐「上级」字段（有些页由 extra/占位分支生成，没带上级）
_FIX_PARENT_INF = 0
for _i5, _q5 in enumerate(pages):
    if _q5[1] != "地点":
        continue
    _nm5 = _q5[2]
    _par5 = PPARENT.get(_nm5)
    if not _par5:
        continue
    _inf5 = _pj(_q5[4], "{}")
    if _inf5.get("上级") == _par5:
        continue
    _inf5["上级"] = _par5
    pages[_i5] = (_q5[0], _q5[1], _q5[2], _q5[3],
                  json.dumps(_inf5, ensure_ascii=False), _q5[5], _q5[6], _q5[7],
                  _q5[8], _q5[9], _q5[10], _q5[11], _q5[12], _q5[13])
    _FIX_PARENT_INF += 1
if _FIX_PARENT_INF:
    print("补上级字段", _FIX_PARENT_INF, "页")

# 简介整段覆盖（人工重写，不加括号注释）
_INTRO_APPLIED = 0
for _i6, _q6 in enumerate(pages):
    if _q6[1] != "地点":
        continue
    _new_lead = PE_INTRO.get(_q6[2])
    if _new_lead and _new_lead != _q6[3]:
        pages[_i6] = (_q6[0], _q6[1], _q6[2], _new_lead, _q6[4], _q6[5], _q6[6],
                      _q6[7], _q6[8], _q6[9], _q6[10], _q6[11], _q6[12], _q6[13])
        _INTRO_APPLIED += 1
if _INTRO_APPLIED:
    print("简介重写", _INTRO_APPLIED, "条")



# 改名后残留的旧页面：内容并入新页面，旧页删除并加重定向
_DEAD = set()
_RENAMED_DONE = []
for _o3, _n3 in (PE.get("rename") or {}).items():
    _so, _sn = f"地点/{_o3}", f"地点/{_n3}"
    if _so not in _idx or _sn not in _idx:
        continue
    _po, _pn = pages[_idx[_so]], pages[_idx[_sn]]
    _so_sec = _pj(_po[5], "[]")
    _sn_sec = _pj(_pn[5], "[]")
    _have2 = {x.get("h") for x in _sn_sec}
    _merged2 = _sn_sec + [x for x in _so_sec if x.get("h") not in _have2]
    _inf2 = _pj(_pn[4], "{}")
    for _k3, _v3 in _pj(_po[4], "{}").items():
        _inf2.setdefault(_k3, _v3)
    pages[_idx[_sn]] = (_pn[0], _pn[1], _pn[2],
                        _pn[3] or _po[3], json.dumps(_inf2, ensure_ascii=False),
                        json.dumps(_merged2, ensure_ascii=False), _pn[6],
                        max(_pn[7] or 0, _po[7] or 0), _pn[8], _pn[9], _pn[10],
                        _pn[11], _pn[12], _pn[13])
    _DEAD.add(_so)
    redirects.append((_so, _sn))
    _RENAMED_DONE.append(_o3)
if _RENAMED_DONE:
    print("改名并页", len(_RENAMED_DONE), "：", "、".join(_RENAMED_DONE))



# 指定补充的子地点（有出处、但原文没有成段描写，需要单独成页）
_EXTRA_PLACES = [
    ("眉山镇", "眉山", "眉山镇是眉山山下的镇市，唐门弟子下山采买、坊市街巷多聚于此。"),
]
PE_EXTRA_PLACES = [(x.get("name"), x.get("parent"), x.get("lead") or "")
                   for x in PE_NEW if x.get("name")]
_EXTRA_PLACES += PE_EXTRA_PLACES
for _nm3, _par3, _lead3 in _EXTRA_PLACES:
    _slug3 = f"地点/{_nm3}"
    if _slug3 in _idx:
        continue
    _pslug = f"地点/{_par3}"
    if _pslug in _idx:
        _pp2 = pages[_idx[_pslug]]
        _ps = _pj(_pp2[5], "[]")
        _row = {"note": _nm3, "quote": "", "script": "", "title": _nm3,
                "slug": _slug3, "seq": 0, "routes": []}
        for _s in _ps:
            if _s.get("h") == "下辖地点":
                _rows_s = _s.setdefault("rows", [])
                if not any((r.get("title") == _nm3 or r.get("slug") == _slug3) for r in _rows_s):
                    _rows_s.append(_row)
                break
        else:
            _ps.append({"h": "下辖地点", "rows": [_row]})
        _pi = _pj(_pp2[4], "{}")
        for _s in _ps:
            if _s.get("h") == "下辖地点":
                _pi["下辖"] = f"{len(_s.get('rows') or [])} 处"
                break
        pages[_idx[_pslug]] = (_pp2[0], _pp2[1], _pp2[2], _pp2[3],
                               json.dumps(_pi, ensure_ascii=False),
                               json.dumps(_ps, ensure_ascii=False),
                               _pp2[6], _pp2[7], _pp2[8], _pp2[9],
                               _pp2[10], _pp2[11], _pp2[12], _pp2[13])
        links.append((_slug3, _pslug, "上级", ""))
        links.append((_pslug, _slug3, "下级", _nm3))
    _scs3 = sorted(SCENES_BY_PLACE.get(_nm3, []), key=lambda x: ORDER.get(x, 99999))
    _inf3 = {"类型": "地点", "上级": _par3}
    _secs3 = []
    if _scs3:
        _inf3["场景"] = "%d 场" % len(_scs3)
        _secs3.append({"h": "发生场景", "rows": [
            {"note": scenes.get(_x3, {}).get("title") or _x3, "quote": "",
             "script": _x3, "title": scenes.get(_x3, {}).get("title") or _x3,
             "seq": 0, "routes": []} for _x3 in _scs3[:60]]})
    pages.append((_slug3, "地点", _nm3, _lead3,
                  json.dumps(_inf3, ensure_ascii=False),
                  json.dumps(_secs3, ensure_ascii=False), json.dumps(["地点"], ensure_ascii=False), 0, "[]",
                  "", "", 0, _region_of(_nm3), _place_type2(_nm3, _lead3, _par3)))
    _idx[_slug3] = len(pages) - 1
    print("新增地点页", _nm3, "→ 上级", _par3)

# 新增地点也套用人工简介
_INTRO2 = 0
for _i9, _q9 in enumerate(pages):
    if _q9[1] != "地点":
        continue
    _nl9 = PE_INTRO.get(_q9[2])
    if _nl9 and _nl9 != _q9[3]:
        pages[_i9] = (_q9[0], _q9[1], _q9[2], _nl9, _q9[4], _q9[5], _q9[6], _q9[7],
                      _q9[8], _q9[9], _q9[10], _q9[11], _q9[12], _q9[13])
        _INTRO2 += 1
if _INTRO2:
    print("新增地点简介套用", _INTRO2, "条")


if _DEAD:
    pages = [p for p in pages if p[0] not in _DEAD]
    print("删除已合并的旧页", len(_DEAD), "个")

# ===== 背景资源：场景页字段 / 背景资源条目 =====
_BG_DONE = 0
_BG_AGG = {}
for _i8, _q8 in enumerate(pages):
    if _q8[1] != "场景":
        continue
    _sc8 = _q8[0].split("/", 1)[1] if "/" in _q8[0] else _q8[0]
    _bgs = SCENE_BG.get(_sc8)
    if not _bgs:
        continue
    _inf8 = _pj(_q8[4], "{}")
    _inf8["背景"] = "、".join(_bgs[:4])
    pages[_i8] = (_q8[0], _q8[1], _q8[2], _q8[3], json.dumps(_inf8, ensure_ascii=False),
                  _q8[5], _q8[6], _q8[7], _q8[8], _q8[9], _q8[10], _q8[11],
                  _q8[12], _q8[13])
    for _b8 in _bgs:
        _BG_AGG.setdefault(_b8, []).append(_sc8)
        links.append((_q8[0], f"背景资源/{_b8}", "背景", _b8))
    _BG_DONE += 1

for _b8 in sorted(_BG_AGG):
    _scs8 = _BG_AGG[_b8]
    _rows8 = [{"note": scenes.get(_x8, {}).get("title") or _x8, "quote": "", "script": _x8,
               "title": scenes.get(_x8, {}).get("title") or _x8, "seq": 0, "routes": []}
              for _x8 in _scs8[:200]]
    add_page(f"背景资源/{_b8}", "背景资源", _b8,
             f"背景资源 {_b8}，共被 {len(_scs8)} 场剧情使用。",
             {"类型": "背景资源", "使用场景": f"{len(_scs8)} 场"},
             [{"h": "使用场景", "rows": _rows8}], ["背景资源"], len(_scs8), [])
print("背景字段", _BG_DONE, "页；背景资源条目", len(_BG_AGG), "个")

# ===== 条件条目（判定库）=====
_COND_USED = {k: set(v) for k, v in COND_USED.items()}
try:
    _tokre = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")
    for _r in c.execute("select script, cond from branch_nodes"):
        for _t in set(_tokre.findall(_r[1] or "")):
            if _t in COND_LIB:
                _COND_USED.setdefault(_t, set()).add(_r[0])
    for _r in c.execute("select script, options from choices"):
        for _t in set(_tokre.findall(_r[1] or "")):
            if _t in COND_LIB:
                _COND_USED.setdefault(_t, set()).add(_r[0])
    for _r in c.execute("select script, branch from branches"):
        for _t in set(_tokre.findall(_r[1] or "")):
            if _t in COND_LIB:
                _COND_USED.setdefault(_t, set()).add(_r[0])
except Exception as _e:
    print("条件反查失败", _e)

_cond_pages = 0
for _cid, _scs in _COND_USED.items():
    _info = COND_LIB.get(_cid) or {}
    _attrs = _info.get("attrs") or []
    _kind = "多路判定" if _info.get("kind") == "switch" else "条件表达式"
    _lead = "%s %s：%s" % (_kind, _cid, "；".join(_attrs)[:120])
    _rows = []
    for _i, _a in enumerate(_attrs, 1):
        _rows.append({"note": ("结果 %d：" % _i if _info.get("kind") == "switch" else "") + str(_a),
                      "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
    _scrows = [{"note": scenes.get(_x, {}).get("title") or _x, "quote": "",
                "script": _x, "title": scenes.get(_x, {}).get("title") or _x,
                "seq": 0, "routes": []} for _x in sorted(_scs)[:60]]
    add_page("条件/" + _cid, "条件", _cid, _lead,
             {"类型": _kind, "结果数": len(_attrs), "引用场景": "%d 场" % len(_scs)},
             [{"h": "判定内容", "rows": _rows}, {"h": "用到这个判定的场景", "rows": _scrows}],
             ["条件"], len(_scs), [], facet=_kind)
    _cond_pages += 1
print("条件条目", _cond_pages, "个（判定库共", len(COND_LIB), "）")

# ---------- 收尾：去掉剧本标签、给重名页加区分 ----------
_LUA = re.compile(r"\{/?\s*(?:size|color|b|i|u|center|right|sprite|img|font)\b[^}]*\}")
_NMFIX = {"呼……": "力竭喘息"}
_pl = [list(_p) for _p in pages]
for _p in _pl:
    if _p[2] in _NMFIX:
        _p[2] = _NMFIX[_p[2]]
for _p in _pl:
    for _i in (2, 3, 5):
        _v = _p[_i]
        if isinstance(_v, str) and "{" in _v and "}" in _v:
            _p[_i] = _LUA.sub("", _v)
_used = set()
# 关于页的收录规模改成按最终页数重算，避免先算后补导致的数字过期
_about = next((_p for _p in _pl if _p[0] == "关于本站"), None)
if _about:
    _c2 = collections.Counter(_x[1] for _x in _pl)
    _ord2 = ["人物", "势力", "地点", "事件", "地图事件", "场景", "剧情段", "剧情单元",
             "关系", "书物", "物品", "武学", "装备", "战技", "战斗角色", "战斗效果",
             "天赋", "成就", "数值", "设施", "路线", "时间线", "条件", "背景资源", "结局"]
    try:
        _s2 = json.loads(_about[5] or "[]")
    except Exception:
        _s2 = []
    for _s in _s2:
        if _s.get("h") == "收录规模":
            _s["rows"] = [{"note": "%s：%d 条" % (_k, _c2[_k]), "quote": "", "script": "",
                            "title": "", "seq": 0, "routes": []}
                           for _k in _ord2 if _c2.get(_k)]
    _about[5] = json.dumps(_s2, ensure_ascii=False)
# 空页兜底：没有正文的页补一节可核查内容；分面缺失的用类型名兼容
for _p in _pl:
    if not (_p[12] or "").strip():
        _p[12] = _p[1]
    if _p[1] in ("条件", "背景资源"):
        continue
    try:
        _ss = json.loads(_p[5] or "[]")
    except Exception:
        _ss = []
    if _ss and any((s.get("rows") or s.get("html") or s.get("text")) for s in _ss):
        continue
    _nm0 = _p[2]
    _r0 = []
    try:
        if _p[1] == "人物":
            _who = _nm0.split("·")[-1]
            for (_sc,) in c.execute(
                    "select distinct script from lines where speaker=? limit 14", (_who,)):
                _t0 = scenes.get(_sc, {}).get("title") or _sc
                _r0.append({"note": _t0, "quote": "", "script": _sc, "title": _t0,
                            "seq": 0, "routes": []})
        elif _p[1] == "地点":
            for (_sc,) in c.execute(
                    "select script from scenes where place like ? limit 14", ("%" + _nm0 + "%",)):
                _t0 = scenes.get(_sc, {}).get("title") or _sc
                _r0.append({"note": _t0, "quote": "", "script": _sc, "title": _t0,
                            "seq": 0, "routes": []})
    except Exception:
        _r0 = []
    if _r0:
        _ss.append({"h": "相关场景", "rows": _r0})
    else:
        _ss.append({"h": "说明",
                    "html": "本页只收录原文中的这一条记录，剧本没有给出更多描写。"})
    _p[5] = json.dumps(_ss, ensure_ascii=False)
_cnt = collections.Counter((_p[1], _p[2]) for _p in _pl)
_seen = collections.Counter()
for _p in _pl:
    _k = (_p[1], _p[2])
    if _cnt[_k] < 2:
        _used.add(_k)
        continue
    _seen[_k] += 1
    _n = _seen[_k]
    _sfx = ""
    _m = re.search(r"位于([^的、，]+)的剧情场景", _p[3] or "")
    if _m:
        _sfx = _m.group(1)
    if not _sfx and _p[12]:
        _sfx = _p[12]
    _cands = []
    if _sfx:
        _cands.append(_p[2] + "（%s）" % _sfx)
    if _sfx:
        _cands.append(_p[2] + "（%s·%d）" % (_sfx, _n))
    _cands.append(_p[2] + "·%d" % _n)
    for _cand in _cands:
        if (_p[1], _cand) not in _used:
            _p[2] = _cand
            break
    _used.add((_p[1], _p[2]))
# 地点页「发生场景」与 infobox 计数对齐（新增地点页也要有）
_FIXSC = 0
for _iP, _qP in enumerate(_pl):
    if _qP[1] != "地点":
        continue
    _scP = sorted(SCENES_BY_PLACE.get(_qP[2], []), key=lambda x: ORDER.get(x, 99999))
    if not _scP:
        continue
    _secsP = _pj(_qP[5], "[]")
    _infP = _pj(_qP[4], "{}")
    _rowsP = [{"note": scenes.get(_x, {}).get("title") or _x, "quote": "", "script": _x,
               "title": scenes.get(_x, {}).get("title") or _x, "seq": 0, "routes": []}
              for _x in _scP[:60]]
    _hasP = False
    for _sP in _secsP:
        if _sP.get("h") == "发生场景":
            _sP["rows"] = _rowsP
            _hasP = True
            break
    if not _hasP:
        _secsP.append({"h": "发生场景", "rows": _rowsP})
    _infP["场景"] = "%d 场" % len(_scP)
    _qP[4] = json.dumps(_infP, ensure_ascii=False)
    _qP[5] = json.dumps(_secsP, ensure_ascii=False)
    _FIXSC += 1
if _FIXSC:
    print("地点场景栅对齐", _FIXSC, "页")

pages = [tuple(_p) for _p in _pl]

c.executemany("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", pages)
valid = {p[0] for p in pages}
_seen = set()
_lk = []
for _a, _b, _k, _l in links:
    if _a not in valid or _b not in valid:
        continue
    key = (_a, _b, _k)
    if key in _seen:
        continue
    _seen.add(key)
    _lk.append((_a, _b, _k, _l))
c.executemany("insert into links values(?,?,?,?)", _lk)
c.executemany("insert or replace into redirects values(?,?)",
              [(a, s) for a, s in redirects if s in valid])
# 别名 → 条目（供正文自动链接与搜索使用）
_al = list(NAME_ALIAS) + [(a, f"人物/{t}") for a, t in CMERGE.items()]
_al += [(a, f"势力/{t}") for a, t in FMERGE.items()]
_al += [(a, f"地点/{t}") for a, t in PMERGE.items()]
_al += [("唐门医馆", "地点/唐门-药铺"), ("唐门药铺", "地点/唐门-药铺")]
c.executemany("insert or replace into aliases values(?,?)",
              [(a, s) for a, s in _al if s in valid and a])
# 列表只列顶层：把有上级的地点记入 place_children，接口会将其排除；子级只能从上级页的「下辖地点」进入
c.execute("delete from place_children")
c.executemany("insert or replace into place_children values(?)",
              [(f"地点/{k}",) for k in PPARENT if f"地点/{k}" in valid]
              + [(f"势力/{k}",) for k in FPARENT if f"势力/{k}" in valid])

# 统一异体字：攻略与部分脚本写作「耕杨」，游戏正文为「耕阳」
c.execute("update pages set lead=replace(lead,'耕杨','耕阳') where lead like '%耕杨%'")
c.execute("update pages set sections=replace(sections,'耕杨','耕阳') where sections like '%耕杨%'")

# 应用已重写的概要，避免重建把事件/剧情段/剧情单元导语退回旧版
for _sumname, _kind in (("ev_sum.json", "事件"), ("seg_sum.json", "剧情段"), ("unit_sum.json", "剧情单元")):
    _sp = os.path.join(BASE, "data", _sumname)
    if not os.path.exists(_sp):
        continue
    try:
        _sd = json.load(open(_sp, encoding="utf-8"))
    except Exception as _e:
        print("  概要读取失败", _sumname, _e)
        continue
    _n = 0
    for _k, _v in _sd.items():
        _t = _v.get("lead", "") if isinstance(_v, dict) else _v
        if not _t or not isinstance(_t, str):
            continue
        _n += c.execute("update pages set lead=? where slug=?", (_t, _k)).rowcount
    print("  概要覆盖 %-14s %d 页" % (_sumname, _n))

c.commit()

print("页面", c.execute("select count(*) from pages").fetchone()[0])
for r in c.execute("select type,count(*) from pages group by type order by 2 desc"):
    print(f"   {r[0]:<6} {r[1]}")
print("链接", c.execute("select count(*) from links").fetchone()[0],
      "重定向", c.execute("select count(*) from redirects").fetchone()[0],
      "别名", c.execute("select count(*) from aliases").fetchone()[0])
