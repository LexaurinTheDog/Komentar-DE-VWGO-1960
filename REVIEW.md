# Zusammenstellung der dokumentierten Teilprüfungen

Am **20. Oktober 2026** wurde der technische Buchstand aus dem bestehenden Prüfledger zusammengestellt. Die elf früheren begrenzten zweiten Durchsichten erfassen **216 unterschiedliche Normeinheiten**, entsprechend sämtlichen Einheiten in `units.jsonl`. Dieser Finalisierungslauf hat **keine neue juristische Einzelprüfung** durchgeführt und **keinen der 216 Kommentarblöcke geändert**. Er bescheinigt keine externe anwaltliche Freigabe und erklärt das Gesamtbuch nicht für abschließend freigegeben.

Die vorhandenen Einzelbewertungen, Korrekturen und Quellenzuordnungen werden in [review-result.json](review-result.json) zusammengeführt. Der unveränderte [Ledger](batch-review-ledger.json) bewahrt die ursprünglichen Berichte. Für jede Charge wurden dessen Inhaltsfingerprint, genaue ID-Liste, Normtext-Hashes und lokaler Einzelbericht gegen den aktuellen Stand geprüft. Ein Fingerprint belegt die Identität des geprüften Materials, nicht seine juristische Richtigkeit. Die früheren Berichtstexte bleiben in [REVIEW-history.md](REVIEW-history.md) erhalten; ihre damaligen Reichweitenangaben sind historische Checkpoints.

| Charge | Stabile IDs | Einheiten | Bericht mit Einzelfeststellungen | Inhaltsfingerprint |
| --- | --- | ---: | --- | --- |
| 1 | p1–p21 | 20 | [Einzelbericht](sources/review-p1-p21/review-result.json) | bestätigt |
| 2 | p22–p41 | 20 | [Einzelbericht](sources/review-p22-p41/review-result.json) | bestätigt |
| 3 | p42–p56 | 20 | [Einzelbericht](sources/review-p42-p56/review-result.json) | bestätigt |
| 4 | p56a–p74 | 20 | [Einzelbericht](sources/review-p56a-p74/review-result.json) | bestätigt |
| 5 | p75–p87c | 20 | [Einzelbericht](sources/review-p75-p87c/review-result.json) | bestätigt |
| 6 | p88–p105 | 20 | [Einzelbericht](sources/review-p88-p105/review-result.json) | bestätigt |
| 7 | p106–p124a | 20 | [Einzelbericht](sources/review-p106-p124a/review-result.json) | bestätigt |
| 8 | p125–p141 | 20 | [Einzelbericht](sources/review-p125-p141/review-result.json) | bestätigt |
| 9 | p142–p160 | 20 | [Einzelbericht](sources/review-p142-p160/review-result.json) | bestätigt |
| 10 | p161–p180 | 20 | [Einzelbericht](sources/review-p161-p180/review-result.json) | bestätigt |
| 11 | p181-182–p195 | 16 | [Einzelbericht](sources/review-p181-p195/review-result.json) | bestätigt |

Keine ID fehlt oder erscheint doppelt. Die [Zusammenstellungsprüfung](finalization-report.json) enthält die vollständigen IDs und Quellennachweise. Ihre Aussage ist die belegte Zusammenführung abgeschlossener Teilprüfungen; sie ist keine zusätzliche unabhängige Gesamtbegutachtung.

Der Rechtsstichtag bleibt **19. Oktober 2026**. Der erneute direkte amtliche [Abruf vom 20. Oktober](sources/finalize-2026-10-20/fetch-log.json) ergab für VwGO-ZIP/XML, Index, Voll-HTML und die beiden Änderungsverkündungen HTTP 200 und bytegenaue Übereinstimmung mit den Manuskriptquellen. PDF-Signatur, Seitenbaum und Textextraktion sowie ZIP-Signatur, CRC und XML-Identität wurden geprüft. Die tatsächlichen Änderungs- und Inkrafttretensartikel wurden erneut gelesen, siehe [Versionsbewertung](sources/finalize-2026-10-20/version-assessment.json). Die ergänzende Firecrawl-Portalausgabe ist als Cachetreffer vom 19. Oktober offengelegt und trägt keinen neuen Aktualitätsnachweis.

Die [unabhängige Strukturermittlung](independent-coverage.json) klassifiziert alle 240 XML-Knoten: 216 Normeinheiten, 22 Strukturknoten, Inhaltsübersicht und Metadaten. Sie vergleicht amtliche Dokumentnummern, exakte Bezeichnungen einschließlich der drei `(XXXX)`-Sammelstellen und die Reihenfolge. Keine operative Anlage oder Eingangsformel wurde ausgelassen; der dokumentarische Hinweis „Anhang EV“ ist gesondert erläutert. Alle weggefallenen und historischen Kurzvermerke sowie Schluss- und Übergangsbestimmungen bleiben sichtbar. [_parse.py](_parse.py) erzeugt denselben Normbestand und kanonischen Text reproduzierbar.

Die [technische Prüfung](quality-report.json) vergleicht den gesamten Gesetzeswortlaut zusätzlich mit dem amtlichen HTML, erhält Listenhierarchien und Fußnoten, zählt sämtliche Kommentarblöcke und prüft lokale Links sowie längere wiederholte Absätze. Die strikte Prüfung steht in [validation.json](validation.json); sie muss 100 % Wortlautübereinstimmung ohne Fehler ergeben. Diese Kontrollen ersetzen keine Rechtsprüfung.

**25 Fallkarten** enthalten die selektiv geprüften amtlichen Entscheidungen, Randnummern oder amtlichen Abschnitte, Kontext und Übertragungsgrenzen. [Fallzuordnung](sources/authority-coverage.json), [Suchprotokoll](sources/search-log.json) und die verlinkten Chargenberichte dokumentieren die tatsächliche Auswahl. Nicht vollständig gelesene Suchtreffer gelten nicht als Autoritäten. Kein Anspruch auf vollständige Rechtsprechungs-, Folgeentscheidungs-, Fachgesetz- oder Landesrechtsabdeckung; historische materielle Rechtslagen werden nicht als heutiges Recht ausgegeben.

Bei der Zusammenstellung wurden veraltete Metadaten der Einleitung berichtigt: elf statt zehn Prüfchargen, 216 statt 200 erfasste Einheiten und 25 statt 23 Fallkarten. Die Belege und ursprünglichen Einzelberichte blieben erhalten. Offen bleiben die ausgewiesenen methodischen Grenzen und jede spätere Freigabeentscheidung; es bestehen keine bekannten ungelösten technischen Blocker dieses Auftrags. Das Buch bleibt ein lokal erstellter Arbeitsentwurf.
