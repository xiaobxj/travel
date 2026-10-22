"""Offline verification against saved AMap responses, not fresh API requests."""
import base64
import json
import re
import subprocess
import sys
from pathlib import Path
from amap_recommendation_audit import nearest, points, KEY

ROOT=Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
audit=read('amap-place-audit.json')
updates=read('amap-place-updates.json') if (ROOT/'amap-place-updates.json').exists() else {'places':{}}
day3_updates=read('amap-place-day3-updates.json') if (ROOT/'amap-place-day3-updates.json').exists() else {'places':{}}
oct4_updates=read('amap-place-oct4-updates.json') if (ROOT/'amap-place-oct4-updates.json').exists() else {'places':{}}
all_updates={**updates['places'],**day3_updates['places'],**oct4_updates['places']}
historical_issues=read('amap-historical-evidence-issues.json') if (ROOT/'amap-historical-evidence-issues.json').exists() else {'places':{}}
observed_gaps=set()
routes=read('amap-routes.json')
cities={c['id']:c for c in read('city-guide-config.json')['cities']}
selections={x['id']:x for x in read('amap-place-selections.json')}
data=read('city-recommendations.json')
assert audit['coordinateSystem']=='GCJ-02'
assert nearest('0.5,0.01',[(0,0),(1,0)])['meters'] in range(1100,1120)
assert nearest('0.5,0',[(0,0),(1,0)])['meters']==0
verified=[]
for slug,place in audit['places'].items():
    if place['status']!='verified':
        assert not selections[slug]['poiId']
        continue
    verified.append(place)
    assert selections[slug]['poiId']==place['poi']['id']
    sources=[read(f) for f in place['poiEvidenceFiles']]
    pois=[p for s in sources for p in s['response'].get('pois',[])]
    actual=next(p for p in pois if p['id']==place['poi']['id'])
    assert all(actual.get(k)==v for k,v in place['poi'].items())
    assert all(s['endpoint']=='v3/place/text' and s['response']['status']=='1' for s in sources)
    segment=routes['segments'][place['segmentIndex']]
    assert place['day']==segment['day'] and place['day'] in cities[place['cityId']]['days']
    assert place['from']==segment['from'] and place['to']==segment['to']
    assert place['mandatoryVia']==segment['via']
    assert place['routeOffsetMeters']==nearest(place['poi']['location'],points(segment))['meters']
    evidence={}
    for field in ['fromAnchor','baseline','withStop']:
        if field not in place:continue
        result=place[field];saved=read(result['evidenceFile']);evidence[field]=saved
        assert saved['endpoint']=='v5/direction/driving' and saved['response']['status']=='1'
        assert saved['params']['strategy']==32
        path=saved['response']['route']['paths'][0]
        gap=historical_issues['places'].get(slug,{}).get('fields',{}).get(field)
        if gap:
            assert gap['evidenceFile']==result['evidenceFile']
            assert gap['historical']=={key:result[key] for key in ['meters','seconds','queriedAt']}
            assert gap['current']==dict(meters=int(path['distance']),seconds=int(path['cost']['duration']),queriedAt=saved['queriedAt'])
            assert gap['current']['queriedAt']>gap['historical']['queriedAt']
            assert (gap['current']['meters'],gap['current']['seconds'])!=(result['meters'],result['seconds'])
            observed_gaps.add((slug,field))
        else:
            assert result['meters']==int(path['distance']) and result['seconds']==int(path['cost']['duration']), (slug,field,result['evidenceFile'],'saved audit and raw response differ')
    if place['comparisonStatus']=='unavailable':continue
    base=evidence['baseline']['params'];insert=evidence['withStop']['params']
    for field in ['origin','destination','origin_id','destination_id','strategy']:
        assert base[field]==insert[field]
    for field,endpoint in [('origin',place['from']),('destination',place['to'])]:
        assert base[field]==routes['pois'][endpoint]['location']
    expected=[routes['pois'][name]['location'] for name in segment['via']]
    assert base.get('waypoints','').split(';')==expected or not expected and 'waypoints' not in base
    added=insert.get('waypoints','').split(';')
    assert place['poi']['location'] in added
    # The original mandatory waypoints retain their relative order.
    positions=[added.index(p) for p in expected]
    assert positions==sorted(positions)
    for field,result_field,raw_field,added_field in [('meters','meters','rawDeltaMeters','addedMeters'),('seconds','seconds','rawDeltaSeconds','addedSeconds')]:
        delta=place['withStop'][field]-place['baseline'][field]
        assert place[raw_field]==delta and place[added_field]==max(0,delta)
    assert place['comparisonStatus']==('review' if place['rawDeltaMeters'] < -500 or place['rawDeltaSeconds'] < -300 else 'ready')
    if slug in historical_issues['places']:
        # Only the old summary's arithmetic survives; this is explicitly not a
        # verified comparison against the now-refreshed historical raw response.
        assert place['baseline']['queriedAt'][:10]==place['withStop']['queriedAt'][:10]
    else:
        assert evidence['baseline']['queriedAt'][:10]==evidence['withStop']['queriedAt'][:10]

