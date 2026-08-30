import React, { useState } from "react";
import { AiOutput, GoldButton, GhostButton } from "../components/Chrome";
import { SourcePicker } from "../components/Dossier";
import { Plus, Trash2, GripVertical, Highlighter } from "lucide-react";

const Label = ({ children }) => (
  <p className="mono text-[11px] uppercase tracking-[0.2em] text-nm-muted mb-2">{children}</p>
);

const area =
  "w-full rounded-xl border border-nm-gold/50 bg-nm-cream px-4 py-3 text-base leading-relaxed focus:border-nm-gold placeholder:text-nm-muted/60";

/* ---------------- M1 ---------------- */
export const M1 = ({ mission, onSubmit, busy }) => {
  const [rewrite, setRewrite] = useState("");
  const [causes, setCauses] = useState(["", "", ""]);
  const set = (i, v) => setCauses(causes.map((c, j) => (j === i ? v : c)));
  const valid = causes.filter((c) => c.trim().length > 8).length >= 3;
  return (
    <div className="space-y-6">
      <AiOutput text={mission.ai_output} />
      <div>
        <Label>Riscrivi il prompt in modo storicamente corretto</Label>
        <textarea
          rows={3}
          value={rewrite}
          onChange={(e) => setRewrite(e.target.value)}
          data-testid="m1-prompt-rewrite"
          placeholder="Es. Analizza le cause strutturali, politiche e immediate dello scoppio della Seconda Guerra Mondiale..."
          className={area}
        />
      </div>
      <div>
        <Label>Cause distinte (almeno 3, di cui 1 strutturale)</Label>
        <div className="space-y-3">
          {causes.map((c, i) => (
            <div key={i} className="flex gap-2 items-start">
              <span className="mono text-xs text-nm-gold font-bold pt-3.5 w-6">{String(i + 1).padStart(2, "0")}</span>
              <textarea
                rows={2}
                value={c}
                onChange={(e) => set(i, e.target.value)}
                data-testid={`m1-cause-${i}`}
                placeholder="Descrivi la causa e collegala a una scheda del dossier (es. S01)"
                className={area}
              />
              {causes.length > 3 && (
                <button
                  onClick={() => setCauses(causes.filter((_, j) => j !== i))}
                  data-testid={`m1-remove-cause-${i}`}
                  className="mt-3 text-nm-err hover:scale-110 transition-transform duration-200"
                >
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
        <GhostButton className="mt-3" onClick={() => setCauses([...causes, ""])} data-testid="m1-add-cause">
          <span className="inline-flex items-center gap-2"><Plus size={13} /> Aggiungi causa</span>
        </GhostButton>
      </div>
      <GoldButton
        disabled={!valid || busy}
        onClick={() => onSubmit({ prompt_rewrite: rewrite, causes: causes.filter((c) => c.trim()) })}
        data-testid="m1-submit"
      >
        {busy ? "Analisi in corso..." : "Invia analisi"}
      </GoldButton>
    </div>
  );
};

/* ---------------- M2 ---------------- */
export const M2 = ({ mission, sources, onSubmit, busy }) => {
  const [option, setOption] = useState("");
  const [highlight, setHighlight] = useState("");
  const [source, setSource] = useState("");

  const capture = () => {
    const sel = window.getSelection()?.toString() || "";
    if (sel.trim().length > 8) setHighlight(sel.trim());
  };

  return (
    <div className="space-y-6">
      <div>
        <Label>Seleziona con il mouse il segmento falso nel testo dell'AI</Label>
        <AiOutput text={mission.ai_output} selectable onSelect={capture} />
      </div>
      <div className="card-nm rounded-xl px-4 py-3 flex items-start gap-3">
        <Highlighter size={16} className="text-nm-gold mt-1 shrink-0" />
        <div className="min-w-0 flex-1">
          <Label>Segmento evidenziato</Label>
          {highlight ? (
            <p className="mono text-sm bg-nm-gold/30 rounded px-2 py-1 break-words" data-testid="m2-highlight-preview">
              {highlight}
            </p>
          ) : (
            <p className="mono text-xs text-nm-muted">Nessuna selezione. Evidenzia la frase inesatta nel pannello nero.</p>
          )}
          <input
            value={highlight}
            onChange={(e) => setHighlight(e.target.value)}
            data-testid="m2-highlight-input"
            placeholder="oppure incolla/scrivi qui il segmento"
            className="mono text-xs w-full mt-2 rounded-lg border border-nm-gold/40 bg-nm-cream px-3 py-2"
          />
        </div>
      </div>
      <div>
        <Label>Quale affermazione e' falsa?</Label>
        <div className="space-y-2">
          {mission.options.map((o) => (
            <button
              key={o.option_id}
              onClick={() => setOption(o.option_id)}
              data-testid={`m2-option-${o.option_id}`}
              className={`w-full text-left rounded-xl border px-4 py-3 transition-colors duration-200 ${
                option === o.option_id ? "border-nm-gold bg-nm-gold/20" : "border-nm-gold/40 bg-nm-card hover:bg-nm-gold/10"
              }`}
            >
              <span className="mono text-[11px] text-nm-gold font-bold mr-2">{o.option_id}</span>
              <span className="text-base">{o.text}</span>
            </button>
          ))}
        </div>
      </div>
      <div>
        <Label>Scheda del dossier che smentisce l'affermazione</Label>
        <SourcePicker sources={sources} value={source} onChange={setSource} testId="m2-source-picker" />
      </div>
      <GoldButton
        disabled={!option || !highlight || !source || busy}
        onClick={() => onSubmit({ option_id: option, highlight, source_id: source })}
        data-testid="m2-submit"
      >
        {busy ? "Verifica..." : "Deposita il fact-checking"}
      </GoldButton>
    </div>
  );
};

/* ---------------- M3 ---------------- */
const COLS = [
  { key: "remota", title: "Cause remote", hint: "Lungo periodo, strutturali" },
  { key: "immediata", title: "Cause immediate", hint: "Scintille 1938-1939" },
];

export const M3 = ({ mission, onSubmit, busy, result }) => {
  const [assign, setAssign] = useState({});
  const [picked, setPicked] = useState(null);
  const cards = mission.cards || [];
  const pool = cards.filter((c) => !assign[c.card_id]);
  const done = Object.keys(assign).length === cards.length;
  const perCard = result?.details?.per_card;

  const place = (cardId, col) => setAssign((a) => ({ ...a, [cardId]: col }));
  const remove = (cardId) => setAssign((a) => { const n = { ...a }; delete n[cardId]; return n; });

  const Card = ({ c, col }) => {
    const flag = perCard?.[c.card_id];
    return (
      <div
        draggable
        onDragStart={(e) => e.dataTransfer.setData("text/plain", c.card_id)}
        onClick={() => setPicked(picked === c.card_id ? null : c.card_id)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setPicked(picked === c.card_id ? null : c.card_id); }
          if (col && e.key === "Backspace") remove(c.card_id);
          if (!col && (e.key === "ArrowLeft" || e.key === "1")) place(c.card_id, "remota");
          if (!col && (e.key === "ArrowRight" || e.key === "2")) place(c.card_id, "immediata");
        }}
        tabIndex={0}
        role="button"
        data-testid={`m3-card-${c.card_id}`}
        className={`cursor-grab active:cursor-grabbing select-none rounded-xl border px-3 py-2.5 text-sm flex items-start gap-2 transition-colors duration-200 ${
          flag === true ? "border-nm-ok bg-nm-ok/15" : flag === false ? "border-nm-err bg-nm-err/15" : "border-nm-gold/50 bg-nm-card hover:bg-nm-gold/10"
        } ${picked === c.card_id ? "ring-2 ring-nm-gold" : ""}`}
      >
        <GripVertical size={14} className="text-nm-gold mt-1 shrink-0" />
        <span className="leading-snug">{c.text}</span>
        {col && (
          <button onClick={(e) => { e.stopPropagation(); remove(c.card_id); }} data-testid={`m3-unplace-${c.card_id}`} className="ml-auto text-nm-muted hover:text-nm-err">
            <Trash2 size={13} />
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <AiOutput text={mission.ai_output} />
      <p className="mono text-[11px] text-nm-muted">
        Trascina le card, oppure selezionane una con Enter e usa le frecce sinistra/destra (accessibile da tastiera).
      </p>
      <div className="grid md:grid-cols-2 gap-4">
        {COLS.map((col) => (
          <div
            key={col.key}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); place(e.dataTransfer.getData("text/plain"), col.key); }}
            data-testid={`m3-column-${col.key}`}
            className="rounded-2xl border-2 border-dashed border-nm-gold/60 bg-nm-cream/60 p-4 min-h-[220px]"
          >
            <div className="mb-3">
              <h3 className="title text-base text-nm-ink">{col.title}</h3>
              <p className="mono text-[10px] uppercase tracking-widest text-nm-muted">{col.hint}</p>
            </div>
            <div className="space-y-2">
              {cards.filter((c) => assign[c.card_id] === col.key).map((c) => <Card key={c.card_id} c={c} col={col.key} />)}
            </div>
            {picked && !assign[picked] && (
              <GhostButton className="mt-3" onClick={() => { place(picked, col.key); setPicked(null); }} data-testid={`m3-place-${col.key}`}>
                Sposta qui
              </GhostButton>
            )}
          </div>
        ))}
      </div>
      <div>
        <Label>Card da classificare ({pool.length})</Label>
        <div className="grid sm:grid-cols-2 gap-2" data-testid="m3-pool">
          {pool.map((c) => <Card key={c.card_id} c={c} />)}
        </div>
      </div>
      <GoldButton disabled={!done || busy} onClick={() => onSubmit({ assignments: assign })} data-testid="m3-submit">
        {busy ? "Controllo..." : "Conferma classificazione"}
      </GoldButton>
    </div>
  );
};

/* ---------------- M4 ---------------- */
export const M4 = ({ mission, onSubmit, busy }) => {
  const [text, setText] = useState("");
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  return (
    <div className="space-y-6">
      <AiOutput text={mission.ai_output} />
      <div>
        <Label>La tua confutazione</Label>
        <textarea
          rows={12}
          value={text}
          onChange={(e) => setText(e.target.value)}
          data-testid="m4-text"
          placeholder="1) Cosa c'e' di vero nella tesi. 2) Cosa omette: almeno due evidenze dal dossier, citate con il codice scheda (S01, S02...). 3) Il nesso logico: perche' quelle evidenze rendono la tesi insufficiente."
          className={area}
        />
        <p className="mono text-[11px] text-nm-muted mt-2">{words} parole &middot; consigliate almeno 120</p>
      </div>
      <GoldButton disabled={words < 30 || busy} onClick={() => onSubmit({ text })} data-testid="m4-submit">
        {busy ? "Valutazione semantica..." : "Invia confutazione"}
      </GoldButton>
    </div>
  );
};

/* ---------------- M5 ---------------- */
export const M5 = ({ mission, sources, onSubmit, busy }) => {
  const [sections, setSections] = useState({});
  const [picked, setPicked] = useState([]);
  const filled = mission.sections.filter((s) => (sections[s.key] || "").trim().length >= 40).length;
  const ready = filled === 4 && picked.length >= 3;
  return (
    <div className="space-y-6">
      <AiOutput text={mission.ai_output} />
      <div className="space-y-5">
        {mission.sections.map((s, i) => {
          const ok = (sections[s.key] || "").trim().length >= 40;
          return (
            <div key={s.key}>
              <div className="flex items-center justify-between mb-2">
                <Label>{`${i + 1}. ${s.label}`}</Label>
                <span className={`mono text-[10px] uppercase tracking-widest ${ok ? "text-nm-ok" : "text-nm-muted"}`}>
                  {ok ? "compilata" : "min. 40 caratteri"}
                </span>
              </div>
              <textarea
                rows={4}
                value={sections[s.key] || ""}
                onChange={(e) => setSections({ ...sections, [s.key]: e.target.value })}
                data-testid={`m5-section-${s.key}`}
                placeholder={s.placeholder}
                className={area}
              />
            </div>
          );
        })}
      </div>
      <div>
        <Label>Checklist fonti citate (almeno 3) &mdash; selezionate: {picked.length}</Label>
        <SourcePicker sources={sources} value={picked} onChange={setPicked} multiple testId="m5-source-picker" />
      </div>
      <GoldButton disabled={!ready || busy} onClick={() => onSubmit({ sections, sources: picked })} data-testid="m5-submit">
        {busy ? "Verdetto in valutazione..." : "Sigilla il rapporto ed esci"}
      </GoldButton>
    </div>
  );
};
