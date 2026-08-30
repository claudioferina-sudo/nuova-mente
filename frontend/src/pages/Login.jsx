import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shell, Masthead, GoldButton, GhostButton } from "../components/Chrome";
import { getClasses, loginStudent, saveLocal, readLocal } from "../lib/api";
import { KeyRound, GraduationCap, ShieldAlert } from "lucide-react";

export default function Login() {
  const nav = useNavigate();
  const [classes, setClasses] = useState([]);
  const [code, setCode] = useState("");
  const [pin, setPin] = useState("");
  const [name, setName] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getClasses().then(setClasses).catch(() => {});
    const st = readLocal();
    if (st?.user) nav("/escape-rooms");
  }, [nav]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      const data = await loginStudent({ class_code: code, pin, student_name: name });
      saveLocal({ user: data.user, class_info: data.class_info });
      nav("/escape-rooms");
    } catch (e2) {
      setErr(e2?.response?.data?.detail || "Accesso non riuscito");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Shell testId="login-page">
      <Masthead eyebrow="Nuova-Mente &middot; Escape room didattiche" title={<>Dossier<br />1939</>} />
      <div className="grid lg:grid-cols-[1.05fr_1fr] gap-10 items-start">
        <div className="max-w-xl">
          <p className="text-lg md:text-xl leading-relaxed text-nm-ink mb-5">
            Un sistema di intelligenza artificiale ha chiuso il caso piu' studiato del Novecento in quattro secondi.
            Ha prodotto una causa sola, una data sbagliata e un verdetto sicuro al 99,8%.
          </p>
          <p className="text-base text-nm-muted mb-8">
            Il tuo compito non e' rispondere a delle domande. E' smontare cinque output difettosi, uno per volta,
            usando soltanto le dodici schede del dossier. Cinque missioni, venti punti ciascuna, cento punti da
            convertire in ore di PBL.
          </p>
          <div className="flex gap-3 flex-wrap">
            {[
              ["12", "schede fonte"],
              ["5", "missioni"],
              ["3", "tentativi per missione"],
              ["50'", "timer non bloccante"],
            ].map(([n, l]) => (
              <div key={l} className="card-nm rounded-xl px-4 py-3">
                <p className="mono text-2xl font-bold text-nm-gold">{n}</p>
                <p className="mono text-[10px] uppercase tracking-widest text-nm-muted">{l}</p>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={submit} className="card-nm rounded-2xl p-6 md:p-8 animate-rise" data-testid="login-form">
          <div className="flex items-center gap-2 mb-6">
            <KeyRound size={16} className="text-nm-gold" />
            <h2 className="title text-base md:text-lg text-nm-ink">Accesso studente</h2>
          </div>
          <label className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted">Codice classe</label>
          <input
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            data-testid="login-class-code"
            placeholder="5AIT"
            className="mono w-full mt-1.5 mb-4 rounded-xl border border-nm-gold/50 bg-nm-cream px-4 py-3 text-lg tracking-[0.2em]"
          />
          <label className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted">PIN</label>
          <input
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            data-testid="login-pin"
            placeholder="••••"
            className="mono w-full mt-1.5 mb-4 rounded-xl border border-nm-gold/50 bg-nm-cream px-4 py-3 text-lg tracking-[0.4em]"
          />
          <label className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted">Nome e cognome</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            data-testid="login-name"
            placeholder="Marco Rossi"
            className="w-full mt-1.5 mb-5 rounded-xl border border-nm-gold/50 bg-nm-cream px-4 py-3 text-lg"
          />
          {err && (
            <p className="mono text-xs text-nm-err mb-4 flex items-center gap-2" data-testid="login-error">
              <ShieldAlert size={14} /> {err}
            </p>
          )}
          <GoldButton type="submit" disabled={busy} className="w-full" data-testid="login-submit">
            {busy ? "Verifica..." : "Entra nel dossier"}
          </GoldButton>
          {classes.length > 0 && (
            <p className="mono text-[11px] text-nm-muted mt-4">
              Classi attive: {classes.map((c) => c.class_code).join(", ")}
            </p>
          )}
          <div className="mt-6 pt-5 border-t border-nm-gold/30 flex items-center justify-between gap-3">
            <p className="mono text-[11px] text-nm-muted flex items-center gap-1.5">
              <GraduationCap size={13} /> Sei il docente?
            </p>
            <GhostButton type="button" onClick={() => nav("/docente")} data-testid="teacher-link">
              Area docente
            </GhostButton>
          </div>
        </form>
      </div>
    </Shell>
  );
}
