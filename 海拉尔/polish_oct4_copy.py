"""Keep the published trip instructions focused on decisions for the traveller."""
from pathlib import Path
import json

root=Path(__file__).parent
path=root/'activities.json'
data=path.read_text(encoding='utf-8')
replacements={
    '酒店停车场只是接入点，未核到餐厅独立入口，不编造内部接驳车程。':'从酒店停车场到餐厅的具体入口，请向酒店确认。',
    '当天运营尚未确认，不把它写成已预约项目。':'是否开行及实际发船时间，以当天景区答复为准。',
    '排队或天气变化另留余量，不沿用旧车程的固定到达承诺。':'排队或天气变化另留余量。',
    '车程以当天“分段车程”内10/4高德复查为准；不再使用旧的1小时46分估算。':'白鹿岛至临江等各段车程见“分段车程”，已于10/4用高德查验。',
    '实吃依据为2025年国庆记录，今日营业未确认，不把高德登记当开门保证。':'实吃依据为2025年国庆记录，出发前请向店家确认是否供餐。',
}
for old,new in replacements.items():
    assert old in data,old
    data=data.replace(old,new)
json.loads(data)
path.write_text(data,encoding='utf-8')
print('Updated five traveller-facing descriptions')
