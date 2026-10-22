from amap_audit import *
from datetime import datetime
raw=json.loads((ROOT/'amap-pois.json').read_text(encoding='utf-8'))
selection={'海拉尔站':('海拉尔站',0),'机场停车场':('呼伦贝尔海拉尔机场',3),'莫日格勒游客中心':('莫日格勒河游客中心',0),'曲水云天':('曲水云天',0),'额尔古纳':('额尔古纳市政府',0),'根河':('根河市政府',0),'敖鲁古雅停车场':('敖鲁古雅使鹿部落',1),'莫尔道嘎':('莫尔道嘎镇政府',0),'森林公园停车场':('莫尔道嘎国家森林公园入口',1),'白鹿岛酒店停车场':('白鹿岛大酒店',1),'临江':('临江村',4),'室韦':('室韦',1),'九卡观景点':('九卡',0),'七卡':('七卡',0),'黑山头':('黑山头镇政府',0),'得耳布尔':('得耳布尔',0)}
pois={n:raw[q][i] for n,(q,i) in selection.items()}
segments=[(1,'海拉尔站','莫日格勒游客中心',[]),(1,'莫日格勒游客中心','额尔古纳',[]),(1,'额尔古纳','根河',[]),(2,'根河','敖鲁古雅停车场',[]),(2,'敖鲁古雅停车场','莫尔道嘎',['得耳布尔']),(3,'莫尔道嘎','森林公园停车场',[]),(3,'森林公园停车场','白鹿岛酒店停车场',[]),(4,'白鹿岛酒店停车场','临江',[]),(5,'临江','室韦',[]),(5,'室韦','九卡观景点',[]),(5,'九卡观景点','七卡',[]),(5,'七卡','黑山头',[]),(5,'黑山头','额尔古纳',[]),(6,'额尔古纳','海拉尔站',[]),(0,'额尔古纳','机场停车场',[]),(0,'海拉尔站','曲水云天',[]),(0,'曲水云天','额尔古纳',[]),(0,'白鹿岛酒店停车场','临江',['莫尔道嘎'])]
output={'queried_at':datetime.now().astimezone().isoformat(),'coordinate_system':'GCJ-02','strategy':32,'pois':pois,'segments':[]}
for day,a,b,via in segments:
    params={'origin':pois[a]['location'],'destination':pois[b]['location'],'strategy':32,'show_fields':'cost,polyline','origin_id':pois[a]['id'],'destination_id':pois[b]['id']}
    if via:params['waypoints']=';'.join(pois[x]['location'] for x in via)
    d=api('v5/direction/driving',params)
    name=f'{day}_{a}_{b}'+('_经'+','.join(via) if via else '')
    (ROOT/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    if not d.get('route',{}).get('paths'):raise RuntimeError(name+' NO ROUTE')
    p=d['route']['paths'][0]
    roads=list(dict.fromkeys(s.get('road_name','未命名路') for s in p['steps']))
    r={'day':day,'from':a,'to':b,'via':via,'distance':int(p['distance']),'duration':int(p['cost']['duration']),'roads':roads,'path':p,'raw_file':name+'.json'}
    output['segments'].append(r)
    print(name,round(r['distance']/1000,1),round(r['duration']/60),'min',','.join(roads),flush=True)
    time.sleep(.3)
(ROOT/'amap-routes.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
