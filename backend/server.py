import logging
import os
import random
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

import scoring
from llm_eval import Evaluation, llm_eval, rules_eval_m1, rules_eval_m4, rules_eval_m5, _cited_sources
from pdf_report import build_report
from seed_data import CLASSES, M3_POOL, MISSIONS, ROOM, SOURCES, TEACHER_PIN

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="Nuova-Mente Dossier 1939")
api = APIRouter(prefix="/api")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NO_ID = {"_id": 0}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def mission_meta(num: int) -> dict:
    for m in MISSIONS:
        if m["mission_num"] == num:
            return m
    raise HTTPException(404, "Missione inesistente")


def public_mission(m: dict, session: Optional[dict] = None) -> dict:
    out = {k: v for k, v in m.items() if k not in ("false_segment", "expected_source_id", "rubric", "hint")}
    if m.get("options"):
        out["options"] = [{"option_id": o["option_id"], "text": o["text"]} for o in m["options"]]
    if m["mission_num"] == 3 and session:
        cards = session.get("m3_cards") or []
        out["cards"] = [{"card_id": c["card_id"], "text": c["text"]} for c in cards]
    return out


def draw_m3_cards() -> List[dict]:
    remote = [c for c in M3_POOL if c["category"] == "remota"]
    imm = [c for c in M3_POOL if c["category"] == "immediata"]
    cards = random.sample(remote, 4) + random.sample(imm, 4)
    random.shuffle(cards)
    return cards


def empty_missions() -> Dict[str, dict]:
    return {
        str(m["mission_num"]): {
            "mission_num": m["mission_num"], "attempts": 0, "hints_used": 0, "points": 0,
            "level": None, "passed": False, "completed": False, "status": "auto",
            "feedback": "", "evaluator": None, "needs_teacher_review": False, "bonus_awarded": False,
        }
        for m in MISSIONS
    }


async def recompute(session: dict) -> dict:
    ms = session["missions"]
    bonuses = min(scoring.MAX_BONUSES, sum(1 for m in ms.values() if m.get("bonus_awarded")))
    session["bonuses"] = bonuses
    session["total_points"] = scoring.session_total(ms, bonuses)
    credits, hours, note = scoring.credits_for(session["total_points"])
    session["credits"] = credits
    session["pbl_hours"] = hours
    session["credits_note"] = note
    await db.sessions.update_one({"id": session["id"]}, {"$set": {
        "missions": ms, "bonuses": bonuses, "total_points": session["total_points"],
        "credits": credits, "pbl_hours": hours, "credits_note": note,
        "current_mission": session.get("current_mission", 1),
    }})
    return session


async def get_session(session_id: str) -> dict:
    s = await db.sessions.find_one({"id": session_id}, NO_ID)
    if not s:
        raise HTTPException(404, "Sessione non trovata")
    return s


# ---------- models ----------
class StudentLogin(BaseModel):
    class_code: str
    pin: str
    student_name: str


class TeacherLogin(BaseModel):
    pin: str


class AttemptIn(BaseModel):
    session_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class HintIn(BaseModel):
    session_id: str


class OverrideIn(BaseModel):
    pin: str
    session_id: str
    mission_num: int
    new_points: int
    reason: str


# ---------- seed ----------
@app.on_event("startup")
async def seed():
    await db.rooms.update_one({"room_id": ROOM["room_id"]}, {"$set": ROOM}, upsert=True)
    for s in SOURCES:
        await db.sources.update_one({"source_id": s["source_id"]}, {"$set": s}, upsert=True)
    for m in MISSIONS:
        await db.missions.update_one({"mission_num": m["mission_num"]}, {"$set": m}, upsert=True)
    for c in CLASSES:
        await db.classes.update_one({"class_code": c["class_code"]}, {"$set": c}, upsert=True)
    logger.info("Seed dossier completato")


# ---------- auth & catalogo ----------
@api.get("/")
async def root():
    return {"app": "Dossier 1939", "status": "ok"}


@api.get("/classes")
async def list_classes():
    return await db.classes.find({}, NO_ID).to_list(100)


@api.post("/auth/student")
async def auth_student(body: StudentLogin):
    cls = await db.classes.find_one({"class_code": body.class_code.strip().upper()}, NO_ID)
    if not cls or cls["pin"] != body.pin.strip():
        raise HTTPException(401, "Codice classe o PIN non valido")
    name = body.student_name.strip()
    if len(name) < 2:
        raise HTTPException(400, "Inserisci nome e cognome")
    user = await db.users.find_one({"class_code": cls["class_code"], "student_name": name}, NO_ID)
    if not user:
        user = {"id": str(uuid.uuid4()), "class_code": cls["class_code"], "student_name": name,
                "role": "student", "created_at": now_iso()}
        await db.users.insert_one(dict(user))
    return {"user": user, "class_info": cls}


