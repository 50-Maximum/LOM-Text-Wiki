# 活侠传追踪Wiki

把《活侠传》本体的简体中文文本全部提取、解析、结构化，做成一个可以全文检索、条目互链的本地百科软件。

单机运行，独立窗口，不修改游戏文件，除「检查更新」外不联网。

## 它解决什么

游戏剧情量很大，台词散落在 Unity 资源包的 Story 表与章节脚本里，想回头查一句话、一个选择、一个旗标出现在哪场戏，几乎不可能。这个工具把全部文本落到可检索的库里，并且把「这句话属于哪一场、这一场在哪个阶段、这个选项通向哪里、这个条件依赖哪些旗标」串起来。

## 注意事项
由于目前LOM-Text-wiki尚不完善，所有事件标题（因原游戏未命名）采用大量ai编辑，置信度不高。
建议在需要考据相关角色、地点、势力等信息时，多多注意相关剧情事件与事件编号序列，并以原剧情文本为重要判断依据。
并不能作为攻略使用，也不建议希望体验完整游戏过程的玩家使用。

## 规模

| 项目 | 数量 |
| --- | --- |
| 台词 | 76,954 条 |
| 说话人 | 227 位 |
| 正文字符 | 约 194 万 |
| 场景 | 2,147 个 |
| 分支节点 | 3,309 个 |
| 分支选项 | 1,196 组（76% 可点击直达下一场） |
| 分支判定 | 3,970 条 |
| 旗标变更 | 3,056 次 |
| 条目页 | 13,458 个 |
| 页面互链 | 21,486 条 |
| 立绘 | 180 张 |

条目页构成：事件 2,572、场景 2,147、剧情段 1,771、条件 3,606、战斗效果 540、地图事件 433、书物 431、关系 373、人物 326、成就 211、背景资源 204、地点 153、天赋 149、战斗角色 111、武学 102、物品 100、势力 90、数值 48、装备 40、其余（路线、战技、时间线、设施、世界观、地图、结局）。

## 功能

- 全文检索：FTS5 索引，命中到句，点开是整场戏
- 阶段目录：外姓弟子、南宫寿宴、江陵围城、唐门衰败、比武招亲、武林大会、武林盟进攻唐门、不限时间
- 场景页：按序排列台词，标旁白/心声，分支选项与旗标改动就地显示，选项可跳转
- 人物页：身份、称号（金色）、所属势力、相关事件分节
- 势力页：上级势力、下辖势力、本派成员三块，带数量
- 地点页：可到达 / 仅提及 / 剧情场景地三态，上下级成树
- 事件页：按正文内容命名，给出阶段与所在场景，前后链接
- 条件页：参数中文化（因果、性情、心相），写成可读句子
- 攻略对照：71 条攻略事件、攻略年表按年月旬对齐场景
- 地图：底图加 433 个事件节点
- 自动更新：读 GitHub Releases，校验 SHA256 后替换重启

## 运行

双击 `活侠传追踪Wiki.exe`。程序在 `127.0.0.1:8765` 起本地服务并开窗，关窗即退出。

开发态直接从源码跑：

```
python src/desktop.py
```

依赖 `pywebview`（或退化为系统 Edge app 窗口 / 默认浏览器）。

## 目录

```
活侠传追踪Wiki.exe
_internal/            Python 运行时
data/wiki.db          成品数据库
data/portrait_index.json
data/update.json      更新源配置
web/wiki.html         前端单页
web/portraits.json    立绘对照
web/flags.json        旗标名称
web/map_nodes.json    地图节点
web/portrait/         立绘 180 张
version.json
```

## 从游戏重建

源游戏目录结构必须包含 `Mortal_Data`。按顺序执行：

```
src/p0_extract.py              从 Unity 资源抽文本
src/p0b_texttable.py           合并 TextAsset 成台词总表
src/p1_parse.py                解析章节脚本：场景、说话人、分支、旗标
src/p2_build_db.py             建 SQLite 与 FTS5 索引
src/restore_extra_tables.py    补回附加表
src/p2b_titles.py              称号
src/name_events.py             事件命名
src/build_scene_next.py        场景衔接
src/build_story_segments.py    剧情段
src/build_branch_tree.py       分支树
src/build_scene_graph2.py      场景图
src/build_scene_clusters4.py   分支簇
src/build_cond_lib.py          条件库
src/build_cond_used.py         条件引用
src/build_flag_names.py        旗标名称
src/build_combat_levels.py     战斗关卡
src/build_battle_level_map.py  关卡对照
src/resolve_battle_levels.py   关卡名解析
src/build_enemy_team_names.py  敌方队伍
src/build_battle_results3.py   战斗结果
src/build_wiki2.py             生成条目页
src/build_release.py           打包发布
```

重建前先关闭正在运行的程序，否则 SQLite 被占用写不进去。

## 打包

```
pyinstaller --noconfirm --distpath dist_build_v07 --workpath build_v07 活侠传追踪Wiki.spec
python src/build_release.py
```

产物在 `release/`：zip 包与 `update.json` 清单（含 size 与 sha256）。

## 自动更新

`data/update.json` 里填仓库：

```json
{ "github": { "owner": "50-Maximum", "repo": "LOM-Text-Wiki" } }
```

程序取 `releases/latest` 的 tag（去掉前缀 v）与本地 `version.json` 比较，有新版则下载 zip、校验 sha256、替换文件、重启。发布时 tag 必须是 `vX.Y.Z`，且与 `version.json` 一致。

## 发布方式

仓库只放源码、规则表与前端页面。数据库、解包中间产物、构建产物、研究笔记与人工订正表都不入库，见 `.gitignore`。安装包走 Releases。

## 数据来源与声明

游戏文本与立绘出自《活侠传》（Legend of Mortal），版权归开发组所有。本项目只把已有文本整理成便于检索的形式，供玩家查阅，不用于商业用途，也不包含游戏可执行文件、不涉及破解。

条目页里的事件命名、剧情段划分、人物分节属于整理工作，判断依据均落在原文台词上，页面保留原文出处，可自行核对。

## 许可

代码以 MIT 发布，游戏素材不适用该许可。
