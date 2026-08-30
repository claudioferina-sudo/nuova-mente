import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shell, Masthead, Panel, GoldButton, GhostButton } from "../components/Chrome";
import { loginTeacher, teacherOverview, teacherAttempts, teacherOverride, pdfUrl } from "../lib/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { Download, ShieldCheck, AlertTriangle, ScrollText } from "lucide-react";

const cellTone = (m) => {
  if (!m) return "bg-nm-card/50 text-nm-muted";
  if (m.status === "overridden") return "bg-nm-warn/25 text-nm-ink border-nm-warn";
  if (m.passed) return "bg-nm-ok/25 text-nm-ink border-nm-ok";
  if (m.completed) return "bg-nm-warn/20 text-nm-ink border-nm-warn";
  if (m.attempts > 0) return "bg-nm-err/15 text-nm-ink border-nm-err";
  return "bg-nm-card/50 text-nm-muted";
};

export default function Teacher() {
  const nav = useNavigate();
  const [pin, setPin] = useState("");
  const [authed, setAuthed] = useState(false);
  const [err, setErr] = useState("");
  const [data, setData] = useState(null);
  const [classFilter, setClassFilter] = useState("");
  const [log, setLog] = useState(null);
  const [ovr, setOvr] = useState(null);

  const refresh = async (p = pin, cc = classFilter) => setData(await teacherOverview(p, cc || undefined));

  const doLogin = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      await loginTeacher(pin);
      setAuthed(true);
      await refresh(pin, "");
    } catch (e2) {
      setErr(e2?.response?.data?.detail || "PIN non valido");
    }
  };

  useEffect(() => { if (authed) refresh(); }, [classFilter]); // eslint-disable-line

  const sessions = useMemo(() => data?.sessions || [], [data]);

  if (!authed)
    return (
      <Shell testId="teacher-login-page">
        <Masthead eyebrow="Area riservata" title="Docente" />
        <form onSubmit={doLogin} className="card-nm rounded-2xl p-8 max-w-md" data-testid="teacher-login-form">
          <label className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted">PIN docente</label>
          <input
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            data-testid="teacher-pin"
            placeholder="••••"
            className="mono w-full mt-2 mb-5 rounded-xl border border-nm-gold/50 bg-nm-cream px-4 py-3 text-lg tracking-[0.4em]"
          />
          {err && <p className="mono text-xs text-nm-err mb-4" data-testid="teacher-error">{err}</p>}
          <div className="flex gap-3">
            <GoldButton type="submit" data-testid="teacher-login-submit">Accedi</GoldButton>
            <GhostButton type="button" onClick={() => nav("/")}>Torna al login studente</GhostButton>
          </div>
        </form>
      </Shell>
    );

  return (
    <Shell testId="teacher-page">
      <Masthead
        eyebrow="Dashboard classe &middot; Dossier 1939"
        title="Registro"
        right={
          <div className="flex items-center gap-3">
            <select
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
              data-testid="class-filter"
              className="mono text-xs rounded-full border border-nm-gold/60 bg-nm-card px-4 py-2.5"
            >
              <option value="">Tutte le classi</option>
              {(data?.classes || []).map((c) => (
                <option key={c.class_code} value={c.class_code}>{c.class_code} &middot; {c.name}</option>
              ))}
            </select>
            <GhostButton onClick={() => refresh()} data-testid="refresh-btn">Aggiorna</GhostButton>
          </div>
        }
      />

      {data?.needs_review > 0 && (
        <p className="mono text-xs text-nm-warn mb-5 flex items-center gap-2" data-testid="review-banner">
          <AlertTriangle size={14} /> {data.needs_review} valutazioni prodotte dal fallback a regole: richiedono revisione.
        </p>
      )}

      <Panel className="p-4 md:p-6 overflow-x-auto" testId="grid-panel">
        <table className="w-full min-w-[860px] border-separate border-spacing-1">
          <thead>
            <tr>
              <th className="text-left mono text-[10px] uppercase tracking-widest text-nm-muted px-2">Studente</th>
              {(data?.missions || []).map((m) => (
                <th key={m.mission_num} className="mono text-[10px] uppercase tracking-widest text-nm-muted px-1" title={m.title}>
                  M{m.mission_num}
                </th>
              ))}
              <th className="mono text-[10px] uppercase tracking-widest text-nm-muted px-2">Tot</th>
              <th className="mono text-[10px] uppercase tracking-widest text-nm-muted px-2">PBL</th>
              <th className="mono text-[10px] uppercase tracking-widest text-nm-muted px-2">Azioni</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.id} data-testid={`row-${s.id}`}>
                <td className="px-2 py-1.5">
                  <p className="text-sm text-nm-ink leading-tight">{s.student_name}</p>
                  <p className="mono text-[10px] text-nm-muted">{s.class_code}</p>
                </td>
                {(data?.missions || []).map((m) => {
                  const st = s.missions?.[String(m.mission_num)];
                  return (
                    <td key={m.mission_num} className="px-1 py-1.5">
                      <button
                        onClick={() => setOvr({ session: s, mission_num: m.mission_num, points: st?.points ?? 0, reason: "" })}
                        data-testid={`cell-${s.id}-${m.mission_num}`}
                        title={st?.feedback || "Nessun tentativo"}
                        className={`w-full rounded-lg border px-2 py-2 mono text-xs hover:ring-2 hover:ring-nm-gold transition-shadow duration-200 ${cellTone(st)}`}
                      >
                        {st?.points ?? "-"}
                        <span className="block text-[9px] opacity-70">
                          {st?.status === "overridden" ? "OVR" : ""}
                          {st?.attempts ? ` t${st.attempts}` : ""}{st?.hints_used ? " h" : ""}
                        </span>
                      </button>
                    </td>
                  );
                })}
                <td className="px-2 mono text-sm font-bold text-nm-ink text-center">{s.total_points}</td>
                <td className="px-2 mono text-xs text-nm-ink text-center">{s.pbl_hours} h</td>
                <td className="px-2">
                  <div className="flex gap-1.5 justify-end">
                    <button
                      onClick={async () => setLog({ session: s, items: await teacherAttempts(s.id, pin) })}
                      data-testid={`log-${s.id}`}
                      className="mono text-[10px] uppercase border border-nm-gold/60 rounded-full px-3 py-1.5 hover:bg-nm-gold/15 transition-colors duration-200"
                    >
                      <ScrollText size={11} className="inline -mt-0.5" /> Log
                    </button>
                    <a
                      href={pdfUrl(s.id)}
                      target="_blank"
                      rel="noreferrer"
                      data-testid={`pdf-${s.id}`}
                      className="mono text-[10px] uppercase border border-nm-gold/60 rounded-full px-3 py-1.5 hover:bg-nm-gold/15 transition-colors duration-200"
                    >
                      <Download size={11} className="inline -mt-0.5" /> PDF
                    </a>
                  </div>
                </td>
              </tr>
            ))}
            {!sessions.length && (
              <tr><td colSpan={9} className="mono text-sm text-nm-muted px-2 py-6">Nessuna sessione registrata.</td></tr>
            )}
          </tbody>
        </table>
        <div className="flex flex-wrap gap-4 mt-5 mono text-[10px] uppercase tracking-widest text-nm-muted">
          {[["bg-nm-ok/25", "superata"], ["bg-nm-warn/20", "sblocco forzato"], ["bg-nm-warn/25", "override"], ["bg-nm-err/15", "in errore"], ["bg-nm-card/50", "non iniziata"]].map(([c, l]) => (
            <span key={l} className="flex items-center gap-1.5"><span className={`w-3 h-3 rounded ${c} border border-nm-gold/40`} /> {l}</span>
          ))}
        </div>
      </Panel>

      <Dialog open={!!log} onOpenChange={() => setLog(null)}>
        <DialogContent className="bg-nm-cream border-2 border-nm-gold max-w-2xl max-h-[80vh] overflow-y-auto" data-testid="log-dialog">
          <DialogHeader><DialogTitle className="title text-xl text-nm-ink">Log tentativi &mdash; {log?.session?.student_name}</DialogTitle></DialogHeader>
          <div className="space-y-3">
            {(log?.items || []).map((a) => (
              <div key={a.id} className="card-nm rounded-xl p-4" data-testid={`log-item-${a.id}`}>
                <p className="mono text-[11px] text-nm-muted mb-1">
                  M{a.mission_num} &middot; tentativo {a.attempt_no} &middot; {a.at?.slice(0, 19).replace("T", " ")} &middot; {a.evaluator}
                </p>
                <p className="mono text-xs font-bold mb-1" style={{ color: a.passed ? "#5B7A61" : "#9C4343" }}>
                  livello {a.level} {a.passed ? "superata" : a.forced ? "sblocco forzato" : "non superata"}
                </p>
                <p className="text-sm text-nm-ink">{a.feedback}</p>
              </div>
            ))}
            {log && !log.items.length && <p className="mono text-sm text-nm-muted">Nessun tentativo.</p>}
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!ovr} onOpenChange={() => setOvr(null)}>
        <DialogContent className="bg-nm-cream border-2 border-nm-gold" data-testid="override-dialog">
          <DialogHeader>
            <DialogTitle className="title text-xl text-nm-ink">
              Override M{ovr?.mission_num} &mdash; {ovr?.session?.student_name}
            </DialogTitle>
          </DialogHeader>
          <p className="text-sm text-nm-muted mb-4 flex gap-2">
            <ShieldCheck size={15} className="text-nm-gold shrink-0 mt-0.5" />
            Il voto automatico non e' definitivo. La motivazione viene registrata nel log e stampata nel PDF.
          </p>
          <label className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted">Punti (0-20)</label>
          <input
            type="number"
            min={0}
            max={20}
            value={ovr?.points ?? 0}
            onChange={(e) => setOvr({ ...ovr, points: parseInt(e.target.value || "0", 10) })}
            data-testid="override-points"
            className="mono w-full mt-1.5 mb-4 rounded-xl border border-nm-gold/50 bg-nm-card px-4 py-2.5"
          />
          <label className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted">Motivazione (obbligatoria)</label>
          <textarea
            rows={3}
            value={ovr?.reason ?? ""}
            onChange={(e) => setOvr({ ...ovr, reason: e.target.value })}
            data-testid="override-reason"
            className="w-full mt-1.5 mb-5 rounded-xl border border-nm-gold/50 bg-nm-card px-4 py-2.5 text-base"
          />
          <div className="flex gap-3">
            <GoldButton
              disabled={!ovr?.reason?.trim()}
              onClick={async () => {
                await teacherOverride({ pin, session_id: ovr.session.id, mission_num: ovr.mission_num, new_points: ovr.points, reason: ovr.reason });
                setOvr(null);
                await refresh();
              }}
              data-testid="override-save"
            >
              Salva override
            </GoldButton>
            <GhostButton onClick={() => setOvr(null)}>Annulla</GhostButton>
          </div>
        </DialogContent>
      </Dialog>
    </Shell>
  );
}
