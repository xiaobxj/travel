"""Read the user's already accessible search tab through normal note clicks.

Does not navigate to legacy search endpoints, create login sessions, or bypass
verification. Stops immediately if the normal site asks for verification.
"""
import json,re,sys,time
from pathlib import Path
from datetime import datetime
from collect_city_xhs import (ROOT,now,parse_count,categories,city_excerpt,screen_content,
                            check_access,AccessBlocked,CARDS_JS,DETAIL_JS,save)
sys.path.insert(0,str(ROOT/'.ui-tools'))
from playwright.sync_api import sync_playwright

def run():
    data=json.loads((ROOT/'city-notes.json').read_text(encoding='utf-8'))
    config=json.loads((ROOT/'city-guide-config.json').read_text(encoding='utf-8'))
    records={n['id']:n for n in data['notes']};stamp=now()
    attempt=dict(at=stamp,status='running',method='CDP existing visible search and normal note clicks',message='读取用户已打开的新版搜索结果')
    data['lastAttempt']=attempt;added=[]
    with sync_playwright() as p:
        b=p.chromium.connect_over_cdp('http://127.0.0.1:9223')
        page=next((x for c in b.contexts for x in c.pages if 'xiaohongshu.com' in x.url and x.locator('section.note-item').count()),None)
        if page is None:raise RuntimeError('No accessible existing search tab')
        try:
            check_access(page)
            if page.locator('div.close-circle').count() and page.locator('div.close-circle').first.is_visible():page.locator('div.close-circle').first.click();page.wait_for_timeout(500)
            query=page.title().replace(' - 小红书搜索','')
            cards=page.locator('section.note-item').evaluate_all(CARDS_JS)
            for card in cards:
                match=re.search(r'/(?:explore|search_result)/([a-f0-9]{24})',card['url'])
                if not match or match[1] in records:continue
                if len(added)>=14:break
                check_access(page);nid=match[1]
                anchor=page.locator(f'section.note-item a.cover[href*="{nid}"]')
                if not anchor.count():continue
                anchor.first.click();page.wait_for_timeout(1800);check_access(page)
                raw=page.evaluate(DETAIL_JS)
                if raw.get('id')!=nid:raise RuntimeError('Opened note id differs from clicked source')
                captured=now();path=ROOT/'city-research'/f'{nid}.json'
                path.write_text(json.dumps(dict(capturedAt=captured,query=query,note=raw),ensure_ascii=False,indent=2),encoding='utf-8')
                text=raw['title']+'\n'+raw['description']
                cities=[c for c in config['cities'] if any(a in text for a in c['aliases'])]
                if cities and not screen_content(raw['title'],raw['description']):
                    count={k:parse_count(raw.get(k)) for k in ['likes','collects','comments']}
                    n=dict(id=nid,title=raw['title'],url=raw['url'],author=raw['author'],cityIds=[c['id'] for c in cities],categories=categories(text),
                           **count,excerpt=raw['description'][:180],cityExcerpts={c['id']:city_excerpt(raw['description'],c,config['cities']) for c in cities},
                           capturedAt=captured,publishedAt=datetime.fromtimestamp(raw['publishedTimestamp']/1000).astimezone().isoformat() if raw.get('publishedTimestamp') else None,
                           origin='cdp',crossCity=len(cities)>1,suspectedAd=any(w in text for w in config['excludePatterns']),approximate=any(re.search('[万亿wWkKmM+]',str(raw.get(k,''))) for k in count),
                           evidenceFile=str(path.relative_to(ROOT)).replace('\\','/'),query=query)
                    records[nid]=n;added.append(nid);print(json.dumps({'id':nid,'title':n['title']},ensure_ascii=False),flush=True)
                    data.update(notes=list(records.values()),lastAttempt=attempt);save(data)
                closer=page.locator('div.close-circle')
                if not closer.count() or not closer.first.is_visible():raise RuntimeError('Normal note close control unavailable')
                closer.first.click();page.wait_for_timeout(700);time.sleep(1.0)
            attempt.update(status='complete',finishedAt=now(),message=f'已从用户正常可访问的新搜索页收录 {len(added)} 篇新笔记。')
        except AccessBlocked as exc:
            attempt.update(status='blocked',code=exc.code,message=str(exc));print(str(exc),flush=True)
        finally:
            data.update(notes=list(records.values()),lastAttempt=attempt);save(data)
            (ROOT/'city-research'/'visible-search-run.json').write_text(json.dumps(dict(attempt=attempt,added=added),ensure_ascii=False,indent=2),encoding='utf-8')
            b.close()
    print('New notes:',len(added),flush=True)
if __name__=='__main__':run()
