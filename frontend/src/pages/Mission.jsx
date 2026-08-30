import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Shell, Masthead, Panel, GoldButton, GhostButton, Stamp } from "../components/Chrome";
import { HUD, MissionRail } from "../components/HUD";
import { DossierDrawer } from "../components/Dossier";
import { M1, M2, M3, M4, M5 } from "../missions/MissionForms";
import { getMissions, getSession, getSources, postAttempt, postHint, finishSession } from "../lib/api";
import { Lightbulb, CheckCircle2, XCircle, Cpu, ScrollText, ArrowRight } from "lucide-react";

export default function Mission() {
  const { sessionId, num } = useParams();
  const nav = useNavigate();
  const n = parseInt(num, 10);
  const [session, setSession] = useState(null);
  const [missions, setMissions] = useState([]);
  const [sources, setSources] = useState([]);
  const [drawer, setDrawer] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [hint, setHint] = useState("");

  const load = useCallback(async () => {
    const [s, ms, src] = await Promise.all([getSession(sessionId), getMissions(sessionId), getSources()]);
    setSession(s);
    setMissions(ms);
    setSources(src);
  }, [sessionId]);

  useEffect(() => { load().catch(() => nav("/escape-rooms")); }, [load, nav]);
  useEffect(() => { setResult(null); setHint(""); }, [n]);

  const mission = missions.find((m) => m.mission_num === n);
  const state = session?.missions?.[String(n)] || {};

  const submit = async (payload) => {
    setBusy(true);
    setResult(null);
    try {
      const r = await postAttempt(n, { session_id: sessionId, payload });
      setResult(r);
      setSession(r.session);
    } catch (e) {
      setResult({ error: e?.response?.data?.detail || "Errore di valutazione" });
    } finally {
      setBusy(false);
    }
  };

  const askHint = async () => {
    const r = await postHint(n, sessionId);
    setHint(r.hint);
    await load();
  };

  const next = async () => {
    if (n === 5) {
      await finishSession(sessionId);
      return nav(`/escape/${sessionId}`);
    }
    nav(`/missione/${sessionId}/${n + 1}`);
  };

  if (!mission) return <Shell testId="mission-loading"><p className="mono text-sm">Caricamento dossier...</p></Shell>;

  const forms = {
    1: <M1 mission={mission} onSubmit={submit} busy={busy} />,
    2: <M2 mission={mission} sources={sources} onSubmit={submit} busy={busy} />,
    3: <M3 mission={mission} onSubmit={submit} busy={busy} result={result} />,
    4: <M4 mission={mission} onSubmit={submit} busy={busy} />,
    5: <M5 mission={mission} sources={sources} onSubmit={submit} busy={busy} />,
  };

  const sidebar = (
    <div className="space-y-5">
      <Panel className="p-5" testId="mission-goal">
        <h3 className="title text-sm text-nm-ink mb-3">Obiettivo</h3>
        <p className="text-sm text-nm-ink/90 mb-4">{mission.student_action}</p>
        <div className="hairline mb-4" />
        <p className="mono text-[10px] uppercase tracking-[0.2em] text-nm-muted mb-1">Trigger di sblocco</p>
        <p className="mono text-[11px] text-nm-ink">{mission.unlock_trigger}</p>
      </Panel>
      <Panel className="p-5" testId="inventory-panel">
        <h3 className="title text-sm text-nm-ink mb-3">Inventario indizi</h3>
        <p className="mono text-[11px] text-nm-muted mb-3">
          Tentativi: {state.attempts || 0}/3 &middot; indizi usati: {state.hints_used || 0}
        </p>
        {hint ? (
          <p className="text-sm bg-nm-gold/20 rounded-xl px-3 py-2.5 border border-nm-gold/50" data-testid="hint-text">{hint}</p>
        ) : state.completed ? (
          <p className="mono text-[11px] text-nm-muted">Missione chiusa: punteggio consolidato.</p>
        ) : (
          <GhostButton className="w-full" onClick={askHint} data-testid="hint-btn">
            <span className="inline-flex items-center gap-2">
              <Lightbulb size={13} /> Chiedi indizio {(state.attempts || 0) >= 1 ? "(-5 pt)" : "(gratis)"}
            </span>
          </GhostButton>
        )}
      </Panel>
      <Panel className="p-5" testId="rubric-panel">
        <h3 className="title text-sm text-nm-ink mb-3">Rubrica</h3>
        <ul className="space-y-1.5 mono text-[11px] text-nm-muted">
          {[["10", "Sblocco forzato"], ["25", "Iniziale"], ["45", "Base"], ["65", "Intermedio"], ["80", "Avanzato"], ["100", "Esperto"]].map(([v, l]) => (
            <li key={v} className={`flex justify-between ${state.level === parseInt(v, 10) ? "text-nm-gold font-bold" : ""}`}>
              <span>{l}</span><span>{v}</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );

  return (
    <Shell sidebar={sidebar} testId={`mission-page-${n}`}>
      <div className="mb-6"><HUD session={session} onOpenDossier={() => setDrawer(true)} /></div>
      <MissionRail
        missions={missions}
        state={session?.missions}
        current={n}
        unlockedUpTo={session?.current_mission || 1}
        onSelect={(k) => nav(`/missione/${sessionId}/${k}`)}
      />
      <Masthead eyebrow={`Missione ${n} di 5 · ${mission.subtitle}`} title={mission.title} />

      <Panel className="p-6 md:p-8" testId="mission-body">
        <div className="flex items-center gap-2 mb-5">
          <Cpu size={14} className="text-nm-gold" />
          <p className="mono text-[10px] uppercase tracking-[0.25em] text-nm-muted">Blocco dialogo &middot; output AI &rarr; azione studente &rarr; sblocco</p>
        </div>
        {(state.completed && !result) && (
          <div className="mb-6 flex flex-wrap items-center gap-4" data-testid="mission-closed-banner">
            <Stamp text={state.passed ? "Missione superata" : "Sblocco forzato"} tone={state.passed ? "ok" : "warn"} />
            <p className="mono text-sm text-nm-ink">{state.points}/20 pt</p>
            {n < 5 && (
              <GoldButton onClick={() => nav(`/missione/${sessionId}/${n + 1}`)} data-testid="continue-btn">
                <span className="inline-flex items-center gap-2">Missione {n + 1} <ArrowRight size={13} /></span>
              </GoldButton>
            )}
            {n === 5 && (
              <GoldButton onClick={next} data-testid="continue-btn">
                <span className="inline-flex items-center gap-2">Chiudi il dossier <ScrollText size={13} /></span>
              </GoldButton>
            )}
          </div>
        )}
        {forms[n]}
      </Panel>

      {result && !result.error && (
        <Panel className="p-6 mt-6 animate-rise" testId="result-panel">
          <div className="flex flex-wrap items-center gap-4 mb-4">
            {result.passed ? (
              <Stamp text="Missione superata" tone="ok" />
            ) : result.forced_unlock ? (
              <Stamp text="Sblocco forzato" tone="warn" />
            ) : (
              <Stamp text="Non superata" tone="err" />
            )}
            <p className="mono text-sm text-nm-ink">
              {result.level_label} &middot; {result.points}/20 pt
              {result.bonus_awarded && <span className="text-nm-ok font-bold ml-2" data-testid="bonus-flag">+10 BONUS</span>}
            </p>
            <p className="mono text-[11px] text-nm-muted ml-auto" data-testid="evaluator-flag">
              valutatore: {result.evaluator === "llm" ? "semantico (Claude Sonnet 4.6)" : "regole (fallback)"}
              {result.needs_teacher_review && " · revisione docente richiesta"}
            </p>
          </div>
          <p className="text-base text-nm-ink mb-4" data-testid="result-feedback">{result.feedback}</p>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              {(result.criteria_met || []).map((c) => (
                <p key={c} className="mono text-[11px] text-nm-ok flex gap-2 items-start mb-1.5">
                  <CheckCircle2 size={13} className="mt-0.5 shrink-0" /> {c}
                </p>
              ))}
            </div>
            <div>
              {(result.criteria_missing || []).map((c) => (
                <p key={c} className="mono text-[11px] text-nm-err flex gap-2 items-start mb-1.5">
                  <XCircle size={13} className="mt-0.5 shrink-0" /> {c}
                </p>
              ))}
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            {(result.passed || result.forced_unlock) ? (
              <GoldButton onClick={next} data-testid="next-mission-btn">
                <span className="inline-flex items-center gap-2">
                  {n === 5 ? <>Chiudi il dossier ed esci <ScrollText size={13} /></> : <>Missione {n + 1} <ArrowRight size={13} /></>}
                </span>
              </GoldButton>
            ) : (
              <>
                <p className="mono text-xs text-nm-warn" data-testid="attempts-left">
                  Tentativi rimasti: {result.attempts_left}. Correggi la risposta e riprova.
                </p>
                {(session?.current_mission || 1) > n && (
                  <GoldButton onClick={() => nav(`/missione/${sessionId}/${n + 1}`)} data-testid="next-mission-btn">
                    <span className="inline-flex items-center gap-2">Missione {n + 1} <ArrowRight size={13} /></span>
                  </GoldButton>
                )}
              </>
            )}
          </div>
        </Panel>
      )}
      {result?.error && (
        <p className="mono text-sm text-nm-err mt-5" data-testid="result-error">{result.error}</p>
      )}

      <DossierDrawer open={drawer} onOpenChange={setDrawer} sources={sources} />
    </Shell>
  );
}
