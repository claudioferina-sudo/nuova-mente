"""Rubrica, scoring, bonus/penalita' e conversione crediti PBL."""

RUBRIC_LEVELS = [
    (10, "Sblocco forzato", "Fase superata dopo 3 tentativi falliti, nessuna competenza dimostrata"),
    (25, "Iniziale", "Individua il problema ma non lo argomenta ne' cita fonti"),
    (45, "Base", "Individua e corregge, fonte citata in modo generico"),
    (65, "Intermedio", "Correzione precisa + fonte pertinente, argomentazione lineare"),
    (80, "Avanzato", "Distingue piani causali, argomenta con almeno 2 evidenze coerenti"),
    (100, "Esperto", "Confutazione strutturata, uso critico e incrociato delle fonti"),
]

MAX_MISSION_POINTS = 20
MAX_SESSION_POINTS = 100
MAX_BONUSES = 2
BONUS_POINTS = 10
HINT_PENALTY = 5
MAX_ATTEMPTS = 3


def snap_level(raw: int) -> int:
    """Porta un punteggio 0-100 al livello di rubrica piu' vicino per difetto."""
    level = 10
    for value, _label, _desc in RUBRIC_LEVELS:
        if raw >= value:
            level = value
    return level


def level_label(level: int) -> str:
    for value, label, _desc in RUBRIC_LEVELS:
        if value == level:
            return label
    return "Iniziale"


def level_descriptor(level: int) -> str:
    for value, _label, desc in RUBRIC_LEVELS:
        if value == level:
            return desc
    return ""


def mission_points(level: int, hints_used: int) -> int:
    base = round(level / 100 * MAX_MISSION_POINTS)
    penalty = HINT_PENALTY * max(0, hints_used)
    return max(0, base - penalty)


def credits_for(total: int):
    if total <= 39:
        return 0, 0.0, "Recupero guidato: ripetizione delle missioni non superate"
    if total <= 59:
        return 1, 0.5, "1 credito di autonomia, 0,5 h di PBL sbloccate"
    if total <= 79:
        return 2, 1.0, "2 crediti di autonomia, 1 h di PBL sbloccata"
    if total <= 94:
        return 3, 1.5, "3 crediti di autonomia, 1,5 h di PBL sbloccate"
    return 4, 2.0, "4 crediti di autonomia, 2 h di PBL sbloccate"


def session_total(missions: dict, bonuses: int) -> int:
    base = sum(int(m.get("points") or 0) for m in missions.values())
    return min(MAX_SESSION_POINTS, base + bonuses * BONUS_POINTS)
