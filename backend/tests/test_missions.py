"""Flusso completo missioni M1..M5, hint, sblocco forzato, finish, PDF."""
import uuid

import pytest
from conftest import API, STUDENT_CLASS, STUDENT_PIN

from seed_data import M3_POOL, MISSIONS

M2_SEGMENT = "Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia"

M1_GOOD = {
    "prompt_rewrite": "Spiega le cause molteplici e i diversi piani causali dello scoppio della Seconda Guerra Mondiale nel 1939, distinguendo cause strutturali di lungo periodo e cause immediate, senza ridurre tutto alla volonta' di un singolo uomo.",
    "causes": [
        "Il Trattato di Versailles (S01) impone alla Germania riparazioni, perdite territoriali e la clausola di responsabilita' (art. 231): una causa strutturale di tipo giuridico-economico che genera revisionismo diffuso, indipendente dalle scelte di un singolo leader.",
        "La crisi del 1929 e la Grande Depressione (S02) portano la disoccupazione tedesca da 1,3 a oltre 6 milioni, erodendo il consenso ai partiti democratici di Weimar: causa strutturale economica.",
        "La crisi della Societa' delle Nazioni (S10) fra Manciuria 1931 ed Etiopia 1935-36 dimostra il fallimento della sicurezza collettiva: causa strutturale istituzionale che rende l'aggressione conveniente.",
    ],
}

M4_GOOD = (
    "La tesi che la guerra sia stata causata unicamente dalla durezza del Trattato di Versailles contiene "
    "una parte di verita': Versailles (S01) genero' effettivamente risentimento, revisionismo e il mito della "
    "pugnalata alle spalle in Germania. Tuttavia omette almeno due evidenze decisive del dossier. Prima evidenza: "
    "la crisi del 1929 (S02) porto' la disoccupazione tedesca da 1,3 a oltre 6 milioni, distruggendo il consenso "
    "ai partiti democratici di Weimar; senza questo collasso economico il NSDAP non avrebbe superato il 37% nel 1932. "
    "Seconda evidenza: la mancata reazione delle democrazie alla rimilitarizzazione della Renania (S05) e la "
    "Conferenza di Monaco (S07) mostrano che l'espansione tedesca fu resa possibile dall'appeasement, non imposta "
    "da Versailles. Quindi Versailles e' una condizione di possibilita', non una causa necessaria e sufficiente: "
    "pertanto la conclusione monocausale non regge, perche' ne consegue che senza crisi economica e senza "
    "appeasement le clausole del 1919 non avrebbero prodotto la guerra del 1939."
)

# Variante che evita il bug del fallback a regole (keyword "crisi" ripetuta):
# usata solo per poter validare il resto del flusso end-to-end.
M1_GOOD_WORKAROUND = {
    "prompt_rewrite": "Spiega le cause molteplici e i diversi piani causali dello scoppio della Seconda Guerra Mondiale nel 1939, distinguendo cause strutturali di lungo periodo e cause immediate, senza ridurre tutto alla volonta' di un singolo uomo.",
    "causes": [
        "Il Trattato di Versailles (S01) impone alla Germania riparazioni, perdite territoriali e la clausola di responsabilita' (art. 231): una causa strutturale giuridico-economica che genera revisionismo diffuso.",
        "La Grande Depressione del 1929 (S02) porta la disoccupazione tedesca da 1,3 a oltre 6 milioni, erodendo il consenso ai partiti democratici di Weimar: causa strutturale economica.",
        "Il fallimento della sicurezza collettiva della Societa' delle Nazioni (S10) fra Manciuria e Etiopia rende l'aggressione conveniente: causa strutturale istituzionale.",
    ],
}

M5_SECTIONS = {
    "contesto": "Fra le due guerre l'Europa e' segnata da un ordine fragile: Versailles (S01) crea revisionismo giuridico e territoriale, la Grande Depressione (S02) distrugge l'economia di Weimar e la Societa' delle Nazioni (S10) si rivela incapace di garantire la sicurezza collettiva.",
    "errori_ai": "L'AI ha commesso quattro errori: iper-semplificazione monocausale (tutto ridotto a Hitler), allucinazione cronologica (patto Molotov-Ribbentrop datato 1941 invece del 23 agosto 1939, cfr. S08), appiattimento dei piani causali (cause remote e immediate messe sullo stesso piano) e tesi parziale su Versailles.",
    "ricostruzione": "Le cause remote sono strutturali: Versailles (S01), la crisi del 1929 (S02), il fallimento della Societa' delle Nazioni (S10) e l'ascesa del nazismo (S03). Le cause immediate sono del 1939: il patto Molotov-Ribbentrop (S08), la crisi di Danzica e l'invasione della Polonia (S09). Le prime creano le condizioni, le seconde innescano il conflitto.",
    "verdetto": "Il conflitto nasce dall'intreccio fra condizioni strutturali e decisioni politiche del 1938-39: nessuna causa singola e' sufficiente. Il verdetto si regge su S01, S02, S08 e S09, incrociate fra loro.",
}


