"""Health / catalogo endpoints."""
from conftest import API, STUDENT_CLASS, STUDENT_PIN, TEACHER_PIN


def test_root(client):
    r = client.get(f"{API}/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_classes(client):
    r = client.get(f"{API}/classes")
    assert r.status_code == 200
    data = r.json()
    codes = {c["class_code"] for c in data}
    assert {"5AIT", "4BSS"} <= codes
    assert all("_id" not in c for c in data)


def test_sources_12(client):
    r = client.get(f"{API}/sources")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 12
    assert {s["source_id"] for s in data} == {f"S{i:02d}" for i in range(1, 13)}
    assert all("_id" not in s for s in data)


def test_rooms(client):
    r = client.get(f"{API}/rooms")
    assert r.status_code == 200
    rooms = r.json()
    assert rooms[0]["room_id"] == "dossier-1939"
    assert rooms[0]["duration_min"] == 50


# ---------- auth ----------
def test_student_login_ok(client):
    r = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": "TEST Login Ok"})
    assert r.status_code == 200
    d = r.json()
    assert d["user"]["student_name"] == "TEST Login Ok"
    assert d["class_info"]["class_code"] == "5AIT"
    assert "_id" not in d["user"]


def test_student_login_bad_pin(client):
    r = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": "0000", "student_name": "TEST Bad"})
    assert r.status_code == 401


def test_student_login_short_name(client):
    r = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": "A"})
    assert r.status_code == 400


def test_student_login_idempotent_user(client):
    body = {"class_code": "5ait", "pin": STUDENT_PIN, "student_name": "TEST Idem User"}
    a = client.post(f"{API}/auth/student", json=body).json()
    b = client.post(f"{API}/auth/student", json=body).json()
    assert a["user"]["id"] == b["user"]["id"]


def test_teacher_login(client):
    assert client.post(f"{API}/auth/teacher", json={"pin": TEACHER_PIN}).status_code == 200
    assert client.post(f"{API}/auth/teacher", json={"pin": "9999"}).status_code == 401


def test_mission_404(client):
    r = client.post(f"{API}/missions/9/attempt", json={"session_id": "x", "payload": {}})
    assert r.status_code == 404


def test_session_404(client):
    assert client.get(f"{API}/sessions/does-not-exist").status_code == 404
