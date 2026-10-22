"""Update source UI and preserve existing day 2 personal records."""
from pathlib import Path
ROOT=Path(__file__).parent
path=ROOT/'itinerary-ui.html'
s=path.read_text(encoding='utf-8')
s=s.replace("2:[null,'敖鲁古雅停车场','得耳布尔','莫尔道嘎']", "2:DATA.activities.days[1].items.map(a=>a.poi||null)")
s=s.replace("function renderMap(){const active=routeNames(state.day);", "function renderMap(){const active=routeNames(state.day);if(state.poi)active.add(state.poi);")
s=s.replace("fitPoints(dayRoutes(state.day).flatMap(r=>r.points),animate)", "fitPoints([...dayRoutes(state.day).flatMap(r=>r.points),...(state.poi&&DATA.pois[state.poi]?[DATA.pois[state.poi].xy]:[])],animate)")
s=s.replace("state.poi?'地图标出附近主线落点；具体入口与支线以现场为准。'", "state.poi?(a.poi?'地图标出已核高德地点；停车及步行入口以现场为准。':'地图标出附近主线落点；具体入口与支线以现场为准。')")
s=s.replace('路线查询 2026/09/06 · 不含景区内部驾驶', 'D2 更新 10/3 · 其余主线 9/6 · 不含游玩')
s=s.replace('来自 2026/09/06 高德路线查询。它不是国庆当天的交通预测', '高德查询：10月3日主线更新于2026/10/03，其余日期主线为2026/09/06。车程是查询时估算')
s=s.replace('主线车程查询于2026/09/06，不保证国庆期间交通、天气或道路开放情况。', "${day===2?'当天车程于2026/10/03 08:30–08:35用高德查验，起点采用根河市政府，终点采用莫尔道嘎镇政府；龙山只到公园POI。':'当天主线车程查询于2026/09/06。'}车程会随路况变化，具体酒店、餐厅接驳另核。")
s=s.replace('点击左侧高德复查可重新算路', '分段车程中可打开高德重新查验')
s=s.replace('function drivingHTML(day){return', 'function drivingHTML(day){if(day===2&&DATA.day2Research)return day2DrivingHTML();return')
marker='function infoHTML(day)'
addition='''function dayNoticeHTML(d){return d.notice?`<div class="route-update"><b>10月3日补充 · 开放提醒</b><p>${escapeHTML(d.notice)}</p><div class="refs">${refs(d.noticeSources||[])}</div></div>`:''}
function day2DrivingHTML(){const r=DATA.day2Research;return `<p class="schedule">高德查验：2026/10/03 08:30–08:35。各段可点击“高德复查”；实际导航会按当时路况重算。</p><div class="route-update"><b>当天基础方案</b><p>根河市政府 → 觉乐驯鹿园 → 得耳布尔镇政府 → 莫尔道嘎镇政府</p><strong>123.8公里 · 2小时10分05秒</strong><p>地图显示这条基础路线；下面的可选方案未叠加进全程总里程。</p></div><div class="section-label"><b>逐段查验</b><small>城镇参考点，非酒店</small></div>${r.legs.map(l=>`<article class="drive-card"><div class="drive-select">${escapeHTML(l.label)}</div><div class="drive-bottom"><span>${(l.distance/1000).toFixed(1)} km</span><span>${time(l.duration)}</span><a href="${escapeHTML(routeLink(l))}" target="_blank" rel="noopener">高德复查 ↗</a></div><p class="drive-query">查询 ${escapeHTML(l.queriedAt.replace('T',' ').slice(0,16))}${l.via.length?' · 途经 '+escapeHTML(l.via.join('、')):''}</p></article>`).join('')}<div class="section-label"><b>整条路线对比</b><small>各方案独立查询</small></div><div class="route-plans">${Object.values(r.plans).map(p=>`<div><b>${escapeHTML(p.label)}</b><span>${(p.distance/1000).toFixed(1)} km · ${time(p.duration)}</span></div>`).join('')}</div><p class="schedule">加车站比基础方案多9分29秒驾驶，连站前停留共多留20–25分钟。加车站和龙山后，整线纯驾驶约2小时24分。龙山导航点不等于登顶：短走45–75分钟，完整登高往返90–120分钟。</p><div class="overview-note">整线合计来自带途经点的完整查询，与独立分段相加可能不同。游玩、午餐、停车拍照、具体酒店与餐厅接驳另计。敖鲁古雅为觉乐的替换方案，详见“游玩安排”。</div><details class="driving-evidence"><summary>高德查验记录</summary><div class="refs">${r.evidenceFiles.map(f=>`<a href="${escapeHTML(f)}" target="_blank" rel="noopener">↗ ${escapeHTML(f)}</a>`).join('')}</div></details>`}
'''
if 'function day2DrivingHTML()' not in s:s=s.replace(marker, addition+marker)
style='''.route-update{background:#eef3e8;border:1px solid #d8e4d0;border-radius:12px;padding:15px 16px;margin:0 0 20px;font-size:12px;line-height:1.8}.route-update>b{font-size:13px}.route-update p{margin:6px 0}.route-update .refs{margin-top:8px}.drive-query{font-size:10px;color:var(--muted);padding:0 15px 12px}.route-plans{border:1px solid var(--line);border-radius:12px;padding:4px 15px;margin-bottom:16px}.route-plans>div{padding:12px 0;border-bottom:1px solid var(--line)}.route-plans>div:last-child{border:0}.route-plans b,.route-plans span{display:block;font-size:12px}.route-plans span{color:var(--muted);margin-top:4px}.driving-evidence{font-size:12px;margin-top:18px}.driving-evidence a{overflow-wrap:anywhere}
'''
if '.route-update{' not in s:s=s.replace('</style>',style+'</style>')
path.write_text(s,encoding='utf-8')
path=ROOT/'interactions.js'
s=path.read_text(encoding='utf-8')
needle="for(const k of ['stars','done'])for(const a of items)personal[k][a.key]"
migration="""if(raw.day2Revision!=='juele-2026-10-03'){if(!localStorage.getItem(storageKey+'-before-day2-20261003'))localStorage.setItem(storageKey+'-before-day2-20261003',JSON.stringify(raw));const remap={'2:0':'2:6','2:1':'2:5','2:2':'2:1','2:3':'2:4'};for(const k of ['stars','done']){const mapped={};for(const [key,value] of Object.entries(raw[k]||{})){const target=key.startsWith('2:')?remap[key]:key;if(target)mapped[target]=value}raw[k]=mapped}raw.day2Revision='juele-2026-10-03';localStorage.setItem(storageKey,JSON.stringify(raw))}"""
if 'before-day2-20261003' not in s:s=s.replace(needle,migration+needle)
s=s.replace("personal.routeRevision='qika-overnight-2026-09-06'", "personal.routeRevision='qika-overnight-2026-09-06';personal.day2Revision='juele-2026-10-03'")
s=s.replace('<p class="schedule">${escapeHTML(d.schedule)}</p><div class="timeline">', '<p class="schedule">${escapeHTML(d.schedule)}</p>${dayNoticeHTML(d)}<div class="timeline">')
path.write_text(s,encoding='utf-8')
path=ROOT/'activity_render.py'
s=path.read_text(encoding='utf-8')
s=s.replace("routes=json.loads((ROOT/'amap-routes.json').read_text(encoding='utf-8'))", "from effective_routes import load_effective_routes\n    routes=load_effective_routes()")
s=s.replace('2026-09-06高德核查，10/5—10/7已按七卡过夜方案重新查询', '10/3路线于2026-10-03用高德更新；其余主线为2026-09-06查询，10/5—10/7采用七卡过夜方案')
s=s.replace("for a in d['items']:\n            txt", "if d.get('notice'):txt += ['**开放提醒：** '+d['notice'],'']\n        for a in d['items']:\n            txt")
path.write_text(s,encoding='utf-8')
print('Updated itinerary UI, day 2 storage migration, and exports renderer')
