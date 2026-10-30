# -*- coding: utf-8 -*-
"""重做首页 + 加「提交当前页修订建议」。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\web\wiki.html"
s = open(P, encoding="utf-8").read()

# ---------- 1. 导航去掉「关于」 ----------
s = s.replace('<a href="#/chapters">原文</a><a href="#/p/%E5%85%B3%E4%BA%8E%E6%9C%AC%E7%AB%99">关于</a>',
              '<a href="#/chapters">原文</a>')

# ---------- 2. CSS ----------
if ".sgbtn" not in s:
    css = """
.hero .meta{margin-top:6px;color:#8a93a1;font-size:12.5px;letter-spacing:.03em}
.sgbtn{position:fixed;left:14px;bottom:12px;z-index:60;padding:6px 12px;border-radius:14px;
  background:#1b1e23;border:1px solid #282c33;color:#8a93a1;font-size:12px;cursor:pointer;user-select:none}
.sgbtn:hover{color:#c8a06a;border-color:#c8a06a}
#sgmask{position:fixed;inset:0;background:rgba(8,9,11,.72);z-index:99;display:flex;
  align-items:center;justify-content:center}
#sgbox{width:min(620px,92vw);background:#1b1e23;border:1px solid #2b2f36;border-radius:8px;padding:18px 20px}
#sgbox h3{margin:0 0 4px;font-size:15px;color:#c8a06a}
#sgbox .who{color:#8a93a1;font-size:12px;margin-bottom:10px;word-break:break-all}
#sgbox textarea{width:100%;height:150px;background:#111316;color:#d9dde3;border:1px solid #282c33;
  border-radius:5px;padding:10px;font:14px/1.7 inherit;resize:vertical;outline:none}
#sgbox textarea:focus{border-color:#c8a06a}
#sgbox .row{display:flex;gap:10px;align-items:center;margin-top:10px}
#sgbox button{padding:7px 16px;border-radius:5px;border:1px solid #2b2f36;background:#22262c;
  color:#d9dde3;cursor:pointer;font-size:13px}
#sgbox button.p{background:#c8a06a;border-color:#c8a06a;color:#141619;font-weight:600}
#sgbox .hint{color:#6f7885;font-size:12px;margin-left:auto}
</style>"""
    s = s.replace("</style>", css, 1)

# ---------- 3. 首页重写 ----------
start = s.index("/* ---------- 首页 ---------- */")
end = s.index("/* ---------- 列表 ---------- */")
NEW = r'''/* ---------- 首页 ---------- */
const QQ_GROUP='914717666';
async function home(){
  $('#side').innerHTML='';
  const t=await api('/api/types');
  const types=(t.types||[]).filter(x=>x.type!=='世界观');
  const order=['地图','人物','势力','地点','事件','剧情段','地图事件','场景','书物','物品',
    '武学','装备','天赋','战技','成就','数值','路线','结局','时间线','背景资源'];
  const cards=types.filter(x=>order.includes(x.type))
                   .sort((a,b)=>order.indexOf(a.type)-order.indexOf(b.type));
  let ver='';
  try{ ver=(await api('/api/appver')).version; }catch(e){}
  let h='<div class="wrap">';
  h+=`<div class="hero"><h1>活侠传追踪Wiki</h1>
    <div class="lead">把《活侠传》的游戏原文拆成可查的条目：人物、势力、地点、事件、武学、物品与场景。
    每条叙述都能点回具体场景，原文按句保留，不做转述改写。</div>
    <div class="meta">单机离线 · v${esc(ver||'')} · 全部内容来自游戏资源与攻略资料</div></div>`;

  h+='<h2>从这里开始</h2><div class="grid">';
  const quick=[
    ['#/search/', '全文检索', '按名字、台词、脚本编号片段查'],
    ['#/chapters', '原文阅读', '按章节逐场读全量剧本'],
    ['#/p/'+encodeURIComponent('地图/大地图'), '大地图', '游戏原版地图，点地名进条目'],
    ['#/p/'+encodeURIComponent('时间线/总览'), '时间线', '按年月旬看剧情推进']
  ];
  for(const [u,n,d] of quick)
    h+=`<a class="card" href="${u}"><h3>${esc(n)}</h3><div class="m">${esc(d)}</div></a>`;
  h+='</div>';

  if(cards.length){
    h+='<h2>全部条目</h2><div class="grid">';
    for(const c of cards)
      h+=`<a class="card" href="#/list/${enc(c.type)}"><h3>${esc(c.type)}</h3>
          <div class="m">${c.n} 条</div></a>`;
    h+='</div>';
  }

  h+='<h2>页面上的标注怎么读</h2>'
   + '<div class="lead">「时间」是攻略标注的剧情时间；「推断时间」由上一场或地图事件时间窗推出，条目里写明依据。'
   + '「入境判定」是从上一场跳进来时必须满足的判定；「开场判定」是本场台词开始前的检查。'
   + '「地图事件」是养成地图上随机刷出的事件，条件与基础概率取自游戏资源。'
   + '「原文摘录」是资源库里提到该条的句子，未经改写。</div>';

  h+='<h2>数据从哪来</h2>'
   + '<div class="lead">一、游戏本体：Unity 资源包里的剧本与文本资产，逐句解出，带入场景、人物、分支。'
   + '二、攻略资料：整理年月旬、触发条件、角色与事件脉络，作为游戏数据之外的第二来源。'
   + '三、判定库：咖啡伴侣（BepInEx 插件）内置判定表，只用于把编号翻成可读条件，不参与剧情叙述。</div>';

  h+='<details><summary>已知局限</summary><div class="lead">'
   + '一、地图事件只有部分带明确起止时间，其余靠旗标控制，时间窗口无法给出。<br>'
   + '二、部分地图事件不唯一对应某场戏（赶路、章节随机、大门这类族），页面改为列出同码剧本。<br>'
   + '三、「关闭条件」仍在核验，未发布，避免误导。<br>'
   + '四、人物简介里「原文中出现 N 处」类的短导语，已补原文摘录，仍待逐条重写。<br>'
   + '五、仍有部分场景未确定地点，条目里不写地点。</div></details>';

  h+='<h2>维护与反馈</h2><div class="lead">'
   + `版本 <b>v${esc(ver||'')}</b>。发现条目有误、地点不对、简介别扭，点左下角「修订建议」提交，`
   + '内容会存到本地并复制到剪贴板，直接发到开发者 QQ 群即可。<br>'
   + `开发者 QQ 群：<b>${QQ_GROUP}</b></div>`;

  h+='</div>';
  $('#main').innerHTML=h;
}

/* ---------- 提交当前页修订建议 ---------- */
function suggestOpen(){
  if($('#sgmask')) return;
  const page=decodeURIComponent(location.hash.replace(/^#/,''))||'/';
  const title=(typeof labelOf==='function'&&labelOf(page))||page;
  const m=document.createElement('div');
  m.id='sgmask';
  m.innerHTML=`<div id="sgbox">
    <h3>提交修订建议</h3>
    <div class="who">当前页：${esc(title)}（${esc(page)}）</div>
    <textarea id="sgtxt" placeholder="哪里不对？请写清条目、原句与你认为正确的内容。"></textarea>
    <div class="row">
      <button class="p" onclick="suggestSend()">保存并复制</button>
      <button onclick="document.getElementById('sgmask').remove()">取消</button>
      <span class="hint">保存后发到 QQ 群 ${QQ_GROUP}</span>
    </div></div>`;
  document.body.appendChild(m);
  setTimeout(()=>{ const x=$('#sgtxt'); if(x) x.focus(); }, 30);
}
async function suggestSend(){
  const t=($('#sgtxt')&&$('#sgtxt').value||'').trim();
  if(!t){ alert('请先写点内容'); return; }
  const page=decodeURIComponent(location.hash.replace(/^#/,''))||'/';
  const title=(typeof labelOf==='function'&&labelOf(page))||page;
  const body={page:page,title:title,text:t};
  try{
    await fetch('/api/suggest',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)});
  }catch(e){}
  const txt='【修订建议】\n页面：'+title+'（'+page+'）\n内容：'+t+'\n版本：'+(window.__VER||'');
  try{ await navigator.clipboard.writeText(txt); }catch(e){}
  const mk=$('#sgmask'); if(mk) mk.remove();
  alert('已保存到本地，内容也已复制到剪贴板。\n可直接发到开发者 QQ 群 '+QQ_GROUP+'。');
}

'''
s = s[:start] + NEW + s[end:]

# ---------- 4. 右下角按钮 + 关于页重定向 ----------
if 'class="sgbtn"' not in s:
    s = s.replace('</body>', """<div class="sgbtn" onclick="suggestOpen()">修订建议</div>
</body>""", 1)

if "关于本站" not in s.split("</style>")[0] + s.split("</style>")[1][:200]:
    pass

open(P, "w", encoding="utf-8").write(s)
print("首页与建议入口已写入")
