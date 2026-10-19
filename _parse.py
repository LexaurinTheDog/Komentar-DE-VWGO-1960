#!/usr/bin/env python3
"""Reproducible extraction from the preserved GII XML; no language-model text parsing."""
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib,json,re,shutil,difflib
W=Path(__file__).resolve().parent
S=W/'sources'
ROOT=ET.parse(S/'vwgo.xml').getroot()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def render(e):
    if e is None:return ''
    if e.tag=='BR':return '\n'
    value=e.text or ''
    for c in e:
        t=render(c)
        if c.tag in ('P','DL','table','row'):t='\n\n'+t+'\n\n'
        elif c.tag=='DT':t='\n\n'+t+' '
        elif c.tag=='DD':t=t+'\n\n'
        elif c.tag=='entry':t=t+' | '
        value+=t+(c.tail or '')
    return value

def clean(e):
    t=render(e).replace('\u00a0',' ')
    return re.sub(r'\n{3,}','\n\n', '\n'.join(re.sub(r'[\t ]+',' ',l).strip() for l in t.splitlines())).strip()
chapters=[];units=[];part='';section='';chapter=0;struct=[]
for n in ROOT.findall('norm'):
    m=n.find('metadaten');g=m.find('gliederungseinheit')
    if g is not None:
        name=g.findtext('gliederungsbez')+' — '+g.findtext('gliederungstitel')
        if len(g.findtext('gliederungskennzahl'))==3:
            part=name;section='';struct=[part]
            if name.startswith('Teil V'):
                chapter+=1;chapters.append(dict(n=chapter,slug='schluss-und-uebergang',title=name))
        else:
            section=name;struct=[part,section];chapter+=1
            chapters.append(dict(n=chapter,slug='abschnitt-'+str(chapter),title=section))
        continue
    label=m.findtext('enbez','')
    if not label or label=='Inhaltsübersicht':continue
    assert '§' in label,label
    numbers=re.findall(r'\d+[a-z]?',label)
    uid='p'+'-'.join(numbers)
    text=clean(n.find('textdaten/text/Content'))
    title=clean(m.find('titel'))
    # GII places the empty-slot disposition in titel, not Content.
    if not text:
        assert title=='(weggefallen)',(label,title)
        text=title
    notes=clean(n.find('textdaten/fussnoten/Content'))
    units.append(dict(id=uid,label=label.replace('(XXXX) ','').strip(),title='',chapter=chapter,structure=struct.copy(),text=text,notes=[notes] if notes else [],official_doknr=n.attrib['doknr'],source_title=title))
(W/'units.jsonl').write_text(''.join(json.dumps(u,ensure_ascii=False)+'\n' for u in units))
canonical=['# Verwaltungsgerichtsordnung — aus amtlicher XML extrahierter Text', 'Quelle: https://www.gesetze-im-internet.de/vwgo/xml.zip', 'XML SHA-256: '+sha(S/'vwgo.xml')]
for u in units:canonical+=['## '+u['label'],u['text'],*u['notes']]
(S/'vwgo-canonical.md').write_text('\n\n'.join(canonical)+'\n')
meta=dict(cc='de',lang='de',repo='Komentar-DE-VWGO-1960',repo_dir='/Volumes/LaCie/open-commentary/de/Komentar-DE-VWGO-1960',title='Kommentar zur Verwaltungsgerichtsordnung',source_path=str(S/'vwgo-canonical.md'),intro_file='00-einleitung.md',intro_desc='Geltungsstand, Methode und Zugang zum Verwaltungsprozess',labels=dict(text='Wortlaut der Vorschrift',chapter='Kommentarkapitel',notes='Amtliche Dokumentationsanmerkung'),chapters=chapters)
(W/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
# Independently enumerate raw norm metadata, without the extraction loop's filters/IDs.
expected=[(n.attrib['doknr'],n.findtext('metadaten/enbez')) for n in ROOT.findall('norm') if '§' in n.findtext('metadaten/enbez','')]
actual=[u['official_doknr'] for u in units]
html=(S/'gii-full.html').read_text(encoding='iso-8859-1')
report=dict(xml_sha256=sha(S/'vwgo.xml'),canonical_sha256=sha(S/'vwgo-canonical.md'),expected_official_identifiers=[x[0] for x in expected],expected_labels=[x[1] for x in expected],extracted_identifiers=actual,expected_count=len(expected),extracted_count=len(units),missing=sorted(set(x[0] for x in expected)-set(actual)),unexpected=sorted(set(actual)-set(x[0] for x in expected)),duplicates=[x for x in set(actual) if actual.count(x)>1],empty_or_repealed=[dict(id=u['id'],label=u['label'],disposition=u['text']) for u in units if len(u['text'])<75],structural_nodes=len(ROOT.findall('.//gliederungseinheit')),annex_disposition=[dict(name='Anhang EV',disposition='Nur Dokumentationsverweis in der allgemeinen Fußnote; weder eigenständige Anlage-Norm noch Anlage-Text in vollständiger VwGO-XML oder HTML. Der historische Einigungsvertrag ist keine im aktuellen VwGO-Korpus enthaltene Anlage. §§ 189–195 und weitere Schlussvorschriften vollständig extrahiert.' )],exclusions=['Inhaltsübersicht ist Navigations-/Strukturtext, keine zusätzliche Rechtsnorm.','22 Strukturknoten werden als Gliederung gespeichert, nicht als Vorschriften kommentiert.'],ok=set(actual)==set(x[0] for x in expected) and len(actual)==len(set(actual)))
(W/'completeness-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
original=Path('/Volumes/LaCie/law-intake/eu/de/gesetze/gii-vwgo.md')
if not (S/'intake-2026-10-02.md').exists():shutil.copyfile(original,S/'intake-2026-10-02.md')
old={}
for a,b in re.findall(r'^#### ([^\n]+)\n(.*?)(?=^#{1,4} |\Z)',original.read_text(),re.M|re.S):
 nums=re.findall(r'\d+[a-z]?',a)
 if '§' in a:
  body=b.split('\n\nFußnote:')[0].strip()
  if not body and '(weggefallen)' in a:body='(weggefallen)'
  old['p'+'-'.join(nums)]=body
norm=lambda t:re.sub(r'\s+',' ',t).strip()
changes=[]
for u in units:
 before=old.get(u['id'],'')
 if norm(before)!=norm(u['text']):changes.append(dict(id=u['id'],old=before,new=u['text'],classification='text_or_documentation_format_difference'))
(S/'change-map.json').write_text(json.dumps(dict(original_sha256=sha(S/'intake-2026-10-02.md'),new_xml_sha256=sha(S/'vwgo.xml'),changes=changes,missing_in_old=sorted(set(u['id'] for u in units)-set(old)),note='Normativer Textvergleich: Gliederung, amtliche Fußnoten und im Titel stehende Wegfallvermerke mechanisch getrennt. Keine normative Wortlautänderung gegenüber dem Intake; Dokumentationsstand hat sich geändert. Beide Fassungen bleiben erhalten.'),ensure_ascii=False,indent=2)+'\n')
print(len(units),'units',len(chapters),'chapters',len(changes),'differences')
