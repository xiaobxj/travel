"""Live, read-only AMap evidence; all output is new and contains no API key."""
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from amap_audit import api

OUT = ROOT / 'planning-20261004'
TZ = dt.timezone(dt.timedelta(hours=8))


def now():
    return dt.datetime.now(TZ).isoformat(timespec='seconds')


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def get_existing():
    routes = json.loads((ROOT / 'amap-routes.json').read_text(encoding='utf-8-sig'))
    audit = json.loads((ROOT / 'amap-place-audit.json').read_text(encoding='utf-8-sig'))
    result = {}
    for key, item in audit['places'].items():
        if any(word in json.dumps(item, ensure_ascii=False) for word in ['林曦', '雅娟', '红姐', '中餐厅', '老鹰嘴']):
            result[key] = item
    save('existing-reference-pois.json', result)
    print(json.dumps({k: {'poi': v.get('poi'), 'status': v.get('status'), 'baseline': v.get('baseline')} for k, v in result.items()}, ensure_ascii=False))
    return routes


def search():
    queries = ['太平林场林曦农家菜', '林曦农家菜', '老鹰嘴', '雅娟饭店 莫尔道嘎', '红姐饭店 莫尔道嘎', '白鹿岛酒店中餐厅']
    data = {'source': 'AMap live API, bypasses local cache', 'queries': []}
    for query in queries:
        params = {'keywords': query, 'city': '150700', 'citylimit': 'true', 'offset': 20, 'extensions': 'all'}
        started = now()
        response = api('v3/place/text', params)
        data['queries'].append({'query': query, 'queriedAtStart': started, 'queriedAt': now(), 'params': params, 'response': response})
        print(query, json.dumps([{k:p.get(k) for k in ['id','name','location','address','adname','type','tel']} for p in response.get('pois',[])],ensure_ascii=False))
        save('poi-search-live.json', data)


if __name__ == '__main__':
    get_existing()
    search()
