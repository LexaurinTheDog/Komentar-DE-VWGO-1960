"""Bounded second-pass evidence checks; no legal-quality certification by length."""
from pathlib import Path
import collections,hashlib,json,re,subprocess,xml.etree.ElementTree as E
W=Path(__file__).resolve().parent
ids=['p1','p2','p3','p4','p5','p6','p7-8','p9','p10','p11','p12','p13','p14','p15','p16','p17','p18','p19','p20','p21']
units=[json.loads(s) for s in (W/'units.jsonl').read_text().splitlines() if s.strip()]
by_id={u['id']:u for u in units}
raw=W/'sources/review-p1-p21/vwgo.xml';r=E.parse(raw).getroot();source_nodes={n.attrib['doknr']:n for n in r}
raw_labels=[n.findtext('metadaten/enbez','') for n in r]
normalize=lambda s:re.sub(r'\s+','',s).replace('\u00ad','')
source_map=[]
for ident in ids:
 u=by_id[ident];n=source_nodes[u['official_doknr']];c=n.find('textdaten/text/Content')
 text=''.join(c.itertext()) if c is not None else ''
 if not text.strip():text=''.join(n.find('metadaten/titel').itertext())
 source_map.append(dict(id=ident,official_doknr=n.attrib['doknr'],official_label=n.findtext('metadaten/enbez'),text_matches_xml=normalize(text)==normalize(u['text']),statutory_sha256=hashlib.sha256(u['text'].encode()).hexdigest(),raw_xml_sha256=hashlib.sha256(E.tostring(n,encoding='utf-8')).hexdigest()))
def blocks(s):return {k:v.strip() for k,v in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',s,re.M|re.S)}
current={};before={};duplicate_ids=[]
for p in sorted((W/'commentary').glob('*.md')):
 b=blocks(p.read_text());duplicate_ids.extend(set(current)&set(b));current.update(b)
 old=subprocess.run(['git','show','244cb82:commentary/'+p.name],cwd=W,check=True,capture_output=True,text=True).stdout
 before.update(blocks(old))
changed=[k for k in current if current[k]!=before[k]]
unassigned_changes=[k for k in changed if k not in ids]
paragraphs=collections.defaultdict(list)
for k in ids:
 for para in current[k].split('\n\n'):
  if len(para)>140:paragraphs[normalize(para)].append(k)
repeats=[v for v in paragraphs.values() if len(v)>1]
case=E.parse(W/'sources/review-p1-p21/local-KVRE425431801.xml').getroot()
assert case.findtext('ecli')=='ECLI:DE:BVerfG:2018:rs20180322.2bvr078016'
assert case.findtext('entsch-datum')=='20180322'
# Statutory quotes printed by the BVerfG in para.6 must still match today's source.
court_text=normalize((W/'sources/review-p1-p21/bverfg-2bvr780-16.txt').read_text())
case_quote_agreement={k:normalize(by_id[k]['text']) in court_text for k in ['p17','p18']}
report=dict(scope='Only assigned twenty commentary units, cross-reference targets read as supporting context',reviewed_ids=ids,units_reviewed=len(ids),baseline_work_commit='244cb82',official_xml=str(raw.relative_to(W)),official_xml_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),fresh_xml_identical_to_authoring=raw.read_bytes()==(W/'sources/vwgo.xml').read_bytes(),source_map=source_map,changed_ids=changed,unassigned_commentary_changes=unassigned_changes,statutory_units_unchanged=(W/'units.jsonl').read_bytes()==subprocess.run(['git','show','244cb82:units.jsonl'],cwd=W,capture_output=True,check=True).stdout,all_commented_units=len(current),missing_commentary=sorted(set(by_id)-set(current)),duplicate_commentary=duplicate_ids,repeated_assigned_full_paragraphs=repeats,case_2018_statutory_quote_agreement=case_quote_agreement,limits='Mechanical evidence only. The substantive per-unit legal review is recorded separately in review-result.json.')
report['ok']=all(x['text_matches_xml'] for x in source_map) and all(case_quote_agreement.values()) and report['fresh_xml_identical_to_authoring'] and report['statutory_units_unchanged'] and not any([unassigned_changes,report['missing_commentary'],duplicate_ids,repeats])
(W/'sources/review-p1-p21/review-source-map.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['ok','units_reviewed','changed_ids','unassigned_commentary_changes','statutory_units_unchanged','all_commented_units','case_2018_statutory_quote_agreement']},ensure_ascii=False))
raise SystemExit(0 if report['ok'] else 1)
