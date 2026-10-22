"""Exact October 5 proposal with lunch and town stops, for user review only."""
import json
import time
from query_amap_planning import OUT, api, now, save

base = json.loads((OUT/'driving-live.json').read_text(encoding='utf-8'))
extra = json.loads((OUT/'extra-stops-driving-live.json').read_text(encoding='utf-8'))
pois={**base['pois'],**extra['pois']}
shilu='驶路部落民宿（餐厅整体参考点）'
via=[shilu,'团结广场','奥利亚列巴房','九卡观景点']
specs=[
    ('recommended_whole','白鹿岛酒店停车场','兰妮农家院',via),
    ('recommended_whole_with_eagle','白鹿岛酒店停车场','兰妮农家院',['老鹰嘴',*via]),
    ('bailudao_to_shilu','白鹿岛酒店停车场',shilu,[]),
    ('shilu_to_square',shilu,'团结广场',[]),
    ('jiuka_to_lanni','九卡观景点','兰妮农家院',[]),
]
evidence={'source':'AMap live API; no local cache','coordinateSystem':'GCJ-02','pois':{},'routes':[],
          'notes':['用于用户审核方案，未改网页或现有路线。',
                   '临江午餐终点采用驶路部落民宿整体POI，不是已核实独立餐厅或停车入口。',
                   '七卡终点为兰妮农家院，仅餐饮/村内参考点，不代表已订住宿。',
                   '整线包含团结广场、奥利亚、九卡；分段独立查询，不以分段时长代替整线。',
                   '老鹰嘴可规划不表示当天允许通行或营业。']}
for record_id,start,end,stops in specs:
    params={'origin':pois[start]['location'],'destination':pois[end]['location'],'strategy':32,'show_fields':'cost,polyline'}
    if stops:params['waypoints']=';'.join(pois[n]['location'] for n in stops)
    started=now()
    for attempt in range(4):
        try:
            response=api('v5/direction/driving',params)
            break
        except RuntimeError as error:
            if 'CUQPS' not in str(error) or attempt==3:raise
            time.sleep(1.2)
    path=response['route']['paths'][0]
    row={'id':record_id,'from':start,'to':end,'via':stops,'params':params,
         'queriedAtStart':started,'queriedAt':now(),'meters':int(path['distance']),'seconds':int(path['cost']['duration']),
         'roads':list(dict.fromkeys(s['road_name'] for s in path['steps'] if s.get('road_name'))),'response':response}
    evidence['routes'].append(row)
    for name in [start,*stops,end]:evidence['pois'][name]=pois[name]
    save('recommended-day4-driving-live.json',evidence)
    print(json.dumps({k:v for k,v in row.items() if k not in ['params','response']},ensure_ascii=False),flush=True)
    time.sleep(.7)
direct, eagle=evidence['routes'][:2]
evidence['eagleIncrement']={'baselineId':direct['id'],'withStopId':eagle['id'],
                           'addedMeters':eagle['meters']-direct['meters'],'addedSeconds':eagle['seconds']-direct['seconds']}
save('recommended-day4-driving-live.json',evidence)
save('recommended-day4-driving-live-summary.json',{**evidence,'routes':[{k:v for k,v in r.items() if k!='response'} for r in evidence['routes']]})
print(json.dumps(evidence['eagleIncrement'],ensure_ascii=False))
