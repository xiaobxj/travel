"""Compare a Qika overnight with Enhe alternatives using AMap driving v5."""
import json,time
from pathlib import Path
from datetime import datetime,timezone
from amap_audit import api

ROOT=Path(__file__).parent
r=json.loads((ROOT/'amap-routes.json').read_text(encoding='utf-8'))
pois=r['pois']
new=json.loads((ROOT/'midpoint-stay-pois.json').read_text(encoding='utf-8'))
pois['恩和']=new['恩和俄罗斯族民族乡人民政府'][0]
queries=[('临江','恩和',['室韦']),('恩和','七卡',[]),('恩和','九卡观景点',[]),('九卡观景点','恩和',[]),('七卡','恩和',[])]
out=[]
for origin,destination,via in queries:
    time.sleep(1.1)
    params={'origin':pois[origin]['location'],'destination':pois[destination]['location'],'strategy':'32','show_fields':'cost,polyline'}
    if via:params['waypoints']=';'.join(pois[v]['location'] for v in via)
    d=api('v5/direction/driving',params)
    path=d['route']['paths'][0]
    item={'from':origin,'to':destination,'via':via,'distance':int(path['distance']),'duration':int(path['cost']['duration']),'path':path}
    out.append(item)
    print(json.dumps({k:v for k,v in item.items() if k!='path'},ensure_ascii=False),flush=True)
evidence={'queried_at':datetime.now(timezone.utc).isoformat(),'pois':pois,'segments':out}
(ROOT/'midpoint-route-audit.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
