"""Check route continuity, rendered Qika days, and migration of saved activities."""
import json
import sys
from pathlib import Path
from effective_routes import load_effective_routes
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.ui-tools'))
from playwright.sync_api import sync_playwright

routes=load_effective_routes(ROOT)
summary=json.loads((ROOT/'daily-summary.json').read_text(encoding='utf-8'))
main=[s for s in routes['segments'] if s['day']]
assert all(a['to']==b['from'] for a,b in zip(main,main[1:]))
for day in summary:
    segments=[s for s in main if s['day']==day['day']]
    assert day['seconds']==sum(s['duration'] for s in segments)
    assert day['km']==round(sum(s['distance'] for s in segments)/1000,1)
    for s in segments:
        assert (ROOT/s['raw_file']).exists()

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#day4')
    page.evaluate("localStorage.setItem('hulunbuir-2026-personal-v1',JSON.stringify({stars:{'5:0':true,'4:2':true},done:{'5:3':true},notes:{4:'七卡订房备注'}}))")
    page.reload()
    page.wait_for_timeout(400)
    assert '七卡村附近' in page.locator('.stay').inner_text()
    assert '3小时18分' in page.locator('.day-metrics').inner_text()
    assert page.locator('[data-star="2"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-star="3"]').get_attribute('aria-pressed')=='false'
    assert page.locator('#note-4').input_value()=='七卡订房备注'
    assert page.evaluate("localStorage.getItem('hulunbuir-2026-personal-v1-before-qika')")
    page.locator('[data-tab="driving"]').click()
    assert page.locator('.drive-card').count()==4
    assert '九卡 → 七卡' in page.locator('.drive-card').last.inner_text()
    page.screenshot(path=str(ROOT/'qika-day4-desktop.png'))
    page.locator('#daynav [data-day="5"]').click()
    assert page.locator('[data-done="2"]').get_attribute('aria-pressed')=='true'
    assert '2小时04分' in page.locator('.day-metrics').inner_text()
    page.locator('[data-tab="driving"]').click()
    assert page.locator('.drive-card').count()==2
    assert '七卡 → 黑山头' in page.locator('.drive-card').first.inner_text()
    page.locator('#aboutBtn').click()
    assert page.locator('#lodgingLink').get_attribute('href')=='lodging-guide.html'
    page.goto((ROOT/'lodging-guide.html').as_uri()+'#night4')
    assert page.locator('#night4 .hotel').count()==5
    assert '七卡村附近' in page.locator('#night4 h2').inner_text()
    page.locator('#night4 details summary').first.click()
    assert '七卡戍边食府' in page.locator('#night4').inner_text()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth')==390
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#day4')
    page.wait_for_timeout(300)
    assert page.evaluate('document.documentElement.scrollWidth')==390
    page.screenshot(path=str(ROOT/'qika-day4-mobile.png'))
    page.locator('[data-view="map"]').click()
    assert '七卡' in page.locator('#mapTitle').inner_text()
    assert not errors, errors
    browser.close()
print('PASS: route continuity, AMap evidence and totals, day 4/5 routes, five Qika stays, saved-state migration, mobile layouts')
