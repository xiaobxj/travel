"""Validate day 3 POIs and driving figures against the original AMap responses."""
import csv
import json
from pathlib import Path

from effective_routes import load_effective_routes

ROOT = Path(__file__).resolve().parent
POI_FILE = 'moerdaoga-extra-pois-20261003-085628.json'
EXTRA_FILE = 'moerdaoga-extra-driving-20261003-085640.json'
FOREST_FILE = 'moerdaoga-forest-bailudao-driving-20261003-085358.json'
FRESH_FILE = 'planning-20261004/day3-lunch-order-live-20261004T083741.json'


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def raw_route(filename, index):
    record = read(filename)['routes'][index]
    assert record['response']['status'] == '1', (filename, index)
    path = record['response']['route']['paths'][0]
    assert record['params']['strategy'] == 32
    assert record['meters'] == int(path['distance'])
    assert record['seconds'] == int(path['cost']['duration'])
    for field in ('origin', 'destination'):
        assert record['params'][field] == record['response']['route'][field]
    return record, path


def check_route(record, filename, index, expected):
    assert record['evidenceFile'] == filename
    assert record['evidenceRouteIndex'] == index
    raw, path = raw_route(filename, index)
    assert (record['distance'], record['duration']) == expected
    assert expected == (raw['meters'], raw['seconds'])
    assert record['queriedAt'] == raw['queriedAt']
    for field in ('from', 'to', 'via'):
        assert record[field] == raw[field]
    return raw, path


def duration(seconds):
    minutes = int(seconds / 60 + .5)
    return f'{minutes // 60}小时{minutes % 60:02d}分' if minutes >= 60 else f'{minutes}分钟'


