import sys,json,time,argparse
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,r'D:\travel\海拉尔\.ui-tools')
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).parent/'research'; ROOT.mkdir(exist_ok=True)
ap=argparse.ArgumentParser(); ap.add_argument('query'); ap.add_argument('--read',type=int,default=0); ap.add_argument('--indices',default=''); ap.add_argument('--saved',action='store_true'); args=ap.parse_args()
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp('http://127.0.0.1:9222',no_defaults=True)
    c=b.contexts[0]; pg=c.new_page()
    if not args.saved:
        pg.goto('https://www.xiaohongshu.com/search_result?keyword='+quote(args.query)+'&source=web_explore_feed',wait_until='domcontentloaded')
        pg.wait_for_timeout(2800)
    cards=json.loads((ROOT/(args.query+'-搜索.json')).read_text(encoding='utf-8')) if args.saved else pg.locator('section.note-item').evaluate_all('els=>els.map(e=>({text:e.innerText,url:Array.from(e.querySelectorAll("a[href]"),a=>a.href).find(s=>s.includes("xsec_token"))}))')
    if not cards:
        cards=pg.locator('a[href*="xsec_token"]').evaluate_all('els=>els.filter(e=>e.innerText.trim()).map(e=>({text:e.innerText,url:e.href}))')
    (ROOT/(args.query+'-搜索.json')).write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
    print('SEARCH',json.dumps([{'index':i,'text':x['text']} for i,x in enumerate(cards)],ensure_ascii=False),flush=True)
    indices=[int(i) for i in args.indices.split(',') if i] if args.indices else range(min(args.read,len(cards)))
    for i in indices:
        card=cards[i]; url=card['url']; note=c.new_page()
        try:
            note.goto(url,wait_until='domcontentloaded',timeout=35000); note.wait_for_timeout(1800)
            selectors={k:note.locator(sel).all_text_contents() for k,sel in {'title':'#detail-title','description':'#detail-desc','author':'.author-container .username','comments':'.comment-item .content','date':'.note-content .date'}.items()}
            record={'query':args.query,'card':card,'url':note.url,**selectors}
            if not selectors['description']: record['body']=note.locator('body').inner_text()
            (ROOT/(args.query+'-'+str(i)+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
            print('NOTE',json.dumps(record,ensure_ascii=False)[:12000],flush=True)
        except Exception as e: print('ERROR',str(e)[:120],flush=True)
        finally: note.close()
        time.sleep(1)
    pg.close()
