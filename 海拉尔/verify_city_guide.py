"""Offline data/build checks; no browser or account access."""
import json
import re
import subprocess
from pathlib import Path
from collect_city_xhs import parse_count, total, rank, categories, screen_content

ROOT = Path(__file__).resolve().parent
assert [parse_count(x) for x in ['1.2万', '3,456', '2.3k', '1.001k', '0', '点赞', '', None, '-1']] == [12000, 3456, 2300, 1001, 0, None, None, None, None]
a = {'id': 'a', 'likes': 100, 'collects': 200, 'comments': 5}
b = {'id': 'b', 'likes': 1000, 'collects': None, 'comments': 8}
c = {'id': 'c', 'likes': 1, 'collects': 2, 'comments': 3}
assert total(a) == 305 and total(b) is None
assert [x['id'] for x in rank([b, c, a])] == ['a', 'c', 'b']
assert set(categories('根河铁锅炖 咖啡 日落 酒店 自驾攻略')) == {'吃饭', '咖啡茶饮', '游玩', '住宿', '攻略'}
assert screen_content('帮我看看路线行不行', '待规划路线') is not None
assert screen_content('海拉尔', '迷糊了迷糊了香迷糊了') is not None
assert screen_content('根河早餐', '根河出发之前在市区吃早餐，吃完出发前往敖鲁古雅，随后继续前往莫尔道嘎。') is None
page = (ROOT / 'itinerary-map.html').read_text(encoding='utf-8')
assert '__DATA__' not in page and '__BASEMAP__' not in page
assert page.count('id="map"') == 1 and page.count('data:image/png;base64,') == 1
config = json.loads((ROOT / 'city-guide-config.json').read_text(encoding='utf-8'))
routes = json.loads((ROOT / 'amap-routes.json').read_text(encoding='utf-8'))
data = json.loads((ROOT / 'city-notes.json').read_text(encoding='utf-8'))
assert len(config['cities']) == 13
assert all(c['poi'] in routes['pois'] for c in config['cities'])
assert len({c['id'] for c in config['cities']}) == len(config['cities'])
assert len({n['id'] for n in data['notes']}) == len(data['notes'])
assert '????' not in json.dumps(data, ensure_ascii=False)
assert all(category in config['categories'] for n in data['notes'] for category in n['categories'])
for note in data['notes']:
    assert all(city in {c['id'] for c in config['cities']} for city in note['cityIds'])
    if note.get('origin') == 'cdp':
        raw = json.loads((ROOT / note['evidenceFile']).read_text(encoding='utf-8'))['note']
        assert note['id'] == raw['id']
        assert all(note[key] == parse_count(raw[key]) for key in ('likes', 'collects', 'comments'))
check = ROOT / '.inline-check.js'
try:
    for index, script in enumerate(re.findall(r'<script>(.*?)</script>', page, re.S)):
        check.write_text(script, encoding='utf-8')
        result = subprocess.run(['node', '--check', str(check)], capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, (index, result.stderr)
finally:
    check.unlink(missing_ok=True)
js = r"""
const assert=require('node:assert/strict');
const {score,sortedNotes,filterRows}=require('./city-guide.js');
const base={cityIds:['genhe'],categories:['吃饭'],suspectedAd:false,title:'根河铁锅炖'};
const rows=[{...base,id:'missing',likes:50000,collects:null,comments:1},{...base,id:'small',likes:2,collects:3,comments:1},{...base,id:'large',likes:10,collects:20,comments:30},{...base,id:'ad',likes:100,collects:100,comments:100,suspectedAd:true}];
assert.equal(score(rows[0]),null);
assert.equal(score({likes:0,collects:0,comments:0}),0);
assert.equal(score({likes:1,collects:'2',comments:3}),null);
assert.deepEqual(sortedNotes(rows).map(n=>n.id),['ad','large','small','missing']);
const options={category:'all',complete:true,excludeAds:true,minimum:0,text:''};
assert.deepEqual(filterRows(rows,'genhe',options).map(n=>n.id),['large','small']);
assert.deepEqual(filterRows(rows,'genhe',{...options,minimum:20}).map(n=>n.id),['large']);
assert.deepEqual(filterRows(rows,'genhe',{...options,text:'咖啡'}),[]);
assert.deepEqual(filterRows(rows,'genhe',{...options,category:'住宿'}),[]);
assert.deepEqual(filterRows(rows,'qika',options),[]);
assert.deepEqual(filterRows(rows,'genhe',{...options,complete:false}).map(n=>n.id),['large','small','missing']);
"""
result = subprocess.run(['node', '-e', js], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert result.returncode == 0, result.stderr
print(json.dumps({'status': 'PASS', 'cities': len(config['cities']), 'notes': len(data['notes']), 'maps': 1,
                  'checks': ['count parsing and unknowns', 'descending total rank', 'city/category/search/minimum/ad filters', '13 valid map anchors', 'single original base map', 'all inline JS syntax', 'Chinese data encoding']}, ensure_ascii=False))
