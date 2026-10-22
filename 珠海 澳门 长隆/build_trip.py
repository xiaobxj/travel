import json,base64,math,csv,html
from pathlib import Path
R=Path(__file__).parent
P=json.loads((R/'selected-pois.json').read_text(encoding='utf-8'))
routes=json.loads((R/'routes.json').read_text(encoding='utf-8'))
sources={}
def source(key,file,summary):
    r=json.loads((R/'research'/file).read_text(encoding='utf-8'))
    sources[key]={'title':(r['title'] or [r['card']['text'].split('\n')[0]])[0], 'author':(r['author'] or ['见原文'])[0], 'url':r['url'],'date':' / '.join(r['date']),'summary':summary,'type':'小红书原文','read':'2026-09-06'}
source('coast','珠海一日游-0.json','海岸线集中在爱情邮局、渔女、香炉湾与日月贝；取同一条线，删去远端海天公园。')
source('coast2','珠海一日游-1.json','作者亲历海岸线；评论回复提到长隆住处去市区海边距离远，因此本方案拆分住宿区域。')
source('macau','澳门一日游 美食-9.json','串联半岛与氹仔；官也街小吃和路氹酒店外观值得顺路安排。本方案减少打卡点，跨区打车。')
source('macaufood','澳门一日游 美食-1.json','作者列出日常面店，强调按所在位置就近吃。保留靠近老城的祥记及金城二食店。')
source('macauwalk','澳门一日游 美食-13.json','老城步行与小吃实测；正文认可金城咖喱，评论提醒牛杂份量大、热门店会排队。')
source('hyatt','珠海 拱北 酒店 推荐-0.json','入住者认可口岸距离和设施；同时提到早餐排队、较晚才能入住。具体房型和政策以酒店为准。')
source('longzhuda','珠海 拱北 酒店 推荐-1.json','多次入住者认可珠海站对面的位置与房间；评论对窗景有不同反馈，不承诺固定景观。')
source('tea','珠海 美食 早茶-0.json','利苑珠光花园店实测：推荐凤爪、菠萝包与腐皮卷；也指出环境普通、节假日价格可能不同。')
source('jinyue','珠海 美食 早茶-1.json','金悦轩拱北店早茶实测，推荐燕窝蛋挞、沙翁、虾饺；作者提醒提前订位。晚餐出品未由此笔记验证。')
source('shipplay','长隆 海洋王国 飞船 两天 酒店-0.json','飞船乐园分层玩法，推荐百慕大历险和深海潜艇。笔记中的场次和提前入园时间不直接沿用。')
source('hotels','长隆 海洋王国 飞船 两天 酒店-1.json','酒店比较笔记，作为地理位置与取舍线索；内容偏汇总，不视作四家均有入住实测。')
source('oceanfood','长隆 海洋王国 必玩 吃饭-0.json','园内就餐实测认可城堡餐厅鸡排饭，建议就近吃；晚餐可考虑酒店，避免为吃饭绕远路。')
source('ocean','长隆 海洋王国 必玩 吃饭-1.json','海洋王国亲历：鲸鲨馆、企鹅馆、剧场和夜间演出是重点。删去保证不排队等不可复用结论。')
source('adult','长隆 海洋王国 必玩 吃饭-3.json','成年游客非自驾亲历：认可鹦鹉过山车及企鹅酒店位置；套票权益和场次仅按官方当天规则使用。')
source('budgethotel','飞船乐园 吃饭-1.json','迎海公寓住客认可接驳便利，同时反映房间有味道、早餐不合口味；仅列预算备选。')
source('shipplay2','飞船乐园 吃饭-4.json','另一位亲子游客认可百慕大与深海潜艇，对海洋单轨车兴趣较低，所以单轨车列为余力项目。')
source('orcafood','飞船乐园 吃饭-12.json','鲸生鲸世午餐实测认可海皇炒饭；是否能坐窗边、看到虎鲸经过无法保证。')
source('coralfood','飞船乐园 吃饭-14.json','珊瑚餐厅亲子就餐实测；虽近期发布，评论说明实际年初到访，潜水员出现也不是固定时间。')
official=[{'title':'海洋王国官方信息','url':'https://www.chimelong.com/zh/oceankingdom/'},{'title':'飞船乐园官方信息','url':'https://www.chimelong.com/zh/zh-park-science/'},{'title':'度假区交通与接驳','url':'https://www.chimelong.com/zh/traffic/type_7.html'},{'title':'澳门旅游局 · 出入境','url':'https://www.macaotourism.gov.mo/zh-hans/travelessential/before-you-travel/travelling-to-macao'}]
items=[]
def add(id,poi,days,cat,name,brief,detail,src,priority=2,location_note='高德地点坐标；进出口以现场指引为准'):
    p=P[poi];items.append(dict(id=id,poi=poi,days=days,cat=cat,name=name,brief=brief,detail=detail,sources=src,priority=priority,location=list(map(float,p['location'].split(','))),address=p['address'],location_note=location_note))
