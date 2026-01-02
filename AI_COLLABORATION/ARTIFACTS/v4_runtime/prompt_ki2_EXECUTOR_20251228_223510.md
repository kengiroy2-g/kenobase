AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Daten Erweiterung
TASK-ID: DIST-004
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 22:33:10] DIST-004 - ARCHITECT (ki1)

### Summary
- Analysiert vorhandene Module: regions.py (106 LOC), regional_affinity.py (571 LOC), popularity_correlation.py (484 LOC)
- REGIONAL_DATA_RESEARCH.md dokumentiert Datenlage: direkte Regionaldaten NICHT verfuegbar
- Proxy-Methode via Gewinner-Anzahl (GQ-Daten) ist bereits konzipiert
- Pressemitteilungen als neue Datenquelle identifiziert (16 Landeslotterien)
- Lotto Hessen API entdeckt (services.lotto-hessen.de) - JSON-Endpunkte fuer KENO
- 3 Erweiterungs-Schritte definiert: Scraper, Popularity-Proxy, EuroJackpot-Mapping

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_DIST-004_ARCHITECT_20251228_223010.md

## [2025-12-28 22:35:10] DIST-004 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---  **status: APPROVED**  **task: DIST-004**  **role: PROXY**  **phase: PROXY_PLAN**  **reviewed_handoff: ki1_DIST-004_ARCHITECT_20251228_223010.md**    ---    # Proxy Review Summary    Plan wurde als **APPROVED** bewertet. Hauptgruende:    1. **Fokussierter Scope:** Nur Phase B ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-004_PROXY_PLAN_20251228_223310.md



MANDATORY WORKFLOW (do first, every task incl docs):
1) Context-sync: read AI_COLLABORATION/SYSTEM_STATUS.json + relevant ADR/Docs; run git status --porcelain.
2) Data claims must cite artifact path + filter + N + repro command (no placeholders).
3) Zero != missing: if unclear, mark UNVERIFIED.
4) Line refs must be verified via: 
l -ba <file> | sed -n 'a,bp'.
5) Deliverable must include: changes + summary + repro commands + CURRENT_STATUS update.
6) No assumptions: verify from current repo snapshot.

RULE CONFIRMATION REQUIRED:
- Include "Rule Confirmation" block in output (CONFIRMED/UNVERIFIED).
- State granularity + semantics + target metric before analysis.

WORKING SET (nur relevante Dateien):
- (leer)

WORKING SET POLICY (enforced in ARCHITECT/PROXY/VALIDATOR):
- Read() ausserhalb WORKING SET kann technisch geblockt sein.
- Wenn du eine Datei ausserhalb brauchst: nutze Grep/Glob, dann fordere sie im Handoff an:

WORKING_SET_REQUEST:
- relative/path/to/file1
- relative/path/to/file2
(max 6)


WORKDIR:
- Du bist bereits im Repo-Root: C:\Users\kenfu\Documents\keno_base
- Vermeide Set-Location/cd auf \\?\\-Pfade (Windows long-path Prefix kann Tools verwirren)
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-BlÃ¶cke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
---
**status: APPROVED**
**task: DIST-004**
**role: PROXY**
**phase: PROXY_PLAN**
**reviewed_handoff: ki1_DIST-004_ARCHITECT_20251228_223010.md**

---

# Proxy Review Summary

Plan wurde als **APPROVED** bewertet. Hauptgruende:

1. **Fokussierter Scope:** Nur Phase B (Popularity-Proxy) - keine unrealistischen Scraper-Plaene
2. **Vorhandene Infrastruktur:** `popularity_correlation.py` (484 LOC) hat bereits:
   - `load_gq_popularity()` fuer GQ-Daten
   - `BIRTHDAY_NUMBERS` Set (1-31)
   - Rolling-Window Analyse
3. **Messbare Criteria:** r > 0.3, p < 0.05, 30-Ziehungen Window
4. **Keine Known Bugs:** Kein globaler Threshold (BUG-001), kein fehlender Orchestrator (BUG-003)

## Handoff erstellt

```
AI_COLLABORATION/HANDOFFS/ki0_DIST-004_PROXY_PLAN_20251228_223310.md
```

## Naechster Schritt

Task kann an **EXECUTOR** weitergeleitet werden mit WORKING_SET:
- `kenobase/analysis/popularity_correlation.py`
- `kenobase/analysis/regional_affinity.py`
- `AI_COLLABORATION/KNOWLEDGE_BASE/REGIONAL_DATA_RESEARCH.md`
- `scripts/analyze_hyp003_regional.py`
- `tests/unit/test_popularity_correlation.py`


FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-004_PROXY_PLAN_20251228_223310.md

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: DIST-004
role: EXECUTOR
phase: EXECUTOR
files_changed: []
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki2_DIST-004_EXECUTOR_20251228_223510.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
