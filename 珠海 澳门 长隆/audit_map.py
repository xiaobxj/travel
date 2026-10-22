"""Cache AMap POIs and route evidence, reusing the locally configured REST credential."""
import sys, json, time, argparse
from pathlib import Path
sys.path.insert(0, r'D:\travel\海拉尔')
from amap_audit import api
ROOT = Path(__file__).parent
OUT = ROOT / 'evidence'
OUT.mkdir(exist_ok=True)

QUERIES = [
 ('zhuhai_station','珠海站','珠海'),('gongbei','拱北口岸','珠海'),
 ('postoffice','爱情邮局','珠海'),('fishergirl','珠海渔女','珠海'),
 ('xianglu','香炉湾沙滩','珠海'),('opera','珠海大剧院','珠海'),
 ('hotpot','十六潮','珠海'),('diandude','点都德','珠海'),('xinhaili','新海利海鲜城','珠海'),
 ('barrier','关闸边检大楼','澳门'),('senado','议事亭前地','澳门'),
 ('rosary','玫瑰圣母堂','澳门'),('stpaul','大三巴牌坊','澳门'),
 ('cunha','官也街','澳门'),('venetian','澳门威尼斯人','澳门'),('londoner','澳门伦敦人','澳门'),
 ('galorest','海湾餐厅','澳门'),('lordstow','安德鲁饼店','澳门'),
 ('ocean','珠海长隆海洋王国','珠海'),('spaceship','长隆飞船乐园','珠海'),
 ('penguinhotel','珠海长隆企鹅酒店','珠海'),('spaceshiphotel','珠海长隆飞船酒店','珠海'),
 ('circushotel','珠海长隆马戏酒店','珠海'),('hengqinbayhotel','珠海长隆横琴湾酒店','珠海'),
 ('yinghaihotel','长隆迎海酒店公寓','珠海'),('miaojirest','妙记潮汕菜','珠海'),
 ('whaleshark','长隆海洋王国鲸鲨馆','珠海'),('penguinhall','长隆海洋王国企鹅馆','珠海'),
 ('parrotcoaster','鹦鹉过山车','珠海'),('belugatheater','白鲸剧场','珠海'),
 ('undersearest','海底餐厅','珠海'),('spaceshipfood','飞船美食广场','珠海')]

def run_pois():
    found = {}
    for key, query, city in QUERIES:
        path = OUT / ('poi-' + key + '.json')
        try:
            if path.exists(): data = json.loads(path.read_text(encoding='utf-8'))
            else:
                data = api('v3/place/text',{'keywords':query,'city':city,'citylimit':'true','offset':5,'extensions':'all'})
                path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
                time.sleep(1.2)
            found[key] = [{k:p.get(k) for k in ['id','name','address','location','type','business_area']} for p in data.get('pois',[])]
            print(key, json.dumps(found[key],ensure_ascii=False),flush=True)
        except Exception as exc: print(key, type(exc).__name__, str(exc)[:150],flush=True)
    (ROOT/'poi-options.json').write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__': run_pois()
