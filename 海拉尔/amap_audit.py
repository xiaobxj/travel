import json, pathlib, requests, time, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).parent
KEY='8741c9533563fe28253346e1001404bd'
QUERIES=['海拉尔站','呼伦贝尔海拉尔机场','莫日格勒河游客中心','曲水云天','额尔古纳市政府','根河市政府','敖鲁古雅使鹿部落','莫尔道嘎镇政府','莫尔道嘎国家森林公园游客中心','莫尔道嘎国家森林公园入口','白鹿岛大酒店','太平村','临江村','室韦','九卡','七卡','黑山头镇政府','得耳布尔']
def api(endpoint,params):
    r=requests.get('https://restapi.amap.com/'+endpoint,params={'key':KEY,**params},timeout=30)
    r.raise_for_status();d=r.json()
    if d.get('status')!='1':raise RuntimeError(str({k:d.get(k) for k in ['status','info','infocode']}))
    return d
if __name__=='__main__':
    results={}
    for q in QUERIES:
        d=api('v3/place/text',{'keywords':q,'city':'150700','citylimit':'true','offset':5,'extensions':'base'})
        results[q]=[{k:p.get(k) for k in ['id','name','location','address','adname','type']} for p in d.get('pois',[])]
        print(q,json.dumps(results[q],ensure_ascii=False),flush=True)
        time.sleep(.25)
    (ROOT/'amap-pois.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