add('postoffice','postoffice',[1],'play','爱情邮局 · 海边灯塔','海岸线第一站 · 留 40 分钟','先在海边灯塔与邮局外拍照，再沿海散步。选择下午前往，不为了赶日出早起。抵达晚时可直接从渔女开始。',['coast','coast2'],1)
add('fishergirl','fishergirl',[1],'play','珠海渔女','城市地标 · 留 20–30 分钟','沿海岸接到渔女，短暂停留即可。步行导航绕行约 20 分钟，实际拍照散步还应加时。',['coast','coast2'],1)
add('xianglu','xianglu',[1],'play','香炉湾沙滩 · 城市阳台','看海、歇脚 · 留 45–60 分钟','沙滩慢走、椰树拍照，再在城市阳台一带休息。海水颜色取决于天气，不按滤镜照片期待。',['coast','coast2'],1)
add('opera','opera',[1],'play','日月贝 · 野狸岛','傍晚看建筑与海景 · 留 60–90 分钟','从香炉湾打车到日月贝附近，逛剧院外观和海韵城。只选一段海边散步，不绕野狸岛完整一圈。',['coast','coast2'],1)
add('liyuan','liyuan',[1],'food','利苑海鲜酒家 · 珠光花园店','午餐首选 · 粤式早茶','推荐凤爪、菠萝包、腐皮卷，按人数少量点单。笔记评价环境普通、份量较大；周末菜单及优惠需到店确认。',['tea'],1)
add('jinyue','jinyue',[1],'food','金悦轩 · 珠海总店','早茶备选 / 晚餐地点候选','原文实际推荐的是早茶：燕窝蛋挞、沙翁与虾饺。若改为晚餐请先确认正餐菜单、价格和订位；晚餐品质未由该笔记直接验证。',['jinyue'],2)
add('longzhuda','longzhuda',[1,2],'stay','龙珠达国际酒店','拱北首选位置 · 建议连住 2 晚','珠海站对面，方便 13 日轻装过关后原路回住处。9/12–9/14 连住两晚，14 日退房后携行李去长隆。这里只推荐位置，尚未查询指定日期房价、库存。',['longzhuda'],1)
add('hyatt','hyatt',[1,2],'stay','珠海拱北凯悦酒店','市区住宿备选 · 较新设施','距离口岸较近；小红书住客认可设施，同时提到早餐排队和入住时间限制。与龙珠达比较实际房价、房型后再选。路线默认使用龙珠达，换酒店需重查首末段。',['hyatt'],2)
add('gongbei','gongbei',[1,2],'transit','拱北口岸','步行过关 · 单程预留 45–90 分钟','此时间是行程预留，不是高德计算。不要把珠海到澳门规划成普通出租车直达；进出境步行完成，澳门一侧再打车。',['macau'],1)
add('barrier','barrier',[2],'transit','澳门关闸','过关后在澳门一侧上车','澳门境内打车从此处开始。车程为高德驾车基础值，另加候车及上客点步行；回程同样在关闸下车。',['macau'],1)
add('senado','senado',[2],'play','议事亭前地','老城起点 · 留 30–40 分钟','广场、周边街巷一起逛，先感受老城，再步行向大三巴方向。',['macau','macauwalk'],1)
add('rosary','rosary',[2],'play','玫瑰圣母堂 · 外观','路过拍照 · 留 10 分钟','高德地点目前标注“暂停开放”，本方案只安排外观。能否入内以当天现场公告为准。',['macau','macauwalk'],2)
add('stpaul','stpaul',[2],'play','大三巴牌坊','澳门地标 · 留 40–60 分钟','台阶与周边街巷一起看，天气热时不再强加大炮台登高。人多就缩短主台阶拍照时间。',['macau','macauwalk'],1)
add('jincheng','jincheng',[2],'food','金城二食店','老城午餐首选 · 咖喱饭','大三巴附近就近解决午餐，原文及另一篇面店合集均提到咖喱。口味、辣度先问店员；按现场营业和排队决定是否换店。',['macaufood','macauwalk'],1)
add('xiangji','xiangji',[2],'food','祥记面家','老城午餐备选 · 虾子捞面','在福隆新街，适合从议事亭附近顺路去；与金城二选一，不为打卡多跑一家。',['macaufood'],2)
add('cunha','cunha',[2],'play','官也街','下午逛吃 · 留 45–60 分钟','从半岛跨区打车，集中体验氹仔街巷与小吃。热门店排太久就跳过，把体力留给后面的酒店外观。',['macau'],1)
add('laoday','laoday',[2],'food','老Day牛杂 · 官也街总店','下午小吃备选','官也街就近吃。评论提到一份量较大，建议两人分享；不能吃辣先说清楚。与蛋球仔按胃口选择。',['macau','macauwalk'],2)
add('zeixian','zeixian',[2],'food','泽贤记 · 官也街店','下午小吃备选 · 蛋球仔','按官也街分店定位，原文提到官也街品牌；具体流心口味建议借鉴天神巷店的实测，门店出品仍可能不同。',['macau','macauwalk'],2)
items[-1]['location']=list(map(float,json.loads((R/'poi-options.json').read_text(encoding='utf-8'))['zeixian'][3]['location'].split(',')));items[-1]['address']='安乐街13–15号'
add('venetian','venetian',[2],'play','威尼斯人 · 大运河购物区','室内休息与拍照 · 留 60–90 分钟','从官也街步行接入，避暑、逛大运河购物区。地图点位为建筑代表位置，室内逛街和找出口需要额外时间。',['macau'],1)
add('londoner','londoner',[2],'play','伦敦人 · 建筑外观','余力收尾 · 留 30–45 分钟','跨过路氹大道看外观，拍完就回关闸。下午太累可以取消此站；不把巴黎人、永利等全部塞进一天。',['macau'],2)
add('ocean','ocean',[3],'play','长隆海洋王国','必玩 · 单独留一整天','9/14 海洋王国，重点看鲸鲨、企鹅和一场剧场演出；刺激项目按兴趣加。营业与夜间演出时间以当天官方公告为准。',['ocean'],1)
add('parrotcoaster','parrotcoaster',[3],'play','鹦鹉过山车','刺激项目 · 可选','入园后看实时排队，喜欢过山车再安排。身高、健康限制以项目现场要求为准，不以亲子笔记中的年龄替代。',['adult'],2)
add('whaleshark','whaleshark',[3],'play','鲸鲨馆','核心推荐 · 留 45–60 分钟','水族馆是这天的重点，给大观景窗留出时间。人多时先逛其他展区再回来，不保证固定时段没有人。',['ocean'],1)
add('penguinhall','penguinhall',[3],'play','企鹅馆','核心推荐 · 留 30–45 分钟','与鲸鲨馆、白鲸剧场串联，带一件薄外套。园内路线按开放通道走，地图连线仅示顺序。',['ocean'],1)
add('belugatheater','belugatheater',[3],'play','白鲸剧场','演出选一场 · 按当天排期','入园先查看当天演出表，把场次插入水族馆之间。座位、入场与水花区域听现场指引。',['ocean'],1)
add('oceanfood','oceanfood',[3],'food','城堡餐厅','园内就近午餐 · 鸡排饭','亲历笔记认可现炸鸡排饭，也推荐卤牛肉饭。菜单和价格可能变化；比起反复出园找饭，优先在游玩路径上吃。',['oceanfood'],1)
add('penguinhotel','penguinhotel',[3,4],'stay','长隆企鹅酒店','本方案长隆住宿首选 · 住 9/14 晚','海洋王国结束后回住处更方便，次日步行去飞船入口。14 日早到先寄存，15 日退房后再寄存；费用与领取时间先向酒店确认。',['adult','hotels'],1)
add('spaceshiphotel','spaceshiphotel',[3,4],'stay','长隆飞船酒店','飞船优先的备选','与飞船乐园相邻，适合更看重 15 日便利的人；14 日海洋王国散场要乘接驳或步行。提前入园及多次出入仅按所购套票权益判断。',['shipplay','hotels'],2)
add('circushotel','circushotel',[3,4],'stay','长隆马戏酒店','比较套票总价的备选','位置介于园区与酒店区，设施较早。此行不强加马戏，只比较包含两园日期的套票总成本。',['hotels'],2)
add('hengqinbayhotel','hengqinbayhotel',[3,4],'stay','长隆横琴湾酒店','更重视酒店度假的备选','酒店体量较大、依赖接驳，当前两天都以乐园为主，优先级放在企鹅和飞船之后。',['hotels','oceanfood'],3)
add('yinghaihotel','yinghaihotel',[3,4],'stay','长隆迎海酒店公寓','预算备选 · 需要接驳','住客提到交通方便，也有气味及早餐不满意反馈。只在价差明显且接受接驳时考虑，不按未验证的“最低价”推荐。',['budgethotel'],3)
add('spaceship','spaceship',[4],'play','长隆飞船乐园','必玩 · 9/15 整日安排','以室内展馆和特色项目为主。优先百慕大、深海潜艇及虎鲸展区；最后一天离开时间尚未提供，不预设能赶上具体车次。',['shipplay','shipplay2'],1)
add('spaceshipgate','spaceshipgate',[4],'transit','飞船乐园主入口附近','定位到售票处 · 不误入酒店通道','高德路线使用主入口售票处代表位置。酒店专属通道在另一端，仅在满足购票权益时使用。',['shipplay'],1)
add('bermuda','bermuda',[4],'play','百慕大历险','优先体验 · 5D 项目','两篇笔记都认可体验感，入园查看实时排队及现场身高限制。排队超过可接受时间就先看展馆。',['shipplay','shipplay2'],1)
add('submarine','spaceship',[4],'play','深海潜艇','优先体验 · 实景海底','两篇笔记均推荐。高德未检索到可靠的独立项目坐标，标记归入飞船园区，进园用官方室内导览找入口。',['shipplay','shipplay2'],1,'园区代表点；不是深海潜艇精确位置')
add('orca','orcafood',[4],'play','鲸奇宇宙 · 虎鲸展区','展馆重点 · 演出另看场次','先看展区，再按当天官方排期选择演出。此处为鲸生鲸世餐厅附近的展区参考位置，不代表二楼剧场入口。',['shipplay','shipplay2'],1,'展区参考点；剧场入口以官方室内导览为准')
add('monorail','spaceship',[4],'play','海洋单轨车','余力项目 · 意见有分歧','有游客推荐，也有亲子游客觉得普通。安排在主项目之后，有空再玩。独立坐标未核实，归入园区代表点。',['shipplay','shipplay2'],3,'园区代表点；不是单轨车精确位置')
add('orcafood','orcafood',[4],'food','鲸生鲸世餐厅','午餐首选 · 单点','原文推荐海皇炒饭；窗边座位先到先得，不保证进餐时能看到虎鲸经过。以菜品和就近位置选择，不为固定座位耗太久。',['orcafood'],1)
add('coralfood','coralfood',[4],'food','珊瑚餐厅','亲子用餐备选','看鱼吃饭的体验型选择，先比较套餐人数与菜单。原文为年初实际体验，不能把笔记中的旧价或潜水员时间当作 9 月承诺。',['coralfood'],2)
days=[
 dict(id=1,date='09.12',week='周六',city='珠海',title='把下午留给海风',sub='早茶 · 情侣路 · 日月贝',map='zhuhai',stay='拱北连住第 1 晚',note='按中午前到达珠海安排；若下午才到，午餐就近解决，直接从渔女开始。',steps=[('11:00','liyuan','午餐，先慢下来'),('13:00','postoffice','灯塔与海边散步'),('14:00','fishergirl','地标短停'),('15:00','xianglu','沙滩与城市阳台'),('16:30','opera','傍晚海边与建筑外观'),('18:30','jinyue','晚餐地点候选，菜单先确认'),('20:00','longzhuda','回拱北休息')]),
 dict(id=2,date='09.13',week='周日',city='澳门',title='一半老城，一半路氹',sub='大三巴 · 官也街 · 威尼斯人',map='macau',stay='回拱北连住第 2 晚',note='行李留在珠海住处，轻装当日往返。两次过关各预留 45–90 分钟；晚间不追加远端景点。',steps=[('08:00','gongbei','出发过关，留足排队时间'),('09:30','barrier','澳门一侧再上出租车'),('10:00','senado','老城广场与街巷'),('10:45','rosary','仅安排外观'),('11:00','stpaul','大三巴与周边'),('12:15','jincheng','老城午餐'),('14:00','cunha','氹仔逛吃'),('15:30','venetian','室内休息与拍照'),('17:00','londoner','可选建筑外观'),('18:00','barrier','返回关闸，步行过关'),('19:30','longzhuda','回拱北吃饭与休息')]),
 dict(id=3,date='09.14',week='周一',city='海洋王国',title='今天，住进海洋旁边',sub='鲸鲨馆 · 企鹅馆 · 夜间演出',map='ocean',stay='企鹅酒店，或长隆备选酒店',note='08:15 左右从拱北带行李出发，先到酒店寄存。默认按普通开园入园；不预设赠送提前入园权益。',steps=[('09:15','penguinhotel','先寄存行李'),('10:00','ocean','入园并查看当天演出表'),('10:30','parrotcoaster','喜欢刺激再玩，可跳过'),('11:30','whaleshark','留时间看鲸鲨'),('12:30','oceanfood','午餐就近吃'),('14:00','penguinhall','企鹅馆与展区'),('下午','belugatheater','选一场，按演出表调整'),('傍晚','ocean','休息补餐，夜间演出看当天公告'),('散场后','penguinhotel','回酒店')]),
 dict(id=4,date='09.15',week='周二',city='飞船乐园',title='再探一次深海宇宙',sub='百慕大 · 深海潜艇 · 虎鲸展区',map='spaceship',stay='退房寄存；返程时间待补',note='退房后先寄存行李，再去飞船主入口。尚未提供返程时间；若当天必须早走，删去余力项目并提前取行李。',steps=[('09:20','spaceshipgate','从企鹅酒店步行到主入口'),('10:00','spaceship','入园，按现场开放顺序调整'),('上午','bermuda','先看排队情况'),('上午','submarine','体验特色项目'),('12:00','orcafood','午餐；珊瑚餐厅备选'),('下午','orca','展馆与当天演出'),('余力','monorail','有空再玩'),('离园时','spaceshipgate','从主入口离开'),('离园后','penguinhotel','返回酒店领取行李')])]
