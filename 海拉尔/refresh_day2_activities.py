"""Apply the October 3 research to the existing itinerary source."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
path = ROOT / 'activities.json'
data = json.loads(path.read_text(encoding='utf-8'))
old = data['days'][1]
bridge = next(x for x in old['items'] if '守望桥' in x['name'])
aoluguya = next(x for x in old['items'] if '敖鲁古雅' in x['name'])
notes = {}
for p in (ROOT / 'route-research-20261003').glob('*.json'):
    raw = json.loads(p.read_text(encoding='utf-8'))
    n = raw.get('note', {})
    if n.get('id'):
        notes[n['id']] = n
    elif n.get('url'):
        notes[n['url'].split('/explore/')[-1].split('?')[0]] = n

sources = {
    'day2-juele': ('6abfd4b100000000180154a8', '小红书 · 10月2日觉乐亲访：喂鹿约1小时'),
    'day2-juele-guide': ('6aaa6dfa000000002601ce9b', '小红书 · 9月16日觉乐游玩记录'),
    'day2-road': ('6abfc384000000001403932d', '小红书 · 近期根白线：落叶与初雪提醒'),
    'day2-road-walk': ('6abcf5190000000013019618', '小红书 · 9月27日根白公路与龙山实走'),
    'day2-station': ('6ab79e38000000000a02514d', '小红书 · 9月26日得耳布尔小镇与车站'),
    'day2-meal': ('6a7b23840000000022032455', '小红书 · 8月得耳布尔用餐记录（历史体验）'),
    'day2-longshan': ('6ab4b79f0000000018028366', '小红书 · 9月24日龙山登高计时记录'),
    'day2-longshan-road': ('6ab6565b000000000b007b40', '小红书 · 9月25日龙山后山驾车路况'),
    'day2-deer-closed': ('6abb2b1b000000001c00d66e', '小红书 · 9月29日神鹿园现场未能进入'),
    'day2-deer-road': ('6ab7290d000000001b033dde', '小红书 · 9月26日神鹿园道路受阻'),
}
for key, (note_id, label) in sources.items():
    assert note_id in notes, note_id
    data['sources'][key] = {'name': label, 'url': notes[note_id]['url']}

def item(name, level, time, detail, drive, sources, poi=None):
    return dict(name=name, level=level, time=time, detail=detail, drive=drive, sources=sources, poi=poi)

items = [
    item('觉乐驯鹿园：林间喂鹿', '优先', '60–90分钟',
         '建议把这里作为当天的喂鹿点，与敖鲁古雅二选一。10月2日亲访笔记记录游玩约1小时、门票35元、苔藓20元，价格和营业以现场为准。按工作人员指引互动，留意鹿角。若已在敖鲁古雅完成喂鹿，可直接跳过。',
         '高德10/3 08:33：根河市政府 → 觉乐16.0公里，18分41秒（约19分钟）。本次核到园区POI，未核实独立停车入口。',
         ['day2-juele', 'day2-juele-guide'], '觉乐驯鹿园'),
    item('根白公路：森林沿途短停', '优先', '合计45–75分钟',
         '把风景留给行车途中，在允许停车的位置挑2–3处短停。近期笔记已有落叶与初雪，现场可能是疏林秋色，不保证整片金黄。未核实独立观景停车场，不在行车道或铁路上拍照。这里的时长仅为下车停留。',
         '高德10/3 08:33：觉乐 → 得耳布尔镇政府63.0公里，1小时02分03秒；得耳布尔 → 莫尔道嘎镇政府44.7公里，48分37秒。拍照停留另加。',
         ['day2-road', 'day2-road-walk'], '得耳布尔'),
    item('得耳布尔镇：午餐与补给', '用餐', '45–60分钟',
         '在镇上吃午餐、休息，再继续去莫尔道嘎。旧笔记提到姗姗馅饼，可作现场找店线索；具体餐厅还未确定，按当天营业和停车方便程度选择。',
         '路线途经点采用得耳布尔镇政府。具体餐厅接驳未核查，不计入已核主线驾驶时间。',
         ['day2-meal'], '得耳布尔'),
    item('得耳布尔站：站前外观', '可选', '10–15分钟',
         '对林区铁路感兴趣时，顺路看站房外观、在允许通行的站前街道散步。不承诺进入站台，也不安排铁轨拍照。没有兴趣可跳过。',
         '高德10/3 08:30：镇政府 → 车站1.1公里，2分42秒；08:35车站 → 莫尔道嘎45.6公里，51分52秒。整线加车站比基础方案多2.9公里、9分29秒驾驶，连停留共多留20–25分钟。',
         ['day2-station'], '得耳布尔站'),
    item('龙山公园：抵达后步行登高', '可选', '短走45–75分／登顶往返90–120分',
         '到莫尔道嘎后看天气与体力决定。时间充裕可走完整登高路线，时间少就短走后折返；两种时长不叠加。近期实走笔记支持完整往返约1.5–2小时。建议步行，不照搬后山驾车登顶路线。',
         '高德10/3 08:35：莫尔道嘎镇政府 → 龙山公园POI 1.3公里，3分17秒，仅到公园导航点，不含上山。独立步行入口尚未核实。',
         ['day2-longshan', 'day2-road-walk', 'day2-longshan-road'], '龙山公园'),
]
aoluguya.update(level='替换', poi='敖鲁古雅停车场',
    detail='更想了解使鹿文化时，用敖鲁古雅替换觉乐，建议文化展陈、鹿苑与园内接驳共留2.5–3小时。两处喂鹿不必都去；选此方案时缩减龙山或沿途停留。博物馆与鹿苑入口、票务以现场为准。',
    drive='高德10/3 08:30：根河市政府 → 敖鲁古雅停车场3.9公里，6分41秒；敖鲁古雅 → 得耳布尔81.2公里，1小时20分19秒。经敖鲁古雅、得耳布尔到莫尔道嘎整线130.0公里、2小时16分23秒，不含游览。')
items.append(aoluguya)
bridge.update(level='可选', poi=None, drive='仅在住宿附近、方便步行时安排；酒店到桥的驾车接驳尚未核查，未给出车程。')
items.append(bridge)
for i, entry in enumerate(items, 1):
    entry['order'] = i
data['updated'] = '2026-10-03'
data['days'][1] = dict(day=2, date='10/3', theme='觉乐驯鹿 → 根白森林 → 莫尔道嘎',
    priority='觉乐与根白公路为重点；得耳布尔午餐，车站和龙山按兴趣增减。敖鲁古雅是觉乐的替换方案。',
    schedule='早餐后从根河出发，觉乐喂鹿 → 根白公路短停 → 得耳布尔午餐 → 车站（可选）→ 莫尔道嘎 → 龙山（可选）。含车站和龙山短走，全日建议6–8小时；登顶或改敖鲁古雅需重新取舍。',
    notice='兴安神鹿园暂不排入固定行程：9月26日和29日亲访记录反馈道路受阻／未能进入，尚无可靠的恢复开放证明。不是认定今天必定关闭；确认开放后再考虑。',
    noticeSources=['day2-deer-road', 'day2-deer-closed'], items=items,
    cut='先取消站前和龙山；已喂过鹿则跳过觉乐。保留根白公路与正常午餐，森林公园和白鹿岛仍放在次日。')
data['ranking'] = ['根白公路沿途森林', '白鹿岛河湾与林间步行', '莫尔道嘎森林公园', '觉乐驯鹿（敖鲁古雅文化为替换）', '临江村与界河短逛', '室韦至黑山头卡线', '莫日格勒河曲水观景']
path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Updated day 2: 7 activities, 10 linked note sources')
