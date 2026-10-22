"""Stage only public itinerary artifacts for the existing CloudBase directory."""
import hashlib
import json
import shutil
from pathlib import Path
from effective_routes import load_effective_routes
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'publish-20261003'
DEST.mkdir(exist_ok=True)
mapping={
    'index.html':'itinerary-map.html',
    'itinerary-map.html':'itinerary-map.html',
    'lodging-guide.html':'lodging-guide.html',
    'daily-activities.csv':'daily-activities.csv',
    'daily-activities.md':'daily-activities.md',
    'driving-times.csv':'driving-times.csv',
    'itinerary-map.png':'itinerary-map.png',
    'lodging-options.csv':'lodging-options.csv',
    'qika-food-pois.json':'qika-food-pois.json',
}
current_routes=load_effective_routes()
for research_key in ('day2Research','day3Research','day4Research'):
    for filename in current_routes[research_key]['evidenceFiles']:
        mapping[filename]=filename
staged_files={p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()}
assert not (staged_files-set(mapping)), 'Unexpected files in publication directory'
for target,source in mapping.items():
    (DEST/target).parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/source,DEST/target)
# API credentials must never be included in public evidence or HTML.
from amap_audit import KEY
assert KEY
for path in (p for p in DEST.rglob('*') if p.is_file()):
    assert KEY.encode() not in path.read_bytes(), path.name
    if path.suffix=='.json':
        def check(value):
            if isinstance(value,dict):
                assert not any(k.lower() in ('key','secretid','secretkey','access_token','refresh_token') for k in value), path.name
                for v in value.values():check(v)
            elif isinstance(value,list):
                for v in value:check(v)
        check(json.loads(path.read_text(encoding='utf-8-sig')))
manifest={name:dict(bytes=(DEST/name).stat().st_size,sha256=hashlib.sha256((DEST/name).read_bytes()).hexdigest()) for name in mapping}
(ROOT/'publish-20261003-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'directory':str(DEST),'files':len(mapping),'entrySha256':manifest['index.html']['sha256']},ensure_ascii=False))
