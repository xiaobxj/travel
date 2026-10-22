"""Apply the researched September 6 lodging shortlist, without changing routes."""
from pathlib import Path
from copy import deepcopy
import json

ROOT=Path(__file__).parent
path=ROOT/'lodging-data.json'
data=json.loads(path.read_text(encoding='utf-8'))
nights=data['nights']
if '七卡' in nights[3]['city']:
    raise SystemExit('当前已采用七卡住宿方案。请编辑 lodging-data.json，再运行 build_ui.py；本脚本仅用于旧版临江清单。')

def hotel(name,rank,address,why,caution,url):
    return dict(name=name,rank=rank,address=address,why=why,caution=caution,url=url)

def keep(day,name):
    return next(h for h in nights[day-1]['hotels'] if h['name']==name)

nights[0]['hotels']=[
    keep(1,'坐望森林野奢民宿'),
    keep(1,'根河洪金家庭客栈'),
    hotel('呼伦贝尔根河楠舍宾馆（冷极广场店）','备选 · 冷极广场附近的小城住宿','根河五峰路113号',
          '地址与冷极广场店名可对应，公开住客反馈涉及停车和房间设施，可与守望桥一带的住宿一起比较。',
          '2026 年 8 月发布的入住反馈提到淋浴水温不稳定；先问目前热水及整夜供暖情况，店名不代表房间朝河。',
          'https://tw.trip.com/hotels/genhe-hotel-detail-130849332/nanshe-hotel/review.html'),
    hotel('根河秀水山庄酒店','备选 · 河畔与清晨景色','根河中央路南中东巷70号',
          '公开页面有江河景房及河边位置线索，住客提到对面拍晨雾，适合比城区便利更看重清晨环境的人。',
          '核对当前店名、实际入口、所订房型是否朝河；历史入住反馈不能替代 10/2 的供暖确认，晨雾也取决于天气。',
          'https://m.ctrip.com/html5/hotel/hoteldetail/7946138.html'),
    hotel('呼伦贝尔根河山水酒店（世纪广场龙凤大厦店）','备选 · 早市与市区便利','根河河西街道世纪广场A座商业楼A栋2号',
          '位于世纪广场一带，公开页面列有停车、餐厅和洗衣设施；更适合把晚餐、早餐与小城生活安排得轻松些。',
          '这是城区便利型选择，不承诺推窗见森林；问清停车位、临街噪声和早餐开餐时间。',
          'https://hotels.ctrip.com/hotels/120273023.html')
]

nights[1]['hotels']=[
    keep(2,'莫尔道嘎伊舒洋大酒店'),
    hotel('山前山后（莫尔道嘎店）','优先比较 · 庭院与秋季房型','莫尔道嘎镇S302丽娟山货铺南40米',
          '公开房型区分“山前”和“山后”，有庭院双床等选择，部分房型标注秋季供暖，适合与传统镇上宾馆对比。',
          '公开点评样本较少；房型宣传中的供暖仍需确认 10/3 是否全天提供，别把“山前山后”理解为每间都能看森林。',
          'https://www.wingontravel.com/hotel/detail-eerguna-135629286/shanqianshanhou-moridaga/'),
    keep(2,'额尔古纳千叶松宾馆'),
    hotel('莫尔道嘎金秋宾馆','备选 · 镇上家庭经营住宿','莫尔道嘎镇325县道北侧，工商银行对面一带',
          '公开页面及住客反馈涉及停车、整洁和周边餐饮，适合在镇里用餐后直接休息的安排。',
          '有住客入住地下家庭房；想要采光和小镇窗景应明确选择地上有窗房，并确认门前停车是否够用。',
          'https://hotels.ctrip.com/hotels/2323938.html'),
    hotel('莫尔道嘎苍麓酒店（部分页面显示千登宾馆）','备选 · 绿星文化广场一带','莫尔道嘎镇302省道，绿星文化广场东100米',
          '可查页面将位置标在镇区广场附近，适合把晚餐与龙山公园周边散步串起来。',
          '同一平台链接的不同抓取页面出现“苍麓”“千登”两个名称；按地址向店家确认当前名称、房间照片与供暖后再选，不作为两家计数。',
          'https://hotels.ctrip.com/hotels/78440803.html')
]

# White Deer Island has one verified local property. Town alternatives are
# explicitly separated; room types are never counted as independent hotels.
local=keep(3,'额尔古纳白鹿岛酒店')
local['scope']='local'
fallbacks=[]
for h in nights[1]['hotels'][:4]:
    alt=deepcopy(h)
    alt['scope']='route-change'
    alt['rank']='改住莫尔道嘎 · '+h['rank'].split(' · ',1)[-1]
    alt['routeImpact']='这家在莫尔道嘎镇，不在白鹿岛。若仍游白鹿岛，当晚需折返镇上；也可调整白鹿岛项目。10/4、10/5 都需重算车程，当前地图时间不适用。'
    fallbacks.append(alt)
