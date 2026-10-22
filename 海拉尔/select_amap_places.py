"""Reviewed POI ids. Reject ambiguous branches, false keyword hits and closures."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
selections=[]
def yes(slug,pid,reason,kind='exact'):
    selections.append(dict(id=slug,poiId=pid,reason=reason,kind=kind))
def no(slug,reason):selections.append(dict(id=slug,poiId=None,reason=reason))
for row in '''hailaer-lublu|B0FFGC4212
hailaer-shaomai|B0FFIQSRS4
hailaer-laoyang|B0K65RH9CV
hailaer-zhao|B0GRRAJ1DZ
hailaer-bread|B0FFKT53GY
hailaer-nogoon|B0J3HZNFNB
hailaer-gogo|B0K66MQXRC
hailaer-shenzaki|B0JUCRCPJQ
hailaer-cliff|B0KRTLT57J
hailaer-museum|B0HK9D2MNE
hailaer-new-yexue|B0J33UUWU3
hailaer-new-yuanfang|B0K6U7WM7R
hailaer-new-petersburg|B0FFH0CJ5O
morigle-new-qushui|B0JRFUNGC1
morigle-new-tuga|B0FFKV4E41
morigle-new-mabeishan|B0J1JCY3KN
eerguna-shuncheng|B0FFGP0R0B
eerguna-xing le|B0FFKUX31D
eerguna-kerulen|B0FFFGOZ1L
eerguna-mengguyuan|B01D600J5B
eerguna-deli|B0FFKYW1J6
eerguna-tieshan|B0FFFA62TL
eerguna-xiaoguo|B0HDMPSVBX
eerguna-hedian|B0KKO130FW
eerguna-new-fuji|B0JRJHBKLS
eerguna-new-mingyuan|B0FFG7D3VM
genhe-kaimenhong|B0FFIH7SU0
genhe-shourong|B0FFHEF0TK
genhe-yijiaren|B0JRGZZD3R
genhe-zhengyi|B0GRMC0Y1G
genhe-market|B0FFHEZLBV
genhe-new-shouwang|B0K2OO88X3
aoluguya-new-museum|B01D601K21
deerbur-guangyuan|B0FFKVX1PO
mordaga-new-longshan|B0FFG8YHW4
bailudao-view|B0FFH04Q7P
bailudao-new-linxi|B0FFHE1DSE
linjiang-new-northhill|B0K2XZ7N9F
linjiang-new-shenxian|B0FFJACTYG
shiwei-two lambs|B0LR3CDKRV
shiwei-taliya|B0KRP7LJ49
shiwei-new-lvyou|B0FFG63UGN
shiwei-new-mumin|B0KUSYLAUV
jiuka-view|B0L367A2EJ
qika-lanni|B0JUVD9NJ0
qika-danjie|B0JUZBU06B
qika-laowu|B0KU3AGQAQ
qika-new-shubian|B0JDN56M8O
qika-new-caoyuan|B0FFKUKKZ1
heishantou-yipinxiang|B0FFI1N1ZR
heishantou-lamb ranch|B0JRZZ1EE9
heishantou-gushan|B01D6004QM
heishantou-new-laogao|B0HULZ3FCR'''.splitlines():
    slug,pid=row.split('|');yes(slug,pid,'人工对照高德返回名称、行政区、地址及行程位置，排除同名异地、周边误匹配和住宿类结果。')
yes('eerguna-new-baohualin','B0FFL1UK69','选定白桦林景区停车场入口作为驾车终点，园内游览另计。','entrance')
yes('aoluguya-reindeer','B0FFFGOOS1','明确使用原行程已采用的景区南门停车场，喂鹿与景区内接驳不计入驾车。','entrance')
yes('deerbur-deer','B0HR9U6CCO','对应得耳布尓兴安神鹿园停车点，距离计算到停车点，入园步行另计。','entrance')
yes('mordaga-forest','B0FFM0VY4Z','沿用原行程森林公园停车场，园内道路与小火车不是本次道路距离。','entrance')
yes('shiwei-new-aoluoqi','B0K1TSUGUV','采用奥洛契庄园游客中心西停车场作为驾车接入点。','entrance')
yes('qika-wulan','B0H2B7KSB8','使用乌兰山景区游客中心作为驾车接入点，山顶观景仍需园内接驳或步行。','entrance')
no('hailaer-nomintala','高德在海拉尔返回西大街、锦都会等分店，原帖未明确分店，暂不将品牌评价归给其中一家。')
no('hailaer-new-menggen','海拉尔有多家孟根楚鲁／孟根础鲁同名或近名茶食店，原帖缺少能确认分店的地址。')
no('genhe-chuantianjiao','未获得与正文“红招牌店”可明确对应的根河 POI。')
no('genhe-shengxianghe','高德为“鑫盛祥和”，原帖为“盛祥和”，地址未交叉确认，不自动当作同一家。')
no('genhe-new-kefir','高德为“开菲尔饮吧”，正文只写开菲尔酸奶，不能仅凭品类词认定商铺。')
yes('genhe-new-linzhongxian','B0FFH22ITR','新增实吃笔记明确写“根河林中鲜小串”，与高德幸福家园店名称及城市对应；其他简称烧烤的记录作为辅助证据。')
no('deerbur-memorial','返回的卡鲁奔营地、山、公园距小镇 40 公里以上，与原帖小镇饭馆内的纪念馆不符。')
yes('mordaga-hongjie','B0KU37EUGG','新增到店笔记写出“奥莉希亚红姐特色砂锅”全称，与高德莫尔道嘎店匹配，另有两篇实吃砂锅反馈。')
no('mordaga-hongzeyuan','本轮关键词查询未返回可对应的固定餐厅。')
no('mordaga-new-bawang','高德有多家铁锅炖，但原帖未给店名，不能从附近结果任挑一家套上好评。')
no('bailudao-restaurant','高德只查到白鹿岛酒店及停车场，没有独立餐厅 POI；餐厅证据保留但不纳入严格核点列表。')
no('linjiang-shilu','高德返回驶路部落精品民宿，地址在临江，可确认场所但未返回花园餐厅独立 POI；不以民宿坐标冒充餐厅入口。')
no('shiwei-tara','本轮查询未找到可对应室韦塔拉牧场餐厅的 POI。')
no('shiwei-mengwu','返回室韦蒙兀部落，未返回能核对到“蒙兀奶茶”的独立商铺。')
no('heishantou-risheng','高德名称为“日晟烤吧有间烤肉店”，与原帖冰煮羊火锅的经营内容不同，暂待核对。')
no('heishantou-sunset','有多个日落点和接驳入口，原帖混合免费点与收费点，尚不能把全部好评归到同一 POI。')
no('heishantou-bonfire','同名篝火搜索结果距黑山头约 106 公里，排除异地匹配。')
no('heishantou-new-youmu','高德明确标注“暂停营业”，不纳入当前推荐。')
no('heishantou-new-mazhi','返回其他马场和周边民宿，没有确切对应马之舞的结果。')
yes('deerbur-new-shanshan','B0IGCOJFO0','新帖明确得耳布尔姗姗馅饼，高德返回镇内清真姗姗馅饼店，名称、类型和所在小镇对应。')
no('deerbur-new-cold','“中国冷极碑”搜索结果与小镇地标的描述尚不能唯一对应，不把附近其他冷极地标代替原帖落点。')
for slug,pid in [
 ('genhe-new-xindingyuan','B0FFFGOPDH'),('mordaga-new-jiemei','B0FFFGP0DC'),
 ('mordaga-new-yajuan','B0H1X430OA'),('mordaga-new-jihe','B0IUCUZO3H'),
 ('shiwei-new-yogurt','B0K1XK2GQY'),('heishantou-new-yunxi','B0KU9CINYC'),
 ('heishantou-new-ziyu','B0FFFGOC7I'),('heishantou-new-mengniu','B0HUP5ODFY')]:
    yes(slug,pid,'本轮已读笔记明确写出店名和小镇，高德返回同名镇内商铺；检查行政区及地址，并排除远处同名分店。')
no('mordaga-new-hulaoda','高德仅在相邻咖啡馆与住宿的地址中提及胡老大，没有返回其独立餐厅 POI；不能用邻店坐标代替餐厅。')
Path(__file__).with_name('amap-place-selections.json').write_text(json.dumps(selections,ensure_ascii=False,indent=2),encoding='utf-8')
print('Reviewed',len(selections),'candidates; accepted',sum(bool(x['poiId']) for x in selections))
