
const $=s=>document.querySelector(s);
const esc=s=>(s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const api=p=>fetch(p).then(r=>r.json());
const enc=s=>encodeURIComponent(s);

let NAME_LIST=[], NAME_MAP={}, NAME_RE=null, TITLES={};
async function loadIndex(){
  const d=await api('/api/nameindex');
  NAME_LIST=d.names||[];
  NAME_MAP={};
  for(const x of NAME_LIST) if(!NAME_MAP[x.name]) NAME_MAP[x.name]=x.slug;
  const names=NAME_LIST.map(x=>x.name).filter((v,i,a)=>a.indexOf(v)===i)
    .sort((a,b)=>b.length-a.length).map(n=>n.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
  if(names.length) NAME_RE=new RegExp('('+names.join('|')+')','g');
}
function linkify(text){
  if(!text) return '';
  if(!NAME_RE) return esc(text);
  NAME_RE.lastIndex=0;
  let out='', last=0, m;
  while((m=NAME_RE.exec(text))!==null){
    out+=esc(text.slice(last,m.index));
    const slug=NAME_MAP[m[0]];
    out+=slug?`<a class="wl" href="#/p/${enc(slug)}">${esc(m[0])}</a>`:esc(m[0]);
    last=m.index+m[0].length;
    if(m[0].length===0) NAME_RE.lastIndex++;
  }
  out+=esc(text.slice(last));
  return out;
}
function fnmark(h){
  if(!h) return h;
  return h.replace(/（(\d+)）/g,(m,n)=>`<sup class="fn" data-fn="${n}" onclick="jumpFn(this)" title="跳转脚注 ${n}">${n}</sup>`);
}
function jumpFn(el){
  const t=document.getElementById('fn-'+el.dataset.fn);
  if(t){ t.scrollIntoView({block:'center'}); t.style.background='#33291a'; setTimeout(()=>t.style.background='',1600); }
}
function secHtml(t){
  return String(t||'').replace(/\n/g,'<br>').split(/<br\s*\/?>/i).map(x=>fnmark(linkify(x))).join('<br>');
}
function rich(s){
  let t=esc(s||'');
  t=t.replace(/\{size=?(\d+)\}/g,(m,n)=>'<span style="font-size:'+Math.max(12,Math.min(34,Math.round(+n*0.6)))+'px">')
     .replace(/\{\/size\}/g,'</span>')
     .replace(/\{color=(#[0-9a-fA-F]{3,8})\}/g,'<span style="color:$1">')
     .replace(/\{\/color\}/g,'</span>')
     .replace(/\{title\}/g,'<span class="ttl">').replace(/\{\/title\}/g,'</span>')
     .replace(/\{punch=[^}]*\}/g,'<span class="punch">').replace(/\{\/punch\}/g,'</span>')
     .replace(/\{\$[^}]*\}/g,'');
  return t;
}
const badge=mode=>({narrative:'旁白',think:'心声',center:'居中',center2:'居中',character:'对白'})[mode]||'对白';
const cls=mode=>({narrative:'narr',think:'think',center:'center center2'})[mode]||'';

/* ---------- 路由 ---------- */
window.addEventListener('hashchange',route);
function go(h){ location.hash=h; }

/* ---------- 返回上一页（站内历史） ---------- */
const NAV=[]; let curHash='', navSuppress=false, navRestore=false;
const POS=new Map();
function labelOf(h){
  if(!h||h==='/') return '首页';
  const p=decodeURIComponent(h).replace(/^#/,'').split('?')[0].replace(/^#/,'').split('/');
  const kind=p[1]||'', arg=p.slice(2).join('/').split('?')[0];
  if(kind==='p') return (arg.split('/').pop()||'条目');
  if(kind==='list') return (arg||'全部')+' 列表';
  if(kind==='scene') return '场景 '+arg.split('?')[0];
  if(kind==='search') return '搜索「'+arg+'」';
  if(kind==='chapters') return '原文';
  return '首页';
}
function updateBack(){
  const el=document.getElementById('backbar');
  if(!el) return;
  const t=NAV[NAV.length-1];
  if(t && t.h!==curHash){
    el.style.display='flex';
    el.innerHTML=`<a href="javascript:void 0" onclick="goBack();return false">← 返回「${esc(t.label)}」</a>`;
  }else{
    el.style.display='none'; el.innerHTML='';
  }
}
function goBack(){
  const t=NAV.pop();
  if(!t){ history.back(); return; }
  navSuppress=true;
  navRestore=true;
  location.hash=t.h.replace(/^#/,'');
  updateBack();
}

async function route(){
  const h=decodeURIComponent(location.hash.replace(/^#/,''))||'/';
  if(h!==curHash){
    if(curHash) POS.set(curHash, window.scrollY||window.pageYOffset||0);
    if(curHash && !navSuppress) NAV.push({h:curHash,label:labelOf(curHash)});
    navSuppress=false;
    curHash=h;
  }
  updateBack();
  const [_,kind,...rest]=h.split('/');
  const rawArg=rest.join('/');
  const _q=(rawArg.split('?')[1]||'');
  const arg=rawArg.split('?')[0];
  window.scrollTo(0,0); $('#main').scrollTop=0;
  try{
    if(!kind||kind==='') await home();
    else if(kind==='p') await renderPage(arg);
    else if(kind==='list'){
      const qs=new URLSearchParams(_q);
      await renderList(arg,qs.get('q')||'',parseInt(qs.get('o')||'0',10)||0,qs.get('f')||'',qs.get('f2')||'');
    }
    else if(kind==='search') await renderSearch(arg);
    else if(kind==='scene') await renderScene(arg);
    else if(kind==='chapters') await renderChapters();
    else await home();
  } finally {
    if(navRestore){
      navRestore=false;
      const y=POS.get(curHash)||0;
      const put=()=>window.scrollTo(0,y);
      requestAnimationFrame(()=>{ requestAnimationFrame(put); setTimeout(put,60); });
    }
    document.title = (labelOf(curHash)||'活侠传') + ' · 活侠传百科';
  }
}

/* ---------- 首页 ---------- */
async function home(){
  $('#side').innerHTML='';
  const wv=await api('/api/page?slug='+enc('世界观/总览'));
  let h='<div class="wrap">';
  if(wv && wv.lead){
    h+=`<div class="hero"><h1>活侠传 · 百科</h1>
      <div class="lead">${fnmark(linkify(wv.lead))}</div></div>`;
    for(const s of (wv.sections||[])){
      if(s.h==='脚注' && s.rows){
        h+='<h2>脚注</h2>';
        for(const r of s.rows){
          let nm=r.note||'', fnnum='';
          const m=nm.match(/^(\d+)\.\s*/);
          if(m){ fnnum=m[1]; nm=nm.slice(m[0].length); }
          h+=`<div class="note"${fnnum?` id="fn-${fnnum}"`:''}>`;
          if(fnnum) h+=`<sup class="fn">${fnnum}</sup> `;
          h+=linkify(nm);
          if(r.quote) h+=`<div class="ev">原文：「${esc(r.quote)}」</div>`;
          h+='</div>';
        }
        continue;
      }
      h+=`<h2>${esc(s.h)}</h2><div class="lead">${fnmark(linkify(s.html||''))}</div>`;
    }
  } else {
    h+=`<div class="hero"><h1>活侠传 · 百科</h1>
    <p>从游戏原文整理的人物、势力、地点、事件、武学、物品与数值条目。每条叙述都能回溯到具体场景的原文；地图事件带触发条件与概率，时间线按月看得到每个月发生了什么。</p>
    <p><a class="chip" href="javascript:void 0" onclick="randomPage();return false">随便看看一条 →</a></p></div>`;
  }
  const t=await api('/api/types');
  const types=(t.types||[]).filter(x=>x.type!=='世界观');
  const order=['人物','势力','地点','事件','剧情段','地图事件','数值','物品','武学','成就','场景','时间线'];
  const cards=types.filter(x=>order.includes(x.type)).sort((a,b)=>order.indexOf(a.type)-order.indexOf(b.type));
  h+='<h2>分类</h2><div class="grid">';
  for(const c of cards)
    h+=`<a class="card" href="#/list/${enc(c.type)}"><h3>${esc(c.type)}</h3>
        <div class="m">${c.n} 个条目</div></a>`;
  h+='</div>';
  const top=await api('/api/pages?type=人物&limit=12');
  h+='<h2>登场最多的人物</h2><div class="grid">';
  for(const r of top.rows)
    h+=`<a class="card" href="#/p/${enc(r.slug)}"><h3>${esc(r.name)}</h3>
        <div class="m">${r.mentions} 处提及</div>
        <div class="ex">${esc((r.lead||'').slice(0,56))}…</div></a>`;
  h+='</div>';
  const fac=await api('/api/pages?type=势力&limit=8');
  h+='<h2>势力</h2><div class="grid">';
  for(const r of fac.rows)
    h+=`<a class="card" href="#/p/${enc(r.slug)}"><h3>${esc(r.name)}</h3>
        <div class="m">${r.mentions} 处提及</div></a>`;
  h+='</div></div>';
  $('#main').innerHTML=h;
}

/* ---------- 列表 ---------- */
function listHash(type,q,offset,facet,facet2){
  let s='#/list/'+enc(type||'');
  const ps=[];
  if(q) ps.push('q='+encodeURIComponent(q));
  if(facet) ps.push('f='+encodeURIComponent(facet));
  if(facet2) ps.push('f2='+encodeURIComponent(facet2));
  if(offset) ps.push('o='+offset);
  return s+(ps.length?('?'+ps.join('&')):'');
}
function listGo(type,q,offset,facet,facet2){
  const h=listHash(type,q,offset,facet,facet2);
  if(decodeURIComponent(location.hash.replace(/^#/,''))===decodeURIComponent(h.slice(1))){
    renderList(type,q,offset,facet,facet2); return;
  }
  go(h);
}

const FACET_LABEL={'人物':'身份','地点':'上级地点','势力':'上级势力','事件':'剧情阶段',
  '场景':'剧情阶段','地图事件':'地点','书物':'出现阶段','物品':'出现阶段',
  '武学':'出现阶段','装备':'出现阶段','天赋':'出现阶段','成就':'出现阶段',
  '战技':'出现阶段','战斗角色':'出现阶段','战斗效果':'出现阶段','设施':'出现阶段',
  '数值':'类型','关系':'类型','路线':'类型'};

async function renderList(type,q,offset,facet,facet2){
  const d=await api(`/api/pages?type=${enc(type||'')}&q=${enc(q||'')}&offset=${offset||0}&limit=100&facet=${enc(facet||'')}&facet2=${enc(facet2||'')}`);
  const t=await api('/api/types');
  const fc=await api('/api/facets?type='+enc(type||''));
  const fc2=await api('/api/facets?type='+enc(type||'')+'&dim=2');
  if(window.LIST_SORT===undefined) window.LIST_SORT='default';
  const hadFocus=(document.activeElement&&document.activeElement.id==='lf');
  const caret=hadFocus?document.activeElement.selectionStart:0;
  let side=`<input class="search-sm" id="lf" placeholder="在本类中筛选" value="${esc(q||'')}">`;
  for(const x of (t.types||[]))
    side+=`<a class="item ${x.type===type?'on':''}" href="#/list/${enc(x.type)}">${esc(x.type)}<span class="n">${x.n}</span></a>`;
  $('#side').innerHTML=side;
  const lf=$('#lf');
  if(lf){
    let tm=null;
    lf.oninput=()=>{ clearTimeout(tm); tm=setTimeout(()=>{
      const nh=listHash(type,lf.value,0,facet,facet2);
      history.replaceState(null,'',nh);
      const hv=decodeURIComponent(nh.slice(1));
      curHash=hv;
      document.title=(labelOf(nh)||'活侠传')+' · 活侠传百科';
      renderList(type,lf.value,0,facet,facet2);
    },300); };
    lf.onkeydown=e=>{ if(e.key==='Enter'){ e.preventDefault();
      const nh=listHash(type,lf.value,0,facet,facet2);
      history.replaceState(null,'',nh); curHash=decodeURIComponent(nh.slice(1));
      renderList(type,lf.value,0,facet,facet2); } };
    if(hadFocus){ lf.focus(); try{ lf.setSelectionRange(caret,caret); }catch(e){} }
  }
  let h=`<div class="wrap"><h1>${esc(type||'全部')}</h1>
    <div class="sub">${d.total} 个条目${q?' · 筛「'+esc(q)+'」':''}${facet?' · '+(FACET_LABEL[type]||'分类')+'「'+esc(facet)+'」':''}</div>`;
  if(fc.facets&&fc.facets.length>1){
    h+=`<div class="chips"><span class="clbl">${esc(FACET_LABEL[type]||'分类')}</span>`;
    h+=`<a class="fchip ${!facet?'on':''}" href="${listHash(type,q,0,'')}">全部<span class="n">${fc.total}</span></a>`;
    for(const f of fc.facets.slice(0,48))
      h+=`<a class="fchip ${facet===f.v?'on':''}" href="${listHash(type,q,0,f.v)}">${esc(f.v)}<span class="n">${f.n}</span></a>`;
    h+='</div>';
  }
  if(fc2.facets&&fc2.facets.length>0){
    h+=`<div class="chips"><span class="clbl">主线</span>`;
    h+=`<a class="fchip ${!facet2?'on':''}" href="${listHash(type,q,0,facet,'')}">全部<span class="n">${fc.total}</span></a>`;
    for(const f of fc2.facets)
      h+=`<a class="fchip ${facet2===f.v?'on':''}" href="${listHash(type,q,0,facet,f.v)}">${esc(f.v)}<span class="n">${f.n}</span></a>`;
    h+='</div>';
  }
  h+=`<div class="bar">
      <button onclick="setListSort('default')"${window.LIST_SORT==='default'?' disabled':''}>默认</button>
      <button onclick="setListSort('name')"${window.LIST_SORT==='name'?' disabled':''}>按名称</button>
      <button onclick="setListSort('mentions')"${window.LIST_SORT==='mentions'?' disabled':''}>按引用数</button>
    </div>`;  let rows=d.rows.slice();
  if(window.LIST_SORT==='name') rows.sort((a,b)=>String(a.name).localeCompare(String(b.name),'zh-Hans-CN'));
  else if(window.LIST_SORT==='mentions') rows.sort((a,b)=>(b.mentions||0)-(a.mentions||0));
  for(const r of rows)
    h+=`<div class="listrow"><div class="nm">${r.title?`<span class="ttl">${esc(r.title)}</span>`:''}<a href="#/p/${enc(r.slug)}">${esc(r.name)}</a>
        <span class="mt">　${esc((r.lead||'').slice(0,44))}</span></div>
        <div class="mt">${r.mentions||''}</div></div>`;
  if(!d.rows.length) h+='<div class="empty">没有条目</div>';
  h+='<div class="pager">';
  if(offset>0) h+=`<button onclick="listGo('${esc(type)}','${esc(q)}',${Math.max(0,offset-100)},'${esc(facet||'')}','${esc(facet2||'')}')">上一页</button>`;
  h+=`<span>${offset+1} - ${Math.min(offset+d.rows.length,d.total)} / ${d.total}</span>`;
  if(offset+d.rows.length<d.total) h+=`<button onclick="listGo('${esc(type)}','${esc(q)}',${offset+100},'${esc(facet||'')}','${esc(facet2||'')}')">下一页</button>`;
  h+='</div></div>';
  $('#main').innerHTML=h;
}

/* ---------- 搜索 ---------- */
function setListSort(k){
  window.LIST_SORT=k;
  const h=decodeURIComponent(location.hash.replace(/^#/,''));
  const p=h.split('/');
  if(p[1]==='list'){
    const arg=(p.slice(2).join('/').split('?')[0]||'');
    const qs=new URLSearchParams(h.split('?')[1]||'');
    listGo(arg,qs.get('q')||'',0,qs.get('f')||'',qs.get('f2')||'');
  }
  else if(p[1]==='p' || p[1]==='search'){ route(); }
  else route();
}

async function renderSearch(q){
  const d=await api('/api/search2?q='+enc(q));
  let h=`<div class="wrap"><h1>搜索「${esc(q)}」</h1>`;
  if(d.pages&&d.pages.length){
    h+='<h2>条目</h2>';
    for(const r of d.pages)
      h+=`<div class="listrow"><div class="nm">${r.title?`<span class="ttl">${esc(r.title)}</span>`:''}<a href="#/p/${enc(r.slug)}">${esc(r.name)}</a>
          <span class="mt">　${esc(r.type)}</span></div><div class="mt">${r.mentions||''}</div></div>`;
  }
  if(d.scenes&&d.scenes.length){
    h+='<h2>场景</h2>';
    for(const s of d.scenes)
      h+=`<div class="hit" onclick="go('#/scene/${enc(s.script)}')">
          <div class="h">${esc(s.chapter)} · ${s.line_count} 句</div><div>${esc(s.title||s.script)}</div></div>`;
  }
  if(d.lines&&d.lines.length){
    h+='<h2>原文</h2>';
    for(const l of d.lines)
      h+=`<div class="hit" onclick="go('#/scene/${enc(l.script)}?seq=${l.seq}')">
          <div class="h">${esc(l.script)} · 第${l.seq}句 · ${esc(l.speaker||'')}</div>
          <div>${esc((l.text||'').replace(/\n/g,' '))}</div></div>`;
  }
  if(!(d.pages||[]).length && !(d.scenes||[]).length && !(d.lines||[]).length) h+='<div class="empty">没有结果</div>';
  h+='</div>';
  $('#main').innerHTML=h;
  $('#side').innerHTML='';
}

/* ---------- 条目页 ---------- */
async function renderPage(slug){
  const d=await api('/api/page?slug='+enc(slug));
  const _sd=document.getElementById('side'); if(_sd) _sd.classList.remove('open');
  if(d.error){ $('#main').innerHTML=`<div class="wrap"><div class="empty">未找到条目「${esc(slug)}」<br><br><a href="#/search/${enc(slug.split('/').pop())}">搜索这个词</a> 或 <a href="#/">回首页</a></div></div>`; return; }
  const inf=d.infobox||{};
  let h='<div class="wrap">';
  h+=`<div class="sub" style="margin:0 0 8px">`;
  if(inf["上级"]) h+=`<a href="#/p/${enc(d.type+'/'+inf['上级'])}">← 返回${esc(inf['上级'])}</a>　`;
  h+=`<a href="#/list/${enc(d.type)}">全部${esc(d.type)}</a></div>`;
  if(d.title) h+=`<div class="ttl-badge">${esc(d.title)}</div>`;
  h+=`<h1>${esc(d.name)}</h1><div class="sub"><span class="tag">${esc(d.type)}</span>
      ${d.mentions?d.mentions+' 处提及':''}${d.chapters&&d.chapters.length?' · 首见 '+esc(d.chapters[0]):''}</div>`;
  if(Object.keys(inf).length){
    h+='<div class="infobox"><div class="ttl">'+esc(d.name)+'</div>';
    for(const [k,v] of Object.entries(inf))
      h+=`<div class="row"><div class="k">${esc(k)}</div><div class="v">${linkify(String(v))}</div></div>`;
    h+='</div>';
  }
  if(d.lead) h+=`<div class="lead">${fnmark(linkify(d.lead))}</div>`;
  const SECS=[];
  let _si=0;
  for(const s of (d.sections||[])){
    if(s.h==='简介'){ h+=`<div class="lead">${secHtml(s.html||'')}</div>`; continue; }
    const sid='sec-'+(++_si);
    if(s.h!=='脚注') SECS.push({h:s.h,id:sid});
    h+=`<h2 id="${sid}">${esc(s.h)}</h2>`;
    if(s.notes){
      for(const n of s.notes)
        h+=`<div class="note"><span class="ch">${esc(n.ch)}</span>${linkify(n.text)}
            ${n.ev?`<div class="ev">原文：「${esc(n.ev)}」</div>`:''}</div>`;
    }
    if(s.rows){
      for(const r of s.rows){
        const t=r.slug?`<a class="ch" href="#/p/${enc(r.slug)}">${esc(r.title||r.slug)}</a>`:(r.script?`<a class="ch" href="#/scene/${enc(r.script)}">${esc(r.title||r.script)}</a>`:'');
        let nm=r.note||'', fnnum='';
        if(s.h==='脚注'){
          const m=nm.match(/^(\d+)\.\s*/);
          if(m){ fnnum=m[1]; nm=nm.slice(m[0].length); }
        }
        h+=`<div class="note"${fnnum?` id="fn-${fnnum}"`:''}>${t}`;
        if(fnnum) h+=`<sup class="fn">${fnnum}</sup> `;
        h+=linkify(nm);
        if(r.quote){
          if(r.script){
            const j=r.seq?`?seq=${r.seq}`:'';
            h+=`<div class="ev">原文：<a href="#/scene/${enc(r.script)}${j}">「${esc(r.quote)}」</a></div>`;
          } else h+=`<div class="ev">原文：「${esc(r.quote)}」</div>`;
        }
        if(r.routes&&r.routes.length) h+=`<div class="ev">路线：${esc(r.routes.join('、'))}</div>`;
        h+='</div>';
      }
    }
    if(s.choices){
      h+='<div class="brwrap"><table class="br"><thead><tr><th>抉择</th><th>条件</th><th>后果</th></tr></thead><tbody>';
      for(const c of s.choices){
        const fl=(c.flags||[]).map(x=>`${x.f}=${x.v}`).join('、');
        const sc=(c.scenes||[]).join('、');
        const link=c.seq?`<a href="#/scene/${enc(d.infobox&&d.infobox['脚本']||'')}?seq=${c.seq}">第${c.seq}句</a>`:'';
        h+=`<tr><td><b>${esc(c.text||('#'+c.idx))}</b> ${link}</td>
            <td>${esc(c.cond||'')}</td>
            <td>${fl?`<span class="eff">${esc(fl)}</span>`:''}${sc?`<span class="eff">→ ${esc(sc)}</span>`:''}</td></tr>`;
      }
      h+='</tbody></table></div>';
    }
    if(s.people){
      h+='<div>';
      for(const p of s.people)
        h+=`<a class="chip" href="#/p/${enc('人物/'+p.name)}">${esc(p.name)}<span class="n">${p.n}</span></a>`;
      h+='</div>';
    }
    if(s.html && s.h!=='简介') h+=`<div>${secHtml(s.html)}</div>`;
  }
  const L=d.links||[], groups={};
  for(const x of L) (groups[x.kind]=groups[x.kind]||[]).push(x);
  if(groups['关系']){
    h+='<h2>关系</h2>';
    for(const r of groups['关系'])
      h+=`<div class="rel"><div class="k"><a href="#/p/${enc(r.dst)}">${esc(r.name||r.dst.split('/').pop())}</a></div>
          <div class="v">${esc(r.label||'')}</div></div>`;
  }
  if(groups['归属']){
    h+='<h2>归属</h2><div>';
    for(const r of groups['归属'])
      h+=`<a class="chip" href="#/p/${enc(r.dst)}">${esc(r.name||r.dst.split('/').pop())}</a>`;
    h+='</div>';
  }
  for(const [kind,label,cap] of [['成员','成员',60],
                                 ['发生地','发生地',5],['出场','出场场景',30],['出场场景','出场场景',30]]){
    if(!groups[kind]) continue;
    h+=`<h2>${label}</h2><div>`;
    groups[kind].slice(0,cap).forEach(r=>{
      const nm=r.name||r.dst.split('/').pop();
      h+=`<a class="chip" href="#/p/${enc(r.dst)}">${esc(nm)}${r.label?`<span class="n">${esc(r.label)}</span>`:''}</a>`;
    });
    if(groups[kind].length>cap) h+=`<span class="chip">…共 ${groups[kind].length} 条</span>`;
    h+='</div>';
  }
  if(d.type==='场景' && d.infobox && d.infobox['脚本']){
    h+='<h2>对话</h2><div class="bar"><button onclick="document.querySelectorAll(\'#pgd details.br\').forEach(x=>x.open=true)">展开全部分支</button><button onclick="document.querySelectorAll(\'#pgd details.br\').forEach(x=>x.open=false)">全部折叠</button></div><div id="pgd">';
    try{
      const sc=await api('/api/scene?script='+enc(d.infobox['脚本']));
      if(sc&&sc.lines&&sc.lines.length){
        const cs={};sc.choices.forEach(x=>cs[x.seq]=x);
        const fl={};sc.flags.forEach(f=>{(fl[f.seq]=fl[f.seq]||[]).push(f);});
        let i=0;
        while(i<sc.lines.length){
          const b=sc.lines[i].branch||'';
          let j=i; while(j<sc.lines.length&&(sc.lines[j].branch||'')===b) j++;
          const body=sc.lines.slice(i,j).map(l=>lineHtml(l,cs,fl)).join('');
          if(b) h+=`<details class="br"><summary title="${esc(b)}">${esc(shortBr(b))}</summary><div class="body">${body}</div></details>`;
          else h+=body;
          i=j;
        }
      }
    }catch(e){}
    h+='</div>';
    h+=`<div class="bar"><button onclick="go('#/scene/${enc(d.infobox['脚本'])}')">读这一场原文</button></div>`;
  }
  const back=(d.backlinks||[]).filter(x=>x.kind!=='出场场景');
  if(back.length){
    h+='<h2>链入页面</h2><div>';
    const seen=new Set();
    for(const b of back){
      const nm=b.name||b.src.split('/').pop();
      const key=b.src;
      if(seen.has(key)) continue;
      seen.add(key);
      if(seen.size>40) break;
      h+=`<a class="chip" href="#/p/${enc(b.src)}">${esc(nm)}<span class="n">${esc(b.kind)}</span></a>`;
    }
    if(back.length>40) h+=`<span class="chip">…共 ${back.length} 条</span>`;
    h+='</div>';
  }
  if(d.cats&&d.cats.length){
    h+='<div class="cats">分类：';
    for(const c of d.cats){
      const typ=['人物','势力','地点','事件','地图事件','书物','物品','武学','成就','装备','场景'].includes(c);
      h+=typ?`<a class="tag" href="#/list/${enc(c)}">${esc(c)}</a>`:`<span class="tag">${esc(c)}</span>`;
    }
    h+='</div>';
  }
  h+='</div>';
  $('#main').innerHTML=h;
  renderSideFor(d,SECS);
}

async function randomPage(){
  try{
    const a=await api('/api/pages?type=&q=&offset=0&limit=1');
    const total=a.total||0;
    if(!total) return;
    const off=Math.floor(Math.random()*total);
    const b=await api('/api/pages?type=&q=&offset='+off+'&limit=1');
    const row=(b.rows||[])[0];
    if(row) go('#/p/'+enc(row.slug));
  }catch(e){}
}

function jumpSec(id){
  const el=document.getElementById(id);
  if(el){ el.scrollIntoView({behavior:'smooth',block:'start'}); }
}

function renderSideFor(d,secs){
  let s='';
  if(secs && secs.length>2){
    s+='<div class="grp">本页目录</div>';
    for(const x of secs)
      s+=`<a class="item" href="javascript:void 0" onclick="jumpSec('${x.id}');return false">${esc(x.h)}</a>`;
  }
  const L=d.links||[];
  const rel=L.filter(x=>x.kind==='关系').slice(0,40);
  if(rel.length){
    s+='<div class="grp">关系</div>';
    for(const r of rel)
      s+=`<a class="item" href="#/p/${enc(r.dst)}">${esc(r.name||r.dst.split('/').pop())}</a>`;
  }
  const sc=L.filter(x=>x.kind==='出场'||x.kind==='出场场景').slice(0,40);
  if(sc.length){
    s+='<div class="grp">出场场景</div>';
    for(const r of sc)
      s+=`<a class="item" href="#/p/${enc(r.dst)}">${esc(r.name||r.dst.split('/').pop())}</a>`;
  }
  const mem=L.filter(x=>x.kind==='成员').slice(0,60);
  if(mem.length){
    s+='<div class="grp">成员</div>';
    for(const r of mem)
      s+=`<a class="item" href="#/p/${enc(r.dst)}">${esc(r.name||r.dst.split('/').pop())}</a>`;
  }
  $('#side').innerHTML=s||'<div class="grp">条目</div><a class="item" href="#/">返回首页</a>';
}

/* ---------- 章节与场景原文 ---------- */
async function renderChapters(){
  const d=await api('/api/scenes');
  let h='<div class="wrap"><h1>原文</h1><div class="sub">按章节浏览全部场景</div>';
  for(const c of d.chapters){
    h+=`<h2>${esc(c.chapter)}${c.name?' · '+esc(c.name):''} <span class="mt">${c.n} 场</span></h2><div>`;
    for(const s of d.scenes.filter(x=>x.chapter===c.chapter))
      h+=`<a class="chip" href="#/scene/${enc(s.script)}">${esc(s.title||s.script)}<span class="n">${s.line_count}</span></a>`;
    h+='</div>';
  }
  h+='</div>';
  $('#main').innerHTML=h;
  $('#side').innerHTML='';
}

function lineHtml(l,cs,fl){
  let extra='';
  const c=cs[l.seq];
  if(c){
    let req='';
    if(c.title) req+=`<span class="cond">判定：${esc(c.title)}</span>`;
    if(c.requires&&c.requires.length) req+=c.requires.map(r=>`<span class="cond">出现条件：${esc(r)}</span>`).join('');
    if(c.cond_text&&c.cond_text.length) req+=c.cond_text.map(r=>`<span class="cond">属性检定：${esc(r)}</span>`).join('');
    const opts=(c.options||[]).map(o=>{
      const name=o.text||o.label||o.key||'';
      return `<span class="opt"><b>${esc(name)}</b>${o.cond?' → 掷骰 '+esc(o.cond):''}</span>`;
    }).join('');
    extra+=`<div class="choice"><div class="ch">◆ ${esc(c.checkpoint)}</div>${req}
      <div style="margin-top:6px">${opts||'<span class="cond">（此判定无预设选项文案）</span>'}</div></div>`;
  }
  if(fl[l.seq]) extra+=`<div class="flagline">⤷ ${fl[l.seq].map(f=>`<span class="opt">${esc(f.flag)} = ${esc(f.value)}</span>`).join('')}</div>`;
  return `<div class="line ${cls(l.mode)}" data-seq="${l.seq}">
      <div class="sp">${TITLES[l.speaker]?`<i class="spt">${esc(TITLES[l.speaker])}</i>`:''}${esc(l.speaker)}<span>${badge(l.mode)}</span></div>
      <div class="tx">${rich(l.text)||'<i style="color:#5b616b">（缺文本）</i>'}<span class="key">${esc(l.key)}</span></div>
    </div>`+extra;
}
function shortBr(b){ const a=(b||'').split(' > '); return a.length>2?'… › '+a.slice(-2).join(' › '):b; }

async function renderScene(sid,jump){
  const [script,qs]=String(sid).split('?');
  if(!jump && qs){ const m=new URLSearchParams(qs).get('seq'); if(m) jump=m; }
  const d=await api('/api/scene?script='+enc(script));
  if(!d.scene) { $('#main').innerHTML='<div class="wrap"><div class="empty">场景不存在</div></div>'; return; }
  const cs={},fl={};
  d.choices.forEach(c=>cs[c.seq]=c);
  d.flags.forEach(f=>{(fl[f.seq]=fl[f.seq]||[]).push(f);});
  const brs=d.branches||{};
  TITLES=d.titles||{};
  let h=`<div class="wrap"><h1>${esc(d.scene.title||d.scene.script)}</h1>
    <div class="sub"><span class="tag">${esc(d.scene.chapter)}</span>
    <a href="#/p/${enc('场景/'+d.scene.script)}">场景条目</a> · ${d.scene.line_count} 句 · ${d.scene.cjk} 字</div>`;
  if(d.scene.place) h+=`<div class="sub">地点：<a href="#/p/${enc('地点/'+d.scene.place)}">${esc(d.scene.place)}</a></div>`;
  if(d.participants&&d.participants.length)
    h+='<div class="sub">参与：'+d.participants.map(p=>`<span class="chip">${esc(p.nm)} ${p.n}</span>`).join('')+'</div>';
  h+=`<div class="bar"><button id="exp">展开全部分支</button><button id="col">全部折叠</button></div>`;
  let i=0,out='';
  while(i<d.lines.length){
    const b=d.lines[i].branch||'';
    let j=i; while(j<d.lines.length && (d.lines[j].branch||'')===b) j++;
    const body=d.lines.slice(i,j).map(l=>lineHtml(l,cs,fl)).join('');
    if(b){
      out+=`<details class="br"><summary title="${esc(b)}">${esc(shortBr(b))}</summary><div class="body">${body}</div></details>`;
    } else out+=body;
    i=j;
  }
  $('#main').innerHTML=h+out+'</div>';
  $('#side').innerHTML='';
  if(jump){
    const el=$('#main').querySelector('.line[data-seq="'+jump+'"]');
    if(el){ let p=el.parentElement; while(p&&p!==$('#main')){ if(p.tagName==='DETAILS') p.open=true; p=p.parentElement; }
      el.scrollIntoView({block:'center'}); el.style.background='#3a2f1d'; }
  }
  $('#exp').onclick=()=>document.querySelectorAll('details.br').forEach(x=>x.open=true);
  $('#col').onclick=()=>document.querySelectorAll('details.br').forEach(x=>x.open=false);
}

/* ---------- 内容版本检查（单机程序内刷新） ---------- */
(function(){
  let v0=null;
  async function chk(){
    try{
      const r=await fetch('/api/version',{cache:'no-store'});
      const d=await r.json();
      const b=document.getElementById('rf');
      if(v0 && d.v!==v0 && b){ b.classList.add('new'); b.title='内容已更新，点一下重新加载'; }
      v0=d.v;
    }catch(e){}
  }
  setTimeout(chk,1200); setInterval(chk,15000);
})();

/* ---------- 搜索框 ---------- */
let qtm=null;
$('#q').addEventListener('input',e=>{
  clearTimeout(qtm);
  const v=e.target.value.trim();
  qtm=setTimeout(()=>{ if(v) go('#/search/'+enc(v)); },260);
});
$('#q').addEventListener('keydown',e=>{ if(e.key==='Enter'){ const v=e.target.value.trim(); if(v) go('#/search/'+enc(v)); }});

(async()=>{ await loadIndex(); route(); })();

/* 快捷键与回到顶部 */
window.addEventListener('scroll',()=>{
  const b=document.getElementById('totop');
  if(b) b.classList.toggle('on',(window.scrollY||0)>600);
});
document.addEventListener('keydown',e=>{
  const tag=(e.target.tagName||'').toUpperCase();
  if(e.key==='/' && tag!=='INPUT' && tag!=='TEXTAREA'){ e.preventDefault(); const q=$('#q'); q.focus(); q.select(); }
  if(e.key==='Escape' && document.activeElement && document.activeElement.id==='q'){
    document.activeElement.value=''; document.activeElement.blur();
  }
  if(e.key==='Backspace' && e.altKey){ e.preventDefault(); goBack(); }
});
