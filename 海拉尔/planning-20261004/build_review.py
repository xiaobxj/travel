"""Build a local review draft. This never edits or uploads the live itinerary."""
import html
import json
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
read=lambda name:json.loads((ROOT/name).read_text(encoding='utf-8'))
main=read('recommended-day4-driving-live-summary.json')
extra=read('extra-stops-driving-live-summary.json')
base=read('driving-live-summary.json')
park=read('park-lunch-detours-live-summary.json')
notes={n['id']:n for n in json.loads((PROJECT/'city-notes.json').read_text(encoding='utf-8'))['notes']}
for path in (ROOT/'xiaohongshu').glob('*.json'):
    n=json.loads(path.read_text(encoding='utf-8')).get('note',{})
    if n.get('id'):notes[n['id']]=n
byroute={r['id']:r for source in [main,extra,base,park] for r in source['routes']}
pois={k:v for source in [main,extra,base,park] for k,v in source.get('pois',{}).items()}
sources={
 'white-food':'6ac030d3000000001402de3a',
 'white-bill':'6abe55060000000012035ff0',
 'white-supply':'6abdf4b9000000001b02dbb5',
 'yajuan':'6a735797000000003300aed8',
 'hongjie':'6aab9cd40000000011038482',
 'hongjie-caution':'6aafcc2e00000000280303d6',
 'shilu':'6abfda6e000000000a024be7',
 'shilu-recent':'6abf7e02000000001802f74e',
 'shiwei':'6ac0bdd20000000012034392',
 'square':'6abe84e000000000020112e6',
 'road':'6abf6a99000000001301b90a',
 'road-leaves':'6abf3bdc0000000012037481',
 'linxi':'68d95f900000000012023085',
 'lanni':'68df890700000000050106d0',
 'eagle':'6abdfce40000000015003129',
}
# One caution note was read yesterday and remains in the research folder.
for key,nid in sources.items():
    if nid not in notes:
        p=PROJECT/'route-research-20261003'/f'{nid}.json'
        assert p.exists(),nid
        notes[nid]=json.loads(p.read_text(encoding='utf-8'))['note']
source_records={key:{'id':nid,'title':notes[nid]['title'],'url':notes[nid]['url']} for key,nid in sources.items()}

