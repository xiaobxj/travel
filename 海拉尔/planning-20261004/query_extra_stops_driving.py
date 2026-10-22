"""Exact optional-stop routes, separate from all prior evidence."""
import json
import time
from query_amap_planning import ROOT, OUT, api, now, save

base = json.loads((ROOT / 'amap-routes.json').read_text(encoding='utf-8-sig'))
search = json.loads((OUT / 'extra-stops-pois-live.json').read_text(encoding='utf-8'))
by_id = {p['id']:p for q in search['queries'] for p in q['response'].get('pois',[])}
pois = dict(base['pois'])
for name, poi_id in [
    ('团结广场','B0J1K7C284'), ('奥利亚列巴房','B0LRGRTQRM'),
    ('驶路部落民宿（餐厅整体参考点）','B0MUZ98SOR'), ('兰妮农家院','B0JUVD9NJ0'),
    ('森林餐厅','B0FFKV59WO'), ('云树里餐厅','B0MRNZ73TP')
]:
    pois[name] = by_id[poi_id]
evidence = {'source':'AMap live; no local cache','coordinateSystem':'GCJ-02','pois':{},'routes':[],
            'notes':['驶路花园餐厅没有单独核实入口，以分类含餐饮的驶路部落民宿整体POI为参考；不视为停车入口。',
                     '森林餐厅、云树里餐厅高德父级为森林公园，仅地图线索；无实吃或当日营业证明。',
                     '驾车路线可计算不表示园内车辆通行获准。团结广场、列巴店、兰妮均为整体POI，不保证停车位置。']}
specs = [
    ('linjiang_to_shilu','临江','驶路部落民宿（餐厅整体参考点）'),
    ('shiwei_to_square','室韦','团结广场'),
    ('square_to_oliya','团结广场','奥利亚列巴房'),
    ('oliya_to_jiuka','奥利亚列巴房','九卡观景点'),
    ('qika_to_lanni','七卡','兰妮农家院'),
    ('park_to_forest_restaurant','森林公园停车场','森林餐厅'),
    ('park_to_yunshuli','森林公园停车场','云树里餐厅'),
]
for record_id, start, end in specs:
    params = {'origin':pois[start]['location'],'destination':pois[end]['location'], 'strategy':32,'show_fields':'cost,polyline'}
    started=now()
    for attempt in range(4):
        try:
            response=api('v5/direction/driving',params)
            break
        except RuntimeError as error:
            if 'CUQPS' not in str(error) or attempt==3:raise
            time.sleep(1.2)
    path=response['route']['paths'][0]
    row={'id':record_id,'from':start,'to':end,'via':[], 'params':params,
         'queriedAtStart':started,'queriedAt':now(),'meters':int(path['distance']),
         'seconds':int(path['cost']['duration']),
         'roads':list(dict.fromkeys(s['road_name'] for s in path['steps'] if s.get('road_name'))),'response':response}
    evidence['routes'].append(row)
    for name in [start,end]:evidence['pois'][name]=pois[name]
    save('extra-stops-driving-live.json',evidence)
    print(json.dumps({k:v for k,v in row.items() if k not in ['params','response']},ensure_ascii=False),flush=True)
    time.sleep(.7)
save('extra-stops-driving-live-summary.json',{**evidence,'routes':[{k:v for k,v in r.items() if k!='response'} for r in evidence['routes']]})
