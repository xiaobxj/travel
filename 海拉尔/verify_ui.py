import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'.ui-tools'))
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).parent
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'itinerary-map.html').as_uri())
    page.wait_for_timeout(600)
    assert page.locator('.overview-card').count()==6
    page.screenshot(path=str(ROOT/'ui-desktop-overview.png'))
    before=page.locator('#map').get_attribute('viewBox')
    page.locator('#daynav [data-day="3"]').click()
    page.wait_for_timeout(500)
    assert page.locator('#panel').inner_text().find('住在河湾')>=0
    assert page.evaluate('window.scrollY')==0
    assert page.locator('#map').get_attribute('viewBox')!=before
    page.locator('[data-activity="2"]').click()
    page.wait_for_timeout(400)
    assert page.locator('#activitybody-2').is_visible()
    assert page.locator('#popup').is_visible()
    page.screenshot(path=str(ROOT/'ui-desktop-day.png'))
    page.locator('[data-tab="driving"]').click()
    page.locator('[data-segment]').first.click()
    page.wait_for_timeout(500)
    assert page.locator('.drive-card.selected').count()==1
    page.locator('#daynav [data-day="4"]').click()
    page.wait_for_timeout(500)
    point=page.evaluate('''() => {const line=document.querySelector('.route-hit[data-day="4"]');const p=line.getPointAtLength(line.getTotalLength()/2);const q=new DOMPoint(p.x,p.y).matrixTransform(line.getScreenCTM());return {x:q.x,y:q.y}}''')
    page.mouse.click(point['x'],point['y'])
    page.wait_for_timeout(500)
    assert page.locator('[data-tab="driving"]').get_attribute('aria-selected')=='true','Map route click did not select driving panel'
    assert page.evaluate('window.scrollY')==0
    vb=page.locator('#map').get_attribute('viewBox')
    page.locator('#zoomIn').click()
    assert page.locator('#map').get_attribute('viewBox')!=vb
    vb=page.locator('#map').get_attribute('viewBox')
    selected_day=page.locator('#daynav .active').get_attribute('data-day')
    rect=page.locator('#map').bounding_box()
    page.mouse.move(rect['x']+rect['width']*.7,rect['y']+rect['height']*.65)
    page.mouse.down()
    page.mouse.move(rect['x']+rect['width']*.7+70,rect['y']+rect['height']*.65+45,steps=8)
    page.mouse.up()
    assert page.locator('#map').get_attribute('viewBox')!=vb
    assert page.locator('#daynav .active').get_attribute('data-day')==selected_day
    page.locator('#aboutBtn').click()
    assert page.locator('#about').is_visible()
    page.keyboard.press('Escape')
    assert not page.locator('#about').is_visible()
    page.locator('#exportBtn').click()
    assert page.locator('#exports a[download]').count()==4
    page.keyboard.press('Escape')
    phone=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1)
    phone.on('pageerror',lambda e:errors.append(str(e)))
    phone.goto((ROOT/'itinerary-map.html').as_uri()+'#day3')
    phone.wait_for_timeout(500)
    assert phone.locator('.sidebar').is_visible()
    assert not phone.locator('.maparea').is_visible()
    assert phone.evaluate('document.documentElement.scrollWidth')==390
    phone.screenshot(path=str(ROOT/'ui-mobile-itinerary.png'))
    phone.locator('[data-view="map"]').click()
    phone.wait_for_timeout(400)
    assert phone.locator('.maparea').is_visible()
    assert not phone.locator('.sidebar').is_visible()
    phone.screenshot(path=str(ROOT/'ui-mobile-map.png'))
    phone.locator('[data-view="list"]').click()
    assert phone.locator('#daynav .active').get_attribute('data-day')=='3'
    assert not errors,errors
    print(json.dumps({'status':'PASS','checks':['overview','day sync','no document scroll','activity expansion','segment selection','map route click','zoom','drag preserves selection','dialogs','mobile layouts','mobile selection preserved'],'page_errors':errors}))
    browser.close()
