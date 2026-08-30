"""Valutatore semantico (Claude Sonnet 4.6) con output JSON validato e fallback a regole."""
import json
import logging
import os
import re
import uuid
from typing import List, Optional

from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError

from seed_data import SOURCES, VALID_CAUSE_KEYWORDS, STRUCTURAL_KEYWORDS
from scoring import snap_level

load_dotenv(Path(__file__).parent / ".env")
logger = logging.getLogger(__name__)

MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-sonnet-4-6"
SOURCE_IDS = [s["source_id"] for s in SOURCES]


class Evaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    criteria_met: List[str] = []
    criteria_missing: List[str] = []
    feedback: str
    passed: bool = False
    evaluator: str = "llm"
    needs_teacher_review: bool = False
    bonus: bool = False


def _dossier_digest() -> str:
    return "\n".join(f"[{s['source_id']}] {s['title']} ({s['year']}): {s['body']}" for s in SOURCES)


def _cited_sources(text: str) -> List[str]:
    upper = text.upper()
    found = [sid for sid in SOURCE_IDS if sid in upper]
    for s in SOURCES:
        key = s["title"].lower().split()[0]
        if len(key) > 5 and key in text.lower() and s["source_id"] not in found:
            found.append(s["source_id"])
    return found


def _split_items(text: str) -> List[str]:
    parts = re.split(r"[\n;]+|(?:^|\s)\d[\).]\s|(?:^|\s)[-•*]\s", text)
    return [p.strip() for p in parts if len(p.strip()) > 12]


def rules_eval_m1(text: str) -> Evaluation:
    low = text.lower()
    items = _split_items(text)
    matched, structural, seen = [], [], set()
    for item in items:
        il = item.lower()
        fingerprint = re.sub(r"\s+", " ", il)[:60]
        if fingerprint in seen:
            continue
        if any(k in il for k in VALID_CAUSE_KEYWORDS):
            seen.add(fingerprint)
            matched.append(fingerprint)
            if any(k in il for k in STRUCTURAL_KEYWORDS):
                structural.append(fingerprint)
    distinct = len(matched)
    has_structural = len(structural) > 0
    passed = distinct >= 3 and has_structural
    score = 10
    if distinct >= 1:
        score = 25
    if distinct >= 3 and not has_structural:
        score = 45
    if passed:
        score = 65
    if passed and len(_cited_sources(text)) >= 2 and len(low) > 350:
        score = 80
    met, missing = [], []
    (met if distinct >= 3 else missing).append("Almeno 3 cause distinte valide")
    (met if has_structural else missing).append("Almeno 1 causa strutturale")
    return Evaluation(
        score=snap_level(score), criteria_met=met, criteria_missing=missing, passed=passed,
        feedback=("Hai individuato %d cause distinte%s." % (distinct, " incluse cause strutturali" if has_structural else ", ma nessuna strutturale")),
        evaluator="rules", needs_teacher_review=True,
    )


def rules_eval_m4(text: str) -> Evaluation:
    low = text.lower()
    cited = _cited_sources(text)
    thesis = any(k in low for k in ["versailles", "trattato", "tesi", "umiliazione", "diktat"])
    link = any(k in low for k in ["quindi", "pertanto", "perche'", "perche", "dunque", "ne consegue", "di conseguenza", "questo dimostra", "cio' mostra"])
    passed = thesis and len(cited) >= 2 and link
    score = 10
    if thesis:
        score = 25
    if thesis and cited:
        score = 45
    if passed:
        score = 80
    if passed and len(cited) >= 3 and len(low) > 600:
        score = 100
    met, missing = [], []
    (met if thesis else missing).append("Tesi avversaria riconosciuta")
    (met if len(cited) >= 2 else missing).append("Almeno 2 evidenze dal dossier")
    (met if link else missing).append("Nesso logico esplicito")
    return Evaluation(
        score=snap_level(score), criteria_met=met, criteria_missing=missing, passed=passed,
        feedback="Fonti riconosciute: %s." % (", ".join(cited) or "nessuna"),
        evaluator="rules", needs_teacher_review=True, bonus=passed and len(cited) >= 2 and link,
    )


def rules_eval_m5(text: str, sections_filled: int, sources_count: int) -> Evaluation:
    passed = sections_filled == 4 and sources_count >= 3
    score = 10
    if sections_filled >= 2:
        score = 25
    if sections_filled == 4 and sources_count >= 1:
        score = 45
    if passed:
        score = 65
    if passed and len(text) > 800:
        score = 80
    met, missing = [], []
    (met if sections_filled == 4 else missing).append("4 sezioni compilate")
    (met if sources_count >= 3 else missing).append("Almeno 3 fonti citate")
    return Evaluation(
        score=snap_level(score), criteria_met=met, criteria_missing=missing, passed=passed,
        feedback="Sezioni compilate: %d/4. Fonti selezionate: %d." % (sections_filled, sources_count),
        evaluator="rules", needs_teacher_review=True,
    )


SYSTEM_PROMPT = """Sei un valutatore didattico di storia per una scuola secondaria italiana.
Valuti la risposta di uno studente contro una rubrica, usando SOLO il dossier fornito.
Non inventi mai fatti storici e non correggi contenuto storico oltre il dossier.
Rispondi SEMPRE ed ESCLUSIVAMENTE con un oggetto JSON valido, senza testo prima o dopo, nella forma:
{"score": <int fra 0 e 100>, "criteria_met": [<string>], "criteria_missing": [<string>], "feedback": "<massimo 60 parole, in italiano semplice, rivolto allo studente, tono incoraggiante e concreto>", "passed": <bool>}
Il punteggio segue questa scala: 10 nessuna competenza; 25 individua il problema senza argomentare; 45 individua e corregge con fonte generica; 65 correzione precisa con fonte pertinente; 80 distingue piani causali con almeno 2 evidenze; 100 confutazione strutturata con uso incrociato delle fonti."""


async def llm_eval(mission: dict, student_text: str, extra: str = "") -> Optional[Evaluation]:
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key or not student_text.strip():
        return None
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=api_key,
            session_id=f"eval-{uuid.uuid4()}",
            system_message=SYSTEM_PROMPT,
        ).with_model(MODEL_PROVIDER, MODEL_NAME)

        prompt = f"""DOSSIER (fonti citabili per source_id):
{_dossier_digest()}

MISSIONE {mission['mission_num']}: {mission['title']}
OUTPUT DIFETTOSO DELL'AI: {mission['ai_output']}
COMPITO ASSEGNATO: {mission['student_action']}
CONDIZIONE DI SBLOCCO: {mission['unlock_trigger']}
RUBRICA SPECIFICA: {mission.get('rubric', '')}
{extra}

RISPOSTA DELLO STUDENTE:
\"\"\"{student_text[:6000]}\"\"\"

Valuta e rispondi solo con il JSON richiesto."""

        raw = await chat.send_message(UserMessage(text=prompt))
        text = raw if isinstance(raw, str) else str(raw)
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        data = json.loads(match.group(0))
        data["score"] = snap_level(int(data.get("score", 10)))
        ev = Evaluation(**data)
        ev.evaluator = "llm"
        return ev
    except (ValidationError, json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("LLM eval JSON non valido: %s", exc)
        return None
    except Exception as exc:  # API down / rete
        logger.warning("LLM eval non disponibile: %s", exc)
        return None
