"""Edge case: indizio richiesto DOPO che la missione e' stata superata."""
import uuid

from conftest import API, STUDENT_CLASS, STUDENT_PIN

SEG = "Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia"


def _session(client):
    name = f"TEST HintAfter {uuid.uuid4().hex[:6]}"
    login = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": name}).json()
    return client.post(f"{API}/sessions", json={
        "user_id": login["user"]["id"], "class_code": STUDENT_CLASS, "student_name": name}).json()


def test_hint_after_pass_must_not_reduce_points(client):
    s = _session(client)
    r = client.post(f"{API}/missions/2/attempt", json={
        "session_id": s["id"], "payload": {"option_id": "O2", "highlight": SEG, "source_id": "S08"}}).json()
    assert r["passed"] is True and r["points"] == 16

    # lo studente clicca "Chiedi indizio" a missione GIA' superata (il bottone resta visibile in UI)
    client.post(f"{API}/missions/2/hint", json={"session_id": s["id"]})
    after = client.get(f"{API}/sessions/{s['id']}").json()
    assert after["missions"]["2"]["points"] == 16, (
        "BUG: l'indizio richiesto dopo il superamento riduce retroattivamente i punti a %s "
        "(server.py take_hint applica la penalita' se completed=True)"
        % after["missions"]["2"]["points"]
    )
    assert after["total_points"] == 26
