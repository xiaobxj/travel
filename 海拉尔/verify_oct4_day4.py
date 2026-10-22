"""Exercise the October 5 day-four route, saved selections and mobile layout."""
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.ui-tools'))
from playwright.sync_api import sync_playwright
from effective_routes import load_effective_routes


def main():
    routes = load_effective_routes(ROOT)
    research = routes['day4Research']
    activities = json.loads((ROOT / 'activities.json').read_text(encoding='utf-8'))
    day = next(d for d in activities['days'] if d['day'] == 4)
    assert day['date'] == '10/5' and len(day['items']) == 7
    assert len(research['legs']) == 5
    assert research['plans']['main']['duration'] // 60 == 258
    assert int(research['plans']['withEagle']['duration'] / 60 + .5) == 285
    assert research['plans']['main']['to'] == '七卡'

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1100})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'itinerary-map.html').as_uri() + '#day4')
        assert page.locator('.activity').count() == 7
        assert '4小时18分' in page.locator('.day-metrics').inner_text()
        content = page.locator('#panel').text_content()
        assert all(name in content for name in ('驶路', '团结广场', '奥利亚', '七卡'))
        assert page.evaluate('document.documentElement.scrollWidth') == 1440
        for poi in ('驶路部落民宿（餐厅整体参考点）', '团结广场', '奥利亚列巴房', '七卡'):
            assert page.locator(f'.map-pin[data-poi="{poi}"]').count() == 1, poi

        # The first five day-four activity indexes predate the two additions.
        # A saved record must retain its meaning and must not star the new items.
        original = {
            'routeRevision': 'qika-overnight-2026-09-06',
            'day2Revision': 'juele-2026-10-03',
            'stars': {f'4:{i}': True for i in range(5)},
            'done': {f'4:{i}': True for i in range(5)},
            'notes': {'4': '原有七卡过夜备注'},
        }
        page.evaluate('(value)=>localStorage.setItem("hulunbuir-2026-personal-v1",JSON.stringify(value))', original)
        page.reload()
        for index in range(5):
            assert page.locator(f'[data-star="{index}"]').get_attribute('aria-pressed') == 'true'
            assert page.locator(f'[data-done="{index}"]').get_attribute('aria-pressed') == 'true'
        for index in (5, 6):
            assert page.locator(f'[data-star="{index}"]').get_attribute('aria-pressed') == 'false'
            assert page.locator(f'[data-done="{index}"]').get_attribute('aria-pressed') == 'false'
        assert page.locator('#note-4').input_value() == '原有七卡过夜备注'
        page.locator('[data-activity="1"]').click()
        page.wait_for_timeout(250)
        page.screenshot(path=str(ROOT / 'oct4-day4-desktop.png'))

        page.locator('[data-tab="driving"]').click()
        driving_text = page.locator('#panel').inner_text()
        assert '4小时18分' in driving_text and '4小时45分' in driving_text
        links = page.locator('.drive-card a').all()
        assert len(links) >= 5
        for link, leg in zip(links, research['legs']):
            params = parse_qs(urlparse(link.get_attribute('href')).query)
            assert params['from'][0].startswith(routes['pois'][leg['from']]['location'])
            assert params['to'][0].startswith(routes['pois'][leg['to']]['location'])
        page.locator('#panel').evaluate('(el)=>el.scrollTop=0')
        page.screenshot(path=str(ROOT / 'oct4-day4-desktop-driving.png'))

        phone = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        phone.on('pageerror', lambda error: errors.append(str(error)))
        phone.goto((ROOT / 'itinerary-map.html').as_uri() + '#day4')
        assert phone.locator('.activity').count() == 7
        phone.locator('[data-activity="1"]').click()
        phone.locator('#activity-1').scroll_into_view_if_needed()
        phone.wait_for_timeout(250)
        assert phone.evaluate('document.documentElement.scrollWidth') == 390
        phone.screenshot(path=str(ROOT / 'oct4-day4-mobile.png'))
        phone.locator('[data-tab="driving"]').click()
        phone.locator('#panel').evaluate('(el)=>el.scrollTop=0')
        assert phone.evaluate('document.documentElement.scrollWidth') == 390
        assert '4小时45分' in phone.locator('#panel').inner_text()
        phone.screenshot(path=str(ROOT / 'oct4-day4-mobile-driving.png'))
        assert not errors, errors
        browser.close()
    print('PASS: day4 seven activities, lunch/river/bakery, five exact navigation legs, 4h18/4h45 plans, Qika endpoint, saved first-five records, desktop/mobile and no JS errors/overflow')


if __name__ == '__main__':
    main()