@api.post("/auth/teacher")
async def auth_teacher(body: TeacherLogin):
    if body.pin.strip() != TEACHER_PIN:
        raise HTTPException(401, "PIN docente non valido")
    return {"role": "teacher", "pin": TEACHER_PIN,
            "classes": await db.classes.find({}, NO_ID).to_list(100)}


@api.get("/rooms")
async def rooms():
    return await db.rooms.find({}, NO_ID).to_list(20)


@api.get("/sources")
async def sources():
    return await db.sources.find({}, NO_ID).to_list(50)


# ---------- sessioni ----------
@api.post("/sessions")
async def create_or_resume(body: Dict[str, str]):
    user_id, class_code = body.get("user_id"), body.get("class_code")
    student_name = body.get("student_name")
    existing = await db.sessions.find_one({"user_id": user_id, "room_id": ROOM["room_id"], "finished_at": None}, NO_ID)
    if existing:
        return existing
    session = {
        "id": str(uuid.uuid4()), "user_id": user_id, "student_name": student_name,
        "class_code": class_code, "room_id": ROOM["room_id"], "started_at": now_iso(),
        "finished_at": None, "current_mission": 1, "missions": empty_missions(),
        "m3_cards": draw_m3_cards(), "bonuses": 0, "total_points": 0, "credits": 0,
        "pbl_hours": 0.0, "credits_note": "", "override_log": [], "duration_min": ROOM["duration_min"],
    }
    await db.sessions.insert_one(dict(session))
    return session


@api.get("/sessions/{session_id}")
async def read_session(session_id: str):
    return await get_session(session_id)


@api.get("/sessions/{session_id}/missions")
async def session_missions(session_id: str):
    s = await get_session(session_id)
    return [public_mission(m, s) for m in MISSIONS]


@api.post("/missions/{num}/hint")
async def take_hint(num: int, body: HintIn):
    meta = mission_meta(num)
    s = await get_session(body.session_id)
    st = s["missions"][str(num)]
    if st["completed"]:
        # missione gia' chiusa: l'indizio e' consultabile senza penalita' retroattive
        return {"hint": meta["hint"], "penalty": 0, "mission_state": st}
    if st["hints_used"] == 0 and st["attempts"] >= 1:
        st["hints_used"] = 1  # hint dal 2o tentativo: -5 pt applicati al punteggio finale
    s["missions"][str(num)] = st
    await recompute(s)
    return {"hint": meta["hint"], "penalty": scoring.HINT_PENALTY if st["hints_used"] else 0, "mission_state": st}


@api.post("/missions/{num}/attempt")
async def attempt(num: int, body: AttemptIn):
    meta = mission_meta(num)
    s = await get_session(body.session_id)
    key = str(num)
    st = s["missions"][key]
    if st["completed"]:
        raise HTTPException(400, "Missione gia' chiusa: punteggio consolidato")
    st["attempts"] += 1
    payload = body.payload
    ev, details = await evaluate(meta, payload, s)

    forced = False
    if not ev.passed and st["attempts"] >= scoring.MAX_ATTEMPTS:
        forced = True
        ev.score = 10
        ev.feedback = "Sblocco forzato dopo 3 tentativi. La missione e' aperta al proseguimento ma senza competenza dimostrata: rivedi le fonti con il docente."

    if ev.passed or forced:
        st["completed"] = True
        st["passed"] = bool(ev.passed)
        st["level"] = ev.score
        st["points"] = scoring.mission_points(ev.score, st["hints_used"])
        st["bonus_awarded"] = bool(ev.bonus and ev.passed and num in (2, 4))
        s["current_mission"] = min(5, num + 1) if num < 5 else 5
    st["feedback"] = ev.feedback
    st["evaluator"] = ev.evaluator
    st["needs_teacher_review"] = ev.needs_teacher_review
    st["criteria_met"] = ev.criteria_met
    st["criteria_missing"] = ev.criteria_missing
    s["missions"][key] = st

    await db.attempts.insert_one({
        "id": str(uuid.uuid4()), "session_id": s["id"], "student_name": s["student_name"],
        "class_code": s["class_code"], "mission_num": num, "attempt_no": st["attempts"],
        "payload": payload, "level": ev.score, "passed": bool(ev.passed), "forced": forced,
        "evaluator": ev.evaluator, "feedback": ev.feedback, "criteria_met": ev.criteria_met,
        "criteria_missing": ev.criteria_missing, "at": now_iso(),
    })
    await recompute(s)
    return {
        "passed": bool(ev.passed), "forced_unlock": forced, "level": ev.score,
        "level_label": scoring.level_label(ev.score), "level_descriptor": scoring.level_descriptor(ev.score),
        "points": st["points"], "attempts": st["attempts"],
        "attempts_left": max(0, scoring.MAX_ATTEMPTS - st["attempts"]),
        "feedback": ev.feedback, "criteria_met": ev.criteria_met, "criteria_missing": ev.criteria_missing,
        "evaluator": ev.evaluator, "needs_teacher_review": ev.needs_teacher_review,
        "bonus_awarded": st.get("bonus_awarded", False), "details": details, "session": s,
    }


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


