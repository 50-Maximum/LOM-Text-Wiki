# -*- coding: utf-8 -*-
"""给旗标配一句人话：官方名优先，其次剧本归纳，人工覆盖高频/易混项。
输出 data/flag_gloss.json，并打印条件里出现最多的旗标，供人工过目。"""
import json, io, os, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
D = lambda n: json.load(io.open(os.path.join(BASE, 'data', n), encoding='utf-8'))
names = D('flag_names.json')
infer = D('flag_infer.json')
conds = D('cond_lib.json')
scene_in = D('scene_conds.json')

MANUAL = {
 'A00001': '分支开关暂存1，每章开头清零',
 'A00002': '分支开关暂存2，每章开头清零',
 'A00003': '分支开关暂存3，每章开头清零',
 'A00004': '分支开关暂存4，每章开头清零',
 'A00005': '分支开关暂存5，每章开头清零',
 'A00006': '分支开关暂存6，每章开头清零',
 'B00001': '选项槽：上一次菜单选的是第几项',
 'B00002': '选项槽：上一次菜单选的是第几项',
 'B00003': '武英殿比试的胜场数，赢下第三场时当场判定',
 'B00004': '本轮是否已触发过锦香宫吃醋事件',
 'C00000': '上一场决斗的结果，0 输 1 赢',
 'M40065': '大师兄弥留、交代后事的那一夜过后置 1；后面的剧本用它区分那一夜之前与之后',
 'TC0001': '决斗事件旗标 1，本场走哪套决斗配置',
 'M00045': '小竹学武功的进度',
 'M60003': '小师妹是否同行武林大会',
 'M60004': '小梅是否同行武林大会',
 'M60005': '小竹是否同行武林大会',
 'M60007': '叶云裳是否同行武林大会',
 'G11004': '是否已攻略小梅',
 'S2700_00': '飞天门一线自由行动已完成',
 'S2600_00': '飞天门一线自由行动已开始',
 'H03003': '与牛头马面（地狱道）交锋的累计次数',
 'Pinball_Broken': '弹珠台是否损坏，0 为已修好',
 'Door_Work_201': '大门打杂（201）做过几次',
 'M30041': '青城阶段自由行动事件计数',
 'S2800_02_Talk_02': '狱中与瑞笙谈过第二段',
 'S2800_02_Talk_03': '狱中与瑞笙谈过第三段',
 'S2800_02_Talk_04': '狱中与瑞笙谈过第四段',
 'S2800_02': '瑞笙坦言私心的那段已走完',
 'S9906_01_Option_01': '乞丐闲谈选过第二项',
 'S9906_01_Option_02': '乞丐闲谈选过第三项',
 'S9906_01_Option_03': '乞丐闲谈选过第四项',
 'S9906_01_Option_04': '乞丐闲谈选过第五项',
 'M00022': '大门自由行动（504）事件计数',
 'Talk_Brother2_00': '炼丹房选过找二师兄',
 'Talk_Sister1_00': '小师妹房里选过第三项',
 'Door_Work_S_01': '大门工作（301）做过几次',
 'Pharmacy_Work_402_01': '药铺工作（402）已做过',
 'Pharmacy_Work_403_01': '药铺工作（403）已做过',
 'Pharmacy_Work_404_01': '药铺工作（404）已做过',
 'M00039': '与三师兄谈话的累计次数',
 'Talk_Girl_05_01': '夏侯兰谈话第 1 段已谈',
 'Talk_Girl_05_01_001': '夏侯兰第 1 段选定的分支',
 'Talk_Girl_05_02': '夏侯兰谈话第 2 段已谈',
 'Talk_Girl_05_02_001': '夏侯兰第 2 段选定的分支',
 'Talk_Girl_05_03': '夏侯兰谈话第 3 段已谈',
 'Talk_Girl_05_04': '夏侯兰谈话第 4 段已谈',
 'Talk_Girl_05_05': '夏侯兰谈话第 5 段已谈',
 'Talk_Girl_05_12': '夏侯兰谈话第 12 段（雪山派灭门）已谈',
 'Talk_Girl_05_12_001': '夏侯兰第 12 段选定的分支',
 'E22001': '剧本里查不到写入与读取，用途未知',
 'S2503_Break_01_001': '夏侯兰点穴弃徒的一段已走',
 'Ch_0_M_Option_02': '开场集会选过第二项',
 'Ch_0_M_Option_03': '开场集会选过第三项',
 'Ch_0_M_Option_04': '开场集会选过第四项',
 'S9906_01': '开场集会选过离开那一项',
 'M70055': '唐升议开武林大会时与 girl8 的那段已走',
 'Door_Work_101': '大门工作（101）做过几次',
 'Talk_Brother3_00': '书房选过找三师兄',
}
STOP = re.compile(r'^[（(]?(读剧本归纳|按写入现场)')
def short_note(note):
    t = (note or '').strip()
    t = re.sub(r'^（[^）]*）', '', t)
    t = re.sub(r'^\([^)]*\)', '', t)
    t = t.replace('\n', ' ')
    seg = re.split(r'[；。]', t)[0].strip()
    return seg[:28]

gloss = {}
for f in set(list(names.keys()) + list(infer.keys()) + list(MANUAL.keys())):
    if f in MANUAL:
        gloss[f] = {'text': MANUAL[f], 'src': 'manual'}
    elif isinstance(names.get(f), str) and names[f].strip() and not names[f].startswith('（'):
        gloss[f] = {'text': names[f].strip()[:28], 'src': 'name'}
    elif isinstance(infer.get(f), dict) and infer[f].get('note'):
        gloss[f] = {'text': short_note(infer[f]['note']), 'src': 'infer'}
json.dump(gloss, io.open(os.path.join(BASE, 'data', 'flag_gloss.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 统计条件里出现的旗标频次
cnt = collections.Counter()
pat = re.compile(r'([A-Za-z]{1,4}\d{2,}|[A-Za-z]+_\d{3,})')
for v in scene_in.values():
    for x in v:
        for m in pat.finditer(x.get('text') or ''):
            cnt[m.group(1)] += 1
for k, v in conds.items():
    for t in v.get('attrs') or []:
        for m in pat.finditer(t):
            cnt[m.group(1)] += 1

o = io.open('_gloss_top.txt', 'w', encoding='utf-8')
o.write('gloss 共 %d 条\n\n条件里出现最多的旗标：\n' % len(gloss))
for f, n in cnt.most_common(45):
    g = gloss.get(f, {})
    o.write('%-16s x%-4d %-10s %s\n' % (f, n, g.get('src', ''), g.get('text', '')))
o.close()
print('ok', len(gloss))
