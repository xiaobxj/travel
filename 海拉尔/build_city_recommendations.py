"""Build auditable place-level recommendations from manually read public notes."""
import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATEGORIES = {'eat': '吃', 'drink': '喝', 'play': '玩', 'fun': '乐'}


def evidence_stats(reviews, notes):
    # Nicknames are the available public author field. Conservatively merge equal
    # names and near-identical bodies; this is not a claim of verified identity.
    groups = []
    for review in reviews:
        note = notes[review['noteId']]
        author = (note.get('author') or '未知作者').strip().casefold()
        path = ROOT / note.get('evidenceFile', '')
        body = json.loads(path.read_text(encoding='utf-8')).get('note', {}).get('description', '') if path.is_file() else note.get('excerpt', '')
        body = re.sub(r'\s+', '', body.split('#')[0])
        group = next((g for g in groups if author in g['authors'] or (len(body) > 80 and any(SequenceMatcher(None, body, b).ratio() >= .92 for b in g['bodies']))), None)
        if group is None:
            group = {'authors': set(), 'bodies': [], 'stances': set()}
            groups.append(group)
        group['authors'].add(author)
        group['bodies'].append(body)
        group['stances'].add(review['stance'] if not note.get('suspectedAd') else 'mention')
    positives = sum('positive' in g['stances'] and not g['stances'] & {'negative', 'mixed'} for g in groups)
    cautions = sum(bool(g['stances'] & {'negative', 'mixed'}) for g in groups)
    if cautions:
        strength, label = 0, '评价有分歧' if positives else '谨慎选择'
    elif positives >= 3:
        strength, label = 3, '多篇交叉支持'
    elif positives == 2:
        strength, label = 2, '两位作者支持'
    elif positives == 1:
        strength, label = 1, '单篇参考'
    else:
        strength, label = -1, '仅有提及' if reviews else '暂无笔记支持'
    return dict(recommendCount=positives, cautionCount=cautions, sourceCount=len(reviews), authorCount=len(groups), strength=strength, evidenceLabel=label)


