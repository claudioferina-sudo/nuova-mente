import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Shell, Masthead, Panel, GoldButton, GhostButton, Stamp } from "../components/Chrome";
import { finishSession, getMissions, pdfUrl } from "../lib/api";
import { Download, RotateCcw, Award } from "lucide-react";

const LADDER = [
  ["0-39", "0", "Recupero guidato"],
  ["40-59", "1", "0,5 h"],
  ["60-79", "2", "1 h"],
  ["80-94", "3", "1,5 h"],
  ["95-100", "4", "2 h"],
];

export default function Escape() {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const [session, setSession] = useState(null);
  const [missions, setMissions] = useState([]);

  useEffect(() => {
    finishSession(sessionId).then(setSession).catch(() => nav("/escape-rooms"));
    getMissions(sessionId).then(setMissions).catch(() => {});
  }, [sessionId]); // eslint-disable-line

  const total = session?.total_points ?? 0;
  const tone = total >= 60 ? "ok" : total >= 40 ? "warn" : "err";

  return (
    <Shell testId="escape-page">
      <Masthead eyebrow="Dossier chiuso" title="Escape" right={<Stamp text={`${total}/100`} tone={tone} />} />
      <div className="grid lg:grid-cols-[1.2fr_1fr] gap-8 items-start">
        <Panel className="p-6 md:p-8" testId="credits-panel">
          <div className="flex items-center gap-2 mb-5">
            <Award size={16} className="text-nm-gold" />
            <p className="mono text-[10px] uppercase tracking-[0.25em] text-nm-muted">Conversione crediti &rarr; PBL</p>
          </div>
          <p className="mono text-6xl font-bold text-nm-gold mb-1" data-testid="final-score">{total}</p>
          <p className="mono text-[11px] uppercase tracking-widest text-nm-muted mb-6">punti su 100</p>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="rounded-xl bg-nm-cream border border-nm-gold/40 px-4 py-3">
              <p className="mono text-[10px] uppercase tracking-widest text-nm-muted">Crediti autonomia</p>
              <p className="mono text-3xl font-bold text-nm-ink" data-testid="final-credits">{session?.credits ?? 0}</p>
            </div>
            <div className="rounded-xl bg-nm-cream border border-nm-gold/40 px-4 py-3">
              <p className="mono text-[10px] uppercase tracking-widest text-nm-muted">Ore PBL sbloccate</p>
              <p className="mono text-3xl font-bold text-nm-ink" data-testid="final-hours">{session?.pbl_hours ?? 0} h</p>
            </div>
          </div>
          <p className="text-base text-nm-ink mb-6" data-testid="credits-note">{session?.credits_note}</p>
          <div className="flex flex-wrap gap-3">
            <a href={pdfUrl(sessionId)} target="_blank" rel="noreferrer" data-testid="download-pdf">
              <GoldButton><span className="inline-flex items-center gap-2"><Download size={13} /> Scarica scheda PDF</span></GoldButton>
            </a>
            <GhostButton onClick={() => nav("/escape-rooms")} data-testid="back-to-rooms">
              <span className="inline-flex items-center gap-2"><RotateCcw size={13} /> Torna alle escape rooms</span>
            </GhostButton>
          </div>
        </Panel>

        <div className="space-y-5">
          <Panel className="p-5" testId="mission-recap">
            <h3 className="title text-sm text-nm-ink mb-4">Punteggio per missione</h3>
            <ul className="space-y-2.5">
              {missions.map((m) => {
                const st = session?.missions?.[String(m.mission_num)] || {};
                return (
                  <li key={m.mission_num} className="flex items-baseline gap-3" data-testid={`recap-m${m.mission_num}`}>
                    <span className="mono text-[11px] text-nm-gold font-bold w-7">M{m.mission_num}</span>
                    <span className="text-sm text-nm-ink flex-1 leading-snug">{m.title}</span>
                    <span className="mono text-sm font-bold text-nm-ink">{st.points || 0}/20</span>
                    {st.status === "overridden" && <span className="mono text-[10px] text-nm-warn">OVR</span>}
                  </li>
                );
              })}
            </ul>
            {session?.bonuses > 0 && (
              <p className="mono text-xs text-nm-ok mt-4">Bonus applicati: +{session.bonuses * 10} pt</p>
            )}
          </Panel>
          <Panel className="p-5" testId="ladder-panel">
            <h3 className="title text-sm text-nm-ink mb-3">Scala di conversione</h3>
            <table className="w-full mono text-[11px]">
              <tbody>
                {LADDER.map(([range, cr, h]) => {
                  const active = session?.credits === parseInt(cr, 10);
                  return (
                    <tr key={range} className={active ? "text-nm-gold font-bold" : "text-nm-muted"}>
                      <td className="py-1">{range}</td>
                      <td className="py-1 text-center">{cr}</td>
                      <td className="py-1 text-right">{h}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Panel>
          <p className="mono text-[11px] text-nm-muted">
            Il punteggio automatico non e' definitivo: il docente puo' sovrascriverlo con motivazione tracciata.
          </p>
        </div>
      </div>
    </Shell>
  );
}
