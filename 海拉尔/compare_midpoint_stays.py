"""Check midpoint overnight options without replacing the accepted route."""
import json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from amap_audit import api

ROOT=Path(__file__).parent

def find(q):
    d=api('v3/place/text',{'keywords':q,'city':'150784','citylimit':'true','offset':8,'extensions':'base'})
    return q,[{k:p.get(k) for k in ['id','name','location','address','type']} for p in d.get('pois',[])]

if __name__=='__main__':
    queries=['恩和俄罗斯族民族乡人民政府','七卡 住宿','九卡 住宿','恩和 酒店']
    results={}
    for q in queries:
        time.sleep(1.1)
        key,value=find(q)
        results[key]=value
    (ROOT/'midpoint-stay-pois.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False))