def new_session(client, name=None):
    name = name or f"TEST {uuid.uuid4().hex[:8]}"
    login = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": name}).json()
    r = client.post(f"{API}/sessions", json={
        "user_id": login["user"]["id"], "class_code": STUDENT_CLASS, "student_name": name})
    assert r.status_code == 200
    return r.json()


def attempt(client, num, session_id, payload):
    return client.post(f"{API}/missions/{num}/attempt",
                       json={"session_id": session_id, "payload": payload}, timeout=120)


# ---------- sessioni ----------
def test_session_create_and_resume(client):
    s = new_session(client)
    assert s["current_mission"] == 1
    assert len(s["missions"]) == 5
    assert len(s["m3_cards"]) == 8
    assert sum(1 for c in s["m3_cards"] if c["category"] == "remota") == 4
    assert "_id" not in s

    again = client.post(f"{API}/sessions", json={
        "user_id": s["user_id"], "class_code": STUDENT_CLASS, "student_name": s["student_name"]})
    assert again.status_code == 200
    assert again.json()["id"] == s["id"], "resume must return the existing session"

    got = client.get(f"{API}/sessions/{s['id']}")
    assert got.status_code == 200
    assert got.json()["id"] == s["id"]


def test_session_missions_hide_solutions(client):
    s = new_session(client)
    r = client.get(f"{API}/sessions/{s['id']}/missions")
    assert r.status_code == 200
    ms = r.json()
    assert len(ms) == 5
    for m in ms:
        assert "false_segment" not in m and "expected_source_id" not in m and "hint" not in m
    m2 = next(m for m in ms if m["mission_num"] == 2)
    assert all("correct" not in o for o in m2["options"])
    m3 = next(m for m in ms if m["mission_num"] == 3)
    assert len(m3["cards"]) == 8
    assert all("category" not in c for c in m3["cards"])


