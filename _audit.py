#!/usr/bin/env python3
"""Independent structure/HTML, local links, coverage and repetition audit."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,hashlib,collections,xml.etree.ElementTree as ET,urllib.parse
W=Path(__file__).resolve().parent
class Node:
 def __init__(self,tag='',attrs=()):self.tag=tag;self.attrs=dict(attrs);self.children=[]
 def text(self):return ''.join(x if isinstance(x,str) else x.text() for x in self.children)
 def walk(self):
  yield self
  for c in self.children:
   if isinstance(c,Node):yield from c.walk()
 def has(self,c):return c in self.attrs.get('class','').split()
class Tree(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in ('br','img','meta','link','hr','input','area','base','col','embed','param','source','track','wbr'):self.stack.append(n)
 def handle_startendtag(self,t,a):self.stack[-1].children.append(Node(t,a))
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:del self.stack[i:];break
 def handle_data(self,s):self.stack[-1].children.append(s)
t=Tree();t.feed((W/'sources/gii-full.html').read_text(encoding='iso-8859-1'))
html={}
for n in t.root.walk():
 if n.has('jnnorm'):
  en=next((x.text() for x in n.walk() if x.has('jnenbez')),'')
  if '§' in en:
   text=''.join(x.text() for x in n.walk() if x.has('jnhtml'))
   if not text.strip():text=next((x.text() for x in n.walk() if x.has('jnentitel')),'')
   html[n.attrs['id']]=(en,text)
units=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines() if l.strip()]
raw=ET.parse(W/'sources/vwgo.xml').getroot()
expected={n.attrib['doknr']:n.findtext('metadaten/enbez') for n in raw.findall('norm') if '§' in n.findtext('metadaten/enbez','')}
actual=[u['official_doknr'] for u in units]
compact=lambda s:re.sub(r'\s+','',s).replace('\u00ad','')
html_mismatch=[u['id'] for u in units if u['official_doknr'] not in html or compact(html[u['official_doknr']][1])!=compact(u['text'])]
com={};duplicates=[];positions={}
for p in sorted((W/'commentary').glob('*.md')):
 for ident,body in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',p.read_text(),re.M|re.S):
  if ident in com:duplicates.append(ident)
  com[ident]=body.strip();positions[ident]=p.name
paragraphs=collections.defaultdict(list)
for ident,s in com.items():
 for para in s.split('\n\n'):
  if len(para)>140:paragraphs[re.sub(r'\s+',' ',para)].append(ident)
repeated=[dict(ids=v,text=k) for k,v in paragraphs.items() if len(v)>1]
sets={k:set(re.findall(r'[a-zäöüß]{4,}',v.lower())) for k,v in com.items()}
pairs=[]
ids=list(com)
for i,a in enumerate(ids):
 for b in ids[i+1:]:
  score=len(sets[a]&sets[b])/len(sets[a]|sets[b])
  pairs.append((score,a,b))
pairs.sort(reverse=True)
meta=json.loads((W/'meta.json').read_text());out=Path(meta['repo_dir'])
broken=[];checked=0;external=set()
paths=list(out.glob('*.md'))+list((out/'cases').glob('*.md'))
for p in paths:
 for link in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',p.read_text()):
  if link.startswith(('https:','http:')):external.add(link);continue
  if link.startswith('#'):continue
  target=urllib.parse.unquote(link.split('#')[0]).strip('<>')
  checked+=1
  if not (p.parent/target).exists():broken.append(dict(file=p.name,target=target))
ordinary_short=[dict(id=u['id'],chars=len(com.get(u['id'],''))) for u in units if len(u['text'])>=160 and len(com.get(u['id'],''))<700]
slots=[]
for label in expected.values():slots+=re.findall(r'\d+[a-z]?',label)
report=dict(expected_xml_norms=len(expected),parsed_norms=len(units),official_html_norms=len(html),individual_numbered_slots=len(slots),missing_xml=sorted(set(expected)-set(actual)),unexpected_xml=sorted(set(actual)-set(expected)),duplicate_norm_ids=[k for k,v in collections.Counter(actual).items() if v>1],html_text_mismatches=html_mismatch,html_comparison='All textual characters compared after removing whitespace and soft hyphens; paragraph/list hierarchy separately retained from XML.',commented_units=len(com),missing_commentary=sorted(set(u['id'] for u in units)-set(com)),extra_commentary=sorted(set(com)-set(u['id'] for u in units)),duplicate_commentary=duplicates,commentary_chars=sum(map(len,com.values())),ordinary_below_700=ordinary_short,minimum_commentary_chars=min(map(len,com.values())),repeated_full_paragraphs=repeated,highest_vocabulary_overlap=[dict(jaccard=round(a,3),unit_a=b,unit_b=c) for a,b,c in pairs[:10]],local_links_checked=checked,broken_local_links=broken,external_links_listed=sorted(external),external_link_policy='Fetched primary sources are recorded in sources/verification.json; official case direct HTTP 403 is disclosed with successful Firecrawl 200 evidence. No blanket live-link or exhaustive authority claim.',scope='Author technical/content-support audit, not independent review',quality_limit='Length and similarity metrics do not prove legal correctness.')
report['ok']=not any(report[k] for k in ['missing_xml','unexpected_xml','duplicate_norm_ids','html_text_mismatches','missing_commentary','extra_commentary','duplicate_commentary','ordinary_below_700','repeated_full_paragraphs','broken_local_links'])
(W/'quality-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['external_links_listed','highest_vocabulary_overlap']},ensure_ascii=False,indent=2))
