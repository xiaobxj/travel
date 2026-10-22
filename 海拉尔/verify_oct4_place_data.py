"""Check October 4 place overrides against selected POIs and original routes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(filename):
    return json.loads((ROOT / filename).read_text(encoding='utf-8-sig'))


def main():
    updates = read('amap-place-oct4-updates.json')
    assert updates['coordinateSystem'] == 'GCJ-02' and updates['strategy'] == 32
    specs = {
        'shiwei-new-tuanjie': ('B0J1K7C284', 4, 'exact', 561, 238, 1),
        'shiwei-new-aoliya': ('B0LRGRTQRM', 4, 'exact', 690, 165, 2),
        'linjiang-shilu': ('B0MUZ98SOR', 4, 'whole-site', 325, 94, 0),
        'qika-lanni': ('B0JUVD9NJ0', 4, 'exact', 76, 6, 4),
        'mordaga-hongjie': ('B0KU37EUGG', 3, 'exact', 1624, 291, 12),
        'mordaga-new-yajuan': ('B0H1X430OA', 3, 'exact', 1765, 391, 14),
    }
    assert set(updates['places']) == set(specs)
    forbidden = {'xy', 'geometry', 'routeOffsetMeters', 'addedMeters', 'addedSeconds',
                 'rawDeltaMeters', 'rawDeltaSeconds', 'baseline', 'withStop', 'currentRouteEvidence'}
    for ident, (poi_id, day, kind, meters, seconds, route_index) in specs.items():
        place = updates['places'][ident]
        assert place['status'] == 'verified' and place['currentRouteLegOnly'] is True
        assert (place['day'], place['kind'], place['comparisonStatus']) == (day, kind, 'unavailable')
        assert not forbidden.intersection(place), ident
        assert place['matchReason'] and place['comparisonNote']
        assert place['matchedPoiId'] == place['poi']['id'] == poi_id
        match = place['poiMatchEvidence']
        assert place['poiEvidenceFiles'] == [match['file']]
        query = read(match['file'])['queries'][match['queryIndex']]
        assert query['response']['status'] == '1'
        candidates = [p for p in query['response']['pois'] if p['id'] == match['poiId']]
        assert len(candidates) == 1 and candidates[0]['id'] == poi_id
        selected = candidates[0]
        assert all(selected[k] == value for k, value in place['poi'].items()), (ident, 'POI changed')
        if 'id' in query['params']:
            assert query['params']['id'] == poi_id

        anchor = place['fromAnchor']
        expected_file = ('planning-20261004/driving-live.json' if day == 3
                         else 'planning-20261004/extra-stops-driving-live.json')
        assert (anchor['evidenceFile'], anchor['evidenceRouteIndex']) == (expected_file, route_index)
        evidence = read(expected_file)
        raw = evidence['routes'][route_index]
        assert raw['response']['status'] == '1' and raw['params']['strategy'] == 32
        path = raw['response']['route']['paths'][0]
        assert (anchor['meters'], anchor['seconds']) == (meters, seconds) == (raw['meters'], raw['seconds'])
        assert (meters, seconds) == (int(path['distance']), int(path['cost']['duration']))
        assert place['queriedAt'] == anchor['queriedAt'] == raw['queriedAt']
        assert place['queriedAt'].startswith('2026-10-04T')
        assert place['anchorName'] == anchor['origin'] == raw['from']
        assert anchor['destination'] == raw['to']
        assert anchor['via'] == raw['via'] == []
        assert anchor['roads'] == raw['roads']
        assert raw['params']['destination'] == selected['location']
        assert raw['params']['origin'] == evidence['pois'][raw['from']]['location']
        assert evidence['pois'][raw['to']]['id'] == poi_id
        for endpoint in ('origin', 'destination'):
            assert raw['params'][endpoint] == raw['response']['route'][endpoint]

    # Preserve the important precision limits of these six matches.
    shilu = updates['places']['linjiang-shilu']
    assert '民宿' in shilu['poi']['name'] and '未核实' in shilu['matchReason']
    assert '住宿' in updates['places']['qika-lanni']['comparisonNote']
    assert 'bailudao-restaurant' not in updates['places']
    print('PASS: 6 October 4 POI matches, exact raw meters/seconds and endpoints; no inferred detour or hotel-restaurant substitution')


if __name__ == '__main__':
    main()
