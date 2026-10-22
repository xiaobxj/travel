"""Recheck the accepted Qika overnight route, retaining raw AMap evidence."""
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from amap_audit import api

ROOT = Path(__file__).parent

def fmt(seconds):
    minutes = int(seconds / 60 + .5)
    return f'{minutes // 60}小时{minutes % 60:02d}分'

def refresh():
    routes = json.loads((ROOT / 'amap-routes.json').read_text(encoding='utf-8'))
    backup = ROOT / 'archive-before-qika'
    backup.mkdir(exist_ok=True)
    for name in ['amap-routes.json', 'activities.json', 'daily-summary.json', 'lodging-data.json']:
        target = backup / name
        if not target.exists():
            target.write_bytes((ROOT / name).read_bytes())
    queries = [(4, '白鹿岛酒店停车场', '临江', []), (4, '临江', '室韦', []),
               (4, '室韦', '九卡观景点', []), (4, '九卡观景点', '七卡', []),
               (5, '七卡', '黑山头', []), (5, '黑山头', '额尔古纳', []),
               (6, '额尔古纳', '海拉尔站', []), (0, '额尔古纳', '机场停车场', []),
               (0, '白鹿岛酒店停车场', '临江', ['莫尔道嘎'])]
    segments = []
    evidence = ROOT / 'qika-amap-evidence'
    evidence.mkdir(exist_ok=True)
    for day, origin, destination, via in queries:
        time.sleep(1.2)
        params = {'origin': routes['pois'][origin]['location'], 'destination': routes['pois'][destination]['location'],
                  'strategy': '32', 'show_fields': 'cost,polyline'}
        if via:
            params['waypoints'] = ';'.join(routes['pois'][v]['location'] for v in via)
        response = api('v5/direction/driving', params)
        if response.get('status') != '1' or not response.get('route', {}).get('paths'):
            raise RuntimeError(f'AMap failed for {origin} -> {destination}: {response.get("info")}')
        path = response['route']['paths'][0]
        assert path.get('steps') and int(path['cost']['duration']) > 0
        timestamp = datetime.now(timezone.utc).isoformat()
        filename = f'{day}_{origin}_{destination}' + ('_经' + '_'.join(via) if via else '') + '.json'
        (evidence / filename).write_text(json.dumps({'queried_at': timestamp, 'response': response}, ensure_ascii=False, indent=2), encoding='utf-8')
        segment = {'day': day, 'from': origin, 'to': destination, 'via': via,
                   'distance': int(path['distance']), 'duration': int(path['cost']['duration']),
                   'roads': list(dict.fromkeys(s.get('road_name', '未命名路') for s in path['steps'])),
                   'raw_file': 'qika-amap-evidence/' + filename, 'queried_at': timestamp, 'path': path}
        segments.append(segment)
        print(f'{day}: {origin} → {destination}: {segment["distance"]/1000:.1f} km / {fmt(segment["duration"])}', flush=True)
    retained = [s for s in routes['segments'] if 1 <= s['day'] <= 3 or s['day'] == 0 and (s['from'] == '海拉尔站' or s['from'] == '曲水云天')]
    for segment in retained:
        segment.setdefault('queried_at', routes['queried_at'])
    routes['segments'] = sorted(retained + segments, key=lambda s: s['day'] or 7)
    routes['queried_at'] = datetime.now(timezone.utc).isoformat()
    routes['revision'] = 'qika-overnight-2026-09-06'
    (ROOT / 'amap-routes.json').write_text(json.dumps(routes, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = json.loads((ROOT / 'daily-summary.json').read_text(encoding='utf-8'))
    summary[3]['stay'] = '七卡村附近（具体民宿待选）'
    for day in summary:
        parts = [s for s in routes['segments'] if s['day'] == day['day']]
        day.update(km=round(sum(s['distance'] for s in parts)/1000, 1), seconds=sum(s['duration'] for s in parts))
        day['duration'] = fmt(day['seconds'])
    (ROOT / 'daily-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    with (ROOT / 'driving-times.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['日期','起点','终点','途经','公里','高德车程','秒','住宿','证据文件'])
        for s in routes['segments']:
            if s['day']:
                writer.writerow([f'10/{s["day"]+1}',s['from'],s['to'],'/'.join(s['via']),round(s['distance']/1000,1),fmt(s['duration']),s['duration'],summary[s['day']-1]['stay'],s['raw_file']])
    print(json.dumps(summary[3:], ensure_ascii=False), flush=True)

if __name__ == '__main__':
    refresh()
