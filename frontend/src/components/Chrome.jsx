import React from "react";
import { Heart } from "lucide-react";

export const Shell = ({ children, sidebar, testId = "app-shell" }) => (
  <div className="min-h-screen paper flex flex-col" data-testid={testId}>
    <main className="flex-1 w-full max-w-[1500px] mx-auto px-5 md:px-10 pt-6 pb-14">
      <div className={sidebar ? "grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-8" : ""}>
        <div className="min-w-0">{children}</div>
        {sidebar && <aside className="min-w-0">{sidebar}</aside>}
      </div>
    </main>
    <footer className="border-t border-nm-gold/40 py-5 px-6 md:px-10">
      <p className="mono text-xs text-nm-muted flex items-center gap-1.5">
        Made with <Heart size={12} className="fill-nm-err text-nm-err" /> by Nuova-Mente
      </p>
    </footer>
  </div>
);

export const Masthead = ({ eyebrow, title, right }) => (
  <header className="mb-8" data-testid="masthead">
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        {eyebrow && <p className="mono text-[11px] tracking-[0.3em] text-nm-gold uppercase mb-2">{eyebrow}</p>}
        <h1 className="title text-3xl sm:text-5xl lg:text-6xl leading-[0.95] text-nm-ink break-words hyphens-auto max-w-full">{title}</h1>
      </div>
      {right}
    </div>
    <div className="hairline mt-5" />
  </header>
);

export const Panel = ({ children, className = "", label, testId }) => (
  <section className={`card-nm rounded-2xl relative overflow-hidden ${className}`} data-testid={testId}>
    {children}
    {label && (
      <div className="absolute bottom-0 left-0 right-0 bg-nm-ink/85 px-4 py-2">
        <p className="mono text-[11px] tracking-widest text-nm-cream uppercase">{label}</p>
      </div>
    )}
  </section>
);

export const GoldButton = ({ children, className = "", ...rest }) => (
  <button
    {...rest}
    className={`mono text-xs font-semibold uppercase tracking-[0.18em] rounded-full px-6 py-3 bg-nm-gold text-nm-ink hover:brightness-105 hover:-translate-y-[1px] active:translate-y-0 transition-[transform,filter,box-shadow] duration-200 shadow-[0_3px_0_0_rgba(43,38,32,0.35)] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 ${className}`}
  >
    {children}
  </button>
);

export const GhostButton = ({ children, className = "", ...rest }) => (
  <button
    {...rest}
    className={`mono text-xs uppercase tracking-[0.18em] rounded-full px-5 py-2.5 border border-nm-gold/70 text-nm-ink hover:bg-nm-gold/15 transition-colors duration-200 disabled:opacity-40 disabled:cursor-not-allowed ${className}`}
  >
    {children}
  </button>
);

export const Stamp = ({ text, tone = "ok" }) => {
  const tones = { ok: "text-nm-ok border-nm-ok", warn: "text-nm-warn border-nm-warn", err: "text-nm-err border-nm-err" };
  return (
    <span
      className={`mono text-[11px] uppercase tracking-[0.2em] border-2 rounded px-3 py-1 animate-stamp inline-block ${tones[tone]}`}
      style={{ transform: "rotate(-8deg)" }}
    >
      {text}
    </span>
  );
};

export const AiOutput = ({ text, onSelect, selectable = false, testId = "ai-output" }) => (
  <div className="rounded-2xl overflow-hidden" data-testid={testId}>
    <div className="ai-panel px-6 py-5">
      <p className="text-[10px] tracking-[0.3em] uppercase text-nm-gold mb-3">
        Output sistema AI &middot; confidenza dichiarata 99,8%
      </p>
      <p
        className="text-sm leading-relaxed whitespace-pre-wrap"
        onMouseUp={selectable ? onSelect : undefined}
        data-testid={selectable ? "ai-output-selectable" : undefined}
      >
        {text}
      </p>
    </div>
  </div>
);
