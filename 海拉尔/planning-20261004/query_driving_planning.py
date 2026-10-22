"""Fresh driving and POI records for review; never mutates the published plan."""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from query_amap_planning import ROOT, OUT, api, now, save

routes = json.loads((ROOT / 'amap-routes.json').read_text(encoding='utf-8-sig'))
pois = dict(routes['pois'])
searches = json.loads((OUT / 'poi-search-live.json').read_text(encoding='utf-8'))
pois['林曦农家菜'] = searches['queries'][0]['response']['pois'][0]
eagles = [p for p in searches['queries'][2]['response']['pois'] if p['id'] == 'B0FFKQN1I0' and p['typecode'] == '110000']
assert len(eagles) == 1
pois['老鹰嘴'] = eagles[0]
detail_evidence = {'source': 'AMap live API; no local cache', 'queries': []}
for name, poi_id in [('红姐饭店', 'B0KU37EUGG'), ('雅娟饭店', 'B0H1X430OA'), ('姐妹饭店', 'B0FFFGP0DC')]:
    params = {'id': poi_id, 'extensions': 'all'}
    started = now()
    response = api('v3/place/detail', params)
    detail_evidence['queries'].append({'label': name, 'params': params, 'queriedAtStart': started, 'queriedAt': now(), 'response': response})
    matches = [p for p in response.get('pois', []) if p['id'] == poi_id]
    assert len(matches) == 1, name
    pois[name] = matches[0]
    save('restaurant-pois-live.json', detail_evidence)
    print(name, json.dumps({k:matches[0].get(k) for k in ['id', 'name', 'location', 'address', 'tel']}, ensure_ascii=False), flush=True)

evidence = {'source': 'AMap live driving API; no local cache', 'coordinateSystem': 'GCJ-02',
            'notes': ['参考点保持原计划：临江为临江贝加尔驿站；七卡为七卡戍边食府，不代表已订住宿。',
                      'POI或驾车规划返回结果不表示餐厅营业、景区开放或道路已获通行许可。',
                      '白鹿岛酒店中餐厅未核实独立POI，不编造停车场到餐厅的驾车路线。',
                      '老鹰嘴按旅游景点B0FFKQN1I0选取；莫尔道嘎镇同名住宿点不作为景点。'],
            'pois': {}, 'routes': []}

def drive(record_id, start, end, via=()):
    params = {'origin': pois[start]['location'], 'destination': pois[end]['location'],
              'strategy': 32, 'show_fields': 'cost,polyline'}
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
    row = {'id': record_id, 'from': start, 'to': end, 'via': list(via),
           'params': params, 'queriedAtStart': started, 'queriedAt': now(),
           'meters': int(path['distance']), 'seconds': int(path['cost']['duration']),
           'roads': list(dict.fromkeys(s['road_name'] for s in path['steps'] if s.get('road_name'))),
           'response': response}
    evidence['routes'].append(row)
    for name in [start, *via, end]:
        evidence['pois'][name] = pois[name]
    save('driving-live.json', evidence)
    print(json.dumps({k:v for k,v in row.items() if k not in ['response', 'params']}, ensure_ascii=False), flush=True)
    time.sleep(.7)

day4 = [s for s in routes['segments'] if s['day'] == 4]
for i, segment in enumerate(day4):
    via = segment.get('mandatoryVia', segment.get('via', []))
    drive(f'day4_leg_{i+1}', segment['from'], segment['to'], via)
whole_via = []
for s in day4:
    whole_via.extend(s.get('mandatoryVia', s.get('via', [])))
    if s != day4[-1]:
        whole_via.append(s['to'])
drive('day4_whole', day4[0]['from'], day4[-1]['to'], whole_via)
drive('bailudao_linxi_linjiang', '白鹿岛酒店停车场', '临江', ['林曦农家菜'])
drive('bailudao_to_linxi', '白鹿岛酒店停车场', '林曦农家菜')
drive('linxi_to_linjiang', '林曦农家菜', '临江')
drive('bailudao_eagle_linjiang', '白鹿岛酒店停车场', '临江', ['老鹰嘴'])
drive('bailudao_to_eagle', '白鹿岛酒店停车场', '老鹰嘴')
drive('eagle_to_linjiang', '老鹰嘴', '临江')
drive('bailudao_linxi_eagle_linjiang', '白鹿岛酒店停车场', '临江', ['林曦农家菜', '老鹰嘴'])
for name, label in [('红姐饭店','hongjie'), ('雅娟饭店','yajuan'), ('姐妹饭店','jiemei')]:
    drive(f'town_to_{label}', '莫尔道嘎', name)
    drive(f'{label}_to_park', name, '森林公园停车场')
save('driving-live-summary.json', {**evidence, 'routes': [{k:v for k,v in r.items() if k != 'response'} for r in evidence['routes']]})
