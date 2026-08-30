# PRD — Nuova-Mente / Escape Room "Dossier 1939"

## Problem statement originale (sintesi fedele)
Escape room didattica in 5 missioni in cui lo studente smonta gli output di un'AI storicamente inaffidabile,
accumula punti (max 100) e li converte in crediti di autonomia e ore di PBL. Web app React + Tailwind,
desktop-first per LIM/laboratorio, usabile su tablet. Errori storici scriptati su DB (l'LLM non inventa
contenuto storico); l'LLM fa solo valutazione semantica delle risposte aperte (M1, M4, M5) e feedback in
lingua semplice. Voto automatico non definitivo (status auto | overridden). Dossier chiuso: 12 schede interne
citabili per source_id; la citazione e' condizione di sblocco. Auth: codice classe + PIN (studenti), PIN docente.

## Scelte utente
- Timer 50 min visibile e NON bloccante
- M3: pool di 16 card, ne vengono estratte 8 (4 remote + 4 immediate) per sessione
- Valutatore: Claude Sonnet 4.6 via Emergent Universal Key
- Auth: solo PIN (studenti codice classe + PIN, docente PIN)
- Contenuti dossier e falsi storici generati dall'agente, revisionabili dal docente

## Architettura
- Backend FastAPI (`/app/backend`): `server.py` (endpoint + motore sessione), `seed_data.py` (12 fonti,
  5 missioni, pool 16 card, classi, PIN docente), `scoring.py` (rubrica, bonus/penalita', crediti PBL),
  `llm_eval.py` (Claude Sonnet 4.6 + fallback a regole con `needs_teacher_review`), `pdf_report.py` (reportlab)
- MongoDB collections: `users`, `classes`, `rooms`, `missions`, `sources`, `sessions`, `attempts`, `overrides`
- Frontend React JSX (`/app/frontend/src`): pagine `Login`, `Rooms`, `Briefing`, `Mission`, `Escape`, `Teacher`;
  componenti `Chrome` (shell/masthead/bottoni/stamp), `HUD` (timer/punteggio/indizi + mission rail),
  `Dossier` (drawer 12 schede + source picker), `missions/MissionForms` (M1..M5)
- Endpoint: `/api/auth/student`, `/api/auth/teacher`, `/api/rooms`, `/api/sources`, `/api/sessions`,
  `/api/sessions/{id}`, `/api/sessions/{id}/missions`, `/api/missions/{n}/attempt`, `/api/missions/{n}/hint`,
  `/api/sessions/{id}/finish`, `/api/teacher/overview`, `/api/teacher/attempts/{id}`, `/api/teacher/override`,
  `/api/leaderboard`, `/api/report/pdf/{id}`

## Personas
- Studente istituto professionale, secondaria II grado: gioca, cita fonti, riceve feedback semplice
- Docente di storia: dashboard classe, log tentativi, override motivato, PDF per il registro

## Requisiti core (statici)
1. 5 missioni con blocco dialogo output AI -> azione studente -> trigger di sblocco
2. 3 tentativi per missione, poi sblocco forzato a livello 10
3. Hint dal 2o tentativo = -5 pt; nessuna penalita' al 1o errore
4. Bonus +10 (M2 citazione esatta, M4 doppia evidenza), max 2 per sessione, cap 100
5. Rubrica 10/25/45/65/80/100 e conversione punteggio -> crediti -> ore PBL
6. Override docente obbligatoriamente motivato e tracciato nel log e nel PDF
7. Dossier chiuso, nessuna ricerca web

## Implementato (30/08/2026)
- Seed completo: 12 schede fonte (Versailles, 1929, nazismo, riarmo, Renania, Anschluss, Monaco,
  Molotov-Ribbentrop, 1 settembre 1939, Societa' delle Nazioni, Spagna, Patto d'Acciaio), 5 missioni, pool 16 card
- Auth codice classe + PIN (5AIT / 4BSS, PIN 1939) e PIN docente (1918); ripresa sessione automatica
- Motore sessione con tentativi, hint, sblocco forzato, persistenza `current_mission`, HUD timer non bloccante
- UI missioni: M1 testo guidato, M2 evidenziazione + choice + citazione fonte, M3 drag&drop accessibile
  da tastiera, M4 testo libero, M5 editor 4 sezioni + checklist fonti
- Validatore semantico Claude Sonnet 4.6 con JSON validato Pydantic e fallback a regole + flag revisione
- Scoring, bonus, penalita', conversione crediti PBL, schermata Escape
- Dashboard docente: griglia studenti x missioni con colori semantici, log tentativi, override motivato, PDF
- Leaderboard opt-in per classe

## Backlog prioritizzato
- P0: nessuno aperto
- P1: revisione dei contenuti del dossier da parte di un docente di storia prima del rilascio in classe;
  editor contenuti (fonti/missioni) dalla dashboard docente
- P1: blocco ulteriori tentativi dopo lo sblocco forzato lato UI (backend gia' chiude la missione)
- P2: SSO d'istituto via OIDC; export CSV di classe; vista gruppo; accessibilita' WCAG completa e test screen reader
- P2: seconda escape room ("Guerra Fredda", card gia' presente disabilitata)

## Prossimi task
1. Far revisionare il dossier a un docente di storia e correggere i testi delle schede
2. Editor docente per fonti e missioni
3. Export CSV registro classe
