"""Research-only digest; deliberately does not modify itinerary product data."""
import json
from pathlib import Path
from datetime import datetime

out=Path(__file__).resolve().parent
root=out.parent
existing={x['id']:x for x in json.loads((out/'existing-food-evidence.json').read_text(encoding='utf8'))}

def food(ident, priority, minutes):
    item=existing[ident]
    return {k:item[k] for k in ['id','name','summary','experience','caution']} | {
        'priority':priority, 'mealBudgetMinutesEstimate':minutes,
        'budgetBasis':'本次安排估时，非原帖实测或餐厅出菜保证。',
        'openingOn20261006':'未电话或店家官方确认',
        'amapPoiHistorical':item['placeCheck'].get('poi'),
        'sources':[{k:s[k] for k in ['id','title','author','publishedAt','url','evidenceFile']} for s in item['sources']],
        'fullLocalEvidence':'existing-food-evidence.json#'+ident,
    }

web={
 'wulan-season':dict(title='携程：额尔古纳河·乌兰山景区',url='https://you.ctrip.com/sight/ergun2026/5711188.html',kind='第三方景点登记与旅客点评',finding='页面列出5月1日至10月31日08:00–17:30，票务咨询0470-2385880。可观景，列有滑草、滑索和秋千。',limits='实时开园字样来自平台，不等于10月6日项目逐项营业确认；附近推荐模块混有异地结果，不用于距离或导航。'),
 'wulan-duration-2024':dict(title='青岛出发，呼伦贝尔自驾游攻略',url='https://you.ctrip.com/travels/hulunbeier458/4144805.html',kind='历史游客游记',publishedAt='2024-08-26',visitDate='2024-08-13',finding='D6乌兰山条目写游览时长1–2小时，内容包括高处看河景及滑草、秋千。',limits='这是2024年夏季行程记录，只作时长尺度；其中旧车程与价格不用于本次规划。'),
 'wulan-duration-package':dict(title='长春康辉：额尔古纳、室韦、乌兰山、呼伦湖精品小包团',url='https://www.kanghuilv.com/line/show.asp?id=133',kind='旅行社自身产品行程',publishedAt=None,finding='自身产品给乌兰山安排60分钟游览，电瓶车另计。',limits='搜索索引可读、打开时超时；是团行程配额，非保证所有游客或项目能在60分钟完成。'),
 'hasar-season':dict(title='携程：黑山头哈撒尔马场',url='https://you.ctrip.com/sight/ergun2026/5712964.html',kind='第三方景点登记',finding='地址为黑山头新镇301省道路旁；7月1日至10月31日登记07:30–20:30；咨询13722002270。',limits='属于季节营业线索，10月6日可骑路线、接待名额和营业须联系马场确认。'),
 'hasar-duration':dict(title='Trip.com：Heishantou Hasar Horse Riding Field',url='https://sg.trip.com/travel-guide/attraction/ergun/heishantou-hasar-horse-riding-field-98706683?curr=KWD&locale=en-SG',kind='第三方游览时长建议',finding='建议游览时间1–3小时。',limits='是场所范围的游览参考，不代表已选骑马套餐的骑乘时长。'),
 'laogao-season':dict(title='携程：老高马场（额尔古纳市黑山头店）',url='https://gs.ctrip.com/html5/you/sight/ergun2026/4003138.html',kind='第三方景点登记',finding='页面登记07:30–19:30，地址301省道梁西村蒙园客栈南50米。',limits='样本仅4条点评，现有小红书没有可归属本店的独立实骑证据；不能套用泛黑山头骑马好评。'),
 'official-grassland':dict(title='额尔古纳市文化旅游体育局：草原在这里景区',url='https://eegn.gov.cn/News/show/1367982.html',kind='政府官方景区介绍',publishedAt='2026-04-29',finding='官方页面介绍黑山头镇东2公里处的草原在这里景区，含观光、餐饮与休闲功能。',limits='可支持该景区存在与位置；没有10月开放时段、马场具体套餐或乌兰山当日开行结论。直接打开失败，搜索索引可读。'),
 'historical-road-official':dict(title='呼伦贝尔市交通运输局：国省干线公路出行信息',url='https://jtj.hlbe.gov.cn/News/show/1379193.html',kind='2025年官方历史路况',publishedAt='2025-09-25',asOf='2025-09-24',finding='列有当时G331黑山头至扎赉诺尔部分养护封闭。',limits='不是2026年10月路况，也不是本次七卡至黑山头X904全线公告；不据此宣称本次卡线关闭。'),
}

horse_sources=[]
for s in existing['heishantou-horse']['sources']:
    horse_sources.append({k:s[k] for k in ['id','title','author','publishedAt','url','evidenceFile']} | {
        'visitPeriod':'2025年国庆（正文明确去年国庆）' if s['id']=='6a9a977d000000002902c6bd' else '2026年发布的七卡至黑山头实走记录，未给固定马场名',
        'limit':'未具名马场，不记为老高或哈撒尔的推荐票。'})

card_sources=[]
for nid in ['6abf6a99000000001301b90a','6abf3bdc0000000012037481']:
    raw=json.loads((root/'planning-20261004/xiaohongshu'/f'{nid}.json').read_text(encoding='utf8'))
    note=raw['note']
    card_sources.append(dict(id=nid,title=note['title'],url=note['url'],localEvidence=f'../planning-20261004/xiaohongshu/{nid}.json',visitDate='2026-10-02',finding='一篇喜欢开阔视野，另一篇认为叶落萧瑟；不承诺完整金秋景色。',limit='只能支持10月2日个人经历，不构成10月6日全线放行或全天路况证明。'))

