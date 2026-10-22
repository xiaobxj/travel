from pathlib import Path
ROOT=Path(__file__).parent
p=ROOT/'city-guide.js'
s=p.read_text(encoding='utf-8')
s=s.replace('距原路线对照段（几何）','距历史路线对照段（几何）')
s=s.replace('>对照 D${p.day}', '>历史对照 D${p.day}').replace('历史历史对照','历史对照')
s=s.replace('${p.baseline&&p.withStop?', '${!p.evidenceIssue&&p.baseline&&p.withStop?')
s=s.replace('距原路线为高德坐标到原行程折线的几何距离','距离为高德坐标到历史行程折线的几何距离')
s=s.replace('仅含驾驶增量；停车、吃饭、步行和游玩另计。','此项按历史对照路线估算；10月3日改线后需重新确认。停车、吃饭、步行和游玩另计。' if False else '仅含对照路线的驾驶增量；停车、吃饭、步行和游玩另计。')
s=s.replace('原路线和底图不改。','10月3日主线已更新为觉乐方案；新增三处采用10月3日完整路线比较，其他项目保留各自标注日期的历史路线对照，不代表本日新路线的绕行增量。')
p.write_text(s,encoding='utf-8')
p=ROOT/'lodging-template.html'
s=p.read_text(encoding='utf-8').replace('次日去敖鲁古雅','次日前往根白公路')
p.write_text(s,encoding='utf-8')
print('Updated mixed-date route comparison labels')
