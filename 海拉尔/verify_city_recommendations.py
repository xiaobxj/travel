"""Check evidence, deduplication and UI filtering without a browser."""
import json
import subprocess
from pathlib import Path
from build_city_recommendations import CATEGORIES, evidence_stats
ROOT=Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
data=json.loads((ROOT/'city-recommendations.json').read_text(encoding='utf-8'))
notes={n['id']:n for n in json.loads((ROOT/'city-notes.json').read_text(encoding='utf-8'))['notes']}
cityids={c['id'] for c in json.loads((ROOT/'city-guide-config.json').read_text(encoding='utf-8'))['cities']}
assert set(data['overviews'])==cityids
assert {c['id'] for c in data['categories']}==set(CATEGORIES)
assert all(set(data['sectionSummaries'][c])==set(CATEGORIES) for c in cityids)
assert len(data['items'])==len({x['id'] for x in data['items']})
# Check complete source coverage and editorial values, so an old generated JSON
# cannot pass simply because its own counts and internal references agree.
source=read('city-entities.json')
source_items=source['items']+read('city-fixed-entities.json')
source_updates=read('city-review-additions.json')
expected={item['id']:item for item in source_items}
assert len(expected)==len(source_items)
assert set(expected)=={item['id'] for item in data['items']}
assert data['overviews']==source['overviews']
for city,sections in source_updates['sections'].items():
    source['sectionSummaries'][city].update(sections)
assert data['sectionSummaries']==source['sectionSummaries']
for item in data['items']:
    original=expected[item['id']]
    amendment=source_updates['items'].get(item['id'],{})
    assert item['reviews']==original['reviews']+amendment.get('reviews',[]),item['id']
    for field,value in {**original,**amendment}.items():
        if field!='reviews':assert item[field]==value,(item['id'],field)
assert data['sampleNotes']==len(notes)
assert data['reviewedNotes']==len({r['noteId'] for x in data['items'] for r in x['reviews']})
for x in data['items']:
    assert x['category'] in CATEGORIES and x['cityId'] in cityids
    assert all(x[k] for k in ['name','summary','experience','caution','routeFit'])
    assert x['reviews'] or (x['placeCheck']['status']=='verified' and x['evidenceLabel']=='暂无笔记支持')
    assert len(x['reviews'])==len({r['noteId'] for r in x['reviews']})
    assert all(r['noteId'] in notes and r['basis'] for r in x['reviews'])
    assert all(x[k]==v for k,v in evidence_stats(x['reviews'],notes).items())
    assert x['recommendCount']<=x['authorCount']<=x['sourceCount']
    if x['cautionCount']: assert x['strength']==0
    if x['strength']==3: assert x['recommendCount']>=3 and x['cautionCount']==0
sample={
 'one':{'author':'A','excerpt':'unique one','likes':None},
 'repeat':{'author':'A','excerpt':'another one'},
 'mention':{'author':'B','excerpt':'unvisited'},
 'negative':{'author':'C','excerpt':'disliked'},
 'ad':{'author':'D','excerpt':'promotion','suspectedAd':True},
 'copy1':{'author':'E','excerpt':'a detailed original travel description '*10},
 'copy2':{'author':'F','excerpt':'a detailed original travel description '*10},
}
reviews=[dict(noteId=k,stance=s) for k,s in [('one','positive'),('repeat','positive'),('mention','mention'),('negative','negative'),('ad','positive')]]
stats=evidence_stats(reviews,sample)
assert stats['recommendCount']==1 and stats['cautionCount']==1 and stats['strength']==0
assert evidence_stats([dict(noteId='one',stance='positive'),dict(noteId='repeat',stance='mixed')],sample)['recommendCount']==0
assert evidence_stats([dict(noteId='copy1',stance='positive'),dict(noteId='copy2',stance='positive')],sample)['recommendCount']==1
assert evidence_stats([dict(noteId='one',stance='positive')],sample)['recommendCount']==1
js=r"""
const assert=require('node:assert/strict');
const {rankItems,selectItems}=require('./city-guide.js');
const rows=[
{id:'conflict',name:'A',cityId:'a',category:'eat',recommendCount:4,strength:0,cautionCount:2,summary:'meal'},
{id:'strong',name:'B',cityId:'a',category:'eat',recommendCount:3,strength:3,cautionCount:0,summary:'beef'},
{id:'single',name:'C',cityId:'a',category:'drink',recommendCount:1,strength:1,cautionCount:0,summary:'coffee'},
{id:'other',name:'D',cityId:'b',category:'eat',recommendCount:9,strength:3,cautionCount:0,summary:'other city'},
{id:'negative',name:'E',cityId:'a',category:'eat',recommendCount:0,strength:0,cautionCount:1,summary:'bad'}];
const f={category:'all',text:'',minimum:0,order:'recommend'};
assert.deepEqual(selectItems(rows,'a',f).map(x=>x.id),['conflict','strong','single','negative']);
assert.deepEqual(selectItems(rows,'a',{...f,order:'evidence'}).map(x=>x.id),['strong','single','conflict','negative']);
assert.deepEqual(selectItems(rows,'a',{...f,minimum:2}).map(x=>x.id),['conflict','strong']);
assert.deepEqual(selectItems(rows,'a',{...f,category:'drink'}).map(x=>x.id),['single']);
assert.deepEqual(selectItems(rows,'a',{...f,text:'BEEF'}).map(x=>x.id),['strong']);
assert.deepEqual(selectItems(rows,'c',f),[]);
"""
result=subprocess.run(['node','-e',js],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert result.returncode==0,result.stderr
print(json.dumps({'status':'PASS','cities':len(cityids),'categories':list(CATEGORIES.values()),'items':len(data['items']),'sourceNotes':data['reviewedNotes'],'checks':['generated coverage and editorial values match source data','source references','author and duplicate-body deduplication','mentions and ads excluded from votes','conflicts retained','unknown counters accepted as evidence','both ranking modes','city/category/text/minimum filters']},ensure_ascii=False))
