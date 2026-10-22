"""AMap-only POI resolution and auditable comparisons against the saved itinerary.

No credentials are saved in evidence, output, or HTML. POI selections require
an explicit reviewed id. Merely being the first search result never verifies it.
"""
import argparse
import hashlib
import json
import math
import time
from datetime import datetime
from pathlib import Path
import requests
from amap_audit import KEY

ROOT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'amap-recommendation-evidence'
R=6371008.8

def now(): return datetime.now().astimezone().isoformat(timespec='seconds')
def read(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))
def write(name,data):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def api(endpoint,params):
    ident=hashlib.sha256(json.dumps([endpoint,params],sort_keys=True).encode()).hexdigest()[:20]
    path=EVIDENCE/(ident+'.json')
    if path.exists():
        saved=json.loads(path.read_text(encoding='utf-8'))
        if saved['queriedAt'][:10]==now()[:10]: return saved['response'],str(path.relative_to(ROOT)),saved['queriedAt']
    for attempt in range(3):
        try:
            response=requests.get('https://restapi.amap.com/'+endpoint,params={'key':KEY,**params},timeout=30)
            if not response.ok: raise RuntimeError('HTTP '+str(response.status_code))
            data=response.json()
        except requests.RequestException as exc: raise RuntimeError(type(exc).__name__) from None
        if data.get('status')=='1': break
        if data.get('infocode') in {'10021','10020'} and attempt<2:
            time.sleep(1.5);continue
        raise RuntimeError('AMap '+str(data.get('infocode'))+' '+str(data.get('info')))
    stamp=now();write(path.relative_to(ROOT),dict(endpoint=endpoint,params=params,queriedAt=stamp,response=data))
    time.sleep(.28)
    return data,str(path.relative_to(ROOT)),stamp

