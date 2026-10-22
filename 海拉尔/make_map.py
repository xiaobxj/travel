import json,math,base64,html,csv
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from activity_render import render_day, write_guide, DATA as ACTIVITIES
R=Path(__file__).parent
d=json.loads((R/'amap-routes.json').read_text(encoding='utf-8'))
colors=['#cc5227','#21805b','#8b53ab','#147f9d','#b78912','#3557c2']
stays=['根河市区','莫尔道嘎镇','白鹿岛（营业及供暖待确认）','七卡村附近（具体民宿待选）','额尔古纳市区','15:00 前海拉尔还车']
notes=['仅到莫日格勒南游客中心；不含景区内接驳/自驾。','经得耳布尔约束根白公路方向；住宿用市/镇中心代表。','仅到森林公园停车场及白鹿岛，园内游览驾驶未计入。','经临江、室韦、九卡到七卡过夜；如白鹿岛至临江需绕莫尔道嘎，车程另加。','七卡出发，经黑山头至额尔古纳；观景、用餐及马场支线另计。','以海拉尔站代表市区。机场停车场备选单独查询；实际还车门店尚未提供。']
def fmt(s):
 m=round(s/60);return f'{m//60}小时{m%60:02d}分' if m>=60 else f'{m}分钟'
def project(lon,lat):
 # AMap static-map zoom=7 uses a 65536px Mercator world.
 w=65536
 def y(a):return (1-math.asinh(math.tan(math.radians(a)))/math.pi)/2*w
 return (512+(lon-120.4)/360*w,512+y(lat)-y(50.6))
def points(r):
 out=[]
 for step in r['path']['steps']:
  for p in step.get('polyline','').split(';'):
   if p:out.append(project(*map(float,p.split(','))))
 return out
png=Image.open(R/'amap-basemap.png').convert('RGB');draw=ImageDraw.Draw(png)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
svg=[]
for idx,r in enumerate(d['segments']):
 if not r['day']:continue
 pts=points(r);col=colors[r['day']-1]
 draw.line(pts,fill=col,width=4)
 svg.append(f'<polyline class="route day{r["day"]}" data-day="{r["day"]}" points="'+ ' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round"><title>{html.escape(r["from"]+" → "+r["to"])} · {r["distance"]/1000:.1f} km · {fmt(r["duration"])}</title></polyline>')
labels={'海拉尔站':(-90,20),'莫日格勒游客中心':(10,12),'额尔古纳':(10,5),'根河':(12,16),'敖鲁古雅停车场':(-125,-10),'莫尔道嘎':(10,20),'森林公园停车场':(-135,0),'白鹿岛酒店停车场':(10,-12),'临江':(10,-14),'室韦':(-48,20),'九卡观景点':(10,0),'七卡':(10,0),'黑山头':(-72,10),'得耳布尔':(10,0)}
sleepdays={'根河':1,'莫尔道嘎':2,'白鹿岛酒店停车场':3,'七卡':4,'额尔古纳':5}
for n,(dx,dy) in labels.items():
 p=d['pois'][n];x,y=project(*map(float,p['location'].split(',')))
 label=n.replace('酒店停车场','').replace('停车场','入口')
 if n in sleepdays:label+=f' 10/{sleepdays[n]+1}宿'
 svg.append(f'<g class="poi"><circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="#233e39" stroke-width="2"/><text x="{x+dx}" y="{y+dy}" font-size="14" fill="#183f35" paint-order="stroke" stroke="#fff" stroke-width="4">{html.escape(label)}</text><title>{html.escape(p["name"])} · {p["location"]}</title></g>')
 draw.ellipse((x-4,y-4,x+4,y+4),fill='white',outline='#233e39',width=2)
 draw.text((x+dx,y+dy-12),label,font=font,fill='#183f35',stroke_width=2,stroke_fill='white')
png.save(R/'itinerary-map.png')
rows=[];cards=[];summ=[]
for day in range(1,7):
 rs=[r for r in d['segments'] if r['day']==day];km=sum(r['distance'] for r in rs)/1000;sec=sum(r['duration'] for r in rs)
 summ.append({'day':day,'km':round(km,1),'duration':fmt(sec),'seconds':sec,'stay':stays[day-1]})
 body=''
 for r in rs:
  a=d['pois'][r['from']]['location'];b=d['pois'][r['to']]['location']
  from urllib.parse import urlencode
  link='https://uri.amap.com/navigation?'+urlencode({'from':a+','+r['from'],'to':b+','+r['to'],'mode':'car','policy':0,'src':'hulunbuir-itinerary','coordinate':'gaode','callnative':0})
  body+=f'<tr><td>{r["from"]} → {r["to"]}'+('（经'+','.join(r['via'])+'）' if r['via'] else '')+f'</td><td>{r["distance"]/1000:.1f} km</td><td>{fmt(r["duration"])}</td><td><a href="{html.escape(link)}" target="_blank" rel="noopener">高德复查</a></td></tr>'
  rows.append([f'10/{day+1}',r['from'],r['to'],'/'.join(r['via']),round(r['distance']/1000,1),fmt(r['duration']),r['duration'],stays[day-1],r['raw_file']])
 cards.append(f'<section id="day{day}"><h2><i style="background:{colors[day-1]}"></i>10/{day+1} · {stays[day-1]}</h2><strong>{km:.1f} km · 高德基础车程 {fmt(sec)}</strong><table>{body}</table><p class="note">{notes[day-1]}</p>'+render_day(day)+'</section>')
