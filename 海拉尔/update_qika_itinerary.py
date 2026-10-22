"""Apply the user's Qika overnight choice to activity and lodging content."""
import json
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).parent

def update():
    def read(name):
        return json.loads((ROOT / name).read_text(encoding='utf-8'))
    def write(name, value):
        (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    activities = read('activities.json')
    summary = read('daily-summary.json')
    routes = read('amap-routes.json')
    def duration(origin, destination, via=None):
        from refresh_qika_routes import fmt
        return fmt(next(s['duration'] for s in routes['segments'] if s['from']==origin and s['to']==destination and s['via']==(via or [])))
    def item(order, level, name, time, detail, sources, drive):
        return dict(order=order, level=level, name=name, time=time, detail=detail, sources=sources, drive=drive)
    activities['ranking'][4] = '临江村与界河短逛'
    activities['sources']['qika-food'] = {'name':'高德：七卡餐饮落点及商户资料（2026-09-06）','url':'qika-food-pois.json'}
    activities['sources']['qika-stay'] = {'name':'卡伦小院：住客餐饮与住宿反馈','url':'https://jp.trip.com/hotels/eerguna-hotel-detail-110599512/ka-lun-xiao-yuan/'}
    activities['days'][3] = {
        'day':4, 'date':'10/5', 'theme':'临江午餐 → 北段卡线 → 七卡过夜',
        'priority':'临江短逛、九卡至七卡沿线观景为重点；室韦短停，白鹿岛晨景按天气安排。',
        'schedule':'09:00左右离开白鹿岛；约11:00到临江，午餐加短逛共1–1.5小时；室韦停20–30分钟，九卡至七卡分散停车观景；争取15:30–16:30到七卡入住，18:00左右晚餐。',
        'items':[
            item(1,'可选','白鹿岛晨景','30–45分钟','早餐前在住宿附近开放区域看晨光；不为等雾拖延出发。当天还要走北段卡线，09:00左右离开。',['video1','bailu'],f'至临江高德基础{duration("白鹿岛酒店停车场","临江")}；若需经莫尔道嘎绕行，则该段为{duration("白鹿岛酒店停车场","临江",["莫尔道嘎"])}，当天相应压缩停留。'),
            item(2,'优先','临江午餐＋村落界河短逛','合计60–90分钟','先吃午餐，再看木刻楞、村落与开放河岸。这次临江作为中午停留点，当天继续前往七卡；不安排临江入住、傍晚观景或次晨看雾。',['video1','video2','xhs'],'午餐与步行时间另计；临江至室韦已纳入当天主线。'),
            item(3,'推荐','室韦小镇与界河短停','20–30分钟','选择方便停车的一处街道或开放界河观景区短逛。与临江景色有重复，按兴趣停留，不进入口岸工作区域。',['video1','video2'],f'临江至室韦{duration("临江","室韦")}；室韦至九卡{duration("室韦","九卡观景点")}。'),
            item(4,'优先','九卡—七卡北段卡线观景','停车合计45–60分钟','按室韦→九卡→七卡逐段导航，在开放停车区看界河、河谷和草原。选2–3处短停，把傍晚留给七卡入住与休息。',['video1','xhs'],f'九卡至七卡{duration("九卡观景点","七卡")}；当天主线合计{summary[3]["km"]}公里、{summary[3]["duration"]}，停车拍照另加。'),
            item(5,'推荐','七卡入住、村内散步与晚餐','入住散步30–45分钟；晚餐约1小时','先办理入住，再在村内慢走。晚餐比较七卡戍边食府、草原美食餐厅或住宿自带餐厅；卡伦小院住客曾推荐羊肉面和野菜抱蛋，供应以当天菜单为准。订房时一并询问10/5晚餐与10/6早餐。',['qika-food','qika-stay'],'住宿先选七卡主街至卡伦小院一带，避免改住恩和镇中心；具体酒店、餐馆入口的短途接驳另计。')
        ],
        'cut':'先取消白鹿岛晨景、缩短室韦，再减少观景停车；保留正常午餐和七卡入住时间。若白鹿岛至临江需要绕行，按新导航增加车程，不追加老鹰嘴、奇乾或恩和。'
    }
    activities['days'][4] = {
        'day':5,'date':'10/6','theme':'七卡南段观景 → 黑山头 → 额尔古纳',
        'priority':'南段卡线慢看为重点；乌兰山观景与黑山头骑马二选一，下午回额尔古纳休息。',
        'schedule':'早餐后09:00左右从七卡出发；沿南段卡线观景，黑山头午餐；乌兰山与骑马最多选一项，15:00–15:30左右离开黑山头，争取16:30前到额尔古纳。',
        'items':[
            item(1,'优先','七卡早餐＋南段卡线观景','早餐30–45分钟；停车观景45–60分钟','早餐优先住宿自带餐食或二姐面馆，营业时间提前问清。沿七卡至黑山头方向行驶，挑开放停车区看河谷与草原，不再折返九卡和室韦。',['video1','xhs','qika-food'],f'七卡至黑山头基础{duration("七卡","黑山头")}；当天全程{summary[4]["km"]}公里、{summary[4]["duration"]}，观景与用餐另计。'),
            item(2,'二选一','乌兰山河湾观景','45–60分钟','偏爱风景摄影时考虑，先确认当日开放和入口。加入这一项就不安排骑马，避免重新把一天排满。',['video1'],'景区入口支线和内部接驳未计入主线；实际选定入口后再导航。'),
            item(3,'二选一','黑山头正规马场短体验','连准备约60分钟','偏爱参与式体验时选择这一项，提前约短时段，确认头盔、教练和实际骑乘时长。天气不适合则取消，午餐后从容返城。',['video1','video2'],'具体马场待选，支线另计；不安排2–3小时长线骑行。'),
            item(4,'推荐','黑山头午餐＋额尔古纳入住休息','午餐45–60分钟；入住后自由安排','在黑山头正常吃午餐，按预约把骑马放在午餐前或后。下午到额尔古纳，散步、晚餐并整理行李，确认次日还车门店。当天不追黑山头日落。',[],f'黑山头至额尔古纳{duration("黑山头","额尔古纳")}；市区餐厅与酒店接驳另计。')
        ],
        'cut':'有延误先取消乌兰山／骑马，再缩短观景停车；保留午餐和下午返城，不追加完整湿地游。'
    }
    activities['days'][5]['items'][0]['detail'] = f'整理行李，检查还车要求后出发。高德复查至海拉尔站约{duration("额尔古纳","海拉尔站")}，机场停车场约{duration("额尔古纳","机场停车场")}；实际还车门店尚未提供，仍按09:00出发、14:00到店预留时间。'
    write('activities.json', activities)
    lodging = read('lodging-data.json')
    pois = read('midpoint-stay-pois.json')['七卡 住宿']
    selected = [pois[i] for i in [0,1,2,3,5]]
    hotels = []
    whys = ['住客确认有自家餐厅，适合入住后就近吃饭；有供暖好评，也有隔音一般的反馈。',
            '高德地址明确在七卡屯，适合与木屋小院比较实际房间；名称带“恩和”，但不是恩和镇中心。',
            '位置在七卡村内，方便与主街餐馆搭配；已有住宿页面可核对房型。',
            '高德落点在七卡队主街附近，可作为比较房型与停车条件的备选；目前只核实位置。',
            '高德地址在七卡队，可作为村内另一家小院候选；目前只核实位置，未取得足够近期入住评价。']
    cautions = ['确认所订房型的整夜供暖、隔音、热水，以及10/5晚餐和10/6早餐；旧评价不保证当日供应。',
                '酒店名称不代表星级；索要实际房型视频，确认卫生、供暖、停车与入口。',
                '历史评价有仅电热毯、隔音一般的反馈，必须确认今年10月是否提供足够供暖。',
                '预订前核对营业、供暖、热水、停车和实拍；不把地图收录当作质量保证。',
                '核对入口及房型实拍，确认独立卫浴、整夜供暖和是否供餐。']
    for i,p in enumerate(selected):
        url = 'https://uri.amap.com/marker?' + urlencode({'position':p['location'],'name':p['name'],'src':'hulunbuir-itinerary','coordinate':'gaode','callnative':'0'})
        if i==0: url=activities['sources']['qika-stay']['url']
        if i==2: url='https://hotels.ctrip.com/hotels/78157918.html'
        hotels.append({'name':p['name'],'rank':'优先比较 · 住宿与餐饮' if i==0 else '备选 · 村内住宿','address':p['address'],'why':whys[i],'caution':cautions[i],'url':url,'scope':'local'})
    lodging['nights'][3] = {
        'day':4,'date':'10/5 → 10/6','city':'七卡村附近','theme':'分开两天车程，住在卡线中段',
        'area':'七卡村主街至卡伦小院一带；先比较供暖、隔音与停车，具体民宿待选',
        'reason':f'10/5由白鹿岛经临江、室韦、九卡到七卡，基础驾驶{summary[3]["duration"]}；10/6由七卡经黑山头到额尔古纳，基础驾驶{summary[4]["duration"]}。临江改为午餐短逛，北段卡线完整保留。',
        'alternative':'五家均为七卡村附近候选。先看实际房型和供暖，不把“恩和乡七卡”误订为恩和镇中心，也不要求每家都有江景。',
        'selectionNote':'5 家七卡附近候选 · 卡伦小院及阿丽莎有住宿评价参考；其余主要核实高德位置，尚未核实国庆房态、价格和服务质量。',
        'evening':'争取15:30–16:30入住，村内短逛，18:00左右晚餐。可比较七卡戍边食府、草原美食餐厅和住宿自家饭店；卡伦小院有羊肉面、野菜抱蛋的住客反馈，是否供应以当日为准。次日早餐后09:00左右出发。',
        'check':'订房时索要房型实拍、准确入口，确认整夜供暖、热水、隔音与停车；一并问清10/5晚餐菜单和10/6早餐时间。地图车程暂以七卡戍边食府代表村内落点，酒店接驳另计。',
        'keywords':['额尔古纳 七卡 民宿 十月 供暖','七卡 卡伦小院 入住','七卡 住宿 餐厅'],
        'hotels':hotels,
        'extraSource':{'name':'七卡餐饮：本次高德查询记录','url':'qika-food-pois.json'}
    }
    write('lodging-data.json', lodging)

if __name__ == '__main__':
    update()
