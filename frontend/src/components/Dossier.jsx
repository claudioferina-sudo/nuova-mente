import React, { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "./ui/sheet";
import { X } from "lucide-react";

export const DossierDrawer = ({ open, onOpenChange, sources }) => {
  const [q, setQ] = useState("");
  const list = (sources || []).filter(
    (s) => !q || `${s.source_id} ${s.title} ${s.body}`.toLowerCase().includes(q.toLowerCase())
  );
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-xl bg-nm-cream border-l-2 border-nm-gold overflow-y-auto paper"
        data-testid="dossier-drawer"
      >
        <SheetHeader>
          <SheetTitle className="title text-2xl text-nm-ink text-left">Dossier &mdash; 12 schede</SheetTitle>
        </SheetHeader>
        <p className="text-sm text-nm-muted mb-4">
          Dossier chiuso: nessuna ricerca esterna. Cita le schede con il loro codice (es. S08).
        </p>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Cerca nel dossier..."
          data-testid="dossier-search"
          className="mono text-sm w-full rounded-full border border-nm-gold/60 bg-nm-card px-4 py-2 mb-5 placeholder:text-nm-muted/70"
        />
        <div className="space-y-3 pb-10">
          {list.map((s) => (
            <article key={s.source_id} className="card-nm rounded-xl p-4" data-testid={`source-card-${s.source_id}`}>
              <div className="flex items-baseline justify-between gap-3 mb-1">
                <h3 className="title text-base text-nm-ink">{s.title}</h3>
                <span className="mono text-[11px] text-nm-gold font-bold shrink-0">{s.source_id}</span>
              </div>
              <p className="mono text-[11px] uppercase tracking-widest text-nm-muted mb-2">
                {s.year} &middot; {s.tag}
              </p>
              <p className="text-sm leading-relaxed text-nm-ink/90">{s.body}</p>
            </article>
          ))}
          {!list.length && <p className="mono text-sm text-nm-muted">Nessuna scheda corrisponde.</p>}
        </div>
      </SheetContent>
    </Sheet>
  );
};

export const SourcePicker = ({ sources, value, onChange, multiple = false, testId = "source-picker" }) => {
  const selected = multiple ? value || [] : value;
  const toggle = (id) => {
    if (!multiple) return onChange(id === value ? "" : id);
    onChange(selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id]);
  };
  return (
    <div className="flex flex-wrap gap-2" data-testid={testId}>
      {(sources || []).map((s) => {
        const on = multiple ? selected.includes(s.source_id) : selected === s.source_id;
        return (
          <button
            key={s.source_id}
            type="button"
            onClick={() => toggle(s.source_id)}
            data-testid={`pick-${s.source_id}`}
            title={s.title}
            className={`mono text-[11px] uppercase tracking-wider rounded-full px-3 py-1.5 border transition-colors duration-200 ${
              on ? "bg-nm-gold border-nm-gold text-nm-ink font-bold" : "border-nm-gold/50 text-nm-muted hover:bg-nm-gold/10"
            }`}
          >
            {s.source_id}
            {on && <X size={11} className="inline ml-1.5 -mt-0.5" />}
          </button>
        );
      })}
    </div>
  );
};