async def evaluate(meta: dict, payload: dict, session: dict):
    num = meta["mission_num"]
    details: Dict[str, Any] = {}

    if num == 1:
        causes = payload.get("causes") or []
        text = (payload.get("prompt_rewrite") or "") + "\n" + "\n".join(causes)
        ev = await llm_eval(meta, text, extra="Verifica in particolare il numero di cause distinte e la presenza di almeno una causa strutturale.")
        if ev is None:
            ev = rules_eval_m1(text)
        return ev, details

    if num == 2:
        choice = payload.get("option_id")
        highlight = _norm(payload.get("highlight", ""))
        source_id = (payload.get("source_id") or "").upper()
        correct_option = next((o["option_id"] for o in meta["options"] if o["correct"]), None)
        target = _norm(meta["false_segment"])
        seg_ok = len(highlight) >= 15 and (highlight in target or target in highlight or
                                           len(set(highlight.split()) & set(target.split())) >= 5)
        exact = highlight == target
        src_ok = source_id == meta["expected_source_id"]
        ok_choice = choice == correct_option
        details = {"option_ok": ok_choice, "segment_ok": seg_ok, "source_ok": src_ok}
        passed = ok_choice and seg_ok and src_ok
        score = 10
        if ok_choice:
            score = 25
        if ok_choice and (seg_ok or src_ok):
            score = 45
        if passed:
            score = 65 if not exact else 80
        met = [k for k, v in {"Affermazione falsa individuata": ok_choice, "Segmento evidenziato corretto": seg_ok, "Fonte citata corretta": src_ok}.items() if v]
        missing = [k for k, v in {"Affermazione falsa individuata": ok_choice, "Segmento evidenziato corretto": seg_ok, "Fonte citata corretta": src_ok}.items() if not v]
        fb = ("Fact-checking completo: hai isolato l'errore e lo hai documentato con la fonte giusta."
              if passed else "Manca ancora: " + ", ".join(missing).lower() + ".")
        return Evaluation(score=score, criteria_met=met, criteria_missing=missing, feedback=fb,
                          passed=passed, evaluator="rules", bonus=passed and exact), details

    if num == 3:
        assignments = payload.get("assignments") or {}
        cards = {c["card_id"]: c for c in (session.get("m3_cards") or [])}
        correct = [cid for cid, cat in assignments.items() if cards.get(cid, {}).get("category") == cat]
        n = len(correct)
        details = {"correct_count": n, "total": len(cards),
                   "per_card": {cid: cards.get(cid, {}).get("category") == cat for cid, cat in assignments.items()}}
        passed = n >= 6
        score = 10 if n < 4 else (25 if n < 6 else (65 if n < 8 else 80))
        return Evaluation(score=score, criteria_met=[f"{n}/8 card classificate correttamente"],
                          criteria_missing=[] if passed else ["Almeno 6/8 classificazioni corrette"],
                          feedback=(f"{n} card su 8 nella colonna giusta." + ("" if passed else " Rileggi la definizione di causa remota.")),
                          passed=passed, evaluator="rules"), details

    if num == 4:
        text = payload.get("text") or ""
        ev = await llm_eval(meta, text, extra="Le evidenze valide sono solo quelle riconducibili alle schede del dossier.")
        rules = rules_eval_m4(text)
        if ev is None:
            ev = rules
        else:
            ev.bonus = rules.bonus and ev.score >= 80
            ev.passed = ev.passed and rules.passed
        details = {"cited_sources": _cited_sources(text)}
        return ev, details

    sections = payload.get("sections") or {}
    selected = payload.get("sources") or []
    filled = sum(1 for v in sections.values() if len((v or "").strip()) >= 40)
    text = "\n\n".join(f"{k.upper()}: {v}" for k, v in sections.items())
    ev = await llm_eval(meta, text + "\n\nFONTI SELEZIONATE: " + ", ".join(selected),
                        extra=f"Sezioni compilate: {filled}/4. Fonti selezionate: {len(selected)}. Se le sezioni compilate sono meno di 4 o le fonti meno di 3, passed deve essere false.")
    rules = rules_eval_m5(text, filled, len(selected))
    if ev is None:
        ev = rules
    else:
        ev.passed = ev.passed and rules.passed
    details = {"sections_filled": filled, "sources_selected": len(selected)}
    return ev, details