assert observed_gaps=={(slug,field) for slug,issue in historical_issues['places'].items() for field in issue['fields']}

# Preserve the historical audit's independent checks and its frozen coverage.
assert len({p['poi']['id'] for p in verified})==70
update_evidence_files=set()
if updates['places']:
    assert updates['coordinateSystem']=='GCJ-02' and updates['strategy']==32

def location(name,document):
    names={p['name']:p['location'] for p in document['pois'].values()}
    names.update({name:p['location'] for name,p in routes['pois'].items()})
    return names[name]

for slug,place in updates['places'].items():
    assert place['status']=='verified' and place['currentRouteEvidence']
    assert place['day'] in cities[place['cityId']]['days']
    queries=[query for filename in place['poiEvidenceFiles'] for query in read(filename)['queries']]
    matches=[(query,poi) for query in queries for poi in query['response'].get('pois',[]) if poi['id']==place['poi']['id']]
    assert matches,slug
    assert any(query['response']['status']=='1' and all(poi.get(k)==v for k,v in place['poi'].items()) for query,poi in matches),slug
    update_evidence_files.update(place['poiEvidenceFiles'])
    evidence={}
    for field in ['fromAnchor','baseline','withStop']:
        result=place[field]
        document=read(result['evidenceFile'])
        saved=document['routes'][result['evidenceRouteKey']]
        evidence[field]=(document,saved)
        update_evidence_files.add(result['evidenceFile'])
        assert document['endpoint']=='v5/direction/driving' and document['coordinateSystem']=='GCJ-02'
        assert document['strategy']==saved['params']['strategy']==32
        assert saved['status']=='ok' and saved['response']['status']=='1'
        path=saved['response']['route']['paths'][0]
        assert result['meters']==saved['meters']==int(path['distance']),(slug,field,'meters')
        assert result['seconds']==saved['seconds']==int(path['cost']['duration']),(slug,field,'seconds')
        assert result['queriedAt']==saved['queriedAtEnd']
        assert result['origin']==saved['origin'] and result['destination']==saved['destination']
        assert result['via']==saved['via']
        for endpoint in ['origin','destination']:
            poi=next(p for p in document['pois'].values() if p['name']==result[endpoint])
            assert saved['params'][endpoint]==poi['location']
            assert saved['params'][endpoint+'_id']==poi['id']
        expected=[location(name,document) for name in saved['via']]
        assert saved['params'].get('waypoints','').split(';')==(expected or [''])
    assert evidence['fromAnchor'][1]['params']['destination']==place['poi']['location']
    base_doc,base_saved=evidence['baseline']
    insert_doc,insert_saved=evidence['withStop']
    base=base_saved['params'];insert=insert_saved['params']
    assert place['baseline']['evidenceFile']==place['withStop']['evidenceFile'], 'Compare routes from one saved query batch'
    assert base['origin']==insert['origin']==location(place['from'],insert_doc)
    assert base['origin_id']==insert['origin_id']
    assert insert['destination']==location(place['to'],insert_doc)
    assert base.get('waypoints','').split(';')==([location(name,base_doc) for name in place['mandatoryVia']] or [''])
    assert insert.get('waypoints','').split(';')==([location(name,insert_doc) for name in place['orderedVia']] or [''])
    baseline_via=base.get('waypoints','').split(';') if base.get('waypoints') else []
    inserted_via=insert.get('waypoints','').split(';') if insert.get('waypoints') else []
    if place['comparisonKind']=='via-insertion':
        assert base['destination']==insert['destination'] and base['destination_id']==insert['destination_id']
        assert inserted_via.count(place['poi']['location'])==1
        assert [p for p in inserted_via if p!=place['poi']['location']]==baseline_via
    else:
        assert place['comparisonKind']=='endpoint-extension'
        assert insert['destination']==place['poi']['location'] and base['destination']!=insert['destination']
        assert inserted_via==baseline_via+[base['destination']], 'The old endpoint becomes the final mandatory stop'
    for field,raw_field,added_field in [('meters','rawDeltaMeters','addedMeters'),('seconds','rawDeltaSeconds','addedSeconds')]:
        delta=place['withStop'][field]-place['baseline'][field]
        assert place[raw_field]==delta and place[added_field]==max(0,delta),(slug,field,'delta')
    assert place['comparisonStatus']==('review' if place['rawDeltaMeters'] < -500 or place['rawDeltaSeconds'] < -300 else 'ready')
    assert base_saved['queriedAtEnd'][:10]==insert_saved['queriedAtEnd'][:10]