def main():
    routes = load_effective_routes(ROOT)
    research = routes['day3Research']
    assert research['day'] == 3 and research['activePlan'] == 'selfDrive'
    places = read('amap-place-day3-updates.json')
    assert places['coordinateSystem'] == 'GCJ-02' and places['strategy'] == 32
    specs = {
        'mordaga-new-hongdoupo': ('红豆坡', 'B0FFFGOZZK', 0, (10212, 1015)),
        'mordaga-new-yimujiuling': ('一目九岭', 'B0FFFGOZZU', 1, (6683, 642)),
        'bailudao-new-rafting': ('白鹿岛漂流', 'B0KDXULSM1', 3, (1638, 281)),
    }
    assert set(places['places']) == set(specs)
    queries = read(POI_FILE)['queries']
    assert all(q['response']['status'] == '1' for q in queries)
    for ident, (name, poi_id, index, expected) in specs.items():
        p = places['places'][ident]
        assert p['status'] == 'verified' and p['currentRouteLegOnly'] is True
        assert p['day'] == 3 and p['comparisonStatus'] == 'unavailable'
        assert p['matchReason'] and p['comparisonNote']
        assert p['poiEvidenceFiles'] == [POI_FILE]
        assert p['poi']['id'] == poi_id and p['poi']['name'] == name
        matches = [v for q in queries for v in q['response']['pois'] if v['id'] == poi_id]
        assert matches and all(all(v[k] == value for k, value in p['poi'].items()) for v in matches)
        raw, _ = raw_route(EXTRA_FILE, index)
        anchor = p['fromAnchor']
        assert (anchor['meters'], anchor['seconds']) == expected == (raw['meters'], raw['seconds'])
        assert anchor['evidenceFile'] == EXTRA_FILE and anchor['evidenceRouteIndex'] == index
        assert p['queriedAt'] == anchor['queriedAt'] == raw['queriedAt']
        assert p['anchorName'] == anchor['origin'] == raw['from']
        assert anchor['destination'] == raw['to'] == name
        assert anchor['via'] == raw['via'] == []
        assert raw['params']['destination'] == p['poi']['location']
        assert raw['params']['origin'] == routes['pois'][p['anchorName']]['location']
        assert routes['pois'][name]['id'] == poi_id
        # A one-way access query does not establish a route offset or detour.
        assert not set(p) & {'xy', 'geometry', 'routeOffsetMeters', 'addedMeters', 'addedSeconds',
                             'rawDeltaMeters', 'rawDeltaSeconds', 'baseline', 'withStop'}
        assert not p.get('currentRouteEvidence')

    # Preserve the original evidence checks even though the current itinerary
    # now selects the October 4 requery for the full route and most legs.
    frozen_specs = [(FOREST_FILE,0,(12721,1100)), (EXTRA_FILE,0,(10212,1015)),
                    (EXTRA_FILE,1,(6683,642)), (EXTRA_FILE,2,(79805,4666)),
                    (EXTRA_FILE,3,(1638,281)), (EXTRA_FILE,4,(109477,7660))]
    for filename,index,expected in frozen_specs:
        raw,_=raw_route(filename,index)
        assert (raw['meters'],raw['seconds']) == expected
    full_raw, full_path = check_route(research['plans']['selfDrive'], FRESH_FILE, 1, (109477, 7467))
    check_route(research['plans']['train'], FOREST_FILE, 2, (102555, 6246))
    assert full_raw['via'] == ['森林公园停车场', '红豆坡', '一目九岭']
    expected_waypoints = ';'.join(routes['pois'][name]['location'] for name in full_raw['via'])
    assert full_raw['params']['waypoints'] == expected_waypoints
    assert full_raw['params']['origin'] == routes['pois']['莫尔道嘎']['location']
    assert full_raw['params']['destination'] == routes['pois']['白鹿岛酒店停车场']['location']
    leg_specs = [
        ('townToPark', FRESH_FILE, 2, (12721, 1069)),
        ('parkToHongdou', EXTRA_FILE, 0, (10212, 1015)),
        ('hongdouToJiuling', FRESH_FILE, 11, (6683, 637)),
        ('jiulingToHotel', FRESH_FILE, 3, (79805, 4692)),
        ('hotelToRafting', FRESH_FILE, 4, (1638, 283)),
    ]
    legs = research['legs']
    assert len(legs) == 5
    for leg, (ident, filename, index, expected) in zip(legs, leg_specs):
        assert leg['id'] == ident
        raw, _ = check_route(leg, filename, index, expected)
        assert raw['params']['origin'] == routes['pois'][leg['from']]['location']
        assert raw['params']['destination'] == routes['pois'][leg['to']]['location']
        assert leg['optional'] is (ident == 'hotelToRafting')
    assert all(a['to'] == b['from'] for a, b in zip(legs, legs[1:]))
    assert legs[-1]['duration'] == 283 and legs[-1]['to'] == '白鹿岛漂流'
    assert research['optionalPins'] == ['白鹿岛漂流']

    main_segments = [s for s in routes['segments'] if s['day']]
    assert all(a['to'] == b['from'] for a, b in zip(main_segments, main_segments[1:]))
    day3 = [s for s in main_segments if s['day'] == 3]
    assert len(day3) == 1
    segment = day3[0]
    assert (segment['distance'], segment['duration']) == (109477, 7467)
    assert segment['from'] == '莫尔道嘎' and segment['to'] == '白鹿岛酒店停车场'
    assert segment['via'] == full_raw['via'] and segment['path'] == full_path
    assert segment['raw_file'] == FRESH_FILE
    assert '白鹿岛漂流' not in segment['via']

    summary = read('daily-summary.json')
    with (ROOT / 'driving-times.csv').open(encoding='utf-8-sig', newline='') as stream:
        csv_rows = list(csv.DictReader(stream))
    for day in summary:
        segments = [s for s in main_segments if s['day'] == day['day']]
        assert day['seconds'] == sum(s['duration'] for s in segments)
        assert day['km'] == round(sum(s['distance'] for s in segments) / 1000, 1)
        assert day['duration'] == duration(day['seconds'])
        rows = [r for r in csv_rows if r['日期'] == f"10/{day['day'] + 1}"]
        assert len(rows) == len(segments)
        for row, seg in zip(rows, segments):
            assert int(row['秒']) == seg['duration']
            assert float(row['公里']) == round(seg['distance'] / 1000, 1)
            assert row['高德车程'] == duration(seg['duration'])
            assert row['住宿'] == day['stay']
    summary3 = next(d for d in summary if d['day'] == 3)
    assert summary3['seconds'] == 7467 and summary3['km'] == 109.5
    assert summary3['evidenceFile'] == FRESH_FILE and summary3['routePlan'] == 'selfDrive'
    csv3 = next(r for r in csv_rows if r['日期'] == '10/4')
    assert csv3['证据文件'] == FRESH_FILE + '#routes/1'
    assert csv3['途经'].split('；') == full_raw['via']
    print('PASS: original October 3 evidence preserved; 3 exact POIs; effective October 4 full route 109477 m / 7467 s, 5 legs, optional 283 s rafting access, summary/CSV and route continuity')


if __name__ == '__main__':
    main()