food=[
 {'name':'雅娟家常菜／红姐砂锅','time':'热饭预留45–60分钟','where':'莫尔道嘎镇内，出镇前的正餐候选',
  'detail':'雅娟可参考排骨炖豆角、野菜煎蛋；红姐可参考菠菜羊肉粉丝、冬瓜排骨砂锅。红姐既有好评，也有等位与服务不满的亲历反馈。两家早餐时段与今日营业尚未确认，不把它们当作已确认早餐店；已入园就不为这两家回头。',
  'drive':'今天高德：镇政府→雅娟1.8公里约7分，雅娟→公园停车场11.6公里约14分；镇政府→红姐1.6公里约5分，红姐→公园停车场11.5公里约14分。',
  'sources':['yajuan','hongjie','hongjie-caution']},
 {'name':'红豆坡＋一目九岭自驾：午间简餐','time':'预留20–30分钟','where':'入园前购买，合法停车休息处吃',
  'detail':'这条自驾路线以备好简餐、水和热饮最省折返。另核到森林餐厅、云树里餐厅，但只有高德餐饮登记，尚无充分实吃资料或今日营业确认；两家只作为公园入口／小火车一侧的现场询问备选。',
  'drive':'高德同批比较：从一目九岭经任一家餐厅再到白鹿岛，比直达多约54.6公里、59分钟驾驶。它们不作为走完一目九岭后的顺路午餐。',
  'sources':['white-supply']},
 {'name':'白鹿岛酒店中餐厅','time':'午后正餐／晚餐预留45–60分钟','where':'抵达白鹿岛后就餐候选',
  'detail':'10月初发布的亲历记录支持餐厅近期有人用餐，可参考菌菇汤、豆角排骨、土豆南瓜等菜品；口味和份量也有分歧。到岛后先问当日午晚餐时段、是否接待外来客及最后点菜时间。不要照搬旧价，先看菜单。',
  'drive':'尚未核到独立餐厅POI；酒店停车场只作白鹿岛接入点，不编造停车场至餐厅的驾车时长。',
  'sources':['white-food','white-bill','white-supply']},
]
stops=[
 {'name':'白鹿岛晨景后出发','time':'晨景20–30分钟，可删','detail':'仍住七卡，建议08:30–09:00左右离开白鹿岛，不为等待晨雾拖延出发。'},
 {'name':'临江：驶路部落俄餐＋村落短逛','time':'用餐60–75分钟；短逛30–45分钟','detail':'午餐保留在临江，尝试鸡肉串、焖罐牛肉、红菜汤。近期两篇明确实吃支持；餐厅按民宿整体落点导航，到场再找实际入口。饭后看木刻楞、村落和开放河岸，不把晨雾或日落写成午间体验。','sources':['shilu','shilu-recent']},
 {'name':'室韦：团结广场＋奥利亚列巴房','time':'合计25–40分钟','detail':'广场看界河，再买列巴作沿途补给。排队明显就只逛广场；不把口岸参观、界河游船一并排满。','sources':['square','shiwei']},
 {'name':'九卡—七卡：沿途河谷观景','time':'停车合计30–45分钟','detail':'选2–3处允许停车的开阔位置看界河与草原。10月2日仍有实走记录，但也有人反馈落叶明显；以河谷与开阔景观为主，不承诺金黄白桦。实际放行与停车按当天现场指示。','sources':['road','road-leaves']},
 {'name':'七卡入住，再吃晚餐','time':'入住休息30分钟；晚餐约60分钟','detail':'仍住七卡。兰妮农家院为住宿餐厅之外的晚餐候选，可问现包饺子、当季蔬菜；口味依据是2025年国庆亲历，今日营业未确认。高德路线以兰妮为七卡村内参考点，不代表已订民宿。','sources':['lanni']},
]
alternatives=[
 {'name':'太平林场 · 林曦农家菜','time':'午餐60–75分钟，替换临江正餐','detail':'如果路上提前饿了，或临江餐厅不开，可在太平改吃东北家常菜。高德显示在白鹿岛到临江途中基本顺路；实吃资料为2025年记录，当前开门时间需确认。','sources':['linxi']},
 {'name':'老鹰嘴','time':'观景20–30分钟；比主方案多约27分钟驾驶','detail':'仅作可选。加上观景共多预留约1小时；路况、步行入口与当天放行合适再去。若要加，优先取消室韦补给或减少卡线停车，不推迟七卡入住。','sources':['eagle','shiwei']},
]
leg_ids=['bailudao_to_shilu','shilu_to_square','square_to_aoliya','aoliya_to_jiuka','jiuka_to_lanni']
missing=[x for x in leg_ids if x not in byroute]
if missing:
    # Route IDs are internal; resolve the two already verified short legs by endpoints.
    for r in extra['routes']:
        if r['from']=='团结广场' and r['to']=='奥利亚列巴房':byroute['square_to_aoliya']=r
        if r['from']=='奥利亚列巴房' and r['to']=='九卡观景点':byroute['aoliya_to_jiuka']=r
legs=[byroute[x] for x in leg_ids]
proposal={'status':'awaiting_user_confirmation','published':False,'overnightConfirmed':'10/5七卡',
 'foodOct4':food,'itineraryOct5':stops,'alternatives':alternatives,
 'mainRoute':byroute['recommended_whole'],'withEagle':byroute['recommended_whole_with_eagle'],
 'legs':legs,'sources':source_records,'dayBudget':'不含晚餐约7–8小时；排队、路况及长时间拍照另加',
 'nextAction':'用户确认具体方案后，再更新行程源文件、构建、检查并发布。'}
