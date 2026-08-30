import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shell, Masthead, GoldButton, GhostButton, Panel } from "../components/Chrome";
import { getRooms, readLocal, clearLocal, startSession, getLeaderboard } from "../lib/api";
import { LogOut, Trophy, Zap, Lock } from "lucide-react";

const HERO = "https://images.unsplash.com/photo-1571841653714-f542a5e00bdc?crop=entropy&cs=srgb&fm=jpg&q=85&w=900";

export default function Rooms() {
  const nav = useNavigate();
  const [rooms, setRooms] = useState([]);
  const [board, setBoard] = useState({ enabled: false, entries: [] });
  const state = readLocal();

  useEffect(() => {
    if (!state?.user) return nav("/");
    getRooms().then(setRooms).catch(() => {});
    getLeaderboard(state.user.class_code).then(setBoard).catch(() => {});
  }, []); // eslint-disable-line

  const enter = async (room) => {
    const s = await startSession({
      user_id: state.user.id,
      class_code: state.user.class_code,
      student_name: state.user.student_name,
    });
    nav(`/briefing/${s.id}`);
  };

  const sidebar = (
    <div className="space-y-5">
      <Panel className="p-5" testId="actions-panel">
        <h3 className="title text-sm text-nm-ink mb-4">Actions</h3>
        <div className="space-y-2.5">
          <GoldButton className="w-full" onClick={() => rooms[0] && enter(rooms[0])} data-testid="sidebar-start">
            Avvia / riprendi
          </GoldButton>
          <GhostButton
            className="w-full"
            onClick={() => { clearLocal(); nav("/"); }}
            data-testid="logout-btn"
          >
            <span className="inline-flex items-center gap-2"><LogOut size={13} /> Esci</span>
          </GhostButton>
        </div>
      </Panel>
      <Panel className="p-5" testId="leaderboard-panel">
        <h3 className="title text-sm text-nm-ink mb-1 flex items-center gap-2">
          <Trophy size={14} className="text-nm-gold" /> Leaderboard
        </h3>
        {board.enabled ? (
          <ol className="mt-3 space-y-2">
            {board.entries.map((e, i) => (
              <li key={i} className="flex justify-between mono text-xs" data-testid={`leader-${i}`}>
                <span className="text-nm-ink truncate">{i + 1}. {e.student_name}</span>
                <span className="text-nm-gold font-bold">{e.total_points}</span>
              </li>
            ))}
            {!board.entries.length && <li className="mono text-xs text-nm-muted">Nessun punteggio registrato.</li>}
          </ol>
        ) : (
          <p className="mono text-xs text-nm-muted mt-2 flex items-start gap-2">
            <Lock size={12} className="mt-0.5" /> Classifica disattivata dal docente per questa classe.
          </p>
        )}
      </Panel>
    </div>
  );

  return (
    <Shell sidebar={sidebar} testId="rooms-page">
      <Masthead
        eyebrow={`${state?.user?.class_code || ""} · ${state?.user?.student_name || ""}`}
        title="Escape Rooms"
      />
      <div className="grid sm:grid-cols-2 gap-6">
        {rooms.map((r) => (
          <button
            key={r.room_id}
            onClick={() => enter(r)}
            data-testid={`room-card-${r.room_id}`}
            className="group text-left card-nm rounded-2xl overflow-hidden relative animate-rise hover:-translate-y-1 transition-transform duration-300"
          >
            <div className="h-52 overflow-hidden">
              <img
                src={HERO}
                alt={r.title}
                className="w-full h-full object-cover grayscale contrast-125 group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="p-5 pb-16">
              <p className="mono text-[10px] uppercase tracking-[0.25em] text-nm-gold mb-2">{r.collection}</p>
              <h2 className="title text-2xl text-nm-ink mb-2">{r.title}</h2>
              <p className="text-sm text-nm-muted leading-relaxed">{r.tagline}</p>
            </div>
            <div className="absolute bottom-0 left-0 right-0 bg-nm-ink/85 px-5 py-3 flex items-center justify-between">
              <p className="mono text-[11px] tracking-widest text-nm-cream uppercase">
                {r.missions_count} missioni &middot; {r.duration_min}'
              </p>
              <span className="mono text-[11px] text-nm-gold uppercase tracking-widest inline-flex items-center gap-1.5">
                <Zap size={12} /> Apri
              </span>
            </div>
          </button>
        ))}
        <div className="card-nm rounded-2xl p-6 flex flex-col justify-center opacity-60" data-testid="room-card-locked">
          <Lock size={18} className="text-nm-muted mb-3" />
          <h2 className="title text-lg text-nm-ink mb-1">Guerra Fredda</h2>
          <p className="text-sm text-nm-muted">In preparazione. Sara' sbloccata dal docente.</p>
        </div>
      </div>
    </Shell>
  );
}
