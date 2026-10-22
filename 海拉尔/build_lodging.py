"""Render a separate lodging guide with sources and user-opened search links."""
from pathlib import Path
from html import escape as esc
from urllib.parse import urlencode
import json, csv

ROOT=Path(__file__).parent

def build():
    data=json.loads((ROOT/'lodging-data.json').read_text(encoding='utf-8'))
    cards=[]
    rows=[]
    export_rows=[]
    for n in data['nights']:
        summary=''.join(f'<div><a href="#hotel{n["day"]}-{i}">{i:02d} {esc(h["name"])}</a>{" <small>（改住莫尔道嘎）</small>" if h.get("scope")=="route-change" else ""}</div>' for i,h in enumerate(n['hotels'],1))
        rows.append(f'<tr><td><a href="#night{n["day"]}">{n["date"]}<br><b>{n["city"]}</b></a><br><small>5 个选择</small></td><td>{n["area"]}</td><td>{summary}</td></tr>')
        local_cards=[]
        fallback_cards=[]
        for i,h in enumerate(n['hotels'],1):
            is_fallback=h.get('scope')=='route-change'
            impact=f'<p class="route-impact">{esc(h["routeImpact"])}</p>' if is_fallback else ''
            card=f'<article class="hotel {"fallback-hotel" if is_fallback else "local-hotel"}" id="hotel{n["day"]}-{i}"><small>{i:02d} · {esc(h["rank"])}</small><h3>{esc(h["name"])}</h3><p class="address">{esc(h["address"])}</p><p>{esc(h["why"])}</p>{impact}<p class="note">选房留意：{esc(h["caution"])}</p><a class="link" href="{esc(h["url"])}" target="_blank" rel="noopener">查看地址、房型及来源 ↗</a></article>'
            (fallback_cards if is_fallback else local_cards).append(card)
            export_rows.append([n['date'],n['city'],i,'改住莫尔道嘎，需重算路线' if is_fallback else '当晚当地候选',h['name'],h['address'],h['why'],h['caution'],h.get('routeImpact',''),h['url']])
        hotels='<div class="hotel-grid">'+''.join(local_cards)+'</div>'
        if fallback_cards:
            hotels+='<div class="fallback-section"><h3>改住莫尔道嘎 · 4 家备选</h3><p class="secondary">以下酒店均在莫尔道嘎镇，不在白鹿岛；选择其中一家需要另行调整 10/4—10/5 的路线。</p><div class="hotel-grid">'+''.join(fallback_cards)+'</div></div>'
        selection=f'<p class="selection-note">{esc(n["selectionNote"])}</p>' if n.get('selectionNote') else '<p class="selection-count">5 家当地候选 · 数字是比较顺序，不是平台评分排名</p>'
        searches=''.join(f'<a class="search" href="https://www.xiaohongshu.com/search_result?{esc(urlencode({"keyword":q,"source":"web_search_result_notes"}))}" target="_blank" rel="noopener">{esc(q)} ↗</a>' for q in n['keywords'])
        extra=n.get('extraSource')
        extra_html=f'<p class="source"><a href="{esc(extra["url"])}" target="_blank" rel="noopener">{esc(extra["name"])} ↗</a></p>' if extra else ''
        cards.append(f'''<section class="night" id="night{n['day']}"><div class="night-head"><span class="badge">0{n['day']}</span><div><small>{n['date']} · 第 {n['day']} 晚</small><h2>{n['city']} · {n['theme']}</h2></div></div><p class="area">建议住：{n['area']}</p><p>{n['reason']}</p><p class="secondary">{n['alternative']}</p>{selection}{hotels}<details><summary>这一晚怎么安排、订房要问什么</summary><p>{n['evening']}</p><p>{n['check']}</p>{extra_html}</details><details><summary>去小红书继续查住客实拍</summary><p class="secondary">以下是搜索入口，需在你自己的浏览器或 App 中打开；不是已核验的笔记或好评榜。</p><div class="searches">{searches}</div></details></section>''')
    template=(ROOT/'lodging-template.html').read_text(encoding='utf-8')
    page=template.replace('__INTRO__',esc(data['intro'])).replace('__ROWS__',''.join(rows)).replace('__NIGHTS__',''.join(cards))
    page=page.replace('</style>', '.selection-count{font-size:11px!important;color:var(--muted)}.selection-note,.route-impact{background:#fbf1e4;border:1px solid #e9d5b8;border-radius:8px;padding:12px;color:#856234}.fallback-section{border-top:1px dashed #d9c3a3;padding-top:22px;margin-top:25px}.fallback-section>p{font-size:12px;margin-top:7px}.fallback-hotel{background:#fffbf5;border-color:#e9dfcf}td small{font-size:10px;color:var(--muted)}td:last-child div{margin:5px 0}.hotel{scroll-margin-top:95px} </style>')
    page=page.replace('<button onclick="window.print()">打印</button>', '<a class="back" href="lodging-options.csv" download>下载对比表</a><button onclick="window.print()">打印</button>')
    (ROOT/'lodging-guide.html').write_text(page,encoding='utf-8')
    with (ROOT/'lodging-options.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['入住至离店','计划住宿地','比较顺序','位置类型','住宿名称','地址','适合原因','选房留意','路线影响','来源链接'])
        writer.writerows(export_rows)
    return page

if __name__=='__main__':
    build()
    print('Built D:/travel/lodging-guide.html')
