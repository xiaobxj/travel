"""Wire October 4 researched routes into the existing interface."""
from pathlib import Path
ROOT=Path(__file__).parent
p=ROOT/'itinerary-ui.html'
s=p.read_text(encoding='utf-8')
s=s.replace("3:['森林公园停车场','森林公园停车场','白鹿岛酒店停车场','白鹿岛酒店停车场']", "3:DATA.activities.days[2].items.map(a=>a.poi||null)")
s=s.replace('D2 更新 10/3 · 其余主线 9/6 · 不含游玩','D2–D3 查验 10/3 · 其余主线 9/6')
s=s.replace('10月3日主线更新于2026/10/03，其余日期主线为2026/09/06', '10月3–4日主线查验于2026/10/03，其余日期主线为2026/09/06')
s=s.replace('10月3日补充 · 开放提醒', '行程补充 · 开放提醒')
s=s.replace("function drivingHTML(day){if(day===2&&DATA.day2Research)return day2DrivingHTML();", "function drivingHTML(day){if(day===3&&DATA.day3Research)return day3DrivingHTML();if(day===2&&DATA.day2Research)return day2DrivingHTML();")
s=s.replace("公园POI。':'当天主线车程查询于2026/09/06。'", "公园POI。':day===3?'当天车程于2026/10/03 08:53–08:56用高德查验。主线含红豆坡与一目九岭两段园内驾驶，不含漂流支线；高德算路不代表当天允许自驾通行。':'当天主线车程查询于2026/09/06。'")
fn='''function day3DrivingHTML(){const r=DATA.day3Research,p=r.plans.selfDrive;const card=l=>`<article class="drive-card"><div class="drive-select">${escapeHTML(l.label)}${l.optional?'<br><small>可选支线 · 未计入主线总里程</small>':''}</div><div class="drive-bottom"><span>${(l.distance/1000).toFixed(1)} km</span><span>${time(l.duration)}</span><a href="${escapeHTML(routeLink(l))}" target="_blank" rel="noopener">高德复查 ↗</a></div><p class="drive-query">查询 ${escapeHTML(l.queriedAt.replace('T',' ').slice(0,16))}</p></article>`;return `<p class="schedule">高德查验：2026/10/03 08:53–08:56。主线包含红豆坡与一目九岭；园内是否允许自驾，入园时先确认。</p><div class="route-update"><b>推荐自驾方案</b><p>莫尔道嘎镇政府 → 森林公园停车场 → 红豆坡 → 一目九岭 → 白鹿岛酒店停车场</p><strong>${(p.distance/1000).toFixed(1)}公里 · ${time(p.duration)}</strong><p>上面是完整路线的纯驾驶；两站步行、午餐、观景和漂流另计。</p></div><div class="section-label"><b>逐段高德查验</b><small>按游玩顺序导航</small></div>${r.legs.map(card).join('')}<div class="overview-note">漂流只核到导航点，未确认实际登船口、下船点与回程接驳，不能将单程翻倍当作往返。白鹿岛酒店停车场也不等于观景台。</div><details class="driving-evidence"><summary>改坐小火车时的路线</summary><p class="schedule">用小火车替换红豆坡＋一目九岭。镇区经公园停车场到白鹿岛整线 ${(r.plans.train.distance/1000).toFixed(1)}公里 · ${time(r.plans.train.duration)}，另留乘车、排队时间。</p>${r.trainLegs.map(card).join('')}</details><details class="driving-evidence"><summary>高德查验记录</summary><div class="refs">${r.evidenceFiles.map(f=>`<a href="${escapeHTML(f)}" target="_blank" rel="noopener">↗ ${escapeHTML(f)}</a>`).join('')}</div></details><p class="schedule">整线与分段分别查询，时间不一定恰好相加；游玩时长均为规划预算。</p>`}
'''
if 'function day3DrivingHTML()' not in s:s=s.replace('function infoHTML(day)',fn+'function infoHTML(day)')
s=s.replace('<div class="route-update"><b>推荐自驾方案</b>', '<div class="route-update drive-card ${state.segment===dayRoutes(3)[0].id?\'selected\':\'\'}" id="segment-${dayRoutes(3)[0].id}"><b>推荐自驾方案</b>')
s=s.replace('上面是完整路线的纯驾驶；两站步行、午餐、观景和漂流另计。</p></div>', '上面是完整路线的纯驾驶；两站步行、午餐、观景和漂流另计。</p><button class="quiet" data-segment="${dayRoutes(3)[0].id}">在地图查看整条路线</button></div>')
p.write_text(s,encoding='utf-8')
p=ROOT/'activity_render.py'
s=p.read_text(encoding='utf-8').replace('10/3路线于2026-10-03用高德更新','10/3–10/4路线于2026-10-03用高德更新')
p.write_text(s,encoding='utf-8')
p=ROOT/'city-guide.js'
s=p.read_text(encoding='utf-8').replace('10月3日主线已更新为觉乐方案；新增三处采用10月3日完整路线比较，其他项目保留各自标注日期的历史路线对照，不代表本日新路线的绕行增量。','10月3日主线采用觉乐方案，10月4日主线采用红豆坡＋一目九岭自驾方案。新地点分别展示整线比较或单程车程；其他项目保留各自日期的历史路线对照，不代表新路线的绕行增量。')
p.write_text(s,encoding='utf-8')
print('Updated day 3 navigation, map activity bindings, and query-date labels')
