from pathlib import Path
ROOT=Path(__file__).parent
p=ROOT/'itinerary-ui.html';s=p.read_text(encoding='utf-8')
s=s.replace('也不含园内驾驶、停车拍照、餐饮和新增项目支线。','停车拍照、餐饮、游玩及未列入主线的支线另计；10月4日已含红豆坡与一目九岭的园内驾驶。')
p.write_text(s,encoding='utf-8')
p=ROOT/'activity_render.py';s=p.read_text(encoding='utf-8').replace('游览、餐饮、酒店接驳与景区内部驾驶另计','游览、餐饮、酒店接驳及未列入主线的景区内部驾驶另计')
p.write_text(s,encoding='utf-8')