alt=''
for r in d['segments']:
 if r['day']==0:alt+=f'<tr><td>{r["from"]} → {r["to"]}'+('（经'+','.join(r['via'])+'）' if r['via'] else '')+f'</td><td>{r["distance"]/1000:.1f} km</td><td>{fmt(r["duration"])}</td></tr>'
bg=base64.b64encode((R/'amap-basemap.png').read_bytes()).decode()
total=sum(s['km'] for s in summ);secs=sum(s['seconds'] for s in summ)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>呼伦贝尔森林北线 · 高德路线核查</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f5ef;color:#233e39;font-family:system-ui,"Microsoft YaHei",sans-serif}header{padding:26px 32px;background:#183f35;color:#fff}h1{font-size:27px;margin:6px 0}header p{opacity:.85;margin:8px 0}.layout{display:grid;grid-template-columns:minmax(440px,1.15fr) minmax(410px,1fr);gap:20px;padding:20px}.mapbox{position:sticky;top:14px;align-self:start;background:white;border-radius:14px;padding:12px;box-shadow:0 2px 12px #0001}.mapview{height:min(78vh,850px);overflow:hidden;touch-action:none;border:1px solid #ddd;border-radius:8px}svg{width:100%;height:100%;cursor:grab}svg:active{cursor:grabbing}.toolbar{display:flex;gap:6px;flex-wrap:wrap;padding-bottom:10px}button{border:1px solid #c8d4cf;background:#fff;border-radius:7px;padding:7px 11px;cursor:pointer}button.active{background:#183f35;color:white}section{background:#fff;padding:18px;margin-bottom:14px;border-radius:12px}h2{font-size:18px;margin:0 0 10px}i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px}table{width:100%;font-size:13px;border-collapse:collapse;margin-top:12px}td{padding:10px 5px;border-bottom:1px solid #eee}td:first-child{width:55%}.note{font-size:13px;color:#64736d;line-height:1.65}a{color:#19745c} .warning{background:#fff3d9;padding:14px;border-radius:8px;line-height:1.6;font-size:14px}.route{cursor:pointer;transition:opacity .15s}.small{font-size:12px;margin:8px 2px}.poi{pointer-events:none}@media(max-width:850px){.layout{display:block;padding:12px}.mapbox{position:relative;top:0;margin-bottom:15px}.mapview{height:65vh}header{padding:20px}h1{font-size:23px}}@media print{.layout{display:block}.mapbox{position:relative}.mapview{height:650px}.toolbar{display:none}section{break-inside:avoid}}
</style><header><small>2026.10.02 — 10.07 / 自驾 6 日</small><h1>沿森林与界河，回到海拉尔</h1><p>高德道路轨迹 · 每日里程与车程 · 五晚住宿</p><p>__TOTAL__ km ｜基础驾驶 __TIME__ ｜10/7 15:00 前还车</p></header><main class="layout"><div class="mapbox"><div class="toolbar"><button class="active" data-filter="0">全程</button>__BUTTONS__<button id="plus">＋</button><button id="minus">－</button><button id="reset">复位</button><button onclick="window.print()">打印</button></div><div class="mapview"><svg id="map" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,__BG__" width="1024" height="1024"/>__SVG__</svg></div><p class="small">拖动平移，滚轮缩放；点击日期或道路查看对应行程。高德底图及道路数据，GCJ-02。</p><p class="small" id="selected">基础车程不含景区内部游览、停车拍照和休息。</p></div><div><div class="warning">查询时间：__DATE__。这是查询时的路线估算，不是国庆当天预测。景区通行、卡线开放和冰雪影响须临行复查。城镇用代表点测算，未替代具体酒店或还车门店。</div>__CARDS__<section><h2>替代路线比较</h2><table>__ALT__</table><p class="note">曲水云天替代南游客中心时，首日两段合计约156.6公里、2小时18分，再加额尔古纳至根河。不要把景区大门等同于观景点。复查链接可能重新推荐路线，卡线需逐段导航。</p></section><section><h2>时间怎么留</h2><p class="note">10/2驾驶留4.5–5小时，另加莫日格勒游览约2小时；10/3驾驶留3小时；10/4园外驾驶留2–2.5小时，另留森林公园游览约3小时（其中园内驾驶尚未计量）；10/5主线驾驶留4–4.5小时，如白鹿岛至临江绕行另加；10/6驾驶留2.5–3小时；10/7驾驶留2.5–3小时，09:00出发，14:00到还车点。</p><p class="note">白鹿岛酒店停车场作为落点，不代表已订房或保证营业。莫尔道嘎公园停车场至白鹿岛查询的是园外转场，未证明景区可穿越。</p></section><section><h2>数据与文档</h2><p class="note">高德 v5/direction/driving，strategy=32（高德推荐），每段采用第一条方案；根河至莫尔道嘎指定经得耳布尔；卡线分别查询九卡、七卡。页面已内嵌底图和路线，无需填写密钥即可查看。</p><a href="https://lbs.amap.com/api/webservice/guide/api/newroute">高德路径规划文档</a> · <a href="https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode">JS安全密钥说明</a></section></div></main><script>
const svg=document.getElementById('map');let box=[0,0,1024,1024];function render(){svg.setAttribute('viewBox',box.join(' '))}function zoom(f){let w=box[2]*f;if(w<180||w>2048)return;box=[box[0]+(box[2]-w)/2,box[1]+(box[3]-w)/2,w,w];render()}document.getElementById('plus').onclick=()=>zoom(.8);document.getElementById('minus').onclick=()=>zoom(1.25);document.getElementById('reset').onclick=()=>{box=[0,0,1024,1024];render()};svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY<0?.9:1.1)},{passive:false});let drag=null;svg.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,b:box.slice()};svg.setPointerCapture(e.pointerId)});svg.addEventListener('pointermove',e=>{if(!drag)return;let k=box[2]/Math.min(svg.clientWidth,svg.clientHeight);box=[drag.b[0]-(e.clientX-drag.x)*k,drag.b[1]-(e.clientY-drag.y)*k,box[2],box[3]];render()});svg.addEventListener('pointerup',()=>drag=null);svg.addEventListener('pointercancel',()=>drag=null);function filter(day){document.querySelectorAll('.route').forEach(p=>p.style.opacity=day===0||Number(p.dataset.day)===day?1:.12);document.querySelectorAll('[data-filter]').forEach(b=>b.classList.toggle('active',Number(b.dataset.filter)===day));if(day)document.getElementById('day'+day).scrollIntoView({behavior:'smooth',block:'nearest'})}document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>filter(Number(b.dataset.filter)));document.querySelectorAll('.route').forEach(p=>p.addEventListener('click',()=>{document.getElementById('selected').textContent=p.querySelector('title').textContent;filter(Number(p.dataset.day))}));
</script></html>'''
for k,v in {'TOTAL':f'{total:.1f}','TIME':fmt(secs),'BUTTONS':''.join(f'<button data-filter="{i}">10/{i+1}</button>' for i in range(1,7)),'BG':bg,'SVG':''.join(svg),'DATE':d['queried_at'],'CARDS':''.join(cards),'ALT':alt}.items():page=page.replace('__'+k+'__',v)
activity_style='.activities{margin-top:16px;border-top:1px solid #e0e8e3;padding-top:10px}.activities h3{font-size:16px;margin:6px 0}.activities details{margin:8px 0;border:1px solid #e1e8e3;border-radius:8px;padding:10px}.activities summary{cursor:pointer;font-size:14px;line-height:1.8}.activities details p{font-size:14px;line-height:1.7}.priority{color:#246348;font-size:12px;border:1px solid #cadbd0;border-radius:4px;padding:2px 4px}.activity-time{display:block;color:#68766e;font-size:12px;margin-left:16px}'
page=page.replace('</style>',activity_style+'</style>').replace('高德道路轨迹 · 每日里程与车程 · 五晚住宿','高德道路轨迹 · 每日游玩顺序与优先级 · 五晚住宿')
intro='<section><h2>按你们的偏好排序</h2><p class="note">'+html.escape(' → '.join(ACTIVITIES['ranking']))+'</p><p class="note">这是森林体验优先的个人化建议，不是平台评分排名。各日按行车先后排列，点击项目展开玩法；优先项目尽量保留，可选项目不必全部完成。新增支线尚未全部核查，表中仍为原主线车程。</p><a href="daily-activities.md">完整游玩说明</a> · <a href="daily-activities.csv">Excel可打开的项目表</a></section>'
page=page.replace('<section id="day1">',intro+'<section id="day1">',1)
(R/'itinerary-map.html').write_text(page,encoding='utf-8')
with (R/'driving-times.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['日期','起点','终点','途经','公里','高德车程','秒','住宿','证据文件']);w.writerows(rows)
(R/'daily-summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8')
write_guide()
from build_ui import build
page = build()
assert all(0<=x<=1024 and 0<=y<=1024 for r in d['segments'] if r['day'] for x,y in points(r))
assert '8741c9533563fe28253346e1001404bd' not in page
print(json.dumps(summ,ensure_ascii=False));print('TOTAL',total,fmt(secs));print('Created itinerary-map.html, itinerary-map.png, driving-times.csv')
