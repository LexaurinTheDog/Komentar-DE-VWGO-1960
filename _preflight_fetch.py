#!/usr/bin/env python3
"""Re-fetch official evidence without replacing the manuscript's dated snapshots."""
from pathlib import Path
import datetime, hashlib, json, urllib.request, urllib.error, zipfile, io
import xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent
S=W/'sources'/'preflight-2026-10-20'; S.mkdir(exist_ok=True)
requests=[
 ('vwgo.zip','https://www.gesetze-im-internet.de/vwgo/xml.zip','zip'),
 ('gii-index.html','https://www.gesetze-im-internet.de/vwgo/','html'),
 ('gii-full.html','https://www.gesetze-im-internet.de/vwgo/BJNR000170960.html','html'),
 ('amendment-2026-152.pdf','https://www.recht.bund.de/bgbl/1/2026/152/regelungstext.pdf?__blob=publicationFile','pdf'),
 ('amendment-2026-111.pdf','https://www.recht.bund.de/bgbl/1/2026/111/regelungstext.pdf?__blob=publicationFile','pdf')]
records=[]
for name,url,kind in requests:
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'OpenCommentary-SourceVerification/1.0'}),timeout=45) as r:
   body=r.read(); status=r.status; headers=dict(r.headers); final=r.url
 except urllib.error.HTTPError as e:
  body=e.read(); status=e.code; headers=dict(e.headers); final=url
 path=S/name; path.write_bytes(body)
 rec=dict(url=url,accessed_at=stamp,http_status=status,content_type=headers.get('Content-Type',headers.get('content-type')),path=str(path.relative_to(W)),sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),final_url=final,response_headers=headers)
 try:
  assert status==200,('HTTP',status)
  if kind=='zip':
   assert body.startswith(b'PK\x03\x04'),'ZIP magic absent'
   with zipfile.ZipFile(io.BytesIO(body)) as z:
    members=[n for n in z.namelist() if n.lower().endswith('.xml')]
    assert len(members)==1,members
    xml=z.read(members[0]); root=ET.fromstring(xml)
    assert root.tag=='dokumente' and root.attrib['doknr']=='BJNR000170960'
    assert root.findtext('norm/metadaten/jurabk')=='VwGO'
    (S/'vwgo.xml').write_bytes(xml)
    rec.update(xml_member=members[0],xml_sha256=hashlib.sha256(xml).hexdigest(),xml_path=str((S/'vwgo.xml').relative_to(W)))
   check='ZIP magic, archive CRC, one XML member parsed, dokumente/doknr/jurabk identity verified'
  elif kind=='pdf':
   assert body.startswith(b'%PDF-'),'PDF magic absent'
   check='PDF magic verified; pdftotext/page-count validation recorded separately'
  else:
   assert b'<html' in body.lower() and b'Verwaltungsgerichtsordnung' in body,'Expected HTML act absent'
   check='HTML with expected act title verified'
  rec.update(accepted=True,format_validation=check)
 except Exception as e: rec.update(accepted=False,format_validation=str(e))
 records.append(rec)
 (S/'fetch-log.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 print(name,status,rec['sha256'],rec['accepted'],flush=True)
v=json.loads((W/'sources/verification.json').read_text())
v['requests'].extend(records)
v['preflight_recheck']=dict(decisive_date=v['authoring_date'],checked_on='2026-10-20',fetch_log=str((S/'fetch-log.json').relative_to(W)),all_requests_accepted=all(x['accepted'] for x in records))
(W/'sources/verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
