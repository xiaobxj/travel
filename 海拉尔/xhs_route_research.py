"""Read public travel notes using the user's connected browser and normal UI."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.ui-tools'))
from playwright.sync_api import sync_playwright
from collect_city_xhs import check_access, AccessBlocked, CARDS_JS, DETAIL_JS, now

OUT = ROOT / 'route-research-20261003'


def emit(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def save(name, data):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def cards(page):
    rows = page.locator('section.note-item').evaluate_all(CARDS_JS)
    save('last-search.json', {'capturedAt': now(), 'title': page.title(), 'url': page.url, 'cards': rows})
    emit({'title': page.title(), 'url': page.url.split('?')[0], 'cards': [{'id': re.search(r'[a-f0-9]{24}', r['url'])[0], 'title': r['title'], 'text': r['text']} for r in rows]})


def close_note(page):
    control = page.locator('div.close-circle')
    if control.count() and control.first.is_visible():
        control.first.click()
        page.wait_for_timeout(400)


def main():
    args = argparse.ArgumentParser()
    args.add_argument('action', choices=['inspect', 'search', 'read', 'scroll'])
    args.add_argument('--query')
    args.add_argument('--ids', nargs='*', default=[])
    opt = args.parse_args()
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9223', timeout=12000)
        page = next(x for c in browser.contexts for x in c.pages if 'xiaohongshu.com' in x.url)
        page.set_default_timeout(10000)
        try:
            check_access(page)
            if opt.action == 'inspect':
                emit({'title': page.title(), 'url': page.url.split('?')[0], 'controls': page.locator('input,textarea').evaluate_all('(els)=>els.map(e=>({id:e.id,placeholder:e.placeholder,visible:!!(e.getBoundingClientRect().width&&e.getBoundingClientRect().height)}))')})
                cards(page)
            elif opt.action == 'search':
                close_note(page)
                boxes = page.locator('textarea:visible,input:visible')
                if not boxes.count():
                    raise RuntimeError('No visible search field; inspect the page before acting.')
                # These are the observed search fields, not the AI chat control.
                candidates = page.locator('#search-input-ai:visible, #search-input-in-feeds:visible, #search-input:visible, textarea[placeholder="搜索小红书"]:visible')
                if not candidates.count():
                    raise RuntimeError('Observed search field unavailable; inspect before acting.')
                field = candidates.first
                field.fill(opt.query)
                page.wait_for_timeout(600)
                if field.input_value() != opt.query:
                    raise RuntimeError('Search input does not contain requested query')
                field.press('Enter')
                page.wait_for_timeout(1800)
                check_access(page)
                cards(page)
            elif opt.action == 'scroll':
                close_note(page)
                page.mouse.wheel(0, 850)
                page.wait_for_timeout(1000)
                check_access(page)
                cards(page)
            elif opt.action == 'read':
                for nid in opt.ids:
                    if not re.fullmatch('[a-f0-9]{24}', nid):
                        raise ValueError('Invalid selected note id')
                    check_access(page)
                    close_note(page)
                    search_title = page.title()
                    anchor = page.locator(f'section.note-item a.cover[href*="{nid}"]')
                    if not anchor.count():
                        emit({'id': nid, 'status': 'not_in_current_results'})
                        continue
                    anchor.first.click()
                    page.wait_for_timeout(1300)
                    check_access(page)
                    raw = page.evaluate(DETAIL_JS)
                    if raw.get('id') != nid:
                        raise RuntimeError('Opened note differs from selected card')
                    evidence = {'capturedAt': now(), 'query': search_title, 'note': raw}
                    save(nid + '.json', evidence)
                    emit(evidence)
                    close_note(page)
                    page.wait_for_timeout(700)
        except AccessBlocked as exc:
            emit({'status': 'blocked', 'code': exc.code, 'message': str(exc)})
        finally:
            browser.close()


if __name__ == '__main__':
    main()
