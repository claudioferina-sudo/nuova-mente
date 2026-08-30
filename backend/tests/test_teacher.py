"""Endpoint docente: overview, log tentativi, override, leaderboard."""
import uuid

from conftest import API, STUDENT_CLASS, STUDENT_PIN, TEACHER_PIN

M2_SEGMENT = "Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia"


def seeded_session(client):
    name = f"TEST Teacher {uuid.uuid4().hex[:6]}"
    login = client.post(f"{API}/auth/student", json={
        "class_code": STUDENT_CLASS, "pin": STUDENT_PIN, "student_name": name}).json()
    s = client.post(f"{API}/sessions", json={
        "user_id": login["user"]["id"], "class_code": STUDENT_CLASS, "student_name": name}).json()
    client.post(f"{API}/missions/2/attempt", json={
        "session_id": s["id"], "payload": {"option_id": "O1", "highlight": "x", "source_id": "S01"}})
    client.post(f"{API}/missions/2/attempt", json={
        "session_id": s["id"], "payload": {"option_id": "O2", "highlight": M2_SEGMENT, "source_id": "S08"}})
    return s


class TestTeacher:
    def test_overview_requires_pin(self, client):
        assert client.get(f"{API}/teacher/overview", params={"pin": "0000"}).status_code == 401
        assert client.get(f"{API}/teacher/overview").status_code == 422

    def test_overview_structure_and_class_filter(self, client):
        s = seeded_session(client)
        r = client.get(f"{API}/teacher/overview", params={"pin": TEACHER_PIN})
        assert r.status_code == 200
        d = r.json()
        assert len(d["missions"]) == 5
        assert len(d["classes"]) == 2
        assert isinstance(d["needs_review"], int)
        ids = {x["id"] for x in d["sessions"]}
        assert s["id"] in ids
        assert all("_id" not in x for x in d["sessions"])

        # filtro classe
        f = client.get(f"{API}/teacher/overview",
                       params={"pin": TEACHER_PIN, "class_code": STUDENT_CLASS}).json()
        assert all(x["class_code"] == STUDENT_CLASS for x in f["sessions"])
        assert s["id"] in {x["id"] for x in f["sessions"]}

        other = client.get(f"{API}/teacher/overview",
                           params={"pin": TEACHER_PIN, "class_code": "4BSS"}).json()
        assert s["id"] not in {x["id"] for x in other["sessions"]}

    def test_attempts_log(self, client):
        s = seeded_session(client)
        assert client.get(f"{API}/teacher/attempts/{s['id']}", params={"pin": "0000"}).status_code == 401
        r = client.get(f"{API}/teacher/attempts/{s['id']}", params={"pin": TEACHER_PIN})
        assert r.status_code == 200
        log = r.json()
        assert len(log) == 2
        assert [a["attempt_no"] for a in log] == [1, 2]
        assert log[0]["passed"] is False and log[1]["passed"] is True
        assert log[0]["mission_num"] == 2
        assert all("_id" not in a and "at" in a and "evaluator" in a for a in log)

    def test_override_updates_points_and_hours(self, client):
        s = seeded_session(client)
        sid = s["id"]
        before = client.get(f"{API}/sessions/{sid}").json()
        assert before["missions"]["2"]["points"] == 16

        # motivazione obbligatoria
        r = client.post(f"{API}/teacher/override", json={
            "pin": TEACHER_PIN, "session_id": sid, "mission_num": 2, "new_points": 20, "reason": "   "})
        assert r.status_code == 400

        # punteggio fuori scala
        r = client.post(f"{API}/teacher/override", json={
            "pin": TEACHER_PIN, "session_id": sid, "mission_num": 2, "new_points": 25, "reason": "ok"})
        assert r.status_code == 400

        # pin errato
        r = client.post(f"{API}/teacher/override", json={
            "pin": "0000", "session_id": sid, "mission_num": 2, "new_points": 20, "reason": "ok"})
        assert r.status_code == 401

        # override valido
        r = client.post(f"{API}/teacher/override", json={
            "pin": TEACHER_PIN, "session_id": sid, "mission_num": 2, "new_points": 20,
            "reason": "TEST argomentazione orale convincente"})
        assert r.status_code == 200
        d = r.json()
        assert d["missions"]["2"]["points"] == 20
        assert d["missions"]["2"]["status"] == "overridden"
        assert d["missions"]["2"]["needs_teacher_review"] is False
        assert len(d["override_log"]) == 1
        assert d["override_log"][0]["old_points"] == 16
        assert d["override_log"][0]["new_points"] == 20
        assert d["override_log"][0]["reason"] == "TEST argomentazione orale convincente"
        # bonus M2 ancora presente -> 20 + 10 = 30
        assert d["total_points"] == 30
        assert d["credits"] == 0 and d["pbl_hours"] == 0.0  # 30 <= 39

        # persistenza
        got = client.get(f"{API}/sessions/{sid}").json()
        assert got["missions"]["2"]["points"] == 20
        assert got["total_points"] == 30
        assert len(got["override_log"]) == 1

        # override a 0 -> passed False
        r2 = client.post(f"{API}/teacher/override", json={
            "pin": TEACHER_PIN, "session_id": sid, "mission_num": 2, "new_points": 0,
            "reason": "TEST annullato"}).json()
        assert r2["missions"]["2"]["passed"] is False
        assert r2["total_points"] == 10

    def test_override_missing_mission(self, client):
        s = seeded_session(client)
        r = client.post(f"{API}/teacher/override", json={
            "pin": TEACHER_PIN, "session_id": s["id"], "mission_num": 9, "new_points": 5, "reason": "x"})
        assert r.status_code == 404

    def test_leaderboard(self, client):
        r = client.get(f"{API}/teacher/leaderboard", params={"class_code": "5AIT"})
        assert r.status_code == 200
        d = r.json()
        assert d["enabled"] is True
        assert len(d["entries"]) <= 10
        pts = [e["total_points"] for e in d["entries"]]
        assert pts == sorted(pts, reverse=True)

        off = client.get(f"{API}/teacher/leaderboard", params={"class_code": "4BSS"}).json()
        assert off["enabled"] is False
        assert off["entries"] == []
