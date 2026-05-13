import type { MouseEventHandler, ReactNode } from "react";

export function HeaderAction({
  label,
  children,
  onClick,
  pressed
}: {
  label: string;
  children: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  pressed?: boolean;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      aria-pressed={pressed}
      onClick={onClick}
      className="grid h-[var(--icon-button-size)] w-[var(--icon-button-size)] place-items-center rounded-2xl border border-[color:var(--line)] bg-[color:var(--card-soft)] text-[color:var(--muted)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)] hover:text-[color:var(--ink)] aria-pressed:border-[color:var(--accent)] aria-pressed:bg-[color:var(--mist)] aria-pressed:text-[color:var(--accent-ink)]"
    >
      {children}
    </button>
  );
}
