import sys,json
from pathlib import Path
sys.path.insert(0,r'D:\travel\海拉尔\.ui-tools')
from playwright.sync_api import sync_playwright
R=Path(__file__).parent
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((R/'index.html').as_uri());page.wait_for_timeout(300)
    assert page.locator('[data-day]').count()==4
    assert page.locator('#base').get_attribute('href').startswith('data:image/png;base64,')
    assert page.evaluate('document.documentElement.scrollWidth')==1440
    page.screenshot(path=str(R/'preview-desktop.png'))
    page.locator('[data-day="2"]').click();assert '一半老城' in page.locator('#dayHead').inner_text()
    page.locator('[data-place="stpaul"]').click();assert '大三巴' in page.locator('#popup').inner_text()
    page.locator('[data-star="stpaul"]').click();assert '已收藏' in page.locator('[data-star="stpaul"]').inner_text()
    page.locator('[data-note="stpaul"]').fill('测试备注');page.reload();page.locator('[data-place="stpaul"]').click();assert page.locator('[data-note="stpaul"]').input_value()=='测试备注'
    page.locator('[data-note="stpaul"]').fill('');page.locator('[data-star="stpaul"]').click()
    page.locator('[data-tab="transport"]').click();page.locator('#panel [data-route]').first.click();assert '高德已查询' in page.locator('#popup').inner_text()
    page.locator('[data-day="3"]').click();page.locator('[data-tab="stay"]').click();assert page.locator('#panel [data-place]').count()==5
    assert page.locator('#mapSelect').input_value()=='resort'
    page.locator('[data-place="yinghaihotel"]').click();assert '迎海' in page.locator('#popup').inner_text()
    page.locator('[data-day="4"]').click();page.locator('[data-place="submarine"]').click();assert '不是深海潜艇精确位置' in page.locator('#popup').inner_text()
    page.locator('[data-close-popup]').click();before=page.locator('#map').get_attribute('viewBox');page.locator('#zin').click();assert page.locator('#map').get_attribute('viewBox')!=before
    rect=page.locator('#map').bounding_box();page.mouse.move(rect['x']+rect['width']*.5,rect['y']+rect['height']*.65);page.mouse.down();page.mouse.move(rect['x']+rect['width']*.5+80,rect['y']+rect['height']*.65+30,steps=6);page.mouse.up()
    page.locator('#sourcesBtn').click();assert page.locator('#sourceBody .source-card').count()>=18;page.keyboard.press('Escape')
    page.locator('#searchBtn').click();page.locator('#search').fill('金城');page.locator('[data-search-id="jincheng"]').click();assert '金城' in page.locator('#popup').inner_text()
    page.locator('#planBtn').click();assert page.locator('#planDialog tbody tr').count()==4;page.keyboard.press('Escape')
    phone=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);phone.on('pageerror',lambda e:errors.append(str(e)))
    phone.goto((R/'index.html').as_uri());assert phone.evaluate('document.documentElement.scrollWidth')==390
    assert phone.locator('.sidebar').is_visible();assert not phone.locator('.maparea').is_visible()
    phone.screenshot(path=str(R/'preview-mobile-list.png'))
    phone.locator('[data-day="4"]').click();phone.locator('[data-place="bermuda"]').click();assert phone.locator('.maparea').is_visible();assert phone.locator('#popup').is_visible()
    phone.wait_for_timeout(350)
    selected_point=phone.evaluate('''() => {const p=project(byId[selected].location);const rect=document.querySelector('#map').getBoundingClientRect();const y=rect.y+(p[1]-view[1])/view[3]*rect.height;return {y,top:document.querySelector('#popup').getBoundingClientRect().y}}''')
    assert selected_point['y'] < selected_point['top'],selected_point
    phone.screenshot(path=str(R/'preview-mobile-map.png'))
    phone.locator('[data-view="list"]').click();assert phone.locator('.sidebar').is_visible();assert '飞船' in phone.locator('#dayHead').inner_text() or '宇宙' in phone.locator('#dayHead').inner_text()
    assert not errors,errors
    print(json.dumps({'status':'PASS','page_errors':errors,'checks':['4 days','actual basemaps','itinerary detail','favorite and notes persistence','AMap routes','5 resort hotels','indoor uncertainty','zoom and drag','sources','search cross-day','overview','mobile list/map','no horizontal overflow']},ensure_ascii=False))
    browser.close()
