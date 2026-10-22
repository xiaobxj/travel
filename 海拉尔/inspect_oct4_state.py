import json
from pathlib import Path
r=Path(__file__).parent
d=json.loads((r/'planning-20261004/day3-lunch-order-live-20261004T083741.json').read_text(encoding='utf-8'))
print([(i,x['id'],x['meters'],x['seconds']) for i,x in enumerate(d['routes'])])
for f in ['activity_render.py','verify_published_page.py']:
    print(f)
    print((r/f).read_text(encoding='utf-8'))
