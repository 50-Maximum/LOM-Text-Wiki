# -*- coding: utf-8 -*-
"""按立绘资源 id 修正说话人：同名的不同人拆开。跑在 build 之前。"""
import sqlite3, io, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.getcwd()
db = sqlite3.connect(os.path.join(BASE, 'data', 'wiki.db'))
db.row_factory = sqlite3.Row
c = db.cursor()

# 资源 id → 具体的人（依据剧本上下文：ch3_1_6_4 三长老对话逐句核对）
SPLIT = {
    'daoshi311': '怀素真人',
    'daoshi312': '不平道长',
    'daoshi313': '铁冠道人',
}

n = 0
for cid, nm in SPLIT.items():
    rows = c.execute("select count(*) from lines where speaker_id=? and speaker='青城长老'", (cid,)).fetchone()[0]
    if rows:
        c.execute("update lines set speaker=? where speaker_id=? and speaker='青城长老'", (nm, cid))
        n += rows
        print('  %s → %s：%d 条' % (cid, nm, rows))

# 青城长老若还有剩余（其他 id），保留原名并记录
left = c.execute("select speaker_id,count(*) n from lines where speaker='青城长老' group by speaker_id").fetchall()
for r in left:
    print('  仍有青城长老未拆：%s %d 条' % (r['speaker_id'], r['n']))

db.commit()
print('共改 %d 条' % n)
