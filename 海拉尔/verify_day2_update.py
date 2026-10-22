"""Check the revised route, saved records, navigation and responsive rendering."""
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.ui-tools'))
from playwright.sync_api import sync_playwright
from effective_routes import load_effective_routes

routes=load_effective_routes()
r=routes['day2Research']
assert (r['plans']['A']['distance'],r['plans']['A']['duration'])==(123794,7805)
assert r['plans']['B']['duration']-r['plans']['A']['duration']==569
assert r['plans']['C']['duration']==8613
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#day2')
    page.wait_for_timeout(400)
    assert page.locator('.activity').count()==7
    assert '123.8' in page.locator('.day-metrics').inner_text()
    assert '恢复开放' in page.locator('.route-update').inner_text()
    old={'routeRevision':'qika-overnight-2026-09-06','stars':{'2:0':True,'2:1':True,'2:3':True,'3:0':True},'done':{'2:2':True},'notes':{'2':'原有住宿备注'}}
    page.evaluate('(raw)=>localStorage.setItem("hulunbuir-2026-personal-v1",JSON.stringify(raw))',old)
    page.reload()
    for i in (4,5,6):assert page.locator(f'[data-star="{i}"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-star="0"]').get_attribute('aria-pressed')=='false'
    assert page.locator('[data-done="1"]').get_attribute('aria-pressed')=='true'
    assert page.locator('#note-2').input_value()=='原有住宿备注'
    saved=page.evaluate('localStorage.getItem("hulunbuir-2026-personal-v1")')
    page.reload()
    assert saved==page.evaluate('localStorage.getItem("hulunbuir-2026-personal-v1")')
    for i,name in ((0,'觉乐驯鹿园'),(3,'得耳布尔站'),(4,'龙山公园'),(5,'敖鲁古雅停车场')):
        page.locator(f'[data-activity="{i}"]').click()
        page.wait_for_timeout(400)
        assert page.locator(f'.map-pin[data-poi="{name}"] .map-selected-glow').count()==1
        assert page.locator(f'#activitybody-{i}').is_visible()
    page.locator('[data-activity="0"]').click()
    page.locator('#panel').evaluate('(e)=>e.scrollTop=0')
    page.screenshot(path=str(ROOT/'day2-desktop-update.png'))
    for anchor in page.locator('#activitybody-0 .refs a').all():
        assert urlparse(anchor.get_attribute('href')).hostname=='www.xiaohongshu.com'
    page.locator('[data-tab="driving"]').click()
    assert page.locator('.drive-card').count()==6
    assert '2小时24分' in page.locator('.route-plans').inner_text()
    for anchor,leg in zip(page.locator('.drive-card a').all(),r['legs']):
        parsed=parse_qs(urlparse(anchor.get_attribute('href')).query)
        assert parsed['from'][0].startswith(routes['pois'][leg['from']]['location'])
        assert parsed['to'][0].startswith(routes['pois'][leg['to']]['location'])
    assert page.locator('.driving-evidence a').count()==5
    page.locator('#panel').evaluate('(e)=>e.scrollTop=0')
    page.screenshot(path=str(ROOT/'day2-driving-update.png'))
    assert page.locator('#cityGuide').is_visible()
    page.locator('#citySelect').select_option('genhe')
    # New places must be available in the default verified-only city guide.
    assert page.evaluate("DATA.cityGuide.recommendations.items.filter(x=>['genhe-new-juele','deerbur-new-station','mordaga-new-longshan'].includes(x.id)).every(x=>x.placeCheck.status==='verified')")
    assert page.locator('[data-focus-place="genhe-new-juele"]').is_visible()
    page.locator('[data-focus-place="genhe-new-juele"]').click()
    page.locator('#searchBtn').click()
    page.locator('#tripSearch').fill('觉乐')
    assert page.locator('[data-result="2:0"]').is_visible()
    page.locator('[data-result="2:0"]').click()
    assert page.locator('#activitybody-0').is_visible()
    phone=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    phone.on('pageerror',lambda e:errors.append(str(e)))
    phone.goto((ROOT/'itinerary-map.html').as_uri()+'#day2')
    phone.wait_for_timeout(300)
    assert phone.evaluate('document.documentElement.scrollWidth')==390
    phone.screenshot(path=str(ROOT/'day2-mobile-update.png'))
    phone.locator('[data-tab="driving"]').click()
    assert phone.evaluate('document.documentElement.scrollWidth')==390
    phone.screenshot(path=str(ROOT/'day2-mobile-driving.png'))
    phone.locator('[data-view="map"]').click()
    assert phone.locator('.map-pin[data-poi="觉乐驯鹿园"]').is_visible()
    assert not errors,errors
    # Refresh the downloadable overview image so it follows the current route.
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#overview')
    page.set_viewport_size({'width':1800,'height':1250})
    page.wait_for_timeout(600)
    page.locator('.maparea').screenshot(path=str(ROOT/'itinerary-map.png'))
    browser.close()
print('PASS: day 2 route totals, six navigation links, source links, saved-state migration, maps, search, desktop/mobile; overview image refreshed')
