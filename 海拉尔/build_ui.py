"""Build the self-contained itinerary UI from the audited route data."""
import json, base64, math
from pathlib import Path

ROOT = Path(__file__).parent

def build():
    from build_lodging import build as build_lodging
    build_lodging()
    from effective_routes import load_effective_routes
    routes=load_effective_routes(ROOT)
    activities=json.loads((ROOT/'activities.json').read_text(encoding='utf-8'))
    summary=json.loads((ROOT/'daily-summary.json').read_text(encoding='utf-8'))
    def project(location):
        lon,lat=map(float,location.split(','))
        def y(a): return (1-math.asinh(math.tan(math.radians(a)))/math.pi)/2*65536
        return [round(512+(lon-120.4)/360*65536,3),round(512+y(lat)-y(50.6),3)]
    pois={name:{**p,'xy':project(p['location'])} for name,p in routes['pois'].items()}
    segments=[]
    for i,r in enumerate(routes['segments']):
        points=[]
        for s in r['path']['steps']:
            points.extend(project(p) for p in s.get('polyline','').split(';') if p)
        segments.append({k:v for k,v in r.items() if k!='path'}|{'id':i,'points':points})
    guide=json.loads((ROOT/'city-guide-config.json').read_text(encoding='utf-8'))
    collected=json.loads((ROOT/'city-notes.json').read_text(encoding='utf-8'))
    guide.update(collected)
    from build_city_recommendations import build as build_recommendations
    guide['recommendations']=build_recommendations()
    for item in guide['recommendations']['items']:
        place=item.get('placeCheck',{})
        if place.get('status')=='verified':place['xy']=project(place['poi']['location'])
    data={'pois':pois,'segments':segments,'summary':summary,'activities':activities,'queried_at':routes['queried_at'],'cityGuide':guide,
          'day2Research':routes['day2Research'],'day3Research':routes['day3Research'],'day4Research':routes['day4Research'],'routesUpdate':routes['routesUpdate']}
    page=(ROOT/'itinerary-ui.html').read_text(encoding='utf-8')
    total_km=sum(s['distance'] for s in routes['segments'] if s['day'])/1000
    total_minutes=int(sum(s['duration'] for s in routes['segments'] if s['day'])/60+.5)
    page=page.replace('__TOTAL_KM__',f'{total_km:.1f}').replace('__TOTAL_TIME__',f'{total_minutes//60}小时{total_minutes%60:02d}分').replace('__TOTAL_SHORT__',f'{total_minutes//60}h {total_minutes%60:02d}m')
    page=page.replace('<h2>这份行程怎么用</h2>', '<h2>这份行程怎么用</h2><p style="margin:0 0 18px"><a class="quiet" id="lodgingLink" href="lodging-guide.html" target="_blank" rel="noopener">⌂ 五晚住宿参考 ↗</a></p>')
    page=page.replace('</style>', (ROOT/'interactions.css').read_text(encoding='utf-8')+'\n</style>')
    page=page.replace('</body>', '<script>\n'+(ROOT/'interactions.js').read_text(encoding='utf-8')+'\n</script></body>')
    page=page.replace('</style>', (ROOT/'city-guide.css').read_text(encoding='utf-8')+'\n</style>')
    page=page.replace('</body>', '<script>\n'+(ROOT/'city-guide.js').read_text(encoding='utf-8')+'\n</script></body>')
    page=page.replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/'))
    page=page.replace('__BASEMAP__',base64.b64encode((ROOT/'amap-basemap.png').read_bytes()).decode())
    (ROOT/'itinerary-map.html').write_text(page,encoding='utf-8')
    return page

if __name__=='__main__':
    build()
    print(f'Built {ROOT / "itinerary-map.html"}')