if day3_updates['places']:
    # Day 3 uses full route and leg evidence with its own comparison model;
    # validate those saved API values before including them in global coverage.
    day3_check=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verify_day3_data.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    assert day3_check.returncode==0,day3_check.stdout+'\n'+day3_check.stderr
    print(day3_check.stdout.strip())

if oct4_updates['places']:
    oct4_check=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verify_oct4_place_data.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    assert oct4_check.returncode==0,oct4_check.stdout+'\n'+oct4_check.stderr
    print(oct4_check.stdout.strip())
    for place in oct4_updates['places'].values():
        update_evidence_files.update(place['poiEvidenceFiles'])
        update_evidence_files.add(place['fromAnchor']['evidenceFile'])

merged_places={**audit['places'],**all_updates}
for slug,issue in historical_issues['places'].items():
    assert issue['overlay']['comparisonStatus']=='unavailable' and issue['overlay']['historicalEvidenceIssue']
    assert issue['overlay']['comparisonNote']
    if slug not in all_updates:
        merged_places[slug]={**merged_places[slug],**issue['overlay'],'evidenceIssue':True}
        merged_places[slug]['comparisonNote']='该地点的旧车程暂不能完整复核，暂不参与绕路排名；请使用高德重新导航。本次新增路线的查验结果见10月3日分段车程。'
        if 'fromAnchor' in issue['fields']:
            merged_places[slug].pop('fromAnchor',None)
merged_verified=[p for p in merged_places.values() if p['status']=='verified']
assert data['amapUniquePois']==len({p['poi']['id'] for p in merged_verified})
assert data['amapUniquePois']==len({x['placeCheck']['poi']['id'] for x in data['items'] if x['placeCheck']['status']=='verified'})
assert data['amapVerifiedItems']==sum(x['placeCheck']['status']=='verified' for x in data['items'])
assert data['amapRouteReady']==sum(x['placeCheck'].get('comparisonStatus')=='ready' for x in data['items'])
byid={x['id']:x for x in data['items']}
assert all(byid[slug]['placeCheck']==place for slug,place in all_updates.items()), 'New evidence must override historical mappings in generated data'
for slug in historical_issues['places']:
    if slug in all_updates:continue
    assert byid[slug]['placeCheck']==merged_places[slug],(slug,'Historical evidence gap must disable route comparison in generated data')
    poi_id=merged_places[slug]['poi']['id']
    assert all(item['placeCheck'].get('comparisonStatus')=='unavailable' for item in data['items'] if item['placeCheck'].get('poi',{}).get('id')==poi_id)
