"""Collect public travel notes through an already opened CDP browser.

Reads note content and public interaction counters only. Does not export login
state, cookies, passwords or account data. Stops on login/risk verification pages.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.ui-tools'))


def now():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def parse_count(value):
    """Unknown stays None. Chinese/English compact counts remain approximate."""
    if isinstance(value, bool) or value is None:
        return None
    raw = str(value).strip().replace(',', '').replace('，', '')
    match = re.fullmatch(r'(\d+(?:\.\d+)?)\s*([万亿wWkKmM]?)\+?', raw)
    if not match:
        return None
    units = {'': 1, '万': 10000, '亿': 100000000, 'w': 10000, 'k': 1000, 'm': 1000000}
    return int(Decimal(match[1]) * units[match[2].lower()])


def total(note):
    values = [note.get(k) for k in ('likes', 'collects', 'comments')]
    return sum(values) if all(type(v) is int and v >= 0 for v in values) else None


def rank(notes):
    return sorted(notes, key=lambda n: (total(n) is None, -(total(n) or 0), n['id']))


def candidate_key(card, city, prefer_local=False):
    local = any(alias in card.get('title', '') for alias in city['aliases'])
    return (not local if prefer_local else False, -(parse_count(card.get('likes')) or 0))


def categories(text):
    rules = {
        '吃饭': r'美食|餐厅|吃饭|早餐|早饭|烧烤|烤肉|火锅|铁锅炖|锅茶|俄餐|列巴|手把肉',
        '咖啡茶饮': r'咖啡|奶茶|茶饮|甜品|下午茶|冰淇淋',
        '游玩': r'景点|景区|森林|草原|骑马|驯鹿|日落|日出|观景|湿地|公园|游玩|晨雾|卡线',
        '住宿': r'民宿|酒店|住宿|住哪|木刻楞|客栈',
        '攻略': r'攻略|路线|行程|自驾|避坑|北线|南线',
    }
    return [name for name, pattern in rules.items() if re.search(pattern, text)] or ['攻略']


def screen_content(title, description):
    if re.search(r'求助|帮我看|帮忙看|求推荐|求.*攻略|路线.*行不行|路线.*咋样|合理不', title):
        return '求助型笔记，未作为体验推荐收录'
    prose = description.split('#', 1)[0].strip()
    if len(re.sub(r'\s', '', prose)) < 25:
        return '可提取的正文信息过少，未作为文字推荐收录'
    return None


def city_excerpt(description, city, cities):
    prose = description.split('#', 1)[0].strip()
    chunks = [s.strip() for s in re.split(r'[\n。；;]+', prose) if s.strip()]
    matches = [s for s in chunks if any(alias in s for alias in city['aliases'])]
    if not matches:
        return description[:110] + ('…' if len(description) > 110 else '')
    def priority(chunk):
        other_places = sum(any(a in chunk for a in c['aliases']) for c in cities if c['id'] != city['id'])
        return (other_places == 0, len(chunk) >= 25, min(len(chunk), 100))
    chosen = max(matches, key=priority)
    # In a long multi-city line, start close to the selected destination mention.
    positions = [chosen.find(a) for a in city['aliases'] if a in chosen]
    start = max(0, min(positions) - 12) if len(chosen) > 140 else 0
    excerpt = chosen[start:start + 110]
    return ('…' if start else '') + excerpt + ('…' if len(chosen) > start + 110 else '')


class AccessBlocked(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


def check_access(page):
    if '/captcha' in page.url or '/verify' in page.url:
        raise AccessBlocked('小红书搜索跳转到人工验证页；请在采集 Edge 手动搜索并完成页面验证。', 'verification')
    text = page.locator('body').inner_text(timeout=10000)
    if '300012' in text or 'IP存在风险' in text:
        raise AccessBlocked('小红书提示 IP 存在风险；请在采集浏览器中恢复正常访问后重试。', '300012')
    if any(word in text for word in ['安全验证', '拖动滑块', '请完成验证', '访问频繁']):
        raise AccessBlocked('小红书要求人工验证或限制访问，采集已停止。', 'verification')
    login = page.locator('.login-container, .login-modal')
    if any(login.nth(i).is_visible() for i in range(login.count())) or ('登录后查看搜索结果' in text):
        raise AccessBlocked('请先在采集浏览器完成小红书登录。', 'login_required')
    return text


CARDS_JS = r"""els => els.map(e => {
 const links=[...e.querySelectorAll('a[href]')].filter(a=>/\/(explore|search_result)\/[a-f0-9]{24}/.test(a.href));
 const link=links.find(a=>a.href.includes('xsec_token='))||links[0];
 return {title:e.querySelector('.title')?.innerText?.trim()||'', text:e.innerText, url:link?.href||'',
 likes:e.querySelector('.like-wrapper .count, .like-wrapper span.count')?.textContent?.trim()||null};
}).filter(x=>x.url)"""

DETAIL_JS = r"""() => {
 const map=window.__INITIAL_STATE__?.note?.noteDetailMap || {};
 const id=location.pathname.match(/[a-f0-9]{24}/)?.[0];
 const entry=map[id] || Object.values(map).find(x=>x?.note?.noteId===id);
 const n=entry?.note || {}, i=n.interactInfo || {};
 const txt=s=>document.querySelector(s)?.textContent?.trim() || null;
 return {id:n.noteId||id,title:txt('#detail-title')||n.title||'',
 description:txt('#detail-desc')||n.desc||'',author:txt('.author-container .username')||n.user?.nickname||'',
 likes:i.likedCount ?? txt('.interact-container .like-wrapper .count'),
 collects:i.collectedCount ?? txt('.interact-container .collect-wrapper .count'),
 comments:i.commentCount ?? txt('.interact-container .chat-wrapper .count'),
 publishedTimestamp:n.time||null,publishedLabel:txt('.note-content .date'),url:location.href};
}"""


def save(data):
    data['notes'] = rank(data['notes'])
    path = ROOT / 'city-notes.json'
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def collect(args):
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    config = json.loads((ROOT / 'city-guide-config.json').read_text(encoding='utf-8'))
    data = json.loads((ROOT / 'city-notes.json').read_text(encoding='utf-8'))
    city_list = config['cities']
    if args.cities:
        requested = set(args.cities.split(','))
        city_list = [c for c in city_list if c['id'] in requested or c['name'] in requested]
        if not city_list:
            raise ValueError('没有匹配的城市。请使用 city-guide-config.json 中的名称或 id。')
    evidence = ROOT / 'city-research'
    evidence.mkdir(exist_ok=True)
    records = {n['id']: n for n in data['notes']}
    coverage = data.get('coverage', [])
    query_suffixes = args.query_suffix or config['querySuffixes']
    attempt = {'at': now(), 'status': 'running', 'message': '正在采集', 'method': 'CDP public note content'}
    data['lastAttempt'] = attempt
    seen_this_run = set(records) if args.only_new else set()
    own_pages = []
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(args.cdp, timeout=12000)
            except Exception as exc:
                raise AccessBlocked('未连接到 CDP 浏览器。请先运行“启动小红书采集浏览器.cmd”并登录。', 'cdp_unavailable') from exc
            context = browser.contexts[0]
            search = context.new_page()
            detail = context.new_page()
            own_pages = [search, detail]
            try:
                for city in city_list:
                    candidates = {}
                    buckets = {}
                    report = {'cityId': city['id'], 'city': city['name'], 'at': now(), 'queries': [], 'read': 0, 'errors': [], 'filtered': []}
                    coverage = [r for r in coverage if r['cityId'] != city['id']]
                    coverage.append(report)
                    for suffix in query_suffixes:
                        query = (city.get('searchName') or city['name']) + ' ' + suffix
                        try:
                            search.goto('https://www.xiaohongshu.com/search_result?keyword=' + quote(query) + '&source=web_explore_feed', wait_until='domcontentloaded', timeout=30000)
                        except BrowserTimeout:
                            check_access(search)
                            same_query = parse_qs(urlparse(search.url).query).get('keyword') == [query]
                            if not same_query or not search.locator('section.note-item').count():
                                report['errors'].append({'query': query, 'reason': '搜索页面加载超时'})
                                print(json.dumps({'query': query, 'error': 'search_timeout'}, ensure_ascii=False), flush=True)
                                continue
                        search.wait_for_timeout(2200)
                        check_access(search)
                        found = []
                        for step in range(args.scrolls + 1):
                            check_access(search)
                            cards = search.locator('section.note-item').evaluate_all(CARDS_JS)
                            found.extend(cards)
                            for card in cards:
                                match = re.search(r'/(?:explore|search_result)/([a-f0-9]{24})', card['url'])
                                if match:
                                    card['id'] = match[1]
                                    card['query'] = query
                                    candidates.setdefault(card['id'], card)
                                    buckets.setdefault(query, {})[card['id']] = card
                            if step < args.scrolls:
                                search.mouse.wheel(0, 750)
                                search.wait_for_timeout(1200)
                        report['queries'].append({'query': query, 'visibleCards': len({c['url'] for c in found})})
                        if not found:
                            body = check_access(search)
                            if '登录' in body and ('手机号' in body or '扫码' in body):
                                raise AccessBlocked('搜索需要登录；请在采集浏览器中完成登录。', 'login_required')
                        time.sleep(args.delay)
                        print(json.dumps({'city': city['name'], 'query': query, 'visibleCards': len({c['url'] for c in found})}, ensure_ascii=False), flush=True)
                    # A finite sample: search likes are used only to choose which detail pages to read.
                    selected_by_id = {}
                    quota = max(1, args.per_city // max(1, len(buckets)))
                    for bucket in buckets.values():
                        ranked = sorted((n for n in bucket.values() if n['id'] not in seen_this_run), key=lambda n: candidate_key(n, city, args.prefer_local))
                        for card in [n for n in ranked if n['id'] not in selected_by_id][:quota]:
                            selected_by_id[card['id']] = card
                    for card in sorted((n for n in candidates.values() if n['id'] not in seen_this_run), key=lambda n: candidate_key(n, city, args.prefer_local)):
                        if len(selected_by_id) >= args.per_city:
                            break
                        selected_by_id.setdefault(card['id'], card)
                    selected = list(selected_by_id.values())[:args.per_city]
                    for card in selected:
                        if card['id'] in seen_this_run:
                            continue
                        try:
                            if urlparse(card['url']).hostname != 'www.xiaohongshu.com':
                                report['errors'].append({'id': card['id'], 'reason': '链接域名不匹配，已跳过'})
                                continue
                            detail.goto(card['url'], wait_until='domcontentloaded', timeout=40000)
                            detail.wait_for_timeout(1800)
                            check_access(detail)
                            raw = detail.evaluate(DETAIL_JS)
                            if not raw['description'] and not raw['title']:
                                report['errors'].append({'id': card['id'], 'reason': '未读取到笔记内容，未计入排序'})
                                continue
                            content = raw['title'] + '\n' + raw['description']
                            matched = [c['id'] for c in config['cities'] if any(alias in content for alias in c['aliases'])]
                            if city['id'] not in matched:
                                report['filtered'].append({'id': card['id'], 'reason': '正文和标题未匹配目的地，已过滤'})
                                continue
                            # Preserve the returned public note URL (including its public link token), never cookies.
                            (evidence / (card['id'] + '.json')).write_text(json.dumps({'capturedAt': now(), 'query': card['query'], 'note': raw}, ensure_ascii=False, indent=2), encoding='utf-8')
                            rejection = screen_content(raw['title'], raw['description'])
                            if rejection:
                                report['filtered'].append({'id': card['id'], 'title': raw['title'], 'reason': rejection})
                                records.pop(card['id'], None)
                                continue
                            record = {'id': card['id'], 'title': raw['title'] or card['title'], 'url': raw['url'], 'author': raw['author'],
                                      'cityIds': matched, 'categories': categories(content), 'crossCity': len(matched) > 1,
                                      'excerpt': raw['description'][:110] + ('…' if len(raw['description']) > 110 else ''),
                                      'capturedAt': now(), 'origin': 'cdp', 'query': card['query'],
                                      'suspectedAd': any(term in content for term in config['excludePatterns']),
                                      'approximate': any(re.search(r'[万亿wWkKmM+]', str(raw.get(k) or '')) for k in ['likes', 'collects', 'comments']),
                                      'evidenceFile': 'city-research/' + card['id'] + '.json'}
                            record['cityExcerpts'] = {c['id']: city_excerpt(raw['description'], c, config['cities']) for c in config['cities'] if c['id'] in matched}
                            for key in ['likes', 'collects', 'comments']:
                                record[key] = parse_count(raw[key])
                            if raw['publishedTimestamp']:
                                record['publishedAt'] = datetime.fromtimestamp(raw['publishedTimestamp'] / 1000).astimezone().isoformat(timespec='seconds')
                            records[record['id']] = record
                            seen_this_run.add(record['id'])
                            report['read'] += 1
                            print(json.dumps({'city': city['name'], 'title': record['title'], 'total': total(record)}, ensure_ascii=False), flush=True)
                            data['notes'] = list(records.values())
                            data['coverage'] = coverage
                            save(data)
                        except AccessBlocked:
                            raise
                        except Exception as exc:
                            report['errors'].append({'id': card['id'], 'reason': type(exc).__name__})
                        time.sleep(args.delay)
                    print(json.dumps({'city': city['name'], 'candidates': len(candidates), 'read': report['read']}, ensure_ascii=False), flush=True)
                has_errors = any(r['errors'] or not any(q['visibleCards'] for q in r['queries']) for r in coverage)
                attempt.update(status='partial' if has_errors else 'complete', message='采集完成，部分笔记未读取或城市无结果。' if has_errors else '本次有限样本采集完成。', finishedAt=now())
            finally:
                # Close only the two pages this script created, leaving the user's browser open.
                for page in own_pages:
                    try:
                        page.close()
                    except Exception:
                        pass
    except AccessBlocked as exc:
        attempt.update(status='blocked', code=exc.code, message=str(exc), finishedAt=now())
        print(str(exc), flush=True)
    except Exception as exc:
        attempt.update(status='partial', message='采集未完成：' + type(exc).__name__, errorDetails=str(exc)[:500], finishedAt=now())
        print(attempt['message'], flush=True)
    finally:
        data.update(notes=list(records.values()), coverage=coverage, lastAttempt=attempt)
        save(data)
        (evidence / 'last-run.json').write_text(json.dumps({'attempt': attempt, 'coverage': coverage}, ensure_ascii=False, indent=2), encoding='utf-8')
        run_name = 'run-' + re.sub(r'[^0-9]', '', attempt['at']) + '.json'
        (evidence / run_name).write_text(json.dumps({'attempt': attempt, 'coverage': coverage}, ensure_ascii=False, indent=2), encoding='utf-8')
        if args.rebuild:
            from build_ui import build
            build()
    return 0 if attempt['status'] == 'complete' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cdp', default='http://127.0.0.1:9223')
    parser.add_argument('--cities', help='Comma-separated city ids or Chinese names')
    parser.add_argument('--query-suffix', action='append', help='Override search suffixes, repeatable')
    parser.add_argument('--prefer-local', action='store_true', help='Prefer candidate titles that explicitly name the destination')
    parser.add_argument('--only-new', action='store_true', help='Skip saved note IDs when choosing candidates')
    parser.add_argument('--per-city', type=int, default=8, help='Maximum detail pages per destination')
    parser.add_argument('--scrolls', type=int, default=1)
    parser.add_argument('--delay', type=float, default=1.5)
    parser.add_argument('--rebuild', action='store_true')
    args = parser.parse_args()
    if args.per_city < 1 or not 0 <= args.scrolls <= 10 or args.delay < 1:
        parser.error('per-city >= 1, scrolls 0..10 and delay >= 1 are required')
    if urlparse(args.cdp).hostname not in ('127.0.0.1', 'localhost', '::1'):
        parser.error('CDP endpoint must be on this computer')
    raise SystemExit(collect(args))
