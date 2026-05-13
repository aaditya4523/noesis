import { BookOpenCheck, Download, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

export function RailControls() {
  return (
    <div
      data-testid="rail-controls"
      className="space-y-2"
    >
      <section aria-label="Artifact actions" className="grid grid-cols-2 gap-2">
        <RailActionButton label="Summarize artifact">
          <Sparkles size={13} aria-hidden="true" />
          Summarize
        </RailActionButton>
        <RailActionButton label="Design PPT">
          <BookOpenCheck size={13} aria-hidden="true" />
          Design PPT
        </RailActionButton>
      </section>
      <div data-testid="export-controls" className="grid grid-cols-2 gap-2">
        <button
          type="button"
          aria-label="Export markdown"
          className="flex h-[var(--button-height)] w-full items-center justify-center gap-2 rounded-[var(--control-radius)] border border-[color:var(--line)] bg-[color:var(--artifact)] px-3 font-mono text-[0.65rem] font-bold uppercase tracking-[0.18em] text-[color:var(--ink)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)]"
        >
          <Download size={13} aria-hidden="true" />
          .md
        </button>
        <button
          type="button"
          aria-label="Export PDF"
          className="flex h-[var(--button-height)] w-full items-center justify-center gap-2 rounded-[var(--control-radius)] border border-[color:var(--line)] bg-[color:var(--action-strong)] px-3 font-mono text-[0.65rem] font-bold uppercase tracking-[0.18em] text-[color:var(--action-strong-ink)] transition-colors duration-200 hover:bg-[color:var(--action-strong-hover)]"
        >
          <Download size={13} aria-hidden="true" />
          PDF
        </button>
      </div>
    </div>
  );
}

function RailActionButton({ label, children }: { label: string; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      className="flex h-[var(--button-height)] w-full items-center justify-center gap-2 rounded-[var(--control-radius)] border border-[color:var(--line)] bg-[color:var(--artifact)] px-3 font-mono text-[0.65rem] font-bold uppercase tracking-[0.18em] text-[color:var(--ink)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)] hover:text-[color:var(--accent-ink)]"
    >
      {children}
    </button>
  );
}
