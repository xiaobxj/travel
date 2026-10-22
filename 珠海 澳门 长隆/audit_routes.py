import sys,json,time,datetime
from pathlib import Path
sys.path.insert(0,r'D:\travel\海拉尔')
from amap_audit import api
ROOT=Path(__file__).parent; EV=ROOT/'evidence'
d=json.loads((ROOT/'poi-options.json').read_text(encoding='utf-8'))
queries=[('jinyue','金悦轩海鲜酒家拱北','珠海'),('bermuda','百慕大历险','珠海'),('submarine','深海潜艇','珠海'),('monorail','海洋单轨车','珠海'),('orcafood','鲸生鲸世餐厅','珠海'),('partyfood','派对厨房','珠海'),('coralfood','长隆珊瑚餐厅','珠海'),('oceanfood','城堡餐厅','珠海')]
for key,q,city in queries:
    path=EV/('poi-'+key+'.json')
    if path.exists():r=json.loads(path.read_text(encoding='utf-8'))
    else:
        r=api('v3/place/text',{'keywords':q,'city':city,'citylimit':'true','offset':5});path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');time.sleep(1.2)
    d[key]=[{k:p.get(k) for k in ['id','name','address','location','type']} for p in r.get('pois',[])]
    print('POI',key,json.dumps(d[key][:3],ensure_ascii=False),flush=True)
(ROOT/'poi-options.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
chosen={k:v[0] for k,v in d.items() if v}
chosen['opera']=d['opera2'][1];chosen['penguinhall']=d['penguinhall2'][0];chosen['spaceshipgate']=d['spaceship2'][1];chosen['londoner']=d['londoner'][1];chosen['jincheng']=d['j Cheng'][0]
(ROOT/'selected-pois.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding='utf-8')
pairs=[(1,'longzhuda','liyuan','taxi'),(1,'liyuan','postoffice','taxi'),(1,'postoffice','fishergirl','walk'),(1,'fishergirl','xianglu','walk'),(1,'xianglu','opera','taxi'),(1,'opera','jinyue','taxi'),(1,'jinyue','longzhuda','taxi'),(2,'longzhuda','gongbei','walk'),(2,'barrier','senado','taxi'),(2,'senado','rosary','walk'),(2,'rosary','stpaul','walk'),(2,'stpaul','jincheng','walk'),(2,'jincheng','cunha','taxi'),(2,'cunha','venetian','walk'),(2,'venetian','londoner','walk'),(2,'londoner','barrier','taxi'),(2,'gongbei','longzhuda','walk'),(3,'longzhuda','penguinhotel','taxi'),(3,'penguinhotel','ocean','walk'),(4,'penguinhotel','spaceshipgate','walk'),(4,'spaceshipgate','penguinhotel','walk'),(4,'penguinhotel','zhuhai_station','taxi')]
routes=[]
for day,a,b,mode in pairs:
    name=a+'-'+b+'-'+mode; path=EV/('route-'+name+'.json')
    params={'origin':chosen[a]['location'],'destination':chosen[b]['location']}
    endpoint='v3/direction/walking' if mode=='walk' else 'v5/direction/driving'
    if mode=='taxi': params.update(strategy=32,show_fields='cost,polyline')
    rec={'id':name,'day':day,'from':a,'to':b,'mode':mode,'endpoint':endpoint,'params':params,'queried_at':datetime.datetime.now().isoformat(timespec='seconds')}
    try:
        if path.exists():raw=json.loads(path.read_text(encoding='utf-8'))
        else:
            raw=api(endpoint,params);path.write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8');time.sleep(1.2)
        p=raw['route']['paths'][0]
        rec.update(status='amap',distance=int(p['distance']),seconds=int(p['duration'] if mode=='walk' else p['cost']['duration']),polyline=[list(map(float,xy.split(','))) for s in p.get('steps',[]) for xy in s.get('polyline','').split(';') if xy])
    except Exception as e:rec.update(status='unavailable',error=type(e).__name__);print('FAIL',name,type(e).__name__,flush=True)
    routes.append(rec);print(name,rec['status'],rec.get('seconds'),rec.get('distance'),flush=True)
    (ROOT/'routes.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2),encoding='utf-8')
