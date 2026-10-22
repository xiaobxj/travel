"""Verify optional food stops separately from earlier planning evidence."""
import json
import time
from query_amap_planning import ROOT, OUT, api, now, save

audit = json.loads((ROOT / 'amap-place-audit.json').read_text(encoding='utf-8-sig'))
found = {}
for key, item in audit['places'].items():
    poi = item.get('poi', {})
    if any(word in poi.get('name','') for word in ['驶路','兰妮','列巴','团结广场']):
        found[key] = poi
print(json.dumps(found, ensure_ascii=False, indent=2))
save('extra-stops-historical-reference.json', found)

queries = [
    ('室韦团结广场', {'keywords':'团结广场', 'city':'150784', 'citylimit':'true', 'offset':20, 'extensions':'all'}),
    ('奥利亚列巴房', {'keywords':'奥利亚', 'city':'150784', 'citylimit':'true', 'offset':20, 'extensions':'all'}),
    ('临江驶路部落花园餐厅', {'keywords':'驶路部落', 'city':'150784', 'citylimit':'true', 'offset':20, 'extensions':'all'}),
    ('七卡兰妮农家院', {'keywords':'兰妮', 'city':'150784', 'citylimit':'true', 'offset':20, 'extensions':'all'}),
    ('森林公园内餐厅', {'keywords':'餐厅', 'location':'120.673537,51.337518', 'radius':1000, 'types':'050000', 'offset':25, 'sortrule':'distance', 'extensions':'all'}),
    ('红豆坡附近餐饮', {'keywords':'', 'location':'120.807667,51.351633', 'radius':3000, 'types':'050000', 'offset':25, 'sortrule':'distance', 'extensions':'all'}),
    ('一目九岭附近餐饮', {'keywords':'', 'location':'120.820550,51.379818', 'radius':3000, 'types':'050000', 'offset':25, 'sortrule':'distance', 'extensions':'all'}),
    ('森林公园餐饮文本', {'keywords':'莫尔道嘎国家森林公园', 'types':'050000', 'city':'150784', 'citylimit':'true', 'offset':25, 'extensions':'all'}),
]
evidence = {'source':'AMap live; no local cache', 'queries':[]}
for label, params in queries:
    endpoint = 'v3/place/around' if 'location' in params else 'v3/place/text'
    started = now()
    response = api(endpoint, params)
    evidence['queries'].append({'label':label, 'endpoint':endpoint, 'params':params, 'queriedAtStart':started, 'queriedAt':now(), 'response':response})
    save('extra-stops-pois-live.json', evidence)
    print(label,json.dumps([{k:p.get(k) for k in ['id','name','location','address','adname','type','parent','tel']} for p in response.get('pois',[])],ensure_ascii=False),flush=True)
    time.sleep(.7)