def build():
    raw = json.loads((ROOT / 'city-notes.json').read_text(encoding='utf-8'))
    notes = {n['id']: n for n in raw['notes']}
    curated = json.loads((ROOT / 'city-entities.json').read_text(encoding='utf-8'))
    extra=ROOT/'city-fixed-entities.json'
    if extra.exists():curated['items'].extend(json.loads(extra.read_text(encoding='utf-8')))
    additions=ROOT/'city-review-additions.json'
    if additions.exists():
        updates=json.loads(additions.read_text(encoding='utf-8'))
        for item in curated['items']:
            update=updates['items'].get(item['id'],{})
            item['reviews'].extend(update.get('reviews',[]))
            item.update({k:v for k,v in update.items() if k!='reviews'})
        for city,sections in updates['sections'].items():curated['sectionSummaries'][city].update(sections)
    audit_path=ROOT/'amap-place-audit.json'
    audit=json.loads(audit_path.read_text(encoding='utf-8')) if audit_path.exists() else {}
    updates_path=ROOT/'amap-place-updates.json'
    place_updates=json.loads(updates_path.read_text(encoding='utf-8')) if updates_path.exists() else {}
    day3_updates_path=ROOT/'amap-place-day3-updates.json'
    if day3_updates_path.exists():
        day3_updates=json.loads(day3_updates_path.read_text(encoding='utf-8'))
        place_updates['places']={**place_updates.get('places',{}),**day3_updates.get('places',{})}
        place_updates['queriedAt']=max(place_updates.get('queriedAt',''),day3_updates.get('queriedAt',''))
    oct4_updates_path=ROOT/'amap-place-oct4-updates.json'
    if oct4_updates_path.exists():
        oct4_updates=json.loads(oct4_updates_path.read_text(encoding='utf-8'))
        place_updates['places']={**place_updates.get('places',{}),**oct4_updates.get('places',{})}
        place_updates['queriedAt']=max(place_updates.get('queriedAt',''),oct4_updates.get('queriedAt',''))
    places={**audit.get('places',{}), **place_updates.get('places',{})}
    issues_path=ROOT/'amap-historical-evidence-issues.json'
    issues=json.loads(issues_path.read_text(encoding='utf-8')) if issues_path.exists() else {}
    for place_id, issue in issues.get('places',{}).items():
        if place_id not in places or place_id in place_updates.get('places',{}):continue
        places[place_id]={**places[place_id],**issue['overlay'],'evidenceIssue':True}
        places[place_id]['comparisonNote']='该地点的旧车程暂不能完整复核，暂不参与绕路排名；请使用高德重新导航。本次新增路线的查验结果见10月3日分段车程。'
        if 'fromAnchor' in issue.get('fields',{}):places[place_id].pop('fromAnchor',None)
    # Same named venue, separate eating/drinking or in-park experience summaries.
    # These do not become additional unique POIs.
    place_aliases={'genhe-breakfast milk':'genhe-kaimenhong','eerguna-milk tea':'eerguna-kerulen',
                   'aoluguya-culture':'aoluguya-reindeer','mordaga-train':'mordaga-forest','qika-grass slide':'qika-wulan',
                   'shiwei-new-mumin-tea':'shiwei-new-mumin','heishantou-new-yunxi-tea':'heishantou-new-yunxi'}
    cities = json.loads((ROOT / 'city-guide-config.json').read_text(encoding='utf-8'))['cities']
    ids = set()
    for item in curated['items']:
        assert item['id'] not in ids, item['id']
        ids.add(item['id'])
        assert item['cityId'] in {c['id'] for c in cities}
        assert item['category'] in CATEGORIES
        assert len({r['noteId'] for r in item['reviews']}) == len(item['reviews'])
        item['placeCheck']=places.get(place_aliases.get(item['id'],item['id']),{'status':'unresolved','reason':'当前条目是区域、品类或多个地点的组合，尚未核到唯一高德 POI。'})
        assert item['reviews'] or item['placeCheck']['status']=='verified',item['id']
        for review in item['reviews']:
            assert review['noteId'] in notes, (item['name'], review['noteId'])
            assert review['stance'] in {'positive', 'mixed', 'negative', 'mention'}
            assert review['basis']
        item.update(evidence_stats(item['reviews'], notes))
    curated['categories'] = [{'id': key, 'name': name} for key, name in CATEGORIES.items()]
    curated['generatedAt'] = datetime.now().astimezone().isoformat(timespec='seconds')
    curated['sampleNotes'] = len(notes)
    curated['amapCheckedAt']=audit.get('queriedAt')
    curated['amapUpdatesCheckedAt']=place_updates.get('queriedAt')
    curated['amapVerifiedItems']=sum(x['placeCheck']['status']=='verified' for x in curated['items'])
    curated['amapUniquePois']=len({x['placeCheck']['poi']['id'] for x in curated['items'] if x['placeCheck']['status']=='verified'})
    curated['amapRouteReady']=sum(x['placeCheck'].get('comparisonStatus')=='ready' for x in curated['items'])
    curated['reviewedNotes'] = len({r['noteId'] for item in curated['items'] for r in item['reviews']})
    curated['method'] = '推荐数按当前样本中明确推荐该项目的不同作者计算，同名作者和高度相似正文合并；仅提及、未体验、疑似推广不计推荐。分歧单独标记，互动量仅作来源信息。证据强度不是统计概率，也不是全平台排名。'
    (ROOT / 'city-recommendations.json').write_text(json.dumps(curated, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 城市吃喝玩乐整理结果', '', f'共 {len(notes)} 篇资料，选用 {curated["reviewedNotes"]} 篇明确证据，整理 {len(ids)} 项具体总结。', '',
             f'其中 {curated["amapUniquePois"]} 个不重复固定地点通过高德 POI 核对，对应 {curated["amapVerifiedItems"]} 项吃喝玩乐总结；{curated["amapRouteReady"]} 项的驾车增量可比较。默认只展示高德已核点。', '',
             curated['method'], '', '| 城市／停靠点 | 吃 | 喝 | 玩 | 乐 |', '|---|---:|---:|---:|---:|']
    for city in cities:
        counts = [str(sum(x['cityId'] == city['id'] and x['category'] == cat for x in curated['items'])) for cat in CATEGORIES]
        lines.append('| '+city['name']+' | '+' | '.join(counts)+' |')
    lines.extend(['', '0 表示暂无足够明确的具体项目证据，HTML 中仍保留该方面的总结及安排建议。计数包含有分歧或谨慎选择的项目，不全是正面推荐。', '',
                  '默认按顺路与证据分层：驾驶增量可比较优先，再按正面支持与分歧分层，按额外驾驶 10 分钟内／30 分钟内／更多分组，同组比较证据和时间。可切换推荐数、证据强度、额外驾驶排序。', '',
                  '高德核点不等于当前营业保证或口味推荐。原路线几何距离与加入指定路段的额外驾车距离分别展示；保留原强制途经点，用同批次基准计算差值。只比较关联日期中几何最近路段，不是全程最优插点；驾驶时间不含停留，也不是国庆预测。明显负差标待核对，不冒充零绕路。', '',
                  '每项完整判断、菜品／玩法、注意事项、行程建议与逐条来源见 itinerary-map.html。原始正文保存在 city-research，人工归纳保存在 city-entities.json、city-fixed-entities.json、city-review-additions.json。高德原始响应保存在 amap-recommendation-evidence，核点与距离结果保存在 amap-place-audit.json。', '',
                  f'整理时间：{curated["generatedAt"]}'])
    (ROOT / '城市吃喝玩乐整理结果.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'items': len(ids), 'sourceNotes': curated['reviewedNotes'], 'sampleNotes': len(notes)}, ensure_ascii=False))
    return curated


if __name__ == '__main__':
    build()
