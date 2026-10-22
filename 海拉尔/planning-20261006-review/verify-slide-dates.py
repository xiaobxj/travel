import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
for name in ['6abe38e1000000001a022c61','6abc968a000000001403824e']:
    n=json.loads((Path(__file__).parent/'xiaohongshu'/f'{name}.json').read_text(encoding='utf8'))['note']
    print(name, datetime.fromtimestamp(n['publishedTimestamp']/1000,timezone(timedelta(hours=8))).isoformat())
