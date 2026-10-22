"""Apply the user's approved meals/day 4 plan and morning/rafting correction."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
data=json.loads((ROOT/'activities.json').read_text(encoding='utf-8'))
proposal=json.loads((ROOT/'planning-20261004/proposal.json').read_text(encoding='utf-8'))
for key,src in proposal['sources'].items():
    data['sources']['oct4-'+key]={'name':'小红书 · '+src['title'],'url':src['url']}
d=data['days'][2]
d.update(schedule='早餐后08:30–09:00出发，上午红豆坡＋一目九岭，抵达白鹿岛酒店后吃午餐。饭后先询问短线漂流是否开行、末班及接驳，再决定是否参加；若不开，改河湾观景和林间短走。',
    priority='上午保留红豆坡＋一目九岭；中午优先白鹿岛酒店餐厅，下午到现场确认短线漂流。小火车仍是上午自驾的替换，不能整套叠加。',
    notice='午餐不是必须靠干粮：今日高德主线纯驾驶约2小时04分。加两处游玩75–105分钟、入园停车缓冲20–30分钟，08:30出发预计12:10–12:50到白鹿岛，09:00出发约12:40–13:20到。酒店当天供餐时段尚未确认，简餐只作兜底。',
    noticeSources=['oct4-white-food','oct4-white-bill'],
    cut='先保证午餐和下午询问漂流。入园或道路延误时，缩短一处步行；漂流不开或天气不合适，就改河湾观景与短走。')
d['meals']=[
 dict(name='午餐首选 · 白鹿岛酒店中餐厅',time='抵达后用餐45–60分钟',detail='出发前或抵达时确认午餐供餐、是否接待外来客和最后点菜时间。近期亲历记录提到菌菇汤、豆角排骨、土豆南瓜等菜品；先看当天菜单。白鹿岛餐厅选择少，带少量简餐和水备用。',sources=['oct4-white-food','oct4-white-bill','oct4-white-supply']),
 dict(name='入园前段备选 · 森林餐厅／云树里餐厅',time='只有当时供餐才停，避免餐后折返',detail='两家高德登记在公园内，放在红豆坡之前基本顺路；从公园停车场分别约606米、104秒与561米、98秒（10/4 08:37查验）。但早餐／早午餐是否供应未核实。走完一目九岭后不要为它们回头：再去白鹿岛会多绕约54.6公里、59分钟。只有高德地点线索，没有足够实吃评价。',sources=[]),
 dict(name='镇内正餐备选 · 雅娟家常菜／红姐砂锅',time='适合尚未出镇时，45–60分钟',detail='雅娟可参考排骨炖豆角、野菜煎蛋；红姐可参考砂锅，既有好评也有服务及等位反馈。今日营业时段未确认。高德10/4 08:28：镇政府到雅娟1.8公里约7分、到红姐1.6公里约5分，两店至公园停车场均约14分；已进园不为这两家折返。',sources=['oct4-yajuan','oct4-hongjie','oct4-hongjie-caution']),
 dict(name='晚餐 · 白鹿岛酒店餐厅',time='游玩结束后45–60分钟',detail='午餐时顺便问晚餐和次日早餐时段，避免玩完漂流再临时找店；也可按当天住宿方安排用餐。酒店停车场只是接入点，未核到餐厅独立入口，不编造内部接驳车程。',sources=['oct4-white-food'])
]
d['items'][0]['drive']='高德10/4 08:37：莫尔道嘎镇政府→公园停车场12.7公里、17分49秒；红豆坡→一目九岭6.7公里、10分37秒。停车场→红豆坡保留10/3独立查询10.2公里、16分55秒。两段园内驾驶已纳入主线，不重复相加。'
d['items'][2]['drive']='高德10/4 08:37：一目九岭→白鹿岛酒店停车场79.8公里、1小时18分12秒。抵达后先问午餐；停车场不是观景台，到观景处接驳未核。'
d['items'][2]['detail']='午餐后或漂流前后，在开放观景处看河湾。若工作人员确认短线即将发船，先按报到时间安排漂流，再短看河湾；无需追求航拍才有的完整双岛视角。'
d['items'][3]['detail']='作为漂流不开或不参加时的替代，沿开放步道慢走。若已经参加短漂，可缩短或取消本项，保留用餐与休息时间。'
d['items'][4].update(level='推荐',name='白鹿岛短线漂流：先到场问开行',time='开行后连准备预留1.5–2小时',
    detail='下午先向景区确认当天短线是否开行、末班、报到入口、下船点和返程接驳。确认合适再参加；近期亲历记录短线船上约1小时，连准备等候预留1.5–2小时。当天运营尚未确认，不把它写成已预约项目。按工作人员要求穿救生衣，注意保暖。',
    drive='高德10/4 08:37：白鹿岛酒店停车场→白鹿岛漂流POI 1.6公里、4分43秒，仅为单程导航点接入；未计入主线总里程，实际登船和回程接驳另确认。')
d=data['days'][3]
d.update(theme='临江俄餐 → 室韦界河 → 七卡过夜',priority='临江午餐与村落、室韦团结广场、九卡至七卡河谷为重点；仍住七卡。太平午餐为替换，老鹰嘴仅可选。',
 schedule='08:30–09:00左右离开白鹿岛，临江吃俄餐、逛村落；室韦看团结广场并买列巴，再沿九卡到七卡入住。全日建议7–8小时（不含晚餐），排队或天气变化另留余量，不沿用旧车程的固定到达承诺。',
 notice='已按你确认保留七卡住宿、临江午餐；老鹰嘴只列可选。10月2日有卡线实走记录，也有落叶明显的反馈；以河谷与开阔景色为主，是否放行按当天现场指示。',noticeSources=['oct4-road','oct4-road-leaves'],
 cut='时间紧先取消白鹿岛晨景和老鹰嘴，再缩短室韦列巴排队及卡线停车；保留正常午餐与七卡入住。临时封路时按现场允许的路线重算，不强行穿行。')
d['items'][0].update(time='20–30分钟，可删',detail='早餐前后在住宿附近开放区域看晨光，不等待不确定的晨雾；建议08:30–09:00左右离开白鹿岛。',drive='车程以当天“分段车程”内10/4高德复查为准；不再使用旧的1小时46分估算。',poi='白鹿岛酒店停车场')
d['items'][1].update(name='临江：驶路部落俄餐＋村落短逛',time='午餐60–75分；短逛30–45分',
 detail='在驶路部落花园俄餐厅吃午餐，可参考鸡肉串、焖罐牛肉、红菜汤，先看当天菜单。近期两篇明确实吃支持；高德采用民宿整体定位，实际餐厅入口与营业再确认。饭后看木刻楞、村落和开放河岸，不把晨雾、日落写成午间必得体验。',
 sources=['oct4-shilu','oct4-shilu-recent'],drive='高德10/4 08:32：白鹿岛酒店停车场→驶路民宿整体126.6公里、1小时54分59秒。参考点不等于独立餐厅入口。',poi='驶路部落民宿（餐厅整体参考点）')
d['items'][2].update(name='室韦：团结广场＋奥利亚列巴房',time='合计25–40分钟',
 detail='先在团结广场看界河，再买列巴作为沿途补给。排队明显就只逛广场；不叠加整套口岸参观或界河游船。广场与列巴房都已核到高德点位。',
 sources=['oct4-square','oct4-shiwei'],drive='高德10/4：驶路参考点→团结广场11.6公里约23分；团结广场→奥利亚列巴房690米约3分（两段查询时刻不同，详见分段车程）。',poi='团结广场')
d['items'][3].update(time='停车合计30–45分钟',detail='选2–3处允许停车的开阔位置看界河与河谷。只在开放区域停车，不攀越围栏或进入农田草垛；树叶状态依现场，不以夏季麦田照片承诺十月景观。',sources=['oct4-road','oct4-road-leaves','oct4-square'],drive='按奥利亚列巴房→九卡→七卡逐段导航，采用10/4高德查验。完整路线与分段分别查询，不直接相加替代整线。',poi='九卡观景点')
d['items'][4].update(name='七卡入住、村内散步与晚餐',time='入住休息约30分；晚餐约60分',detail='仍住七卡。先入住，再按住宿方供餐安排吃晚饭；兰妮农家院是村内另一候选，可问现包饺子和当季蔬菜。实吃依据为2025年国庆记录，今日营业未确认，不把高德登记当开门保证。',sources=['oct4-lanni','qika-food','qika-stay'],drive='主线终点仍用七卡戍边食府作村内参考，保持次日路线衔接；具体民宿与兰妮餐厅间的接驳另核。',poi='七卡')
d['items']=d['items'][:5]+[
 dict(order=6,level='可选',name='老鹰嘴：额外河谷观景',time='20–30分钟；连额外驾驶约多1小时',detail='仅在开放与停车条件合适、时间充裕时加入；不采用旧帖车速或未经允许的入口。若加入，缩减室韦和卡线停车。',sources=['oct4-eagle','oct4-shiwei'],drive='高德已分别查询带老鹰嘴与不带老鹰嘴的完整路线，新增驾驶约27分钟；精确整线差值见分段车程。',poi='老鹰嘴'),
 dict(order=7,level='替换',name='太平林场：林曦农家菜午餐',time='60–75分钟，替换临江午餐',detail='提前饿了或临江餐厅不开时，改在太平吃东北家常菜、当季蔬菜。旧亲历有实吃支持，当前营业先确认；两顿完整午餐不叠加。',sources=['oct4-linxi'],drive='高德10/4 08:28：白鹿岛停车场→林曦95.2公里、1小时19分26秒；林曦→临江31.0公里、33分37秒，基本沿白鹿岛到临江的路线。',poi='林曦农家菜')]
data['updated']='2026-10-04'
(ROOT/'activities.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'itinerary-ui.html';s=p.read_text(encoding='utf-8')
s=s.replace("4:['白鹿岛酒店停车场','临江','室韦','九卡观景点','七卡']", "4:DATA.activities.days[3].items.map(a=>a.poi||null)")
s=s.replace('D2–D3 查验 10/3 · 其余主线 9/6','D3–D4 查验10/4 · D2查验10/3')
s=s.replace('10月3–4日主线查验于2026/10/03，其余日期主线为2026/09/06','10月4–5日主线查验于2026/10/04，10月3日主线查验于2026/10/03，其余日期主线为2026/09/06')
s=s.replace("function drivingHTML(day){if(day===3", "function drivingHTML(day){if(day===4&&DATA.day4Research)return day4DrivingHTML();if(day===3")
s=s.replace('高德查验：2026/10/03 08:53–08:56。主线包含红豆坡与一目九岭；', '高德主线更新：${escapeHTML(r.queriedAt.replace(\'T\',\' \').slice(0,16))}。分段各标实际查询时间，主线包含红豆坡与一目九岭；')
s=s.replace('当天车程于2026/10/03 08:53–08:56用高德查验。主线含', '当天主线于2026/10/04用高德查验，分段各标实际查询时间。主线含')
s=s.replace("通行。':'当天主线车程查询于2026/09/06。'", "通行。':day===4?'当天主线于2026/10/04用高德查验，包含临江俄餐、团结广场、列巴房、九卡及七卡参考点。':'当天主线车程查询于2026/09/06。'")
fn='''function mealsHTML(d){return d.meals?.length?`<details class="meal-plan" open><summary>今天吃在哪里 · 午餐与备选</summary>${d.meals.map(m=>`<article><b>${escapeHTML(m.name)}</b><small>${escapeHTML(m.time)}</small><p>${escapeHTML(m.detail)}</p><div class="refs">${refs(m.sources||[])}</div></article>`).join('')}</details>`:''}
function day4DrivingHTML(){const r=DATA.day4Research,p=r.plans.main,e=r.plans.withEagle;return `<p class="schedule">高德查验 ${escapeHTML(r.queriedAt.replace('T',' ').slice(0,16))}。镇村点均为导航参考，具体酒店及餐厅入口另核。</p><div class="route-update drive-card ${state.segment===dayRoutes(4)[0].id?'selected':''}" id="segment-${dayRoutes(4)[0].id}"><b>临江午餐 · 七卡过夜</b><p>白鹿岛 → 驶路部落 → 团结广场 → 奥利亚列巴房 → 九卡 → 七卡</p><strong>${(p.distance/1000).toFixed(1)}公里 · ${time(p.duration)}</strong><p>不含吃饭、村内步行和观景停车。</p><button class="quiet" data-segment="${dayRoutes(4)[0].id}">在地图查看整条路线</button></div>${r.legs.map(l=>`<article class="drive-card"><div class="drive-select">${escapeHTML(l.label)}</div><div class="drive-bottom"><span>${(l.distance/1000).toFixed(1)} km</span><span>${time(l.duration)}</span><a href="${escapeHTML(routeLink(l))}" target="_blank" rel="noopener">高德复查 ↗</a></div><p class="drive-query">查询 ${escapeHTML(l.queriedAt.replace('T',' ').slice(0,16))}</p></article>`).join('')}<div class="route-update"><b>老鹰嘴 · 可选</b><p>加入后整线 ${(e.distance/1000).toFixed(1)}公里 · ${time(e.duration)}，比主线多 ${(Math.round((e.distance-p.distance)/100)/10).toFixed(1)}公里、约${Math.round((e.duration-p.duration)/60)}分钟驾驶。观景另留20–30分钟。</p></div><p class="schedule">太平林曦午餐为临江正餐的替换，车程见游玩安排。整线与分段独立查询，时间不一定恰好相加；当天是否放行依现场指示。</p><details class="driving-evidence"><summary>高德查验记录</summary><div class="refs">${r.evidenceFiles.map(f=>`<a href="${escapeHTML(f)}" target="_blank" rel="noopener">↗ ${escapeHTML(f)}</a>`).join('')}</div></details>`}
'''
if 'function mealsHTML' not in s:s=s.replace('function infoHTML(day)',fn+'function infoHTML(day)')
css='.meal-plan{border:1px solid var(--line);border-radius:12px;background:white;margin:0 0 24px;padding:14px;font-size:12px}.meal-plan>summary{font-size:13px;font-weight:650;cursor:pointer}.meal-plan article{border-top:1px solid var(--line);padding:14px 0 2px;margin-top:12px}.meal-plan small{display:block;color:var(--muted);margin:4px 0}.meal-plan p{line-height:1.9}'
if '.meal-plan{' not in s:s=s.replace('</style>',css+'</style>')
p.write_text(s,encoding='utf-8')
p=ROOT/'interactions.js';s=p.read_text(encoding='utf-8').replace('${dayNoticeHTML(d)}<div class="timeline">','${dayNoticeHTML(d)}${mealsHTML(d)}<div class="timeline">');p.write_text(s,encoding='utf-8')
p=ROOT/'city-guide.js';s=p.read_text(encoding='utf-8').replace('高德已核点 · 10月4日行程补充','高德已核点 · 10月${p.day+1}日行程补充');p.write_text(s,encoding='utf-8')
p=ROOT/'activity_render.py';s=p.read_text(encoding='utf-8').replace('10/3–10/4路线于2026-10-03用高德更新','10/4–10/5路线于2026-10-04用高德更新；10/3路线为2026-10-03查验')
needle="        for a in d['items']:\n            txt"
insert="        for meal in d.get('meals',[]):\n            txt += ['**餐饮：'+meal['name']+'｜'+meal['time']+'**','',meal['detail'],'']\n            rows.append([d['date'],'餐饮','参考',meal['name'],meal['time'],meal['detail'],'见当天高德分段查验',s['stay']])\n        for a in d['items']:\n            txt"
if "for meal in d.get('meals'" not in s:s=s.replace(needle,insert)
p.write_text(s,encoding='utf-8')
print('Applied approved Oct 4 meals/rafting and Oct 5 itinerary; publishing remains a later step')
