#!/usr/bin/env python3
"""Enumerate every official XML norm independently of _parse.py's selection loop."""
from pathlib import Path
import collections, hashlib, json, re, sys, xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent
source=W/'sources/vwgo.xml'
r=ET.parse(source).getroot()
assert r.tag=='dokumente' and r.findtext('norm/metadaten/jurabk')=='VwGO'
units=[json.loads(line) for line in (W/'units.jsonl').read_text().splitlines() if line.strip()]
inventory=[];expected=[];unknown=[];annexes=[];entry_formulas=[]
for node in r:
 if node.tag!='norm':
  unknown.append(dict(tag=node.tag));continue
 metadata=node.find('metadaten'); label=metadata.findtext('enbez','')
 body=node.find('textdaten/text/Content')
 text=''.join(body.itertext()).strip() if body is not None else ''
 record=dict(official_doknr=node.attrib['doknr'],label=label,has_operative_content=bool(text))
 if metadata.find('gliederungseinheit') is not None:
  record['kind']='structure'
  record['structure']=ET.tostring(metadata.find('gliederungseinheit'),encoding='unicode')
  if text:unknown.append(record)
 elif label=='Inhaltsübersicht':record['kind']='navigation'
 elif re.fullmatch(r'(?:\(XXXX\) )?§{1,2} \d+[a-z]?(?: (?:bis|und) \d+[a-z]?)?',label):
  record['kind']='numbered_provision';expected.append(record)
 elif re.search(r'Anlage|Anhang',label,re.I):
  record['kind']='annex';annexes.append(record);unknown.append(record)
 elif label=='Eingangsformel':
  record['kind']='eingangsformel';entry_formulas.append(record);unknown.append(record)
 elif node.attrib['doknr']==r.attrib['doknr'] and not label and not text:
  record['kind']='act_metadata_and_documentary_notes'
 else:
  record['kind']='unclassified';unknown.append(record)
 inventory.append(record)
expected_labels=[e['label'] for e in expected];parsed_labels=[u['label'] for u in units]
expected_ids=[e['official_doknr'] for e in expected];parsed_ids=[u.get('official_doknr') for u in units]
dups=lambda xs:[x for x,n in collections.Counter(xs).items() if n>1]
by_id={e['official_doknr']:e['label'] for e in expected}
mismatch=[dict(id=u.get('official_doknr'),expected=by_id.get(u.get('official_doknr')),parsed=u['label']) for u in units if by_id.get(u.get('official_doknr'))!=u['label']]
html=(W/'sources/gii-full.html').read_text(encoding='iso-8859-1')
annex_disposition=[dict(label='Anhang EV',source_location='norm[1]/textdaten/fussnoten/Content',
  disposition='Documentary reference only. No annex norm or operative annex content exists in this complete XML; HTML contains the same one general-footnote reference, and official index has no annex link. No historical annex text is synthesized.',
  xml_annex_nodes=annexes,html_reference_count=html.count('Anhang EV'))]
report=dict(source_path='sources/vwgo.xml',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 expected_identifiers=expected_ids,parsed_identifiers=parsed_ids,expected_labels=expected_labels,parsed_labels=parsed_labels,
 expected_count=len(expected),parsed_count=len(units),raw_norm_count=len(inventory),classification_counts=dict(collections.Counter(e['kind'] for e in inventory)),
 missing=sorted(set(expected_labels)-set(parsed_labels)),extra=sorted(set(parsed_labels)-set(expected_labels)),
 missing_doknr=sorted(set(expected_ids)-set(parsed_ids)),extra_doknr=sorted(set(parsed_ids)-set(expected_ids)),
 duplicate_official_doknr=dups([e['official_doknr'] for e in inventory]),duplicate_expected_labels=dups(expected_labels),
 duplicate_parsed_labels=dups(parsed_labels),duplicate_parsed_ids=dups([u['id'] for u in units]),
 label_doknr_mismatches=mismatch,source_order_preserved=expected_ids==parsed_ids,
 unknown_nodes=unknown,all_nodes=inventory,annex_disposition=annex_disposition,
 eingangsformel=dict(present=bool(entry_formulas),nodes=entry_formulas,unnumbered_operative_nodes=[e for e in inventory if not e['label'] and e['has_operative_content']],
  disposition='Verified absence in current full XML and HTML; no text invented.'),
 historical_versions=dict(repeated_official_labels=dups(expected_labels),repeated_official_doknr=dups([e['official_doknr'] for e in inventory]),
  assessment='One consolidated current XML document, one node per official identifier. Historical transition rules and repealed slots retained; no concatenation of date versions. Intake comparison in sources/change-map.json.'))
report['ok']=not any(report[k] for k in ['missing','extra','missing_doknr','extra_doknr','duplicate_official_doknr','duplicate_expected_labels','duplicate_parsed_labels','duplicate_parsed_ids','label_doknr_mismatches','unknown_nodes']) and report['source_order_preserved'] and len(inventory)==len(list(r))
(W/'independent-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['ok','raw_norm_count','classification_counts','expected_count','parsed_count','missing','extra','label_doknr_mismatches','unknown_nodes']},ensure_ascii=False))
sys.exit(0 if report['ok'] else 1)
