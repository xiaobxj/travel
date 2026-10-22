"""Fresh same-batch comparison for park lunch; preserves earlier evidence."""
import json
import time
from query_amap_planning import OUT, api, now, save

existing = json.loads((OUT/'extra-stops-driving-live.json').read_text(encoding='utf-8'))
route_pois = json.loads((OUT/'driving-live.json').read_text(encoding='utf-8'))['pois']
pois = {name:existing['pois'][name] for name in ['森林餐厅','云树里餐厅']}
pois['白鹿岛酒店停车场']=route_pois['白鹿岛酒店停车场']
pois['一目九岭']={'id':'B0FFFGOZZU','name':'一目九岭','location':'120.820550,51.379818',
                'anchorNote':'景点整体POI，独立停车入口未核实。'}
specs=[('baseline_jiuling_to_bailudao','一目九岭','白鹿岛酒店停车场',[])]
for label,name in [('forest','森林餐厅'),('yunshuli','云树里餐厅')]:
    specs.extend([
        (f'jiuling_to_{label}','一目九岭',name,[]),
        (f'{label}_to_bailudao',name,'白鹿岛酒店停车场',[]),
        (f'jiuling_via_{label}_bailudao','一目九岭','白鹿岛酒店停车场',[name]),
    ])
evidence={'source':'AMap live API; no local cache','pois':pois,'routes':[],
          'notes':['只比较同批驾车路线；开车可规划不等于园内允许通行。',
                   '餐厅为父级森林公园的餐饮POI，未证实当天营业，也无实吃品质来源。',
                   '总绕行只以完整途经路线减去直达基线；不拼接分段估算。']}
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
    save('park-lunch-detours-live.json',evidence)
    print(json.dumps({k:v for k,v in row.items() if k not in ['params','response']},ensure_ascii=False),flush=True)
    time.sleep(.7)
baseline=evidence['routes'][0]
evidence['comparisons']={label:{'baselineId':baseline['id'],'withStopId':evidence['routes'][index]['id'],
                               'addedMeters':evidence['routes'][index]['meters']-baseline['meters'],
                               'addedSeconds':evidence['routes'][index]['seconds']-baseline['seconds']}
                         for label,index in [('forest',3),('yunshuli',6)]}
save('park-lunch-detours-live.json',evidence)
save('park-lunch-detours-live-summary.json',{**evidence,'routes':[{k:v for k,v in r.items() if k!='response'} for r in evidence['routes']]})
print(json.dumps(evidence['comparisons'],ensure_ascii=False))
