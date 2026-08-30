"""RCA unit test: il fallback a regole M1 collassa cause distinte che condividono una keyword."""
import sys

sys.path.insert(0, "/app/backend")

from llm_eval import rules_eval_m1  # noqa: E402

TEXT_GOOD = (
    "Spiega le cause molteplici dello scoppio della guerra.\n"
    "Il Trattato di Versailles (S01) impone riparazioni: causa strutturale giuridica.\n"
    "La crisi del 1929 e la Grande Depressione (S02) portano la disoccupazione a 6 milioni.\n"
    "La crisi della Societa' delle Nazioni (S10) mostra il fallimento della sicurezza collettiva.\n"
)


def test_rules_m1_collapses_distinct_causes_sharing_keyword():
    ev = rules_eval_m1(TEXT_GOOD)
    print("score:", ev.score, "passed:", ev.passed, "missing:", ev.criteria_missing)
    # 3 cause storicamente distinte e valide (Versailles, crisi 1929, Societa' delle Nazioni)
    assert ev.passed is True, (
        "BUG: rules_eval_m1 conta solo hits[0] per item, quindi 'crisi del 1929' e "
        "'crisi della Societa' delle Nazioni' collassano nella stessa keyword 'crisi' -> distinct=2"
    )