(ROOT/'proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2),encoding='utf-8')
esc=html.escape
def refs(keys):
    return '<div class="refs">'+' '.join(f'<a target="_blank" rel="noopener" href="{esc(source_records[k]["url"])}">↗ {esc(source_records[k]["title"])}</a>' for k in keys)+'</div>'
def cards(rows):
    return ''.join(f'<article><div class="meta">{esc(row["time"])}</div><h3>{esc(row["name"])}</h3>'+ (f'<div class="where">{esc(row["where"])}</div>' if row.get('where') else '')+f'<p>{esc(row["detail"])}</p>'+ (f'<p class="drive">{esc(row["drive"])}</p>' if row.get('drive') else '')+refs(row.get('sources',[]))+'</article>' for row in rows)
def nav(r):
    return 'https://uri.amap.com/navigation?'+urlencode({'from':pois[r['from']]['location']+','+r['from'],'to':pois[r['to']]['location']+','+r['to'],'mode':'car','policy':'0','coordinate':'gaode','callnative':'0','src':'hulunbuir-itinerary'})
def duration(seconds):
    minutes=round(seconds/60)
    return f'{minutes//60}小时{minutes%60:02d}分' if minutes>=60 else f'{minutes}分钟'
rows=''.join(f'<tr><td>{esc(r["from"])} → {esc(r["to"])}</td><td>{r["meters"]/1000:.1f}公里</td><td>{duration(r["seconds"])}</td><td><a target="_blank" rel="noopener" href="{esc(nav(r))}">高德导航 ↗</a></td></tr>' for r in legs)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>待确认 · 10/4餐饮与10/5行程</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f7f1;color:#253f35;font:15px/1.8 system-ui,'Microsoft YaHei',sans-serif}main{max-width:1060px;padding:32px 20px 70px;margin:auto}h1{font-size:30px;line-height:1.4;margin:12px 0}h2{font-size:24px;margin:36px 0 16px}h3{font-size:19px;margin:5px 0}p{margin:10px 0}.status{display:inline-block;background:#fff0d0;color:#79551e;border-radius:20px;padding:4px 14px}.intro{color:#627367;max-width:850px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}article{background:white;border:1px solid #dce4d8;border-radius:14px;padding:21px}.food article:first-child{grid-column:1/-1}.meta{font-size:13px;color:#6b7a62}.where{font-size:13px;color:#64756b}.drive{background:#f1f5ec;border-radius:8px;padding:12px;font-size:13px}.refs{display:flex;gap:8px;flex-wrap:wrap;font-size:12px;margin-top:12px}a{color:#2a6750;text-decoration:none}a:hover{text-decoration:underline}.callout{padding:20px;background:#e6efdf;border-radius:14px;margin:20px 0}.callout b{font-size:23px}.table{overflow-x:auto;background:white;border-radius:14px;padding:12px}table{border-collapse:collapse;width:100%;min-width:530px;font-size:13px}td,th{padding:12px 8px;text-align:left;border-bottom:1px solid #e0e7dc}small{color:#68796f}.check{border:1px solid #d6b46a;background:#fffaec;border-radius:12px;padding:20px;margin-top:30px}@media(max-width:620px){main{padding:22px 15px 50px}h1{font-size:25px}.grid{grid-template-columns:1fr}article{padding:17px}.food article:first-child{grid-column:auto}.callout b{font-size:20px}}
</style><main><span class="status">待你确认 · 尚未上传</span><h1>10/4 吃在哪里，10/5 怎么玩</h1><p class="intro">10/5仍住七卡，已按你的回复保留。下面是准备补进网页的具体内容；车程来自今天10/4的高德查询，游玩与用餐时间是规划预算。</p>
<h2>10/4 · 餐饮补充</h2><div class="grid food">'''+cards(food)+'''</div><h2>10/5 · 临江俄餐、室韦与北段卡线</h2><div class="callout"><b>221.2公里 · 纯驾驶约4小时14分</b><p>白鹿岛 → 临江驶路部落 → 室韦团结广场 → 奥利亚列巴房 → 九卡 → 七卡</p><small>08:32完整途经路线查询。全日游玩建议约7–8小时，不含晚餐；具体餐厅开门、排队和住宿接驳另核。</small></div><div class="grid">'''+cards(stops)+'''</div><h2>可选调整</h2><div class="grid">'''+cards(alternatives)+'''</div><h2>10/5 · 已核分段车程</h2><div class="table"><table><thead><tr><th>路段</th><th>距离</th><th>驾驶</th><th>复查</th></tr></thead><tbody>'''+rows+'''</tbody></table></div><p class="intro">各段及完整路线分别查询，时间可能不恰好相加。驶路采用民宿整体定位，餐厅入口另确认；兰妮为七卡餐饮参考点，实际民宿接驳未计入。高德算路和近日亲历记录均不能保证10/5现场放行。</p><div class="check"><strong>准备请你确认：</strong><p>10/4按“自驾午间备简餐＋白鹿岛酒店餐厅晚餐”；10/5保留临江俄餐午餐，林曦为替换，老鹰嘴只作可选。确认后才更新线上网页。</p></div></main></html>'''
(ROOT/'review.html').write_text(page,encoding='utf-8')
print('Built local proposal.json and review.html; no live files changed or uploaded')
