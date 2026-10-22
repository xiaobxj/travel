"""Verify public artifact hashes and a fresh browser rendering after deployment."""
import hashlib
import json
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
ROOT=Path(__file__).parent
BASE='https://ddosvoid-xbxj-travel-d8a9eef5fd2-1301066507.tcloudbaseapp.com/hailar-erguna/'
parser=argparse.ArgumentParser()
parser.add_argument('--day',type=int,choices=[2,3,4],default=4)
DAY=parser.parse_args().day
manifest=json.loads((ROOT/'publish-20261003-manifest.json').read_text(encoding='utf-8'))
def verify(name):
    response=requests.get(BASE+name,timeout=40,headers={'Cache-Control':'no-cache'})
    response.raise_for_status()
    digest=hashlib.sha256(response.content).hexdigest()
    assert digest==manifest[name]['sha256'], (name,'Public content does not match current build')
    return {'file':name,'http':response.status_code,'sha256':digest}
with ThreadPoolExecutor(max_workers=5) as pool:
    results=list(pool.map(verify,manifest))
sys.path.insert(0,str(ROOT/'.ui-tools'))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    response=page.goto(BASE+f'index.html#day{DAY}',wait_until='networkidle')
    if response.status!=200 and '由腾讯云 CloudBase 提供的测试域名' in page.locator('body').inner_text():
        page.get_by_text('确定访问',exact=True).wait_for(timeout=15000)
        page.get_by_text('确定访问',exact=True).click()
        page.locator('#daynav').wait_for(timeout=20000)
    else:
        assert response.status==200
    page.locator(f'#daynav [data-day="{DAY}"]').click()
    expected={2:(7,'觉乐','123.8','2小时10分',6),3:(5,'红豆坡','109.5','2小时04分',7),4:(7,'临江','221.3','4小时18分',5)}[DAY]
    assert page.locator('.activity').count()==expected[0]
    assert expected[1] in page.locator('.day-subtitle').inner_text()
    assert expected[2] in page.locator('.day-metrics').inner_text()
    assert expected[3] in page.locator('.day-metrics').inner_text()
    if DAY==3:
        assert page.locator('.meal-plan article').count()==4
        assert '12:10–12:50' in page.locator('#panel').inner_text()
    page.locator('[data-tab="driving"]').click()
    assert page.locator('.drive-card a').count()==expected[4]
    if DAY==2:assert '2小时24分' in page.locator('.route-plans').inner_text()
    elif DAY==3:assert '2小时04分' in page.locator('.route-update').inner_text()
    else:assert '4小时45分' in page.locator('#panel').inner_text()
    page.screenshot(path=str(ROOT/f'published-day{DAY}-desktop.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-tab="activities"]').click()
    page.wait_for_timeout(200)
    assert page.evaluate('document.documentElement.scrollWidth')==390
    page.screenshot(path=str(ROOT/f'published-day{DAY}-mobile.png'))
    assert not errors,errors
    browser.close()
result={'status':'PASS','url':BASE+f'index.html#day{DAY}','files':results,'browserErrors':errors}
(ROOT/'publish-20261003-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','publicFilesMatched':len(results),'browserErrors':errors,'url':result['url']},ensure_ascii=False))
