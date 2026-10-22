import json,html,csv
from pathlib import Path
ROOT=Path(__file__).parent
DATA=json.loads((ROOT/'activities.json').read_text(encoding='utf-8'))
def render_day(day):
    d=DATA['days'][day-1]
    parts=[f'<div class="activities"><h3>游玩顺序 · {html.escape(d["theme"])}</h3><p class="note"><b>优先级：</b>{html.escape(d["priority"])}</p><p class="note">{html.escape(d["schedule"])}</p>']
    for a in d['items']:
        refs=[]
        for key in a['sources']:
            s=DATA['sources'][key]
            refs.append(f'<a href="{html.escape(s["url"])}" target="_blank" rel="noopener">{html.escape(s["name"])}</a>' if s['url'] else html.escape(s['name']))
        parts.append(f'<details><summary><span class="priority">{html.escape(a["level"])}</span> {a["order"]}. {html.escape(a["name"])} <span class="activity-time">{html.escape(a["time"])}</span></summary><p>{html.escape(a["detail"])}</p><p class="note">车程口径：{html.escape(a["drive"])}</p>'+ ('<p class="note">参考：'+'；'.join(refs)+'</p>' if refs else '')+'</details>')
    parts.append(f'<p class="note"><b>时间不足时：</b>{html.escape(d["cut"])}</p></div>')
    return ''.join(parts)

def write_guide():
    summary=json.loads((ROOT/'daily-summary.json').read_text(encoding='utf-8'))
    from effective_routes import load_effective_routes
    routes=load_effective_routes()
    total_km=sum(s['distance'] for s in routes['segments'] if s['day'])/1000
    total_minutes=int(sum(s['duration'] for s in routes['segments'] if s['day'])/60+.5)
    txt=['# 呼伦贝尔森林北线：每日游玩与优先级','', '2026年10月2日早晨海拉尔出发，10月7日15:00前海拉尔还车。全程自驾。', '',DATA['basis'],'','**推荐排序：** '+' > '.join(DATA['ranking']),'','每一天按游玩先后排列；“优先”尽量保留，“推荐”有时间安排，“可选”可以删，“替换”和“二选一”不叠加。游玩时长为规划建议，并非已确认的营业或项目时长。','', f'**车程口径：** 10/4–10/5路线于2026-10-04用高德更新；10/3路线为2026-10-03查验；其余主线为2026-09-06查询，10/5—10/7采用七卡过夜方案；合计{total_km:.1f}公里、{total_minutes//60}小时{total_minutes%60:02d}分。仅为主线基础驾驶，游览、餐饮、酒店接驳及未列入主线的景区内部驾驶另计。','', '| 日期 | 基础里程 | 基础驾驶 | 住宿 |','|---|---:|---|---|']
    for s in summary:txt.append(f'| 10/{s["day"]+1} | {s["km"]}公里 | {s["duration"]} | {s["stay"]} |')
    rows=[]
    for d,s in zip(DATA['days'],summary):
        txt+=['',f'## {d["date"]}：{d["theme"]}','',f'**住宿：** {s["stay"]}。**基础驾驶：** {s["duration"]}。','',f'**优先级：** {d["priority"]}','',d['schedule'],'']
        if d.get('notice'):txt += ['**开放提醒：** '+d['notice'],'']
        for meal in d.get('meals',[]):
            txt += ['**餐饮：'+meal['name']+'｜'+meal['time']+'**','',meal['detail'],'']
            rows.append([d['date'],'餐饮','参考',meal['name'],meal['time'],meal['detail'],'见当天高德分段查验',s['stay']])
        for a in d['items']:
            txt += [f'{a["order"]}. **[{a["level"]}] {a["name"]}｜{a["time"]}**','',f'   {a["detail"]}','',f'   车程口径：{a["drive"]}','']
            rows.append([d['date'],a['order'],a['level'],a['name'],a['time'],a['detail'],a['drive'],s['stay']])
        txt += [f'**删减顺序：** {d["cut"]}']
    txt+=['','## 参考资料','', '第一份视频侧重路线与景点；第二份视频侧重使鹿文化、界河与家庭体验。小红书原帖的路况、价格和时刻表属于作者当时的经历；本次不沿用其中趁无人拦进入封闭道路的做法。官方景观与文化介绍也不等于2026年国庆营业保证。','']
    for s in DATA['sources'].values():
        txt.append(f'- [{s["name"]}]({s["url"] or s.get("file", "")})')
    (ROOT/'daily-activities.md').write_text('\n'.join(txt)+'\n',encoding='utf-8')
    with (ROOT/'daily-activities.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['日期','游玩顺序','优先级','项目','建议时长','具体玩法','车程口径','住宿']);w.writerows(rows)

if __name__=='__main__':write_guide()
