import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'city-recommendations.json').read_text(encoding='utf8'))
notes={n['id']:n for n in json.loads((root/'city-notes.json').read_text(encoding='utf8'))['notes']}
ids=['qika-lanni','qika-new-shubian','qika-new-caoyuan','heishantou-yipinxiang','heishantou-new-yunxi','heishantou-lamb ranch','heishantou-new-laogao','heishantou-horse','qika-wulan','qika-grass slide','eerguna-shuncheng','eerguna-new-mingyuan','eerguna-xiaoguo']
selected=[]
for x in data['items']:
    if x['id'] not in ids:continue
    y={k:x.get(k) for k in ['id','name','cityId','summary','experience','caution','routeFit','reviews','placeCheck']}
    y['sources']=[]
    for rv in x['reviews']:
        n=notes[rv['noteId']]
        raw=json.loads((root/n['evidenceFile']).read_text(encoding='utf8'))['note']
        y['sources'].append({**{k:n.get(k) for k in ['id','title','author','publishedAt','url','evidenceFile']},'description':raw['description']})
    selected.append(y)
out=root/'planning-20261006-review/existing-food-evidence.json'
out.write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf8')
for y in selected:
    print('\n'+y['id']+' '+y['name']+' '+y['experience'])
    print(y['caution'])
    print('POI',y['placeCheck'].get('poi'))
    for s in y['sources']:
        print(s['id'],s['publishedAt'],s['title'])
        if y['id'] in ['qika-wulan','qika-grass slide','heishantou-horse']:print(s['description'])
