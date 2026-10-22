"""Exercise day 3 choices, saved indexes, map pins and navigation links."""
import sys
from pathlib import Path
from urllib.parse import parse_qs,urlparse
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.ui-tools'))
from playwright.sync_api import sync_playwright
from effective_routes import load_effective_routes
r=load_effective_routes()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#day3')
    assert page.locator('.activity').count()==len(page.evaluate('DATA.activities.days.find(d=>d.day===3).items'))
    assert '109.5' in page.locator('.day-metrics').inner_text()
    assert '2小时04分' in page.locator('.day-metrics').inner_text()
    assert page.locator('.map-pin[data-poi="红豆坡"]').count()==1
    assert page.locator('.map-pin[data-poi="一目九岭"]').count()==1
    page.evaluate("localStorage.setItem('hulunbuir-2026-personal-v1',JSON.stringify({routeRevision:'qika-overnight-2026-09-06',day2Revision:'juele-2026-10-03',stars:{'3:0':true,'3:1':true},done:{'3:2':true},notes:{3:'原有白鹿岛住宿备注'}}))")
    page.reload()
    assert page.locator('[data-star="0"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-star="1"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-done="2"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-star="4"]').get_attribute('aria-pressed')=='false'
    assert page.locator('#note-3').input_value()=='原有白鹿岛住宿备注'
    page.locator('[data-activity="4"]').click()
    assert page.locator('.map-pin[data-poi="白鹿岛漂流"] .map-selected-glow').count()==1
    assert '4分43秒' in page.locator('#activitybody-4').inner_text()
    assert page.locator('#activitybody-4 .refs a').count()==2
    page.wait_for_timeout(400)
    page.screenshot(path=str(ROOT/'day3-desktop-update.png'))
    page.locator('[data-tab="driving"]').click()
    links=page.locator('.drive-card a').all()
    assert len(links)==7
    for link,leg in zip(links,r['day3Research']['legs']+r['day3Research']['trainLegs']):
        q=parse_qs(urlparse(link.get_attribute('href')).query)
        assert q['from'][0].startswith(r['pois'][leg['from']]['location'])
        assert q['to'][0].startswith(r['pois'][leg['to']]['location'])
    page.locator('[data-segment]').first.click()
    assert page.locator('.drive-card.selected').count()==1
    page.locator('#citySelect').select_option('mordaga')
    assert page.locator('[data-focus-place="mordaga-new-hongdoupo"]').count()==1
    assert page.locator('[data-focus-place="mordaga-new-yimujiuling"]').count()==1
    page.locator('#citySelect').select_option('bailudao')
    assert page.locator('[data-focus-place="bailudao-new-rafting"]').count()==1
    page.locator('[data-focus-place="bailudao-new-rafting"]').click()
    page.locator('#searchBtn').click()
    page.locator('#tripSearch').fill('漂流')
    assert page.locator('[data-result="3:4"]').count()==1
    page.locator('[data-result="3:4"]').click()
    assert page.locator('#activitybody-4').is_visible()
    phone=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    phone.on('pageerror',lambda e:errors.append(str(e)))
    phone.goto((ROOT/'itinerary-map.html').as_uri()+'#day3')
    phone.locator('[data-activity="0"]').click()
    phone.locator('#activity-0').scroll_into_view_if_needed()
    phone.wait_for_timeout(400)
    assert phone.evaluate('document.documentElement.scrollWidth')==390
    phone.screenshot(path=str(ROOT/'day3-mobile-update.png'))
    phone.locator('[data-tab="driving"]').click()
    phone.locator('#panel').evaluate('(e)=>e.scrollTop=0')
    assert phone.evaluate('document.documentElement.scrollWidth')==390
    phone.screenshot(path=str(ROOT/'day3-mobile-driving.png'))
    assert not errors,errors
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#overview')
    page.set_viewport_size({'width':1800,'height':1250})
    page.wait_for_timeout(600)
    page.locator('.maparea').screenshot(path=str(ROOT/'itinerary-map.png'))
    browser.close()
print('PASS: day 3 timings, existing saved records, five route legs, optional rafting, replacement plan, city pins, search, desktop/mobile')
