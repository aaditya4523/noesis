import type { ReactNode } from "react";

export function HeaderAction({ label, children }: { label: string; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      className="grid h-[var(--icon-button-size)] w-[var(--icon-button-size)] place-items-center rounded-2xl border border-[color:var(--line)] bg-white/76 text-[color:var(--muted)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)] hover:text-[color:var(--ink)]"
    >
      {children}
    </button>
  );
}
