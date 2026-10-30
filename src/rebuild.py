# -*- coding: utf-8 -*-
"""一键重建：build_wiki2.py → curate_people → curate_factions → curate_text。"""
import subprocess, sys, os, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
steps = [
    ('说话人校正', [sys.executable, os.path.join('src', 'fix_speakers.py')]),
    ('分支变量表', [sys.executable, os.path.join('src', 'build_switch_map.py')]),
    ('分支人话表', [sys.executable, os.path.join('src', 'build_branch_human.py')]),
    ('build', [sys.executable, os.path.join('src', 'build_wiki2.py')]),
    ('人物整理', [sys.executable, os.path.join('src', 'curate_people.py')]),
    ('补充人物', [sys.executable, os.path.join('src', 'curate_extra_people.py')]),
    ('入属微调', [sys.executable, os.path.join('src', 'curate_membership.py')]),
    ('势力整理', [sys.executable, os.path.join('src', 'curate_factions.py')]),
    ('文案收尾', [sys.executable, os.path.join('src', 'curate_text.py')]),
    ('地点场景栅', [sys.executable, os.path.join('src', 'curate_place_scenes.py')]),
    ('旗标建页', [sys.executable, os.path.join('src', 'curate_flags.py')]),
    ('数值补全', [sys.executable, os.path.join('src', 'curate_numbers.py')]),
    ('官方表校名', [sys.executable, os.path.join('src', 'curate_tables.py')]),
    ('旗标判定结论', [sys.executable, os.path.join('src', 'curate_infer.py')]),
    ('其余旗标补位', [sys.executable, os.path.join('src', 'curate_name_rest.py')]),
    ('旗标名与计数', [sys.executable, os.path.join('src', 'curate_flag_names.py')]),
    ('旗标位置说明', [sys.executable, os.path.join('src', 'curate_flag_notes2.py')]),
    ('旗标人话表', [sys.executable, os.path.join('src', 'build_gloss.py')]),
    ('旗标人话补注', [sys.executable, os.path.join('src', 'curate_gloss.py')]),
    ('旗标写入点', [sys.executable, os.path.join('src', 'curate_flag_origin.py')]),
    ('判定说明', [sys.executable, os.path.join('src', 'curate_cond_explain.py')]),
    ('进入条件页', [sys.executable, os.path.join('src', 'curate_cond_gate.py')]),
    ('剧本变量人话', [sys.executable, os.path.join('src', 'curate_branch_vars.py')]),
    ('事件判定旗标', [sys.executable, os.path.join('src', 'curate_event_flags.py')]),
    ('条件编号补原文', [sys.executable, os.path.join('src', 'curate_cond_refs.py')]),
    ('关于页计数', [sys.executable, os.path.join('src', 'curate_about.py')]),
]
for name, cmd in steps:
    t0 = time.time()
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print('[失败] %s 退出码 %d' % (name, r.returncode))
        sys.exit(r.returncode)
    print('[完成] %s  %.1fs' % (name, time.time() - t0))
print('全部完成')