for day in days:day['steps']=[dict(time=t,item=i,note=n) for t,i,n in day['steps']]
maps=json.loads((R/'map-config.json').read_text(encoding='utf-8'))
for m in maps:m['image']='data:image/png;base64,'+base64.b64encode((R/('map-'+m['id']+'.png')).read_bytes()).decode()
data=dict(days=days,items=items,sources=sources,official=official,routes=routes,maps=maps,assumptions='暂按 2026 年、两位成人、9/12 中午前到达及 9/15 可完整游玩安排；人数、儿童身高、抵离班次与住宿预算仍待补。',checked='2026-09-06')
(R/'travel-data.json').write_text(json.dumps({**data,'maps':[{k:v for k,v in m.items() if k!='image'} for m in maps]},ensure_ascii=False,indent=2),encoding='utf-8')
template=(R/'template.html').read_text(encoding='utf-8')
(R/'index.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
with (R/'交通时间.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['日期','出发','到达','方式','基础分钟','距离公里','说明'])
    for r in routes:w.writerow(['9/'+str(11+r['day']),P[r['from']]['name'],P[r['to']]['name'],'步行' if r['mode']=='walk' else '打车参考',math.ceil(r.get('seconds',0)/60),round(r.get('distance',0)/1000,2),'高德查询；不含等车、过关、园内排队'])
md=['# 珠海 · 澳门 · 长隆｜四日非自驾手册','',data['assumptions'],'','打开 index.html 使用交互地图。地图底图和已查询路线可离线查看，导航和小红书链接需联网。','']
lookup={i['id']:i for i in items}
for day in days:
    md.extend(['## '+day['date']+' '+day['city'],'',day['note'],'','|时间|安排|说明|','|---|---|---|'])
    md.extend('|'+s['time']+'|'+lookup[s['item']]['name']+'|'+s['note']+'|' for s in day['steps']);md.extend(['','住宿：'+day['stay'],''])
md.extend(['## 来源与时间口径','','推荐基于已通过登录浏览器读取的小红书原文及部分已加载评论；未以转载摘要替代原文。作者评价是个人体验，未核实商业合作关系，不作为全网口碑排行。','高德为 2026/09/06 查询快照，不是出行日交通预测。澳门过关单程预留 45–90 分钟属规划估算；园内步行及室内绕行另算。9/14、9/15 营业与演出时间以官方当天公告为准。','酒店与餐厅未查询指定日期实时价格、库存、订位情况。',''])
md.extend('- ['+s['title']+']('+s['url']+') — '+s['author']+'。'+s['summary'] for s in sources.values())
(R/'行程与来源.md').write_text('\n'.join(md),encoding='utf-8')
print('Built',len(items),'places,',len(sources),'original notes,',len(routes),'AMap routes.')
