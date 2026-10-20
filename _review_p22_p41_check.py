"""Reproducible checks for exactly p22–p41, independent of prose length."""
from pathlib import Path
import collections,hashlib,json,re,subprocess,xml.etree.ElementTree as E
W=Path(__file__).resolve().parent;S=W/'sources/review-p22-p41';ids=[f'p{i}' for i in range(22,42)]
units=[json.loads(s) for s in (W/'units.jsonl').read_text().splitlines() if s.strip()]
byid={u['id']:u for u in units};r=E.parse(S/'vwgo.xml').getroot();nodes={n.attrib['doknr']:n for n in r};norm=lambda s:re.sub(r'\s+','',s).replace('\u00ad','')
source_map=[]
for ident in ids:
 u=byid[ident];n=nodes[u['official_doknr']];c=n.find('textdaten/text/Content');text=''.join(c.itertext()) if c is not None else ''
 if not text.strip():text=''.join(n.find('metadaten/titel').itertext())
 source_map.append(dict(id=ident,official_label=n.findtext('metadaten/enbez'),official_doknr=n.attrib['doknr'],text_matches_xml=norm(text)==norm(u['text']),statutory_sha256=hashlib.sha256(u['text'].encode()).hexdigest(),raw_node_sha256=hashlib.sha256(E.tostring(n)).hexdigest()))
def blocks(s):return {k:v.strip() for k,v in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',s,re.M|re.S)}
cur={};before={};dups=[]
for p in sorted((W/'commentary').glob('*.md')):
 b=blocks(p.read_text());dups.extend(set(cur)&set(b));cur.update(b)
 old=subprocess.run(['git','show','83744f3:commentary/'+p.name],cwd=W,capture_output=True,check=True,text=True).stdout;before.update(blocks(old))
changed=[k for k in cur if cur[k]!=before[k]];unassigned=[k for k in changed if k not in ids]
paras=collections.defaultdict(list)
for k in ids:
 for p in cur[k].split('\n\n'):
  if len(p)>140:paras[norm(p)].append(k)
repeats=[v for v in paras.values() if len(v)>1]
casechecks={}
for stem,docket in [('6B2-04','6 B 2.04'),('10PKH1-22','10 PKH 1.22'),('6C6-23','6 C 6.23')]:
 j=json.loads((S/('case-'+stem+'-firecrawl.json')).read_text());md=j['markdown'].replace('\u00ad','');casechecks[stem]=j['metadata']['statusCode']==200 and docket in md and 'ECLI:DE:BVerwG:' in md and len(md)>10000
fragments=['vor Beginn des Geschäftsjahres','die Reihenfolge, in der die ehrenamtlichen Richter zu den Sitzungen heranzuziehen sind','bei unvorhergesehener Verhinderung','eine Hilfsliste aus ehrenamtlichen Richtern aufgestellt werden','die am Gerichtssitz oder in seiner Nähe wohnen']
quote30=all(norm(t) in norm(byid['p30']['text']) and norm(t) in norm((S/'local-wbre202300391.md').read_text()) for t in fragments)
report=dict(reviewed_ids=ids,units_reviewed=20,baseline_work_commit='83744f3',official_xml='sources/review-p22-p41/vwgo.xml',official_xml_sha256=hashlib.sha256((S/'vwgo.xml').read_bytes()).hexdigest(),fresh_xml_identical_to_authoring=(S/'vwgo.xml').read_bytes()==(W/'sources/vwgo.xml').read_bytes(),source_map=source_map,changed_ids=changed,unassigned_commentary_changes=unassigned,statutory_units_unchanged=(W/'units.jsonl').read_bytes()==subprocess.run(['git','show','83744f3:units.jsonl'],cwd=W,check=True,capture_output=True).stdout,all_commented_units=len(cur),missing_commentary=sorted(set(byid)-set(cur)),duplicate_commentary=dups,repeated_assigned_full_paragraphs=repeats,case_fulltext_identity_checks=casechecks,case_2023_section30_operative_fragment_agreement=quote30,case_2023_fragments=fragments,case_2023_comparison_limit='Court paragraph paraphrases the statute, inserting citations and omitting Verwaltungsgerichts for the OVG; no full verbatim historical edition agreement claimed.',external_xml_unchanged_since_previous_version_check={n:(S/(n+'.xml')).read_bytes()==(W/'sources/review-p1-p21'/(n+'.xml')).read_bytes() for n in ['gvg','drig']},limits='Technical checks do not establish substantive correctness; per-unit assessments are in review-result.json. Exactly assigned commentary units reviewed.')
report['ok']=all(x['text_matches_xml'] for x in source_map) and all(casechecks.values()) and quote30 and all(report['external_xml_unchanged_since_previous_version_check'].values()) and report['fresh_xml_identical_to_authoring'] and report['statutory_units_unchanged'] and not any([unassigned,dups,repeats,report['missing_commentary']])
(S/'review-source-map.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['ok','units_reviewed','changed_ids','unassigned_commentary_changes','statutory_units_unchanged','case_fulltext_identity_checks','case_2023_section30_operative_fragment_agreement']},ensure_ascii=False))
raise SystemExit(0 if report['ok'] else 1)
