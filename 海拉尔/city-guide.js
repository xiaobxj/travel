/* Place-level synthesis on the existing map. Inlined by build_ui.py. */
(() => {
'use strict';
function validCount(v){return typeof v==='number'&&Number.isFinite(v)&&v>=0}
function score(n){return ['likes','collects','comments'].every(k=>validCount(n[k]))?n.likes+n.collects+n.comments:null}
function sortedNotes(rows){return rows.slice().sort((a,b)=>{const x=score(a),y=score(b);if(x===null&&y!==null)return 1;if(y===null&&x!==null)return -1;return (y??0)-(x??0)||String(a.id).localeCompare(String(b.id))})}
function filterRows(rows,cityId,options){return sortedNotes(rows.filter(n=>(n.cityIds||[]).includes(cityId)&&(options.category==='all'||(n.categories||[]).includes(options.category))&&(!options.excludeAds||!n.suspectedAd)&&(!options.complete||score(n)!==null)&&(!options.minimum||(score(n)!==null&&score(n)>=options.minimum))&&(!options.text||[n.title,n.cityExcerpts?.[cityId],n.excerpt,n.author].join(' ').toLocaleLowerCase().includes(options.text.toLocaleLowerCase()))))}

function routeReady(x){return x.placeCheck?.status==='verified'&&x.placeCheck?.comparisonStatus==='ready'}
function routeSeconds(x){return routeReady(x)?x.placeCheck.addedSeconds:Infinity}
function routeBand(x){const s=routeSeconds(x);return s<=600?0:s<=1800?1:s<Infinity?2:3}
function supportTier(x){return x.recommendCount>0?(x.cautionCount?1:0):(x.cautionCount?3:2)}
function rankItems(rows, order='recommend'){
 return rows.slice().sort((a,b)=>{
  const count=b.recommendCount-a.recommendCount, evidence=b.strength-a.strength;
  if(order==='route')return Number(routeReady(b))-Number(routeReady(a))||supportTier(a)-supportTier(b)||routeBand(a)-routeBand(b)||evidence||routeSeconds(a)-routeSeconds(b)||count||a.name.localeCompare(b.name,'zh-CN');
  if(order==='detour')return Number(routeReady(b))-Number(routeReady(a))||routeSeconds(a)-routeSeconds(b)||evidence||count||a.name.localeCompare(b.name,'zh-CN');
  return (order==='evidence'?evidence||count:count||evidence)||a.cautionCount-b.cautionCount||a.name.localeCompare(b.name,'zh-CN');
 });
}
function selectItems(rows,cityId,filters){return rankItems(rows.filter(x=>x.cityId===cityId&&(filters.category==='all'||x.category===filters.category)&&x.recommendCount>=filters.minimum&&(!filters.verified||x.placeCheck?.status==='verified')&&(!filters.maxMinutes||(routeReady(x)&&routeSeconds(x)<=filters.maxMinutes*60))&&(!filters.text||[x.name,x.summary,x.experience,x.caution,x.placeCheck?.poi?.name,x.placeCheck?.poi?.address].join(' ').toLocaleLowerCase().includes(filters.text.toLocaleLowerCase()))),filters.order)}
if(typeof module!=='undefined'&&typeof document==='undefined'){module.exports={score,sortedNotes,filterRows,rankItems,selectItems};return}
const guide=DATA.cityGuide, cities=guide.cities, notes=guide.notes||[], esc=escapeHTML;
const synthesis=guide.recommendations, items=synthesis.items, categories=synthesis.categories;
const noteMap=new Map(notes.map(n=>[n.id,n]));
let current=cities[0].id;
const filters={category:'all',text:'',minimum:0,order:'route',verified:true,maxMinutes:0};
const byId=id=>cities.find(c=>c.id===id);
const panel=document.createElement('aside');panel.className='city-guide';panel.id='cityGuide';panel.setAttribute('aria-label','城市吃喝玩乐总结');
document.querySelector('.workspace').appendChild(panel);
document.querySelector('.top-actions').insertAdjacentHTML('afterbegin','<button id="cityGuideToggle" class="quiet city-guide-toggle">城市详情</button>');
document.querySelector('.mobile-switch').insertAdjacentHTML('beforeend','<button data-city-view="true">城市</button>');
const layer=el('g',{id:'cityPinLayer'},map);
const placeLayer=el('g',{id:'recommendationPinLayer'},map);let focusedPlace=null;
function filteredNotes(cityId,options){return filterRows(notes,cityId,options||{category:'all',complete:false,minimum:0,excludeAds:false,text:''})}
function safeURL(raw){try{const u=new URL(raw);return u.protocol==='https:'&&(u.hostname==='xiaohongshu.com'||u.hostname.endsWith('.xiaohongshu.com'))?u.href:'#'}catch{return '#'}}
function num(v){return validCount(v)?v.toLocaleString('zh-CN'):'未读取'}
function km(v){return v<100?'不足 0.1':(v/1000).toFixed(1)}
function minutes(v){return v<60?'不足 1':String(Math.round(v/60))}
function amapURL(p){const u=new URL('https://uri.amap.com/marker');u.searchParams.set('position',p.location);u.searchParams.set('name',p.name);u.searchParams.set('src','hailaer_itinerary');u.searchParams.set('coordinate','gaode');u.searchParams.set('callnative','0');return u.href}
function placeHTML(x){
 const p=x.placeCheck;
 if(!p||p.status!=='verified')return `<div class="place-unverified">地点待核对：${esc(p?.reason||'尚未获得唯一固定地点')}</div>`;
 const address=typeof p.poi.address==='string'&&p.poi.address?p.poi.address:'高德未提供详细门牌';
 if(p.currentRouteLegOnly)return `<div class="place-check"><div class="place-verified">高德已核点 · 10月${p.day+1}日行程补充</div><div class="place-name">${esc(p.poi.name)}</div><p class="place-address">${esc(p.poi.adname||'')} · ${esc(address)}</p><p class="place-anchor">从${esc(p.anchorName)}驾车 ${km(p.fromAnchor.meters)} km / ${minutes(p.fromAnchor.seconds)} 分钟</p><p class="place-footnote">${esc(p.comparisonNote)}</p><div class="place-actions"><button data-focus-place="${esc(x.id)}">在原图定位</button><a href="${esc(amapURL(p.poi))}" target="_blank" rel="noopener noreferrer">高德查看 ↗</a></div><details class="place-calculation"><summary>查验依据</summary><p>${esc(p.matchReason)}</p><p>单程 ${p.fromAnchor.meters} 米 / ${p.fromAnchor.seconds} 秒；高德查询 ${esc(p.queriedAt.replace('T',' ').slice(0,19))}。游玩、步行与排队另计。</p></details></div>`;
 if(p.currentRouteEvidence)return `<div class="place-check"><div class="place-verified">高德已核点 · 10月3日补充</div><div class="place-name">${esc(p.poi.name)}</div><p class="place-address">${esc(p.poi.adname||'')} · ${esc(address)}</p><div class="route-metrics"><div><span>整线增加距离</span><strong>＋${km(p.addedMeters)} km</strong></div><div><span>整线增加驾驶</span><strong>＋${minutes(p.addedSeconds)} 分钟</strong></div></div>${p.fromAnchor?`<p class="place-anchor">从${esc(p.anchorName)}驾车 ${km(p.fromAnchor.meters)} km / ${minutes(p.fromAnchor.seconds)} 分钟</p>`:''}<p class="place-footnote">${esc(p.comparisonNote)}</p><div class="place-actions"><button data-focus-place="${esc(x.id)}">在原图定位</button><a href="${esc(amapURL(p.poi))}" target="_blank" rel="noopener noreferrer">高德查看 ↗</a></div><details class="place-calculation"><summary>查验依据</summary><p>${esc(p.matchReason)}</p><p>基准 ${(p.baseline.meters/1000).toFixed(1)} km / ${(p.baseline.seconds/60).toFixed(1)} 分钟；加入后 ${(p.withStop.meters/1000).toFixed(1)} km / ${(p.withStop.seconds/60).toFixed(1)} 分钟。仅含驾驶，游玩和步行另计。</p><p>高德查询 ${esc(p.queriedAt.replace('T',' ').slice(0,19))}，参考点为城镇政府或公园POI，具体酒店和步行入口另核。</p></details></div>`;
 return `<div class="place-check"><div class="place-verified">高德已核点${p.kind==='entrance'?' · 按入口／停车点计算':''}</div><div class="place-name">${esc(p.poi.name)}</div><p class="place-address">${esc(p.poi.adname)} · ${esc(address)}</p><div class="route-metrics"><div><span>距历史路线对照段（几何）</span><strong>${km(p.routeOffsetMeters)} km</strong></div><div><span>加入该路段后</span><strong>${routeReady(x)?'＋'+km(p.addedMeters)+' km':'增量待核对'}</strong></div><div><span>额外驾驶</span><strong>${routeReady(x)?'＋'+minutes(p.addedSeconds)+' 分钟':'暂不排名'}</strong></div></div>${p.fromAnchor?`<p class="place-anchor">从${esc(p.anchorName)}驾车 ${km(p.fromAnchor.meters)} km / ${minutes(p.fromAnchor.seconds)} 分钟</p>`:''}<p class="place-route">历史对照 D${p.day}：${esc(p.from)} → ${p.mandatoryVia?.length?esc(p.mandatoryVia.join(' → '))+' → ':''}${esc(p.to)}</p>${routeReady(x)?'<p class="place-footnote">仅含对照路线的驾驶增量；停车、吃饭、步行和游玩另计。</p>':`<p class="place-footnote">${esc(p.comparisonNote)}</p>`}<div class="place-actions"><button data-focus-place="${esc(x.id)}">在原图定位</button><a href="${esc(amapURL(p.poi))}" target="_blank" rel="noopener noreferrer">高德查看 ↗</a></div><details class="place-calculation"><summary>距离依据</summary><p>POI：${esc(p.poi.id)}。${esc(p.matchReason)}</p><p>距离为高德坐标到历史行程折线的几何距离，不代表可直达；参考点为地图中既有城市／停靠点，不是你的酒店。</p>${!p.evidenceIssue&&p.baseline&&p.withStop?`<p>同批次高德重算：原路段 ${(p.baseline.meters/1000).toFixed(2)} km / ${(p.baseline.seconds/60).toFixed(1)} 分钟；插点后 ${(p.withStop.meters/1000).toFixed(2)} km / ${(p.withStop.seconds/60).toFixed(1)} 分钟。原始差值 ${(p.rawDeltaMeters/1000).toFixed(2)} km / ${(p.rawDeltaSeconds/60).toFixed(1)} 分钟。小幅负差按约零显示；明显负差单独标记。</p>`:''}<p>保留原起终点及强制途经点，高德推荐策略 32；日期 ${esc(p.fromAnchor?.queriedAt?.slice(0,10)||p.queriedAt.slice(0,10))}，不是国庆路况预测。</p></details></div>`;
}
function dayLinks(c){return c.days.map(d=>`<button data-city-day="${d}">10 / ${d+1} · D${d}</button>`).join('')}
function sourceHTML(r){
 const n=noteMap.get(r.noteId), labels={positive:'支持',mixed:'有保留',negative:'负面反馈',mention:'仅提及'};
 return `<li><div class="source-heading"><span class="stance ${r.stance}">${labels[r.stance]}</span><a href="${esc(safeURL(n.url))}" target="_blank" rel="noopener noreferrer">${esc(n.title)} ↗</a></div><p>${esc(r.basis)}</p><div class="source-meta">${esc(n.author||'作者未读取')} · 发布 ${esc(n.publishedAt?.slice(0,10)||'日期未读取')}<br>赞 ${num(n.likes)} · 藏 ${num(n.collects)} · 评 ${num(n.comments)}${score(n)!==null?' · 合计 '+(n.approximate?'约 ':'')+num(score(n)):''}<br>采集 ${esc((n.capturedAt||'').replace('T',' ').slice(0,16))}${n.suspectedAd?' · 疑似推广，不计推荐票':''}</div></li>`;
}
function itemHTML(x,index){
 return `<article class="recommendation"><div class="recommendation-head"><span class="recommendation-rank">${String(index+1).padStart(2,'0')}</span><h4>${esc(x.name)}</h4></div><div class="evidence-row"><span class="support-count">${x.recommendCount} 位作者推荐</span><span class="evidence-level ${x.cautionCount?'disputed':''}">${esc(x.evidenceLabel)}</span>${x.cautionCount?`<span>${x.cautionCount} 位有保留</span>`:''}</div><p class="recommendation-summary">${esc(x.summary)}</p>${placeHTML(x)}<dl class="recommendation-facts"><div><dt>${x.category==='eat'?'怎么点':x.category==='drink'?'怎么选':'怎么玩'}</dt><dd>${esc(x.experience)}</dd></div><div><dt>留意</dt><dd>${esc(x.caution)}</dd></div><div class="route-fit"><dt>行程建议</dt><dd>${esc(x.routeFit)}</dd></div></dl>${x.sourceCount?`<details class="recommendation-sources"><summary>帖子依据 · ${x.sourceCount} 篇 / ${x.authorCount} 组作者</summary><ul>${x.reviews.map(sourceHTML).join('')}</ul></details>`:'<p class="source-gap">暂无可归属该店／场所的实体验笔记，仅保留高德固定地点线索。</p>'}</article>`;
}
function renderResults(){
 const rows=selectItems(items,current,filters), all=items.filter(x=>x.cityId===current);
 document.getElementById('cityResultInfo').textContent=`${rows.length} / ${all.length} 项 · ${({route:'顺路＋证据',detour:'额外驾驶从少到多',evidence:'证据强度优先',recommend:'推荐作者数优先'})[filters.order]}${filters.verified?' · 只看高德已核点':''}${filters.maxMinutes?' · 额外驾驶 ≤ '+filters.maxMinutes+' 分钟':''}${filters.minimum?' · 至少 '+filters.minimum+' 位推荐':''}`;
 panel.querySelectorAll('[data-guide-category]').forEach(b=>{const active=b.dataset.guideCategory===filters.category;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
 document.getElementById('cityResults').innerHTML=categories.filter(cat=>filters.category==='all'||filters.category===cat.id).map(cat=>{
  const selected=rows.filter(x=>x.category===cat.id), existing=all.filter(x=>x.category===cat.id);
  return `<section class="guide-section" aria-labelledby="heading-${cat.id}"><div class="guide-section-heading"><h3 id="heading-${cat.id}"><span class="category-symbol ${cat.id}">${cat.name}</span>${({eat:'餐厅与招牌菜',drink:'咖啡、奶茶与冷饮',play:'景点与沿途风景',fun:'参与体验与闲逛'})[cat.id]}</h3><span>${selected.length} 项</span></div><p class="section-takeaway">${esc(synthesis.sectionSummaries[current][cat.id])}</p>${selected.length?selected.map(itemHTML).join(''):existing.length?'<div class="city-empty">当前条件下没有项目。可调整筛选；未核到唯一高德地点的旧资料默认隐藏。</div>':'<div class="evidence-gap">证据不足 · 暂不编排名</div>'}</section>`;
 }).join('');
}
function renderPanelCity(){
 const c=byId(current), attempt=guide.lastAttempt;
 panel.innerHTML=`<button class="city-guide-close" id="cityGuideClose" aria-label="关闭城市详情">×</button><div class="city-kicker">沿途吃喝玩乐</div><label for="citySelect" class="visually-hidden">选择城市或停靠点</label><select id="citySelect">${cities.map(x=>`<option value="${esc(x.id)}" ${x.id===current?'selected':''}>${esc(x.name)} · ${esc(x.kind)}</option>`).join('')}</select><h2>${esc(c.name)}</h2><p class="city-overview">${esc(synthesis.overviews[current])}</p><div class="city-day-links">${dayLinks(c)}</div><p class="amap-sample">全程 ${synthesis.amapUniquePois} 个固定地点已核对高德，距离与帖子证据分别展示。</p><div class="guide-category-nav" aria-label="筛选吃喝玩乐"><button data-guide-category="all" aria-pressed="true">全部</button>${categories.map(x=>`<button data-guide-category="${x.id}" aria-pressed="false">${x.name}</button>`).join('')}</div><details class="guide-filter-details"><summary>排序与筛选</summary><div class="city-filters"><label>排序<select id="cityOrder"><option value="route" ${filters.order==='route'?'selected':''}>顺路＋证据</option><option value="detour" ${filters.order==='detour'?'selected':''}>额外驾驶最少</option><option value="recommend" ${filters.order==='recommend'?'selected':''}>推荐作者数优先</option><option value="evidence" ${filters.order==='evidence'?'selected':''}>证据强度优先</option></select></label><label>至少几位推荐<input id="cityMinimum" type="number" min="0" step="1" value="${filters.minimum}"></label><label>最多额外驾驶<select id="cityMaxMinutes">${[[0,'不限'],[10,'10 分钟'],[20,'20 分钟'],[30,'30 分钟'],[60,'60 分钟']].map(([v,label])=>`<option value="${v}" ${filters.maxMinutes===v?'selected':''}>${label}</option>`).join('')}</select></label><label class="wide"><input id="cityVerified" type="checkbox" ${filters.verified?'checked':''}> 只看高德核到的固定地点</label><label class="wide">查找项目<input id="citySearch" type="search" placeholder="店名、招牌菜或体验" value="${esc(filters.text)}"></label></div></details><div id="cityResultInfo" class="city-result-info" role="status"></div><div id="cityResults"></div><details class="guide-method"><summary>这些排名怎么来的</summary><p>默认“顺路＋证据”：先看驾车增量可比较的地点，再按有正面支持且无分歧、有分歧、仅线索、负面反馈分层；各层按额外驾驶 10 分钟内、30 分钟内、30 分钟以上分组，同组先看证据强度，再比较驾驶分钟数。</p><p>${esc(synthesis.method)}</p><p>距离使用<a href="https://lbs.amap.com/api/webservice/guide/api/newroute" target="_blank" rel="noopener noreferrer">高德驾车 API</a>。每项选其关联日期中距原路线最近的一条路段作比较，不代表穷举全行程后的最小绕行。保留原起终点和强制途经点，用同批次基准减法计算增量；10月3日主线采用觉乐方案，10月4日主线采用红豆坡＋一目九岭自驾方案。新地点分别展示整线比较或单程车程；其他项目保留各自日期的历史路线对照，不代表新路线的绕行增量。</p><p>高德登记证明能核对到地点，不等于营业或口味得到验证。无独立笔记的地点标“暂无笔记支持”。</p><p>“多篇交叉支持”至少 3 组作者明确推荐且没有负面或混合评价；2 组为“两位作者支持”，1 组为“单篇参考”。负面或混合反馈单独标记，同票优先无分歧项目。</p><p>按公开昵称保守去重，并合并高度相似正文，无法验证真人身份。路线罗列不当作推荐，商铺所在城市按正文核对。互动数缺项的笔记仍可提供具体体验证据。</p><p>当前共 ${synthesis.sampleNotes} 篇采集记录，${synthesis.reviewedNotes} 篇用于 ${items.length} 项具体总结。仅归纳文字内容，不推断未读图片中的店名。历史价格、时刻和营业信息需临行确认；“行程建议”是结合你的路线做的安排。</p><p>整理于 ${esc(synthesis.generatedAt.replace('T',' ').slice(0,16))}。</p></details>${attempt&&attempt.status!=='complete'?`<div class="city-status">本轮采集${attempt.status==='blocked'?'受阻':'尚未完成'}，以上为已保存资料的总结。</div>`:''}`;
 renderResults();
}

function scalePlacePin(){
 if(!focusedPlace)return;
 const p=focusedPlace.placeCheck,scale=box[2]/Math.max(1,map.clientWidth);
 placeLayer.setAttribute('transform',`translate(${p.xy[0]} ${p.xy[1]}) scale(${scale})`);
}
function drawPlacePin(){
 placeLayer.replaceChildren();if(!focusedPlace)return;
 const p=focusedPlace.placeCheck;
 el('circle',{r:13,fill:'#b56837',stroke:'#fff','stroke-width':3},placeLayer);
 el('circle',{r:3,fill:'#fff'},placeLayer);
 const name=el('text',{x:19,y:5,class:'fixed-place-label'},placeLayer);name.textContent=p.poi.name;
 const title=el('title',{},placeLayer);title.textContent=focusedPlace.name+' · '+p.poi.location;
 scalePlacePin();
}
function focusPlace(id){
 const item=items.find(x=>x.id===id);if(item?.placeCheck?.status!=='verified')return;
 focusedPlace=item;
 if(matchMedia('(max-width:720px)').matches){closeCity();document.body.classList.add('mobile-map');document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view==='map'))}
 else if(matchMedia('(max-width:1180px)').matches)document.body.classList.remove('city-guide-open');
 const xy=item.placeCheck.xy,w=100,h=w*box[3]/box[2];
 moveBox([xy[0]-w/2,xy[1]-h/2,w,h]);drawPlacePin();
 $('status').textContent='高德核点：'+item.placeCheck.poi.name;
}

function scaleCityPins(){const scale=box[2]/Math.max(1,map.clientWidth);layer.querySelectorAll('[data-city]').forEach(g=>{const c=byId(g.dataset.city),p=DATA.pois[c.poi];g.setAttribute('transform',`translate(${p.xy[0]} ${p.xy[1]}) scale(${scale})`)})}
function drawPins(){
 layer.replaceChildren();
 cities.forEach((c,i)=>{
  const g=el('g',{'class':'city-pin'+(c.id===current?' active':''),'data-city':c.id,tabindex:0,role:'button','aria-label':'查看'+c.name+'吃喝玩乐'},layer);
  // Separate nearby destination labels with leaders to the unchanged map coordinates.
  const offset={aoluguya:[-24,34],shiwei:[-26,24]}[c.id]||[0,0];
  if(offset[0]||offset[1])el('line',{x1:0,y1:0,x2:offset[0],y2:offset[1],stroke:'#63816a','stroke-width':1,'stroke-dasharray':'2 2'},g);
  const pin=el('g',{transform:`translate(${offset[0]} ${offset[1]})`},g);
  el('path',{d:'M0 0C-4-6-11-12-11-20a11 11 0 1 1 22 0C11-12 4-6 0 0Z'},pin);
  const num=el('text',{x:0,y:-17,'text-anchor':'middle',class:'pin-number'},pin);num.textContent=i+1;
  const label=el('text',{x:offset[0]<0?-14:14,y:-18,'text-anchor':offset[0]<0?'end':'start',class:'pin-label'},pin);label.textContent=c.name;
  g.addEventListener('click',()=>{if(!suppressClick)selectCity(c.id)});
  g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectCity(c.id)}});
 });
 scaleCityPins();
 const keys=new Set(cities.map(c=>c.poi));
 document.querySelectorAll('#pinLayer [data-poi]').forEach(g=>{if(keys.has(g.dataset.poi))g.style.display='none'});
}
function showCity(){document.body.classList.add('city-guide-open');if(matchMedia('(max-width:720px)').matches){document.body.classList.add('mobile-city');document.body.classList.remove('mobile-map');document.querySelectorAll('[data-view]').forEach(b=>b.classList.remove('active'));document.querySelector('[data-city-view]').classList.add('active')}}
function closeCity(){document.body.classList.remove('city-guide-open','mobile-city');document.querySelector('[data-city-view]').classList.remove('active');if(matchMedia('(max-width:720px)').matches)document.querySelector('[data-view="list"]').classList.add('active')}
function selectCity(id,{focus=false,open=true}={}){if(!byId(id))return;current=id;focusedPlace=null;placeLayer.replaceChildren();renderPanelCity();panel.scrollTop=0;drawPins();if(open)showCity();if(focus){const p=DATA.pois[byId(id).poi];moveBox([p.xy[0]-box[2]/2,p.xy[1]-box[3]/2,box[2],box[3]])}$('status').textContent='已显示'+byId(id).name+'吃喝玩乐'}

