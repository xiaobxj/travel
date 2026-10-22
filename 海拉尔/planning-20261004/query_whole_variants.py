"""Add fresh full-day alternatives to the planning-only evidence."""
import json
import time
from pathlib import Path
from query_amap_planning import OUT, api, now, save

evidence = json.loads((OUT / 'driving-live.json').read_text(encoding='utf-8'))
pois = evidence['pois']
specs = [
    ('day4_whole_linxi', '白鹿岛酒店停车场', '七卡', ['林曦农家菜', '临江', '室韦', '九卡观景点']),
    ('day4_whole_linxi_eagle', '白鹿岛酒店停车场', '七卡', ['林曦农家菜', '老鹰嘴', '临江', '室韦', '九卡观景点']),
    ('linxi_to_eagle', '林曦农家菜', '老鹰嘴', []),
]
for record_id, start, end, via in specs:
    params = {'origin': pois[start]['location'], 'destination': pois[end]['location'], 'strategy': 32, 'show_fields': 'cost,polyline'}
    if via:
        params['waypoints'] = ';'.join(pois[n]['location'] for n in via)
    started = now()
    for attempt in range(4):
        try:
            response = api('v5/direction/driving', params)
            break
        except RuntimeError as error:
            if 'CUQPS' not in str(error) or attempt == 3:
                raise
            time.sleep(1.2)
    path = response['route']['paths'][0]
    row = {'id': record_id, 'from': start, 'to': end, 'via': via, 'params': params,
           'queriedAtStart': started, 'queriedAt': now(), 'meters': int(path['distance']),
           'seconds': int(path['cost']['duration']),
           'roads': list(dict.fromkeys(s['road_name'] for s in path['steps'] if s.get('road_name'))),
           'response': response}
    evidence['routes'].append(row)
    save('driving-live.json', evidence)
    print(json.dumps({k:v for k,v in row.items() if k not in ['params','response']}, ensure_ascii=False), flush=True)
    time.sleep(.7)
save('driving-live-summary.json', {**evidence, 'routes': [{k:v for k,v in r.items() if k != 'response'} for r in evidence['routes']]})