def coordinate(s): return tuple(map(float,s.split(',')))
def distance(a,b):
    a,b=coordinate(a) if isinstance(a,str) else a,coordinate(b) if isinstance(b,str) else b
    lat1,lat2=map(math.radians,[a[1],b[1]]);dl=math.radians(b[0]-a[0]);dy=lat2-lat1
    return R*2*math.asin(min(1,math.sqrt(math.sin(dy/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2)))

def points(segment):
    return [coordinate(p) for step in segment['path']['steps'] for p in step.get('polyline','').split(';') if p]

def nearest(location,polyline):
    """Local equirectangular point-to-segment distance, not road accessibility."""
    lon,lat=coordinate(location);coslat=math.cos(math.radians(lat))
    xy=[(R*math.radians(x-lon)*coslat,R*math.radians(y-lat)) for x,y in polyline]
    best=(float('inf'),0,0)
    for i,(a,b) in enumerate(zip(xy,xy[1:])):
        dx,dy=b[0]-a[0],b[1]-a[1];denom=dx*dx+dy*dy
        t=max(0,min(1,-(a[0]*dx+a[1]*dy)/denom)) if denom else 0
        d=math.hypot(a[0]+dx*t,a[1]+dy*t)
        if d<best[0]:best=(d,i,t)
    return {'meters':round(best[0]),'progress':best[1]+best[2]}

def compact(p):
    return {k:p.get(k) for k in ['id','name','location','address','adname','cityname','type','typecode']}

def search(plan):
    routes=read('amap-routes.json');cities={c['id']:c for c in read('city-guide-config.json')['cities']}
    result=read('amap-place-candidates.json') if (ROOT/'amap-place-candidates.json').exists() else {}
    for entry in plan:
        city=cities[entry['cityId']];anchor=routes['pois'][city['poi']];found={};files=[]
        for query in entry['queries']:
            d,file,stamp=api('v3/place/text',dict(keywords=query,city='150700',citylimit='true',offset=10,extensions='base'))
            files.append(file)
            for p in d.get('pois',[]):
                if not p.get('location'):continue
                found[p['id']]=compact(p)|{'anchorMeters':round(distance(anchor['location'],p['location']))}
        rows=sorted(found.values(),key=lambda p:p['anchorMeters'])
        result[entry['id']]=dict(cityId=entry['cityId'],queries=entry['queries'],pois=rows,evidenceFiles=files,queriedAt=stamp)
        write('amap-place-candidates.json',result)
        print(json.dumps({'id':entry['id'],'pois':[{k:p[k] for k in ['id','name','address','anchorMeters']} for p in rows[:5]]},ensure_ascii=False),flush=True)

def drive(origin,destination,via=None):
    params=dict(origin=origin['location'],destination=destination['location'],origin_id=origin['id'],destination_id=destination['id'],strategy=32,show_fields='cost,polyline')
    if via:params['waypoints']=';'.join(p['location'] for p in via)
    d,file,stamp=api('v5/direction/driving',params)
    paths=d.get('route',{}).get('paths',[])
    if not paths:raise RuntimeError('AMap returned no driving route')
    p=paths[0]
    return {'meters':int(p['distance']),'seconds':int(p['cost']['duration']),'evidenceFile':file,'queriedAt':stamp,'roads':list(dict.fromkeys(s.get('road_name','未命名路') for s in p['steps']))}

def audit(selections):
    routes=read('amap-routes.json');candidates=read('amap-place-candidates.json')
    cities={c['id']:c for c in read('city-guide-config.json')['cities']}
    lines={i:points(s) for i,s in enumerate(routes['segments']) if s['day']}
    old=read('amap-place-audit.json') if (ROOT/'amap-place-audit.json').exists() else {}
    output={'queriedAt':now(),'coordinateSystem':'GCJ-02','routeSnapshotAt':routes['queried_at'],'strategy':32,'places':old.get('places',{})}
    for entry in selections:
        row=candidates[entry['id']];city=cities[row['cityId']];anchor=routes['pois'][city['poi']]
        if not entry.get('poiId'):
            output['places'][entry['id']]={'status':'unresolved','reason':entry['reason'],'queriedAt':row['queriedAt']}
            continue
        poi=next(p for p in row['pois'] if p['id']==entry['poiId'])
        matches=[]
        for i,line in lines.items():
            segment=routes['segments'][i]
            if segment['day'] not in city['days']:continue
            matches.append((nearest(poi['location'],line)['meters'],i))
        _,index=min(matches)
        s=routes['segments'][index];near=nearest(poi['location'],lines[index])
        record={'status':'verified','poi':compact(poi),'cityId':city['id'],'matchReason':entry['reason'],
                'kind':entry.get('kind','exact'),'queriedAt':row['queriedAt'],'poiEvidenceFiles':row['evidenceFiles'],
                'anchorName':city['poi'],'anchorStraightMeters':round(distance(anchor['location'],poi['location'])),
                'routeOffsetMeters':near['meters'],'segmentIndex':index,'day':s['day'],'from':s['from'],'to':s['to'],'mandatoryVia':s['via']}
        try:
            record['fromAnchor']=drive(anchor,poi)
            base_via=[routes['pois'][name] for name in s['via']]
            ordered=[(nearest(p['location'],lines[index])['progress'],p) for p in base_via]
            ordered.append((near['progress'],poi))
            ordered.sort(key=lambda pair:pair[0])
            via=[]
            for _,p in ordered:
                if not via or p['id']!=via[-1]['id']:via.append(p)
            baseline=drive(routes['pois'][s['from']],routes['pois'][s['to']],base_via)
            inserted=drive(routes['pois'][s['from']],routes['pois'][s['to']],via)
            delta_m=inserted['meters']-baseline['meters'];delta_s=inserted['seconds']-baseline['seconds']
            record.update(baseline=baseline,withStop=inserted,orderedVia=[p['name'] for p in via],
                          addedMeters=max(0,delta_m),addedSeconds=max(0,delta_s),rawDeltaMeters=delta_m,rawDeltaSeconds=delta_s,
                          comparisonStatus='review' if delta_m < -500 or delta_s < -300 else 'ready')
            record['comparisonNote']='同策略同批次重算；差值不包含用餐、游玩、停车与步行。'
            if record['comparisonStatus']=='review':record['comparisonNote']='插点后高德改选路线，返回明显负差；不作为已核实的少绕路排名。'
        except RuntimeError as exc:
            record.update(comparisonStatus='unavailable',comparisonNote=str(exc))
        output['places'][entry['id']]=record
        write('amap-place-audit.json',output)
        print(json.dumps({'id':entry['id'],'name':poi['name'],'offsetM':near['meters'],'addedM':record.get('addedMeters'),'addedMin':round(record.get('addedSeconds',0)/60,1),'status':record['comparisonStatus']},ensure_ascii=False),flush=True)
    write('amap-place-audit.json',output)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['search','audit']);parser.add_argument('--ids');args=parser.parse_args()
    rows=read('amap-place-plan.json' if args.mode=='search' else 'amap-place-selections.json')
    if args.ids:rows=[x for x in rows if x['id'] in args.ids.split(',')]
    (search if args.mode=='search' else audit)(rows)
