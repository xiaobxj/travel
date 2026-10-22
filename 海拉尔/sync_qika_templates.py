"""One-time, idempotent alignment of UI sources with the Qika itinerary."""
from pathlib import Path

ROOT = Path(__file__).parent
def replace(name, pairs):
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    for old, new in pairs:
        if new in text:
            continue
        if old not in text and new not in text:
            raise ValueError(f'Missing source in {name}: {old[:60]}')
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

replace('itinerary-ui.html', [
    ("'白鹿岛','临江','额尔古纳'", "'白鹿岛','七卡','额尔古纳'"),
    ('晨光之后，慢游临江','沿界河慢行，住进七卡'),
    ("4:['白鹿岛酒店停车场','临江','临江','临江','临江'],5:['室韦','七卡',null,'黑山头']", "4:['白鹿岛酒店停车场','临江','室韦','九卡观景点','七卡'],5:['七卡',null,'黑山头','额尔古纳']"),
    ('976.9','__TOTAL_KM__'), ('14 小时 57 分钟','__TOTAL_TIME__'), ('14h 57m','__TOTAL_SHORT__'),
])
replace('lodging-template.html', [
    ('10/5 临江','10/5 七卡'),
    ('主行程仍以原来五个住宿城镇与高德代表点计时。这里的住宿参考不改变地图、日期、收藏、打卡或既有路线。',
     '主行程已改为10/5七卡附近过夜、10/6额尔古纳过夜。地图以七卡村内代表点计时；本页提供具体住宿候选。'),
])
replace('activity_render.py', [
    ("    txt=['# 呼伦贝尔森林北线", "    routes=json.loads((ROOT/'amap-routes.json').read_text(encoding='utf-8'))\n    total_km=sum(s['distance'] for s in routes['segments'] if s['day'])/1000\n    total_minutes=int(sum(s['duration'] for s in routes['segments'] if s['day'])/60+.5)\n    txt=['# 呼伦贝尔森林北线"),
    ("'**车程口径：** 沿用2026-09-06高德核查；合计976.9公里、14小时57分，仅为原主线基础转场。新增景点、具体餐厅与酒店接驳、景区内部驾驶未全部计入，不能把新增项目都叠加后继续声称总车程不变。'",
     "f'**车程口径：** 2026-09-06高德核查，10/5—10/7已按七卡过夜方案重新查询；合计{total_km:.1f}公里、{total_minutes//60}小时{total_minutes%60:02d}分。仅为主线基础驾驶，游览、餐饮、酒店接驳与景区内部驾驶另计。'"),
])
replace('make_map.py', [
    ("'临江村','额尔古纳市区'", "'七卡村附近（具体民宿待选）','额尔古纳市区'"),
    ("'临江':4", "'七卡':4"),
    ('当前推荐路线约126公里；指定经莫尔道嘎绕行约183公里。道路开放仍需临行核实。','经临江、室韦、九卡到七卡过夜；如白鹿岛至临江需绕莫尔道嘎，车程另加。'),
    ('已分段约束室韦、九卡观景点、七卡、黑山头，不能替代当日通行确认。','七卡出发，经黑山头至额尔古纳；观景、用餐及马场支线另计。'),
    ('10/5推荐路线驾驶留2.5–3小时，绕行留3.5–4小时；10/6驾驶留4.5–5小时；','10/5主线驾驶留4–4.5小时，如白鹿岛至临江绕行另加；10/6驾驶留2.5–3小时；'),
])
