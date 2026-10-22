"""Add the researched October 4 options while preserving saved activity indexes."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
path=ROOT/'activities.json'
data=json.loads(path.read_text(encoding='utf-8'))
sources={
 'day3-selfdrive':('6ab928f0000000000a020cd0','小红书 · 9月27日公园自驾：红豆坡与一目九岭'),
 'day3-rafting-short':('6abd1b580000000012034cc9','小红书 · 9月30日发布：白鹿岛短线漂流体验'),
 'day3-rafting-long':('6aba1746000000001403af31','小红书 · 9月28日发布：漂流长短线与等候体验'),
 'day3-train-stops':('6ab78d3600000000140390ab','小红书 · 9月27日小火车：每站下车约4小时'),
}
notes={}
for p in (ROOT/'route-research-20261003').glob('*.json'):
    n=json.loads(p.read_text(encoding='utf-8')).get('note',{})
    if n.get('id'):notes[n['id']]=n
for k,(note_id,name) in sources.items():
    data['sources'][k]={'name':name,'url':notes[note_id]['url']}
d=data['days'][2]
d.update(theme='红豆坡 · 一目九岭 → 白鹿岛',
 priority='上午以红豆坡＋一目九岭自驾两站为主，小火车作为替换；下午白鹿岛看河湾，短线漂流视开行和天气决定。',
 schedule='按开园时间入园，上午红豆坡＋一目九岭，午餐后去白鹿岛看河湾。若短线漂流开行且天气合适，用它替换一部分河畔散步；含短漂全日建议6–8小时。',
 notice='公园自驾两站与完整小火车体验二选一，不叠加整套游览。高德算出园内路线不代表当天允许自驾通行，入口先确认；漂流以当天开行、末班和接驳安排为准。',
 noticeSources=['day3-selfdrive','day3-rafting-short'],
 cut='时间紧时保留红豆坡或一目九岭其中一处，再去白鹿岛。漂流不开或天气不合适，就看河湾、短走；不再叠加小火车与长线漂流。')
items=d['items'][:4]
items[0].update(name='公园自驾：红豆坡＋一目九岭',time='含两段园内转场约2–2.5小时',poi='红豆坡',
 detail='先在红豆坡落叶松林步道慢走拍照，建议30–45分钟；再到一目九岭步行登观景台，看层叠林海，建议45–60分钟。这些停留时间是规划预算。时间紧不走需折返停车点的猎人之路；到入口先确认当天自驾开放线路。两处都已标在地图上，可点击各点查看。',
 drive='高德10/3 08:53–08:56：莫尔道嘎镇政府 → 森林公园停车场12.7公里、18分20秒；停车场 → 红豆坡10.2公里、16分55秒；红豆坡 → 一目九岭6.7公里、10分42秒。园内两段驾驶已纳入当天主线，不再另加。',
 sources=['day3-selfdrive','park'])
items[1].update(name='森林小火车：替换上午自驾',time='选站预留2–3小时；全站可达4小时',poi='森林公园停车场',
 detail='喜欢火车或不想多走路时，用小火车替换红豆坡＋一目九岭自驾两站。可重点选择第一站登高、第三站溪畔；近期亲历帖每站都下用了约4小时，排队也可能挤占白鹿岛下午时间。车次、站点和末班以现场为准，不去铁轨拍照。',
 drive='高德10/3 08:53：采用小火车方案时，从森林公园停车场 → 白鹿岛酒店停车场89.8公里、1小时24分。镇区经公园停车场到白鹿岛的完整路线102.6公里、1小时44分06秒，不含乘车和等候。',
 sources=['day3-train-stops','forest'])
items[2].update(poi='白鹿岛酒店停车场',
 drive='高德10/3 08:56：一目九岭 → 白鹿岛酒店停车场79.8公里、1小时17分46秒。终点是酒店停车场，不是观景台；到实际观景处的接驳尚未核查。')
items[3].update(poi='白鹿岛酒店停车场',level='可选',
 detail='沿当天开放的林间或河畔步道慢走。若安排短线漂流，这项可缩短或取消；不把观景、散步、漂流都排成必须完成。',
 drive='仅安排停车后在开放区域步行；未给出酒店到独立步道入口的驾车时间。')
items.append(dict(order=5,level='可选',name='白鹿岛短线漂流',time='连准备预留1.5–2小时',poi='白鹿岛漂流',
 detail='近期两篇亲历帖都描述短线船上约1小时，偏慢漂看河流和森林；连准备、等候预留1.5–2小时。长线有约2.5小时体验，不建议再叠加。先问当天是否开行、末班、短线终点与回程接驳；穿保暖衣物并按工作人员要求穿救生衣。价格按现场公示，不把旧帖报价当承诺。',
 drive='高德10/3 08:56：白鹿岛酒店停车场 → 白鹿岛漂流POI 1.6公里、4分41秒。仅为单程到导航点，未计入主线总里程；实际登船入口、下船点和回程接驳尚未核查，不按单程翻倍估算。',
 sources=['day3-rafting-short','day3-rafting-long']))
d['items']=items
data['updated']='2026-10-03'
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated day 3: five activities; original four saved indexes preserved')
