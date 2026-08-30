"""RCA: recompute() non persiste current_mission -> l'avanzamento si perde al reload/ripresa."""
import uuid

from conftest import API, STUDENT_CLASS, STUDENT_PIN

M2_SEGMENT = "Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia"


def test_current_mission_is_persisted_after_pass(client):
    name = f"TEST CurMis {uuid.uuid4().hex[:6]}"
    login = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": name}).json()
    s = client.post(f"{API}/sessions", json={
        "user_id": login["user"]["id"], "class_code": STUDENT_CLASS, "student_name": name}).json()
    assert s["current_mission"] == 1

    r = client.post(f"{API}/missions/2/attempt", json={
        "session_id": s["id"],
        "payload": {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"}}).json()
    assert r["passed"] is True
    # la risposta dell'API dichiara l'avanzamento
    assert r["session"]["current_mission"] == 3

    # ...ma il DB no: recompute() non include current_mission nell'$set
    persisted = client.get(f"{API}/sessions/{s['id']}").json()
    assert persisted["current_mission"] == 3, (
        "BUG: current_mission non persistito (DB=%s). recompute() aggiorna solo "
        "missions/bonuses/total_points/credits/pbl_hours/credits_note."
        % persisted["current_mission"]
    )


def test_current_mission_persisted_after_forced_unlock(client):
    name = f"TEST CurMisF {uuid.uuid4().hex[:6]}"
    login = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": name}).json()
    s = client.post(f"{API}/sessions", json={
        "user_id": login["user"]["id"], "class_code": STUDENT_CLASS, "student_name": name}).json()
    bad = {"option_id": "O1", "highlight": "x", "source_id": "S01"}
    for _ in range(3):
        r = client.post(f"{API}/missions/2/attempt", json={"session_id": s["id"], "payload": bad}).json()
    assert r["forced_unlock"] is True
    persisted = client.get(f"{API}/sessions/{s['id']}").json()
    assert persisted["missions"]["2"]["completed"] is True  # questo si persiste
    assert persisted["current_mission"] == 3, (
        "BUG: dopo lo sblocco forzato current_mission resta %s nel DB -> alla ripresa "
        "lo studente viene rimandato alla missione gia' sbloccata" % persisted["current_mission"]
    )