payload={
 'researchedAt':datetime.now().astimezone().isoformat(),
 'targetDate':'2026-10-06','scope':'七卡早餐、乌兰山、黑山头午餐与骑马、额尔古纳晚餐；只供确认前研究。',
 'userPreference':'风景为主、乌兰山优先；骑马仅作备选，不继续扩查，不与完整乌兰山游玩强行叠加。',
 'productModified':False,'drivingPolicy':'本研究不新增或引用任何平台/笔记驾驶时间；交由当轮高德路线查验。',
 'breakfast':{
    'recommendedPlan':'先向七卡住宿方确认早餐供应与最早开餐；未确认前保留提前购置列巴、水等补给。',
    'mealBudgetMinutesEstimate':[30,45],
    'namedCandidate':food('qika-lanni','仅询问是否供早餐；不可直接当作已验证早餐店',[30,45]),
    'evidenceLimit':'兰妮唯一实吃帖是2025-10-03的农家菜、现包饺子与蔬菜，没有早餐或晨间营业证据。戍边食府、草原美食餐厅只是历史高德落点，不能补造早餐菜单。',
 },
 'lunch':[food('heishantou-yipinxiang','第一候选：排骨焖面/东北大丰收，两位2026作者明确支持',[45,60]),food('heishantou-new-yunxi','第二候选：家常菜配锅茶，单篇2026-09-15实吃支持',[45,60])],
 'dinner':[food('eerguna-shuncheng','第一候选：顺成盛大家园店红焖羊肉，现做需要等候',[60,90]),food('eerguna-new-mingyuan','第二候选：喜欢清水手把羊排时选铭源；肥瘦、嚼劲存在个人口味差异',[60,90])],
 'horseCandidates':[
    dict(name='黑山头哈撒尔马场',priority='可优先询问具体短线套餐',historicalAmapPoi=None,phone='13722002270',webSources=['hasar-season','hasar-duration'],timeBudgetMinutesEstimate=[90,120],timeBasis='参考平台场所1–3小时，按准备＋短程骑行安排90–120分钟；不是已确认套餐时长。',limitations='未核新高德POI、当天开行、价格或接待名额；不能把平台评分当安全或服务保证。'),
    dict(name='老高马场（额尔古纳市黑山头店）',priority='沿用既有高德落点的备选询价',historicalAmapPoi=existing['heishantou-new-laogao']['placeCheck']['poi'],webSources=['laogao-season'],timeBudgetMinutesEstimate=[90,120],timeBasis='仅本次骑马活动预算，需确认具体线路长度、准备时间和体验者适合程度。',limitations='现有小红书无可明确归属该店的实骑好评，泛黑山头体验不得套用。')
 ],
 'horseGeneralXhsSources':horse_sources,
 'wulan':{
    'name':'额尔古纳河·乌兰山景区','amapPoiHistorical':existing['qika-wulan']['placeCheck']['poi'],
    'recommendedExperience':'以上山看界河太极湾为主，滑草作为有余量且当天开放时的附加项目。',
    'viewOnlyBudgetMinutesEstimate':[75,90], 'viewAndOneRideBudgetMinutesEstimate':[90,120],
    'timeEvidence':'2024年实走游记写1–2小时；旅行社自身产品安排60分钟。这里给出的75–90及90–120分钟是本次规划估时，排队长需增加或取消项目。',
    'webSources':['wulan-season','wulan-duration-2024','wulan-duration-package'],
    'xhsSources':[{k:s[k] for k in ['id','title','author','publishedAt','url','evidenceFile']} for s in existing['qika-wulan']['sources']],
    'currentOpeningStatus':'仅第三方季节登记覆盖10月，未找到10月6日景区/项目逐项官方营业确认；咨询0470-2385880。',
    'seasonalEvidenceLimit':'滑草正面小红书来源68d00669为2025年；2026年8月七卡线实走支持观景，但不能外推10月6日项目开放。',
 },
 'borderRoad':{'status':'未找到2026-10-06 X904七卡→乌兰山→黑山头当日官方通行公告。','recentVisitSources':card_sources,'excludedHistoricalOfficialSource':'historical-road-official','decision':'高德可规划与笔记近期走过都不等于当天放行；以现场交通管理为准。'},
 'webSources':web,
 'discardedClaims':[
   '新浪自媒体FAQ存在缆车价格、形式、运营季相互矛盾，未当作官方开行、票价或运行时长依据。',
   '未采用马场企业排行榜的安全、马匹温顺、最佳路线等宣传保证。',
   '没有根据小红书农家菜好评推断早餐服务，没有把2026年发布但描述去年国庆的骑马帖当成本年国庆经历。',
 ],
}
(out/'food-activities-research.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
print('Saved food-activities-research.json: 2 lunches, 2 dinners, 2 horse candidates, breakfast limit, Wulan timing and 8 linked web sources')
for meal in payload['lunch']+payload['dinner']:
    print(meal['name'])
    for source in meal['sources']:
        print(source['author'],source['publishedAt'],source['id'])
