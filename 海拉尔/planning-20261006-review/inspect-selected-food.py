import json
from pathlib import Path
items=json.loads(Path(__file__).with_name('existing-food-evidence.json').read_text(encoding='utf8'))
for x in items:
    if x['id'] not in ['qika-lanni','heishantou-yipinxiang','heishantou-new-yunxi','eerguna-shuncheng','eerguna-new-mingyuan']:continue
    print('\n'+x['id'])
    for s in x['sources']:
        print(s['id'],s['publishedAt'],s['url'])
        if x['id']=='qika-lanni':print(s['description'])
        else:
            for line in s['description'].splitlines():
                if any(w in line for w in ['一品香','云汐','顺成','铭源','羊肉','大丰收','锅茶','排骨焖面']):print(line)
