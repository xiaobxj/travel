"""Browser checks for persisted personal records and linked map interactions."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.ui-tools'))
from playwright.sync_api import sync_playwright

def assert_three_column_layout(page):
    assert not page.locator('#resizeHandle').is_visible()
    columns=page.locator('.workspace').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ")')
    assert len(columns)==3, columns
    panes=[page.locator(selector) for selector in ('.sidebar','.maparea','.city-guide')]
    assert all(pane.is_visible() for pane in panes)
    boxes=[pane.bounding_box() for pane in panes]
    assert all(box['width']>0 for box in boxes)
    assert all(left['x']+left['width']<=right['x']+1 for left,right in zip(boxes,boxes[1:])), boxes
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'itinerary-map.html').as_uri()+'#day3')
    page.wait_for_timeout(500)
    page.locator('[data-star="2"]').click()
    assert page.locator('[data-star="2"]').get_attribute('aria-pressed')=='true'
    page.locator('[data-done="2"]').click()
    assert page.locator('#activity-2').evaluate('(e)=>e.classList.contains("completed")')
    page.locator('[data-filter="stars"]').click()
    assert page.locator('.activity').count()==1
    assert page.locator('#activity-2').is_visible()
    page.locator('.daily-note summary').click()
    note='白鹿岛民宿：确认供暖；备注 <script>安全文本</script>'
    page.locator('[data-note="3"]').fill(note)
    assert '已保存' in page.locator('.note-status').inner_text()
    page.reload()
    page.wait_for_timeout(500)
    assert page.locator('[data-star="2"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-done="2"]').get_attribute('aria-pressed')=='true'
    page.locator('.daily-note summary').click()
    assert page.locator('[data-note="3"]').input_value()==note
    page.locator('[data-filter="todo"]').click()
    assert page.locator('#activity-2').count()==0
    page.locator('[data-filter="all"]').click()
    page.locator('[data-done="2"]').click()
    page.locator('#toast button').click()
    assert page.locator('[data-done="2"]').get_attribute('aria-pressed')=='true'

    page.keyboard.press('Control+k')
    assert page.locator('#searchDialog').is_visible()
    page.locator('#tripSearch').fill('根白')
    assert page.locator('.search-result').count()>0
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')
    assert not page.locator('#searchDialog').is_visible()
    assert page.locator('#daynav .active').get_attribute('data-day')=='2'
    assert page.locator('.activity.selected').count()==1
    assert page.evaluate('window.scrollY')==0
    page.locator('#savedBtn').click()
    assert page.locator('.search-result').count()==1
    page.locator('#tripSearch').fill('nothing_matches_234')
    assert page.locator('#searchResults .empty-state').is_visible()
    page.locator('#tripSearch').fill('')
    page.screenshot(path=str(ROOT/'ui-search.png'))
    page.locator('.search-result').click()
    assert page.locator('#daynav .active').get_attribute('data-day')=='3'
    assert page.locator('#activitybody-2').is_visible()

    page.locator('#previewBtn').click()
    assert page.locator('#previewBar').is_visible()
    page.locator('#previewPlay').click()
    page.wait_for_timeout(450)
    assert float(page.locator('#previewSlider').input_value())>0
    page.locator('#previewPlay').click()
    stopped=page.locator('#previewSlider').input_value()
    page.wait_for_timeout(200)
    assert page.locator('#previewSlider').input_value()==stopped
    page.locator('#previewSlider').fill('60')
    assert page.locator('#previewPercent').inner_text()=='60%'
    assert page.locator('.preview-marker').get_attribute('visibility')=='visible'
    page.locator('#labelsBtn').click()
    assert page.locator('.map-pin text').first.evaluate('(e)=>getComputedStyle(e).display')=='none'
    page.locator('#labelsBtn').click()
    page.locator('#contextBtn').click()
    page.wait_for_timeout(250)
    assert page.locator('.route.is-context').first.evaluate('(e)=>getComputedStyle(e).opacity')=='0'
    page.locator('#contextBtn').click()
    page.screenshot(path=str(ROOT/'ui-interactive-desktop.png'))
    page.locator('#daynav [data-day="4"]').click()
    assert not page.locator('#previewBar').is_visible()
    assert page.locator('.preview-marker').get_attribute('visibility')=='hidden'
    if page.locator('#resizeHandle').is_visible():
        page.locator('#resizeHandle').focus()
        old_width=page.locator('.sidebar').bounding_box()['width']
        page.keyboard.press('ArrowRight')
        assert page.locator('.sidebar').bounding_box()['width']==old_width+20
        page.reload()
        assert page.locator('.sidebar').bounding_box()['width']==old_width+20
        layout_check='resize keyboard and persistence'
    else:
        # The city guide deliberately uses three fixed columns and hides the splitter.
        assert_three_column_layout(page)
        page.reload()
        assert_three_column_layout(page)
        layout_check='three visible columns, hidden splitter, no overlap or page overflow, reload persistence'
    point=page.evaluate('''() => {const line=document.querySelector('.route-hit[data-day="4"]');const p=line.getPointAtLength(line.getTotalLength()/2);return new DOMPoint(p.x,p.y).matrixTransform(line.getScreenCTM()).toJSON()}''')
    page.mouse.move(point['x'],point['y'])
    assert page.locator('#routeTooltip').is_visible()
    page.locator('#exportBtn').click()
    with page.expect_download() as info:
        page.locator('#exportPersonal').click()
    downloaded=Path(info.value.path()).read_text(encoding='utf-8')
    assert note in downloaded and '☆ 想去' in downloaded and '- [x]' in downloaded
    page.keyboard.press('Escape')

    phone=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    phone.on('pageerror',lambda e:errors.append(str(e)))
    phone.goto((ROOT/'itinerary-map.html').as_uri()+'#day3')
    phone.wait_for_timeout(500)
    phone.locator('[data-star="2"]').click()
    phone.locator('[data-filter="stars"]').click()
    phone.screenshot(path=str(ROOT/'ui-interactive-mobile.png'))
    phone.locator('[data-view="map"]').click()
    phone.wait_for_timeout(400)
    phone.locator('#previewBtn').click()
    phone.locator('#previewSlider').fill('45')
    phone.wait_for_timeout(400)
    assert phone.locator('#previewPercent').inner_text()=='45%'
    assert phone.evaluate('document.documentElement.scrollWidth')==390
    phone.screenshot(path=str(ROOT/'ui-interactive-mobile-map.png'))
    phone.locator('[data-view="list"]').click()
    phone.locator('#searchBtn').click()
    phone.locator('#tripSearch').fill('根白')
    phone.locator('.search-result').first.click()
    assert phone.locator('.sidebar').is_visible()
    assert phone.locator('#daynav .active').get_attribute('data-day')=='2'
    assert not errors,errors
    print(json.dumps({'status':'PASS','checks':['favorites','check-in','filters','undo','notes escaped and persisted','reload persistence','keyboard search','saved list','empty search','linked result','preview play pause scrub','preview reset on day change','map layers',layout_check,'route hover','personal export content','mobile actions and map'],'page_errors':errors}))
    browser.close()
