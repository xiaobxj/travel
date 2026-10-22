import sys,json,time,requests,math
from pathlib import Path
sys.path.insert(0,r'D:\travel\海拉尔')
from amap_audit import api,KEY
ROOT=Path(__file__).parent; EV=ROOT/'evidence'; EV.mkdir(exist_ok=True)
points=json.loads((ROOT/'poi-options.json').read_text(encoding='utf-8'))
queries=[('opera2','日月贝','珠海'),('hyatt','珠海拱北凯悦酒店','珠海'),('longzhuda','龙珠达国际酒店','珠海'),('liyuan','利苑海鲜酒家珠光花园','珠海'),('xiangji','祥记面家','澳门'),('j Cheng','金城二食店','澳门'),('laoday','老Day牛杂','澳门'),('zeixian','泽贤记','澳门'),('penguinhall2','企鹅馆','珠海'),('spaceship2','长隆宇宙飞船','珠海')]
for key,q,city in queries:
    path=EV/('poi-'+key+'.json')
    try:
        if path.exists():d=json.loads(path.read_text(encoding='utf-8'))
        else:
            d=api('v3/place/text',{'keywords':q,'city':city,'citylimit':'true','offset':6,'extensions':'base'})
            path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');time.sleep(1.2)
        points[key]=[{k:p.get(k) for k in ['id','name','address','location','type']} for p in d.get('pois',[])]
        print(key,json.dumps(points[key],ensure_ascii=False),flush=True)
    except Exception as e:print(key,type(e).__name__,flush=True)
(ROOT/'poi-options.json').write_text(json.dumps(points,ensure_ascii=False,indent=2),encoding='utf-8')
maps=[{'id':'zhuhai','center':[113.575,22.252],'zoom':13},{'id':'macau','center':[113.554,22.177],'zoom':13},{'id':'ocean','center':[113.538,22.098],'zoom':16},{'id':'spaceship','center':[113.537,22.094],'zoom':16},{'id':'resort','center':[113.54,22.114],'zoom':14},{'id':'transfer','center':[113.55,22.17],'zoom':12}]
for m in maps:
    path=ROOT/('map-'+m['id']+'.png')
    if not path.exists():
        r=requests.get('https://restapi.amap.com/v3/staticmap',params={'key':KEY,'location':','.join(map(str,m['center'])),'zoom':m['zoom'],'size':'1024*1024','scale':1},timeout=35)
        if r.headers.get('Content-Type','').startswith('image'):path.write_bytes(r.content);print('MAP',m['id'],len(r.content),flush=True)
        else:print('MAP ERROR',m['id'],r.text[:100],flush=True)
        time.sleep(1.2)
(ROOT/'map-config.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2),encoding='utf-8')
