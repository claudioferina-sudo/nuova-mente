import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Shell, Masthead, GoldButton, GhostButton, Panel } from "../components/Chrome";
import { getRooms, getSession, getMissions } from "../lib/api";
import { FileText, Target, AlertTriangle } from "lucide-react";

export default function Briefing() {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const [room, setRoom] = useState(null);
  const [session, setSession] = useState(null);
  const [missions, setMissions] = useState([]);

  useEffect(() => {
    getRooms().then((r) => setRoom(r[0]));
    getSession(sessionId).then(setSession).catch(() => nav("/escape-rooms"));
    getMissions(sessionId).then(setMissions).catch(() => {});
  }, [sessionId]); // eslint-disable-line

  const sidebar = (
    <Panel className="p-5" testId="briefing-rules">
      <h3 className="title text-sm text-nm-ink mb-4 flex items-center gap-2">
        <AlertTriangle size={14} className="text-nm-gold" /> Regole
      </h3>
      <ul className="space-y-3 text-sm text-nm-ink/90">
        {[
          "3 tentativi per missione. Al terzo errore la missione si sblocca ma vale 10/100.",
          "L'indizio al secondo tentativo costa 5 punti. Al primo errore nessuna penalita'.",
          "Bonus +10 pt: fact-checking con citazione esatta (M2) o confutazione con doppia evidenza (M4). Max 2 volte.",
          "Il timer di 50 minuti e' visibile ma non blocca nulla.",
          "Dossier chiuso: nessuna ricerca web. Solo le 12 schede interne.",
          "Il punteggio automatico non e' definitivo: il docente puo' sovrascriverlo con motivazione.",
        ].map((t) => (
          <li key={t} className="flex gap-2">
            <span className="text-nm-gold mono">&mdash;</span>
            <span>{t}</span>
          </li>
        ))}
      </ul>
    </Panel>
  );

  return (
    <Shell sidebar={sidebar} testId="briefing-page">
      <Masthead
        eyebrow="Briefing operativo"
        title={room?.title || "Dossier 1939"}
        right={
          <div className="flex gap-2">
            <GhostButton onClick={() => nav("/escape-rooms")} data-testid="back-rooms">Indietro</GhostButton>
            <GoldButton onClick={() => nav(`/missione/${sessionId}/1`)} data-testid="start-mission-btn">
              Inizia missione 1
            </GoldButton>
          </div>
        }
      />
      <Panel className="p-6 md:p-8 mb-6" testId="briefing-text">
        <div className="flex items-center gap-2 mb-4">
          <FileText size={15} className="text-nm-gold" />
          <p className="mono text-[11px] uppercase tracking-[0.25em] text-nm-muted">Classificato &middot; uso didattico</p>
        </div>
        <p className="text-lg md:text-xl leading-relaxed text-nm-ink">{room?.briefing}</p>
      </Panel>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {missions.map((m) => (
          <article key={m.mission_num} className="card-nm rounded-2xl p-5 pb-14 relative animate-rise" data-testid={`briefing-mission-${m.mission_num}`}>
            <p className="mono text-3xl font-bold text-nm-gold/70 mb-2">M{m.mission_num}</p>
            <h3 className="title text-base text-nm-ink mb-1.5 leading-tight">{m.title}</h3>
            <p className="text-sm text-nm-muted mb-3">{m.subtitle}</p>
            <p className="mono text-[11px] text-nm-ink/80 flex gap-2">
              <Target size={12} className="text-nm-gold shrink-0 mt-0.5" /> {m.unlock_trigger}
            </p>
            <div className="absolute bottom-0 left-0 right-0 bg-nm-ink/85 px-4 py-2">
              <p className="mono text-[11px] tracking-widest text-nm-cream uppercase">Max {m.max_points} punti</p>
            </div>
          </article>
        ))}
      </div>
      {session?.total_points > 0 && (
        <p className="mono text-xs text-nm-warn mt-6" data-testid="resume-note">
          Sessione ripresa: {session.total_points} punti gia' accumulati. Prossima missione: M{session.current_mission}.
        </p>
      )}
    </Shell>
  );
}