panel.addEventListener('change',e=>{const t=e.target;if(t.id==='citySelect'){selectCity(t.value,{focus:true});return}if(t.id==='cityOrder')filters.order=t.value;else if(t.id==='cityVerified')filters.verified=t.checked;else if(t.id==='cityMaxMinutes')filters.maxMinutes=Number(t.value);else return;renderResults()});
panel.addEventListener('input',e=>{if(e.target.id==='citySearch')filters.text=e.target.value.trim();else if(e.target.id==='cityMinimum')filters.minimum=Math.max(0,Math.floor(Number(e.target.value)||0));else return;renderResults()});
panel.addEventListener('click',e=>{if(e.target.closest('#cityGuideClose'))closeCity();const place=e.target.closest('[data-focus-place]');if(place)focusPlace(place.dataset.focusPlace);const category=e.target.closest('[data-guide-category]');if(category){filters.category=category.dataset.guideCategory;renderResults()}const day=e.target.closest('[data-city-day]');if(day){selectDay(Number(day.dataset.cityDay));if(matchMedia('(max-width:720px)').matches)closeCity()}});
$('cityGuideToggle').onclick=()=>{if(document.body.classList.contains('city-guide-open'))closeCity();else showCity()};document.querySelector('[data-city-view]').onclick=showCity;
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{document.body.classList.remove('mobile-city');document.querySelector('[data-city-view]').classList.remove('active')}));
const previousScalePins=scalePins;scalePins=function(){previousScalePins();scaleCityPins();scalePlacePin()};
const previousRenderMap=renderMap;renderMap=function(){previousRenderMap();drawPins();drawPlacePin()};
const previousSelectPoi=selectPoi;selectPoi=function(name){previousSelectPoi(name);if(suppressClick)return;const city=cities.find(c=>c.poi===name);if(city)selectCity(city.id)};
window.CityGuide={score,sortedNotes,filteredNotes,selectCity,rankItems,selectItems,focusPlace};
renderPanelCity();drawPins();
})();
