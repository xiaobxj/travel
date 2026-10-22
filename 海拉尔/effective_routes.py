"""Apply the October 3 route update without rewriting the historical AMap audit."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINAL_EVIDENCE = 'genhe-juele-station-longshan-final-driving-20261003-083501.json'
JUELE_EVIDENCE = 'juele-reindeer-driving-20261003-083330.json'
STOPS_EVIDENCE = 'genhe-moerdaoga-new-stops-driving-20261003-083036.json'
JUELE_POI_EVIDENCE = 'juele-reindeer-poi-20261003-083308.json'
STOPS_POI_EVIDENCE = 'genhe-moerdaoga-new-stops-poi-20261003-083005.json'
DAY3_MAIN_EVIDENCE = 'moerdaoga-extra-driving-20261003-085640.json'
DAY3_TRAIN_EVIDENCE = 'moerdaoga-forest-bailudao-driving-20261003-085358.json'
DAY3_POI_EVIDENCE = 'moerdaoga-extra-pois-20261003-085628.json'
DAY3_REFRESH_EVIDENCE = 'planning-20261004/day3-lunch-order-live-20261004T083741.json'
DAY4_MAIN_EVIDENCE = 'planning-20261004/day4-final-driving-20261004.json'
DAY4_RECOMMENDED_EVIDENCE = 'planning-20261004/recommended-day4-driving-live.json'
DAY4_STOPS_EVIDENCE = 'planning-20261004/extra-stops-driving-live.json'
DAY4_BASE_EVIDENCE = 'planning-20261004/driving-live.json'
DAY4_POI_EVIDENCE = 'planning-20261004/extra-stops-pois-live.json'
DAY4_LINXI_POI_EVIDENCE = 'planning-20261004/poi-search-live.json'


def _read(root, filename):
    return json.loads((root / filename).read_text(encoding='utf-8-sig'))


def _route_record(source, filename, route_key, record_id, label, start, end, via=()):
    route = source['routes'][route_key]
    if route.get('status') != 'ok':
        raise ValueError(f'Unverified driving evidence: {filename} / {route_key}')
    path = route['response']['route']['paths'][0]
    if (int(path['distance']), int(path['cost']['duration'])) != (route['meters'], route['seconds']):
        raise ValueError(f'Driving evidence summary disagrees with response: {route_key}')
    return {
        'id': record_id, 'label': label, 'from': start, 'to': end, 'via': list(via),
        'distance': route['meters'], 'duration': route['seconds'],
        'km': round(route['meters'] / 1000, 3), 'minutes': round(route['seconds'] / 60, 2),
        'queriedAt': route['queriedAtEnd'], 'evidenceFile': filename,
        'evidenceRouteKey': route_key, 'roads': route['roads'],
    }


def load_effective_routes(root=ROOT):
    """Return an in-memory route overlay and its public ``day2Research`` evidence."""
    root = Path(root)
    routes = _read(root, 'amap-routes.json')
    final = _read(root, FINAL_EVIDENCE)
    juele = _read(root, JUELE_EVIDENCE)
    stops = _read(root, STOPS_EVIDENCE)
    plans = {}
    plan_specs = [
        ('A', '根河→觉乐→得耳布尔→莫尔道嘎',
         'A_genhe_juele_derbur_moerdaoga', '莫尔道嘎', ['觉乐驯鹿园', '得耳布尔']),
        ('B', '加得耳布尔站外观',
         'B_genhe_juele_derbur_station_moerdaoga', '莫尔道嘎', ['觉乐驯鹿园', '得耳布尔', '得耳布尔站']),
        ('C', '加得耳布尔站与龙山公园',
         'C_genhe_juele_derbur_station_moerdaoga_longshan', '龙山公园',
         ['觉乐驯鹿园', '得耳布尔', '得耳布尔站', '莫尔道嘎']),
    ]
    for plan_id, label, route_key, end, via in plan_specs:
        plans[plan_id] = _route_record(final, FINAL_EVIDENCE, route_key, plan_id,
                                       label, '根河', end, via)
    leg_specs = [
        (juele, JUELE_EVIDENCE, 'genhe_to_juele', '根河', '觉乐驯鹿园'),
        (juele, JUELE_EVIDENCE, 'juele_to_derbur', '觉乐驯鹿园', '得耳布尔'),
        (juele, JUELE_EVIDENCE, 'derbur_to_moerdaoga', '得耳布尔', '莫尔道嘎'),
        (stops, STOPS_EVIDENCE, 'derbur_to_station', '得耳布尔', '得耳布尔站'),
        (final, FINAL_EVIDENCE, 'station_to_moerdaoga', '得耳布尔站', '莫尔道嘎'),
        (final, FINAL_EVIDENCE, 'moerdaoga_to_longshan', '莫尔道嘎', '龙山公园'),
    ]
    legs = [_route_record(source, filename, key, key, f'{start}→{end}', start, end)
            for source, filename, key, start, end in leg_specs]
    poi_sources = {
        '根河': final['pois']['genhe'], '觉乐驯鹿园': final['pois']['juele'],
        '得耳布尔': final['pois']['derbur'], '得耳布尔站': final['pois']['station'],
        '莫尔道嘎': final['pois']['moerdaoga'], '龙山公园': final['pois']['longshan'],
    }
    poi_notes = {
        '根河': '根河市人民政府，仅作市区参考点，不代表住宿位置。',
        '觉乐驯鹿园': 'G332旁景区导航点，未查得独立已核实停车入口。',
        '得耳布尔': '得耳布尔镇人民政府，仅作镇区参考点。',
        '得耳布尔站': '火车站整体POI，仅安排站前外观，不表示可以进站游览。',
        '莫尔道嘎': '莫尔道嘎镇人民政府，仅作镇区参考点。',
        '龙山公园': '公园整体导航点；独立步行入口未核实，步行登山不计入车程。',
    }
    poi_baselines = {name: {**copy.deepcopy(poi), 'anchorNote': poi_notes[name]}
                     for name, poi in poi_sources.items()}
    routes['pois'].update(copy.deepcopy(poi_baselines))
    research = {
        'day': 2, 'queriedAt': final['queriedAtEnd'],
        'queryWindow': {'start': stops['queriedAtStart'], 'end': final['queriedAtEnd']},
        'activePlan': 'A', 'pins': ['根河', '觉乐驯鹿园', '得耳布尔', '莫尔道嘎'],
        'optionalPins': ['得耳布尔站', '龙山公园'], 'poiBaselines': poi_baselines,
        'plans': plans, 'legs': legs,
        'increments': {'station': final['increments']['station_B_minus_A'],
                       'longshan': final['increments']['longshan_C_minus_B']},
        'evidenceFiles': [FINAL_EVIDENCE, JUELE_EVIDENCE, STOPS_EVIDENCE,
                          JUELE_POI_EVIDENCE, STOPS_POI_EVIDENCE],
        'notes': [
            '本轮驾车查询直接请求高德，未使用本地同日缓存；历史原始路线审计保留。',
            'A/B/C总车程各自来自完整途经路线；分段单独查询，不用于拼接总时间。',
            '车程不含游玩、用餐、摄影、停车及步行；国庆路况与出发时刻可能改变预测。',
            '根白线摄影没有独立已核实停车入口，因此不另造POI或单独路线。',
            '神鹿园因近期闭园线索不列为本日默认停靠；觉乐营业信息另见当次笔记证据。',
            '第3天另有10月3日补充查验；其余日期路线保持历史审计，不表示在本轮重新查询。',
        ],
    }
    active = plans['A']
    raw_active = final['routes'][active['evidenceRouteKey']]
    replacement = {
        'day': 2, 'from': active['from'], 'to': active['to'], 'via': active['via'],
        'distance': active['distance'], 'duration': active['duration'], 'roads': active['roads'],
        'path': copy.deepcopy(raw_active['response']['route']['paths'][0]),
        'raw_file': FINAL_EVIDENCE, 'evidence_route_key': active['evidenceRouteKey'],
        'queried_at': active['queriedAt'], 'effective_plan': 'A',
    }
    rebuilt = []
    inserted = False
    for segment in routes['segments']:
        if segment['day'] == 2:
            if not inserted:
                rebuilt.append(replacement)
                inserted = True
        else:
            rebuilt.append(segment)
    if not inserted:
        raise ValueError('Historical route has no day 2 to replace')
    routes['segments'] = rebuilt
    routes['day2Research'] = research
    routes['routesUpdate'] = {
        'day': 2, 'activePlan': 'A', 'queriedAt': active['queriedAt'],
        'baseQueriedAt': routes['queried_at'], 'baseAuditFile': 'amap-routes.json',
        'evidenceFile': FINAL_EVIDENCE, 'evidenceRouteKey': active['evidenceRouteKey'],
        'note': '仅替换构建时的第2天；其余日期仍使用历史路线审计。',
    }
    return _apply_day4(_apply_day3(routes, root), root)


def _apply_day3(routes, root):
    """Apply verified park stops while keeping the historical audit immutable."""
    extra = _read(root, DAY3_MAIN_EVIDENCE)
    train = _read(root, DAY3_TRAIN_EVIDENCE)
    fresh = _read(root, DAY3_REFRESH_EVIDENCE)

    def record(source, filename, index, record_id, label=None, optional=False):
        raw = source['routes'][index]
        response = raw['response']
        if str(response.get('status')) != '1':
            raise ValueError(f'Unverified driving evidence: {filename} / {index}')
        path = response['route']['paths'][0]
        if (int(path['distance']), int(path['cost']['duration'])) != (raw['meters'], raw['seconds']):
            raise ValueError(f'Driving evidence summary disagrees with response: {filename} / {index}')
        roads = list(dict.fromkeys(step['road_name'] for step in path['steps'] if step.get('road_name')))
        return {
            'id': record_id, 'label': label or f"{raw['from']}→{raw['to']}",
            'from': raw['from'], 'to': raw['to'], 'via': raw['via'],
            'distance': raw['meters'], 'duration': raw['seconds'],
            'km': round(raw['meters'] / 1000, 3), 'minutes': round(raw['seconds'] / 60, 2),
            'queriedAt': raw['queriedAt'], 'evidenceFile': filename,
            'evidenceRouteIndex': index, 'roads': roads, 'optional': optional,
        }

    plans = {
        'selfDrive': record(fresh, DAY3_REFRESH_EVIDENCE, 1, 'selfDrive',
                            '莫尔道嘎→森林公园停车场→红豆坡→一目九岭→白鹿岛酒店停车场'),
        'train': record(train, DAY3_TRAIN_EVIDENCE, 2, 'train',
                        '莫尔道嘎→森林公园停车场→白鹿岛酒店停车场（小火车方案）'),
    }
    legs = [
        record(fresh, DAY3_REFRESH_EVIDENCE, 2, 'townToPark'),
        record(extra, DAY3_MAIN_EVIDENCE, 0, 'parkToHongdou'),
        record(fresh, DAY3_REFRESH_EVIDENCE, 11, 'hongdouToJiuling'),
        record(fresh, DAY3_REFRESH_EVIDENCE, 3, 'jiulingToHotel'),
        record(fresh, DAY3_REFRESH_EVIDENCE, 4, 'hotelToRafting', optional=True),
    ]
    pins = ['莫尔道嘎', '森林公园停车场', '红豆坡', '一目九岭', '白鹿岛酒店停车场']
    optional_pins = ['白鹿岛漂流']
    notes = {
        '莫尔道嘎': '莫尔道嘎镇人民政府，仅作镇区出发参考点，不代表住宿位置。',
        '森林公园停车场': '高德停车场导航点；小火车班次与园内道路能否自驾通行，以入口当天确认为准。',
        '红豆坡': '景点整体导航点，停车后步行游览时间另计；不代表独立停车入口。',
        '一目九岭': '景点整体导航点，登观景台与步行时间另计；不代表独立停车入口。',
        '白鹿岛酒店停车场': '已核实的酒店停车场导航点，到河湾观景台的接驳或步行路线尚未核实。',
        '白鹿岛漂流': '高德水上活动导航点，非已核实的当天报到或上船点；短线是否开行须现场确认。',
    }
    poi_baselines = {
        name: {**copy.deepcopy(extra['pois'][name]), 'anchorNote': notes[name]}
        for name in pins + optional_pins
    }
    routes['pois'].update(copy.deepcopy(poi_baselines))
    active = plans['selfDrive']
    routes['day3Research'] = {
        'day': 3, 'queriedAt': active['queriedAt'],
        'queryWindow': {'start': train['queriedAt'], 'end': fresh['queriedAtEnd']},
        'activePlan': 'selfDrive', 'pins': pins, 'optionalPins': optional_pins,
        'poiBaselines': poi_baselines, 'plans': plans, 'legs': legs,
        'trainLegs': [legs[0], record(train, DAY3_TRAIN_EVIDENCE, 1, 'parkToHotel')],
        'morningViaHongdou': record(fresh, DAY3_REFRESH_EVIDENCE, 0, 'morningViaHongdou'),
        'evidenceFiles': [DAY3_MAIN_EVIDENCE, DAY3_TRAIN_EVIDENCE, DAY3_POI_EVIDENCE,
                          DAY3_REFRESH_EVIDENCE],
        'notes': [
            '主线总车程来自含全部途经点的一次完整高德查询；分段单独查询，不用于拼接总时间。',
            '自驾游览与小火车为替代方案；园内车辆能否通行及小火车班次，以入口当天确认为准。',
            '主线止于白鹿岛酒店停车场，不含漂流支线、游览、用餐、停车、步行和排队。',
            '酒店停车场至漂流导航点仅查得单程，未核实接驳、报到位置或返程，不据此推算往返。',
            '完整主线及部分分段于2026年10月4日08:37重新查询；公园停车场至红豆坡、小火车方案保留10月3日证据，各记录均标注自身查询时间。',
        ],
    }
    replacement = {
        'day': 3, 'from': active['from'], 'to': active['to'], 'via': active['via'],
        'distance': active['distance'], 'duration': active['duration'], 'roads': active['roads'],
        'path': copy.deepcopy(fresh['routes'][1]['response']['route']['paths'][0]),
        'raw_file': DAY3_REFRESH_EVIDENCE, 'evidence_route_index': 1,
        'queried_at': active['queriedAt'], 'effective_plan': 'selfDrive',
    }
    rebuilt = []
    inserted = False
    for segment in routes['segments']:
        if segment['day'] == 3:
            if not inserted:
                rebuilt.append(replacement)
                inserted = True
        else:
            rebuilt.append(segment)
    if not inserted:
        raise ValueError('Historical route has no day 3 to replace')
    routes['segments'] = rebuilt
    routes['routesUpdate']['updatedDays'] = [2, 3]
    routes['routesUpdate']['note'] = '第2、3天采用2026年10月3日高德查验；其他日期保留历史路线审计。'
    return routes


def _apply_day4(routes, root):
    """Use one complete day-4 route and preserve the audited day-5 start."""
    final = _read(root, DAY4_MAIN_EVIDENCE)
    recommended = _read(root, DAY4_RECOMMENDED_EVIDENCE)
    stops = _read(root, DAY4_STOPS_EVIDENCE)
    baseline = _read(root, DAY4_BASE_EVIDENCE)

    def record(source, filename, index, record_id, label=None, optional=False):
        raw = source['routes'][index]
        response = raw['response']
        if str(response.get('status')) != '1':
            raise ValueError(f'Unverified driving evidence: {filename} / {index}')
        path = response['route']['paths'][0]
        if (int(path['distance']), int(path['cost']['duration'])) != (raw['meters'], raw['seconds']):
            raise ValueError(f'Driving evidence summary disagrees with response: {filename} / {index}')
        for side, parameter in (('from', 'origin'), ('to', 'destination')):
            if raw['params'][parameter] != source['pois'][raw[side]]['location']:
                raise ValueError(f'Driving evidence endpoint disagrees with POI: {filename} / {index}')
        return {
            'id': record_id, 'label': label or f"{raw['from']}→{raw['to']}",
            'from': raw['from'], 'to': raw['to'], 'via': raw['via'],
            'distance': raw['meters'], 'duration': raw['seconds'],
            'km': round(raw['meters'] / 1000, 3), 'minutes': round(raw['seconds'] / 60, 2),
            'queriedAt': raw['queriedAt'], 'evidenceFile': filename,
            'evidenceRouteIndex': index, 'evidenceRouteId': raw['id'],
            'roads': raw['roads'], 'optional': optional,
        }

    plans = {
        'main': record(final, DAY4_MAIN_EVIDENCE, 0, 'main',
                       '白鹿岛酒店停车场→临江驶路部落→团结广场→奥利亚列巴房→九卡→七卡'),
        'withEagle': record(final, DAY4_MAIN_EVIDENCE, 1, 'withEagle',
                            '主线加老鹰嘴（可选）', optional=True),
    }
    legs = [
        record(recommended, DAY4_RECOMMENDED_EVIDENCE, 2, 'bailudaoToShilu'),
        record(recommended, DAY4_RECOMMENDED_EVIDENCE, 3, 'shiluToSquare'),
        record(stops, DAY4_STOPS_EVIDENCE, 2, 'squareToBakery'),
        record(stops, DAY4_STOPS_EVIDENCE, 3, 'bakeryToJiuka'),
        record(baseline, DAY4_BASE_EVIDENCE, 3, 'jiukaToQika'),
    ]
    active = plans['main']
    pins = [active['from'], *active['via'], active['to']]
    if [legs[0]['from'], *(leg['to'] for leg in legs)] != pins:
        raise ValueError('Day 4 leg endpoints do not follow the complete main route')
    # Keep this exact village anchor; replacing it with the dinner POI would
    # silently move the following day's previously audited departure point.
    if final['pois']['七卡']['location'] != routes['pois']['七卡']['location']:
        raise ValueError('Day 4 would change the audited day 5 start coordinate')
    optional_pins = ['老鹰嘴', '林曦农家菜', '兰妮农家院']
    poi_notes = {
        '白鹿岛酒店停车场': '已核实酒店停车场导航点，与第3天主线终点一致。',
        '驶路部落民宿（餐厅整体参考点）': '临江午餐采用民宿整体POI，不是已核实的独立餐厅或停车入口。',
        '团结广场': '室韦界河短逛参考点；停车及步行时间另计。',
        '奥利亚列巴房': '室韦列巴补给参考点；地图登记不等于10月5日营业确认。',
        '九卡观景点': '高德景点整体定位，名称含落日不表示安排等日落；只在允许停车的位置停留。',
        '七卡': '保留原七卡戍边食府村内参考点，以接续第5天；不代表已订住宿或指定用餐。',
        '老鹰嘴': '仅作可选支线；高德可规划不等于当天道路开放或车辆可直接到达观景位置。',
        '林曦农家菜': '太平林场午餐备选，已选临江俄餐时不重复安排一顿正餐。',
        '兰妮农家院': '七卡村内晚餐备选，不代表住宿；不纳入主线终点。',
    }
    poi_sources = copy.deepcopy(final['pois'])
    poi_search = _read(root, DAY4_LINXI_POI_EVIDENCE)
    linxi = [poi for query in poi_search['queries'] for poi in query['response'].get('pois', [])
             if poi.get('id') == 'B0FFHE1DSE']
    if not linxi:
        raise ValueError('Missing verified Linxi restaurant POI')
    poi_sources['林曦农家菜'] = linxi[0]
    poi_baselines = {
        name: {**copy.deepcopy(poi_sources[name]), 'anchorNote': poi_notes[name]}
        for name in pins + optional_pins
    }
    routes['pois'].update(copy.deepcopy(poi_baselines))
    increment = copy.deepcopy(final['eagleIncrement'])
    if (increment['addedMeters'], increment['addedSeconds']) != (
            plans['withEagle']['distance'] - active['distance'],
            plans['withEagle']['duration'] - active['duration']):
        raise ValueError('Day 4 optional-stop increment disagrees with complete routes')
    routes['day4Research'] = {
        'day': 4, 'queriedAt': active['queriedAt'], 'activePlan': 'main',
        'queryWindow': {'start': min(leg['queriedAt'] for leg in legs), 'end': final['queriedAt']},
        'pins': pins, 'optionalPins': optional_pins, 'poiBaselines': poi_baselines,
        'plans': plans, 'legs': legs,
        'sideLegs': [record(stops, DAY4_STOPS_EVIDENCE, 4, 'qikaToLanni', optional=True)],
        'increments': {'eagle': increment}, 'eagleIncrement': increment,
        'evidenceFiles': [DAY4_MAIN_EVIDENCE, DAY4_RECOMMENDED_EVIDENCE, DAY4_STOPS_EVIDENCE,
                          DAY4_BASE_EVIDENCE, DAY4_POI_EVIDENCE, DAY4_LINXI_POI_EVIDENCE],
        'notes': [
            '完整主线与加老鹰嘴方案为同批高德实时查询；分段使用当天各次原始查询，分别标注查询时间，不将分段相加替代整体车程。',
            '主线按临江俄餐、室韦团结广场、奥利亚列巴、九卡至七卡安排；太平仅为沿途经过或备选午餐，不重复安排正餐。',
            '七卡沿用原村内参考点，住宿仍在七卡；兰妮仅作村内晚餐候选。',
            '高德可规划不表示10月5日临江至室韦、九卡入口或九卡至七卡道路已确认放行；当天以交通管理和现场指示为准。',
            '老鹰嘴额外驾驶来自完整路线差值，不含停车、摄影和步行；仅在道路允许且时间充足时选择。',
            '所有车程不含用餐、逛村、停车、步行及排队。地图营业登记不能替代当天营业确认。',
        ],
    }
    replacement = {
        'day': 4, 'from': active['from'], 'to': active['to'], 'via': active['via'],
        'distance': active['distance'], 'duration': active['duration'], 'roads': active['roads'],
        'path': copy.deepcopy(final['routes'][0]['response']['route']['paths'][0]),
        'raw_file': DAY4_MAIN_EVIDENCE, 'evidence_route_index': 0,
        'queried_at': active['queriedAt'], 'effective_plan': 'main',
    }
    rebuilt = []
    inserted = False
    for segment in routes['segments']:
        if segment['day'] == 4:
            if not inserted:
                rebuilt.append(replacement)
                inserted = True
        else:
            rebuilt.append(segment)
    if not inserted:
        raise ValueError('Historical route has no day 4 to replace')
    routes['segments'] = rebuilt
    routes['routesUpdate']['updatedDays'] = [2, 3, 4]
    routes['routesUpdate']['note'] = '第2天采用10月3日查验；第3天主线及第4天采用10月4日查验，各分段保留自身证据时间；其余日期保留历史路线审计。'
    return routes