# ---------- M2 (rules, deterministico) ----------
class TestMission2:
    def test_m2_pass_with_bonus(self, client):
        s = new_session(client)
        r = attempt(client, 2, s["id"], {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"})
        assert r.status_code == 200
        d = r.json()
        assert d["passed"] is True
        assert d["level"] == 80
        assert d["points"] == 16
        assert d["bonus_awarded"] is True
        assert d["session"]["total_points"] == 26
        assert d["session"]["current_mission"] == 2 + 1
        assert d["details"] == {"option_ok": True, "segment_ok": True, "source_ok": True}
        # persistenza
        got = client.get(f"{API}/sessions/{s['id']}").json()
        assert got["missions"]["2"]["points"] == 16
        assert got["missions"]["2"]["passed"] is True
        assert got["total_points"] == 26

    def test_m2_wrong_option_fails_and_decrements_attempts(self, client):
        s = new_session(client)
        d = attempt(client, 2, s["id"], {"option_id": "O1", "highlight": M2_SEGMENT, "source_id": "S08"}).json()
        assert d["passed"] is False
        assert d["attempts"] == 1
        assert d["attempts_left"] == 2
        assert "Affermazione falsa individuata" in d["criteria_missing"]

    def test_m2_wrong_source_fails(self, client):
        s = new_session(client)
        d = attempt(client, 2, s["id"], {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S01"}).json()
        assert d["passed"] is False
        assert d["details"]["source_ok"] is False

    def test_m2_already_passed_rejects(self, client):
        s = new_session(client)
        attempt(client, 2, s["id"], {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"})
        r = attempt(client, 2, s["id"], {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"})
        assert r.status_code == 400


# ---------- M3 (rules) ----------
class TestMission3:
    def test_m3_all_correct(self, client):
        s = new_session(client)
        cats = {c["card_id"]: c["category"] for c in M3_POOL}
        assignments = {c["card_id"]: cats[c["card_id"]] for c in s["m3_cards"]}
        d = attempt(client, 3, s["id"], {"assignments": assignments}).json()
        assert d["passed"] is True
        assert d["level"] == 80
        assert d["points"] == 16
        assert d["details"]["correct_count"] == 8
        assert "8 card su 8" in d["feedback"]
        assert d["bonus_awarded"] is False, "M3 must not award bonus (bonus only on M2/M4)"

    def test_m3_six_correct_passes(self, client):
        s = new_session(client)
        cats = {c["card_id"]: c["category"] for c in M3_POOL}
        assignments = {}
        for i, c in enumerate(s["m3_cards"]):
            right = cats[c["card_id"]]
            wrong = "immediata" if right == "remota" else "remota"
            assignments[c["card_id"]] = wrong if i < 2 else right
        d = attempt(client, 3, s["id"], {"assignments": assignments}).json()
        assert d["details"]["correct_count"] == 6
        assert d["passed"] is True
        assert d["level"] == 65

    def test_m3_all_wrong_fails(self, client):
        s = new_session(client)
        cats = {c["card_id"]: c["category"] for c in M3_POOL}
        assignments = {c["card_id"]: ("immediata" if cats[c["card_id"]] == "remota" else "remota")
                       for c in s["m3_cards"]}
        d = attempt(client, 3, s["id"], {"assignments": assignments}).json()
        assert d["passed"] is False
        assert d["details"]["correct_count"] == 0
        assert d["level"] == 10


# ---------- hint + sblocco forzato ----------
class TestHintAndForcedUnlock:
    def test_hint_after_failed_attempt_applies_penalty(self, client):
        s = new_session(client)
        # tentativo 1 fallito
        attempt(client, 2, s["id"], {"option_id": "O1", "highlight": "x", "source_id": "S01"})
        h = client.post(f"{API}/missions/2/hint", json={"session_id": s["id"]})
        assert h.status_code == 200
        hd = h.json()
        assert "S08" in hd["hint"]
        assert hd["penalty"] == 5
        assert hd["mission_state"]["hints_used"] == 1
        # ora supera: 80 -> 16 base - 5 penalita' = 11
        d = attempt(client, 2, s["id"], {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"}).json()
        assert d["passed"] is True
        assert d["points"] == 11, f"expected 16-5=11, got {d['points']}"

    def test_hint_before_any_attempt_is_free(self, client):
        s = new_session(client)
        hd = client.post(f"{API}/missions/2/hint", json={"session_id": s["id"]}).json()
        assert hd["penalty"] == 0
        assert hd["mission_state"]["hints_used"] == 0
        d = attempt(client, 2, s["id"], {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"}).json()
        assert d["points"] == 16

    def test_forced_unlock_after_3_failed_attempts(self, client):
        s = new_session(client)
        bad = {"option_id": "O1", "highlight": "x", "source_id": "S01"}
        d1 = attempt(client, 2, s["id"], bad).json()
        d2 = attempt(client, 2, s["id"], bad).json()
        assert d1["forced_unlock"] is False and d2["forced_unlock"] is False
        assert d2["attempts_left"] == 1
        d3 = attempt(client, 2, s["id"], bad).json()
        assert d3["forced_unlock"] is True
        assert d3["level"] == 10
        assert d3["passed"] is False
        assert d3["points"] == 2
        assert d3["attempts_left"] == 0
        assert d3["session"]["current_mission"] == 3, "forced unlock must allow progress"
        got = client.get(f"{API}/sessions/{s['id']}").json()
        assert got["missions"]["2"]["completed"] is True
        assert got["missions"]["2"]["passed"] is False
        assert got["missions"]["2"]["level"] == 10


# ---------- M1 / M4 / M5 (LLM con fallback a regole) ----------
class TestLLMMissions:
    def test_m1_pass(self, client):
        s = new_session(client)
        d = attempt(client, 1, s["id"], M1_GOOD).json()
        assert d["passed"] is True, f"M1 should pass: {d['feedback']} / {d['criteria_missing']}"
        assert d["level"] >= 65
        assert d["evaluator"] in ("llm", "rules")
        assert d["points"] > 0

    def test_m1_trivial_fails(self, client):
        s = new_session(client)
        d = attempt(client, 1, s["id"], {"prompt_rewrite": "non lo so", "causes": ["a", "b", "c"]}).json()
        assert d["passed"] is False
        assert d["attempts_left"] == 2

    def test_m4_pass_with_bonus(self, client):
        s = new_session(client)
        d = attempt(client, 4, s["id"], {"text": M4_GOOD}).json()
        assert d["passed"] is True, f"M4 should pass: {d['feedback']} / {d['criteria_missing']}"
        assert d["level"] >= 80
        assert len(d["details"]["cited_sources"]) >= 2
        assert d["bonus_awarded"] is True

    def test_m4_empty_fails(self, client):
        s = new_session(client)
        d = attempt(client, 4, s["id"], {"text": "Versailles fu duro."}).json()
        assert d["passed"] is False

    def test_m5_requires_4_sections_and_3_sources(self, client):
        s = new_session(client)
        short = dict(M5_SECTIONS)
        short["verdetto"] = "breve"
        d = attempt(client, 5, s["id"], {"sections": short, "sources": ["S01", "S02", "S08"]}).json()
        assert d["passed"] is False
        assert d["details"]["sections_filled"] == 3

        d2 = attempt(client, 5, s["id"], {"sections": M5_SECTIONS, "sources": ["S01", "S02"]}).json()
        assert d2["passed"] is False
        assert d2["details"]["sources_selected"] == 2

    def test_m5_pass(self, client):
        s = new_session(client)
        d = attempt(client, 5, s["id"], {"sections": M5_SECTIONS,
                                         "sources": ["S01", "S02", "S08", "S09"]}).json()
        assert d["passed"] is True, f"M5 should pass: {d['feedback']} / {d['criteria_missing']}"
        assert d["details"]["sections_filled"] == 4
        assert d["details"]["sources_selected"] == 4


# ---------- sessione completa + finish + pdf ----------
class TestFullRun:
    def test_complete_all_missions_and_finish(self, client):
        s = new_session(client, name=f"TEST Full {uuid.uuid4().hex[:6]}")
        sid = s["id"]

        d1 = attempt(client, 1, sid, M1_GOOD_WORKAROUND).json()
        assert d1["passed"] is True, d1["feedback"]

        d2 = attempt(client, 2, sid, {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"}).json()
        assert d2["passed"] is True

        cats = {c["card_id"]: c["category"] for c in M3_POOL}
        assignments = {c["card_id"]: cats[c["card_id"]] for c in s["m3_cards"]}
        d3 = attempt(client, 3, sid, {"assignments": assignments}).json()
        assert d3["passed"] is True

        d4 = attempt(client, 4, sid, {"text": M4_GOOD}).json()
        assert d4["passed"] is True, d4["feedback"]

        d5 = attempt(client, 5, sid, {"sections": M5_SECTIONS, "sources": ["S01", "S02", "S08", "S09"]}).json()
        assert d5["passed"] is True, d5["feedback"]

        fin = client.post(f"{API}/sessions/{sid}/finish")
        assert fin.status_code == 200
        f = fin.json()
        assert f["finished_at"]
        assert f["bonuses"] <= 2
        expected_base = sum(f["missions"][str(i)]["points"] for i in range(1, 6))
        assert f["total_points"] == min(100, expected_base + f["bonuses"] * 10)
        assert f["credits"] in (0, 1, 2, 3, 4)
        assert f["pbl_hours"] in (0.0, 0.5, 1.0, 1.5, 2.0)
        assert f["credits_note"]
        # coerenza tabella conversione
        import scoring
        assert (f["credits"], f["pbl_hours"]) == scoring.credits_for(f["total_points"])[:2]

        # nuova sessione dopo finish (finished_at non piu' None)
        fresh = client.post(f"{API}/sessions", json={
            "user_id": s["user_id"], "class_code": STUDENT_CLASS, "student_name": s["student_name"]}).json()
        assert fresh["id"] != sid

        # PDF
        pdf = client.get(f"{API}/report/pdf/{sid}", timeout=60)
        assert pdf.status_code == 200
        assert pdf.headers["content-type"] == "application/pdf"
        assert pdf.content[:4] == b"%PDF"
        assert len(pdf.content) > 1000


def test_mission_seed_integrity():
    assert len(MISSIONS) == 5
    assert len(M3_POOL) == 16
    assert sum(1 for c in M3_POOL if c["category"] == "remota") == 8