nights[2]['hotels']=[local]+fallbacks
nights[2]['selectionNote']='这晚有 5 个住宿选项：1 家已核实的白鹿岛当地酒店 + 4 家莫尔道嘎改住备选。尚未核实到白鹿岛当地另外 4 家独立酒店；同一家主楼与木屋不重复计数。'
nights[2]['alternative']='白鹿岛不合适时，可以比较下列 4 家莫尔道嘎镇住宿。它们与前一晚候选有重合，是为了方便连住或改住；改住会改变 10/4—10/5 路线，需要重新核算。'

nights[3]['hotels']=[
    keep(4,'额尔古纳米莉莎旅游之家客栈'),
    hotel('时光里·民宿（额尔古纳室韦临江村店）','优先比较 · 村内木刻楞与庭院','额尔古纳室韦镇临江屯主街09号',
          '公开页面有花园、山景及复式房型，住客反馈提及木刻楞和阁楼，适合喜欢村内特色房间的选择。',
          '复式房先看楼梯与床位分布；确认整夜供暖、停车位置、实际窗景，不把住客的观景步行时间当作保证。',
          'https://m.ctrip.com/html5/hotel/hoteldetail/2637589.html'),
    hotel('额尔古纳临江玛丽亚列巴房之家民宿','备选 · 列巴早餐与家庭氛围','额尔古纳室韦临江一幢1号玛丽亚列巴房',
          '公开页面列有停车和庭院，入住反馈集中提及早餐与列巴，适合希望住宿也带一点当地生活体验的人。',
          '页面亦有隔音方面的反馈；问清房间位置、早餐是否包含及 10 月供应时间。餐饮体验不等于房间能看江景。',
          'https://wap.ctrip.com/html5/hotel/hoteldetail/2490460.html'),
    hotel('额尔古纳室韦临江热妮娅之家','备选 · 村内靠河方向','额尔古纳室韦临江村主街向北，门牌号30（右侧）',
          '住客反馈描述前方河流与后方山坡的位置关系，可作为优先核对河景朝向的候选。',
          '南北向房间体验不同，直接要所订房型窗外视频；核实卫生、热水和供暖，并确认入住的是临江这家。',
          'https://hotels.ctrip.com/hotels/1124741.html'),
    hotel('临江维吉·Taigahut｜俄风庭院民宿（额尔古纳临江村店）','备选 · 主街上的俄风庭院','额尔古纳临江村主干道左边',
          '住宿详情页明确在临江村主干道，可与其他木刻楞院落比较房型与院景，适合村内散步和用餐。',
          '公开地址较粗，预订前要店家发送准确落点和停车入口；再看近期实拍、供暖与隔音，不承诺江景。',
          'https://m.ctrip.com/html5/hotel/hoteldetail/2327915.html')
]

nights[4]['hotels']=[
    keep(5,'额尔古纳云顿酒店'),
    keep(5,'额尔古纳叶尼塞庄园'),
    hotel('西山驿站·Family民宿（额尔古纳湿地店）','备选 · 城区庭院与家庭房','额尔古纳热电街100号',
          '公开页面有花园和停车设施，适合偏爱民宿庭院、希望最后一晚仍有一点住宿氛围的自驾客。',
          '名称带湿地不代表住在景区内或每间都有湿地视野；确认早餐、停车出入口及整夜供暖。',
          'https://m.ctrip.com/html5/hotel/hoteldetail/76567598.html'),
    hotel('额尔古纳千鹤大酒店','备选 · 市区餐饮与停车','额尔古纳胜利街126号',
          '公开页面列有餐饮、停车、充电和洗衣设施，适合长途行程后整理衣物、早点休息。',
          '优先核对实际房型、夜间安静程度及早餐开餐时间；最后一晚以便于返程为主，不承诺自然景观。',
          'https://hotels.corporatetravel.ctrip.com/hotels/5653458.html'),
    hotel('额尔古纳大酒店','备选 · 城区常规酒店','额尔古纳大街287号',
          '公开页面列有停车、自助早餐和洗衣设施，可作为特色民宿之外的常规酒店选择。',
          '确认具体楼栋、房间新旧、停车与早餐安排，留足 10/7 退房和返回海拉尔的时间。',
          'https://hotels.ctrip.com/hotels/700602.html')
]

data['intro']='每晚列出 5 个可比较的住宿选项，按你们的林间小城、森林河湾和边境小村偏好排序。其中白鹿岛为 1 家当地酒店加 4 家改住莫尔道嘎的备选，其余四晚各 5 家当地候选。尚未查询 10/2—10/7 的实时房价和余房。'
for n in nights:
    for h in n['hotels']:
        h.setdefault('scope','local')
    assert len(n['hotels'])>=5
    assert len({h['url'] for h in n['hotels']})==len(n['hotels'])
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'choices_by_night':{n['city']:len(n['hotels']) for n in nights},'unique_properties':len({h['url'] for n in nights for h in n['hotels']})},ensure_ascii=False))