for slug in ['mordaga-new-jiemei','eerguna-new-fuji','eerguna-tieshan','mordaga-hongjie','bailudao-restaurant','shiwei-new-aoliya']:
    assert byid[slug]['cautionCount'] and byid[slug]['strength']==0
assert byid['mordaga-new-hulaoda']['placeCheck']['status']=='unresolved'
for path in list((ROOT/'amap-recommendation-evidence').glob('*.json'))+[ROOT/name for name in update_evidence_files]+[ROOT/'city-recommendations.json',ROOT/'itinerary-map.html']:
    assert KEY not in path.read_text(encoding='utf-8'), 'Credential must not be embedded'

html=(ROOT/'itinerary-map.html').read_text(encoding='utf-8')
embedded=re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)',html).group(1)
assert base64.b64decode(embedded)==(ROOT/'amap-basemap.png').read_bytes()
assert html.count('id="map"')==1
assert 'recommendationPinLayer' in html and 'data-focus-place' in html
js=r"""
const assert=require('node:assert/strict');
const {rankItems,selectItems}=require('./city-guide.js');
const base={cityId:'a',category:'eat',recommendCount:1,strength:1,cautionCount:0};
function row(id,seconds,extra={}) {return {...base,id,name:id,placeCheck:{status:'verified',comparisonStatus:'ready',addedSeconds:seconds},...extra}}
const rows=[row('strong',120,{recommendCount:3,strength:3}),row('close',60),row('far',900),row('conflict',5,{cautionCount:1,strength:0}),row('map-only',0,{recommendCount:0,strength:-1}),row('review',0,{placeCheck:{status:'verified',comparisonStatus:'review'}}),row('unresolved',0,{placeCheck:{status:'unresolved'}})];
const filters={category:'all',minimum:0,order:'route',verified:true,maxMinutes:0,text:''};
assert.deepEqual(selectItems(rows,'a',filters).map(x=>x.id),['strong','close','far','conflict','map-only','review']);
assert.deepEqual(selectItems(rows,'a',{...filters,maxMinutes:10}).map(x=>x.id),['strong','close','conflict','map-only']);
assert.deepEqual(selectItems(rows,'a',{...filters,order:'detour'}).map(x=>x.id),['map-only','conflict','close','strong','far','review']);
assert.equal(selectItems(rows,'a',{...filters,minimum:2})[0].id,'strong');
assert.equal(selectItems(rows,'b',filters).length,0);
const real=require('./city-recommendations.json').items;
for(const city of new Set(real.map(x=>x.cityId))) {
 const selected=selectItems(real,city,filters);
 assert(selected.length>0);
 assert(selected.every(x=>x.placeCheck.status==='verified'));
}
"""
result=subprocess.run(['node','-e',js],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert result.returncode==0,result.stderr
print(json.dumps(dict(status='PASS_WITH_DOCUMENTED_GAPS' if observed_gaps else 'PASS',historicalPois=len(verified),updatedPlaces=len(all_updates),day3UpdatedPlaces=len(day3_updates['places']),uniquePois=len({p['poi']['id'] for p in merged_verified}),routeReady=sum(p.get('comparisonStatus')=='ready' for p in merged_verified),historicalEvidenceGaps={slug:list(issue['fields']) for slug,issue in historical_issues['places'].items()},checks=['historical POI and intact route responses retained','refreshed historical responses verified as current values; gaps explicitly recorded and excluded from route comparison','updated POI original responses','API distances and times by evidenceRouteKey','same-batch signed deltas','via insertion and endpoint extension','mandatory waypoints retained','day3 strict evidence checks delegated to verify_day3_data.py','merged mapping and unique counts','route geometry','conflicts retained','route sorting and filters','unchanged basemap','no API credential in artifacts']),ensure_ascii=False))
