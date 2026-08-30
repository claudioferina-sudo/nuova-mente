import React, { useEffect, useState } from "react";
import { Timer, Trophy, Lightbulb, FolderOpen } from "lucide-react";
import { GhostButton } from "./Chrome";

const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

export const HUD = ({ session, onOpenDossier }) => {
  const [elapsed, setElapsed] = useState(0);
  const durationSec = (session?.duration_min || 50) * 60;

  useEffect(() => {
    if (!session?.started_at) return;
    const start = new Date(session.started_at).getTime();
    const tick = () => setElapsed(Math.max(0, Math.floor((Date.now() - start) / 1000)));
    tick();
    const i = setInterval(tick, 1000);
    return () => clearInterval(i);
  }, [session?.started_at]);

  const remaining = durationSec - elapsed;
  const over = remaining <= 0;
  const hints = Object.values(session?.missions || {}).reduce((a, m) => a + (m.hints_used || 0), 0);

  return (
    <div className="card-nm rounded-2xl px-5 py-4 flex flex-wrap items-center gap-x-8 gap-y-3" data-testid="hud">
      <div className="flex items-center gap-2">
        <Timer size={16} className={over ? "text-nm-err" : "text-nm-gold"} />
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.2em] text-nm-muted">Tempo</p>
          <p className={`mono text-lg font-bold ${over ? "text-nm-err animate-pulse-soft" : "text-nm-ink"}`} data-testid="hud-timer">
            {over ? `+${fmt(elapsed - durationSec)}` : fmt(remaining)}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Trophy size={16} className="text-nm-gold" />
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.2em] text-nm-muted">Punteggio</p>
          <p className="mono text-lg font-bold text-nm-ink" data-testid="hud-score">
            {session?.total_points ?? 0}<span className="text-nm-muted text-sm">/100</span>
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Lightbulb size={16} className="text-nm-gold" />
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.2em] text-nm-muted">Indizi usati</p>
          <p className="mono text-lg font-bold text-nm-ink" data-testid="hud-hints">{hints}</p>
        </div>
      </div>
      {session?.bonuses > 0 && (
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.2em] text-nm-muted">Bonus</p>
          <p className="mono text-lg font-bold text-nm-ok" data-testid="hud-bonus">+{session.bonuses * 10}</p>
        </div>
      )}
      <div className="ml-auto">
        <GhostButton onClick={onOpenDossier} data-testid="open-dossier-btn">
          <span className="inline-flex items-center gap-2"><FolderOpen size={14} /> Dossier fonti</span>
        </GhostButton>
      </div>
      {over && (
        <p className="mono text-[11px] text-nm-warn w-full">
          Tempo consigliato superato: il timer non blocca la sessione, puoi continuare.
        </p>
      )}
    </div>
  );
};

export const MissionRail = ({ missions, state, current, unlockedUpTo, onSelect }) => (
  <nav className="flex flex-wrap gap-2 mb-6" data-testid="mission-rail">
    {missions.map((m) => {
      const st = state?.[String(m.mission_num)] || {};
      const unlocked = m.mission_num <= Math.max(current || 1, unlockedUpTo || 1);
      const tone = st.passed
        ? "bg-nm-ok/20 border-nm-ok text-nm-ink"
        : st.completed
        ? "bg-nm-warn/20 border-nm-warn text-nm-ink"
        : unlocked
        ? "bg-nm-card border-nm-gold text-nm-ink"
        : "bg-nm-card/40 border-nm-gold/25 text-nm-muted";
      return (
        <button
          key={m.mission_num}
          disabled={!unlocked}
          onClick={() => onSelect(m.mission_num)}
          data-testid={`mission-tab-${m.mission_num}`}
          className={`mono text-[11px] uppercase tracking-[0.15em] border rounded-full px-4 py-2 transition-colors duration-200 disabled:cursor-not-allowed ${tone} ${
            m.mission_num === current ? "ring-2 ring-nm-gold" : ""
          }`}
        >
          M{m.mission_num} <span className="lowercase tracking-normal">· {st.points || 0}/20</span>
        </button>
      );
    })}
  </nav>
);
