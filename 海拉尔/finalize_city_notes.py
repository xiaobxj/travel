"""Review saved public evidence and produce city-specific excerpts and an audit summary."""
import json
from pathlib import Path
from collect_city_xhs import categories, city_excerpt, now, save, screen_content, total

ROOT = Path(__file__).resolve().parent


def finalize():
    config = json.loads((ROOT / 'city-guide-config.json').read_text(encoding='utf-8'))
    data = json.loads((ROOT / 'city-notes.json').read_text(encoding='utf-8'))
    kept, excluded = [], []
    for note in data['notes']:
        if note.get('origin') != 'cdp':
            kept.append(note)
            continue
        raw = json.loads((ROOT / note['evidenceFile']).read_text(encoding='utf-8'))['note']
        reason = screen_content(raw['title'], raw['description'])
        if note['id'] == '6a44f0d50000000021019edc':
            reason = '行前提问是否放弃卡线，无实际游览体验'
        if reason:
            excluded.append({'id': note['id'], 'title': note['title'], 'reason': reason, 'evidenceFile': note['evidenceFile']})
            continue
        note['cityExcerpts'] = {c['id']: city_excerpt(raw['description'], c, config['cities']) for c in config['cities'] if c['id'] in note['cityIds']}
        kept.append(note)
    previous = {n['id']: n for n in data.get('qualityReview', {}).get('excluded', [])}
    previous.update({n['id']: n for n in excluded})
    review = {'at': now(), 'excluded': list(previous.values())}
    data.update(notes=kept, qualityReview=review)
    save(data)
    summary = []
    for city in config['cities']:
        rows = [n for n in kept if city['id'] in n['cityIds']]
        summary.append({'city': city['name'], 'id': city['id'], 'notes': len(rows),
                        'complete': sum(total(n) is not None for n in rows),
                        'local': sum(len(n['cityIds']) == 1 for n in rows),
                        'categories': {category: sum(category in n['categories'] for n in rows) for category in config['categories']}})
    report = {'reviewedAt': review['at'], 'uniqueNotes': len(kept), 'freshNotes': sum(n.get('origin') == 'cdp' for n in kept),
              'archiveNotes': sum(n.get('origin') == 'archive' for n in kept),
              'incompleteCounters': sum(total(n) is None for n in kept),
              'adFlagged': sum(bool(n.get('suspectedAd')) for n in kept), 'excluded': list(previous.values()), 'cities': summary}
    (ROOT / 'city-research' / 'quality-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 城市笔记采集结果', '', f'复核时间：{review["at"]}', '',
             f'共 {report["uniqueNotes"]} 篇去重笔记，其中累计 CDP 采集 {report["freshNotes"]} 篇、历史存档 {report["archiveNotes"]} 篇。',
             f'{report["incompleteCounters"]} 篇互动数不完整，不计算互动总量，但有具体实体验的仍可作为总结依据；{report["adFlagged"]} 篇带明显推广用语，不计推荐票。', '',
             '右侧以吃、喝、玩、乐四方面展示具体总结，默认按顺路与证据分层，支持推荐作者数、证据强度、额外驾驶排序。原始笔记仍保存点赞＋收藏＋评论总量，作为来源信息，不代替推荐票。跨城游记可关联多个地点，下表不能相加作为总篇数。“关联”只是候选匹配，具体推荐项目另按正文人工核对城市与态度。', '',
             '| 城市／停靠点 | 关联笔记 | 三项完整 | 单地笔记 |', '|---|---:|---:|---:|']
    lines.extend(f'| {c["city"]} | {c["notes"]} | {c["complete"]} | {c["local"]} |' for c in summary)
    lines.extend(['', '采集筛选：按笔记 id 去重；标题和正文须匹配目的地；排除求助类与正文信息过少的笔记。展示筛选：城市、吃喝玩乐类别、最低推荐作者数、店名或关键词。来源正文、采集时间和三项计数保存在 city-research，每张总结卡片可展开来源并打开原帖。',
                  '', '原文中的票价、营业与通行信息是作者描述，未作独立核验。此页面保留行程原地图，仅增加地点标记。'])
    (ROOT / '城市笔记采集结果.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    result = finalize()
    print(json.dumps(result, ensure_ascii=False))