@api.post("/sessions/{session_id}/finish")
async def finish(session_id: str):
    s = await get_session(session_id)
    if not s.get("finished_at"):
        s["finished_at"] = now_iso()
        await db.sessions.update_one({"id": session_id}, {"$set": {"finished_at": s["finished_at"]}})
    await recompute(s)
    return s


# ---------- docente ----------
def check_teacher(pin: str):
    if pin.strip() != TEACHER_PIN:
        raise HTTPException(401, "PIN docente non valido")


@api.get("/teacher/overview")
async def overview(pin: str, class_code: Optional[str] = None):
    check_teacher(pin)
    query = {"class_code": class_code} if class_code else {}
    sessions = await db.sessions.find(query, NO_ID).sort("started_at", -1).to_list(300)
    classes = await db.classes.find({}, NO_ID).to_list(100)
    return {
        "classes": classes,
        "missions": [{"mission_num": m["mission_num"], "title": m["title"]} for m in MISSIONS],
        "sessions": sessions,
        "needs_review": sum(1 for s in sessions for m in s["missions"].values() if m.get("needs_teacher_review")),
    }


@api.get("/teacher/attempts/{session_id}")
async def attempts_log(session_id: str, pin: str):
    check_teacher(pin)
    return await db.attempts.find({"session_id": session_id}, NO_ID).sort("at", 1).to_list(200)


@api.post("/teacher/override")
async def override(body: OverrideIn):
    check_teacher(body.pin)
    if not body.reason.strip():
        raise HTTPException(400, "La motivazione dell'override e' obbligatoria")
    if not 0 <= body.new_points <= scoring.MAX_MISSION_POINTS:
        raise HTTPException(400, "Punteggio fuori scala (0-20)")
    s = await get_session(body.session_id)
    key = str(body.mission_num)
    st = s["missions"].get(key)
    if not st:
        raise HTTPException(404, "Missione inesistente")
    entry = {"id": str(uuid.uuid4()), "mission_num": body.mission_num, "old_points": st["points"],
             "new_points": body.new_points, "reason": body.reason.strip(), "at": now_iso()}
    st["points"] = body.new_points
    st["status"] = "overridden"
    st["needs_teacher_review"] = False
    st["completed"] = True
    st["passed"] = body.new_points > 0
    s["missions"][key] = st
    s["override_log"] = (s.get("override_log") or []) + [entry]
    await db.overrides.insert_one({**entry, "session_id": s["id"]})
    await db.sessions.update_one({"id": s["id"]}, {"$set": {"override_log": s["override_log"]}})
    await recompute(s)
    return s


@api.get("/leaderboard")
async def leaderboard(class_code: str):
    cls = await db.classes.find_one({"class_code": class_code}, NO_ID)
    if not cls or not cls.get("leaderboard_enabled"):
        return {"enabled": False, "entries": []}
    sessions = await db.sessions.find({"class_code": class_code}, NO_ID).to_list(300)
    entries = sorted(({"student_name": s["student_name"], "total_points": s.get("total_points", 0)} for s in sessions),
                     key=lambda x: -x["total_points"])[:10]
    return {"enabled": True, "entries": entries}


@api.get("/report/pdf/{session_id}")
async def report_pdf(session_id: str):
    s = await get_session(session_id)
    await recompute(s)
    buf = build_report(s, [{"mission_num": m["mission_num"], "title": m["title"]} for m in MISSIONS])
    filename = f"dossier1939_{(s.get('student_name') or 'studente').replace(' ', '_')}.pdf"
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown():
    client.close()
