"""Fresh October 4 route order comparison; read-only planning evidence."""
import json
import time
from query_amap_planning import ROOT, OUT, api, now, save

day3 = json.loads((ROOT/'moerdaoga-extra-driving-20261003-085640.json').read_text(encoding='utf-8'))
park = json.loads((OUT/'park-lunch-detours-live.json').read_text(encoding='utf-8'))
pois={**day3['pois'],**park['pois']}
specs=[
    ('morning_baseline','森林公园停车场','一目九岭',['红豆坡']),
    ('full_day3_baseline','莫尔道嘎','白鹿岛酒店停车场',['森林公园停车场','红豆坡','一目九岭']),
    ('town_to_park','莫尔道嘎','森林公园停车场',[]),
    ('jiuling_to_bailudao','一目九岭','白鹿岛酒店停车场',[]),
    ('bailudao_to_rafting','白鹿岛酒店停车场','白鹿岛漂流',[]),
]
for label,name in [('forest','森林餐厅'),('yunshuli','云树里餐厅')]:
    specs.extend([
        (f'park_via_{label}_hongdou_to_jiuling','森林公园停车场','一目九岭',[name,'红豆坡']),
        (f'park_to_{label}','森林公园停车场',name,[]),
        (f'{label}_to_hongdou',name,'红豆坡',[]),
    ])
specs.append(('hongdou_to_jiuling','红豆坡','一目九岭',[]))
stamp=now().replace('-','').replace(':','').replace('+0800','')
filename=f'day3-lunch-order-live-{stamp}.json'
evidence={'source':'AMap live API; no local cache','coordinateSystem':'GCJ-02','queriedAtStart':now(),
          'pois':{},'routes':[],
          'notes':['当天早午餐时段及营业尚未电话确认，驾车路线不表示餐厅营业。',
                   '园内道路允许私家车通行以景区入口当日答复为准。',
                   '酒店停车场不代表酒店餐厅入口；漂流为整体POI，不保证为当日报到或上船点。',
                   '比较完整途经路线；不将分段累加成总时间。']}
for record_id,start,end,via in specs:
    params={'origin':pois[start]['location'],'destination':pois[end]['location'],'strategy':32,'show_fields':'cost,polyline'}
    if via:params['waypoints']=';'.join(pois[n]['location'] for n in via)
    started=now()
    for attempt in range(4):
        try:
            response=api('v5/direction/driving',params)
            break
        except RuntimeError as error:
            if 'CUQPS' not in str(error) or attempt==3:raise
            time.sleep(1.2)
    path=response['route']['paths'][0]
    row={'id':record_id,'from':start,'to':end,'via':via,'params':params,'queriedAtStart':started,'queriedAt':now(),
         'meters':int(path['distance']),'seconds':int(path['cost']['duration']),
         'roads':list(dict.fromkeys(s['road_name'] for s in path['steps'] if s.get('road_name'))),'response':response}
    evidence['routes'].append(row)
    for name in [start,*via,end]:evidence['pois'][name]=pois[name]
    save(filename,evidence)
    print(json.dumps({k:v for k,v in row.items() if k not in ['params','response']},ensure_ascii=False),flush=True)
    time.sleep(.7)
by_id={r['id']:r for r in evidence['routes']}
baseline=by_id['morning_baseline']
evidence['comparisons']={label:{'baselineId':baseline['id'],'withStopId':by_id[f'park_via_{label}_hongdou_to_jiuling']['id'],
                              'addedMeters':by_id[f'park_via_{label}_hongdou_to_jiuling']['meters']-baseline['meters'],
                              'addedSeconds':by_id[f'park_via_{label}_hongdou_to_jiuling']['seconds']-baseline['seconds']}
                        for label in ['forest','yunshuli']}
evidence['queriedAtEnd']=now()
save(filename,evidence)
save(filename.replace('.json','-summary.json'),{**evidence,'routes':[{k:v for k,v in r.items() if k!='response'} for r in evidence['routes']]})
print(filename,json.dumps(evidence['comparisons'],ensure_ascii=False))
