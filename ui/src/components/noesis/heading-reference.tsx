import { useState } from "react";
import type { ReactNode } from "react";
import type { HeadingReferenceItem } from "./types";

type HeadingReferenceProps = {
  activeHeading: string;
  children?: ReactNode;
  items: HeadingReferenceItem[];
  onSelectHeading: (id: string) => void;
};

export function HeadingReference({
  activeHeading,
  children,
  items,
  onSelectHeading
}: HeadingReferenceProps) {
  const [isOutlineOpen, setIsOutlineOpen] = useState(false);

  return (
    <aside className="hidden min-h-0 xl:block">
      <div
        data-testid="reference-rail"
        className="flex h-full flex-col justify-between gap-5 text-[color:var(--ink)]"
      >
        <section
          data-testid="heading-accordion"
          className="sticky top-0 overflow-hidden rounded-[var(--control-radius)] border border-[color:var(--line)] bg-[color:var(--card-soft)] font-mono text-[0.68rem] font-bold uppercase tracking-[0.18em] transition-colors duration-300"
        >
          <button
            type="button"
            aria-label={isOutlineOpen ? "Close outline" : "Open outline"}
            aria-controls="heading-reference-panel"
            aria-expanded={isOutlineOpen}
            className="flex h-[var(--button-height)] w-full cursor-pointer items-center justify-between px-3 text-[color:var(--ink)] transition-colors duration-200 hover:bg-[color:var(--mist)]"
            onClick={() => setIsOutlineOpen((current) => !current)}
          >
            <span>Outline</span>
            <span className={isOutlineOpen ? "text-[color:var(--accent-ink)]" : "text-[color:var(--subtle)]"}>
              {isOutlineOpen ? "Close" : "Open"}
            </span>
          </button>
          <div
            id="heading-reference-panel"
            className={`grid overflow-hidden transition-[grid-template-rows,opacity] duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] ${
              isOutlineOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0 pointer-events-none"
            }`}
          >
            <nav
              aria-label="Markdown headings"
              data-testid="heading-reference"
              className={`min-h-0 space-y-1 overflow-hidden px-3 transition-[padding,border-color] duration-300 ${
                isOutlineOpen ? "border-t border-[color:var(--line)] py-3" : "border-t-0 border-transparent py-0"
              }`}
            >
              {items.map((item) => {
                const active = activeHeading === item.id;

                return (
                  <button
                    key={item.id}
                    type="button"
                    aria-label={`${item.level} ${item.label}`}
                    aria-current={active ? "true" : "false"}
                    onClick={() => onSelectHeading(item.id)}
                    className={`block w-full rounded-r-xl px-2 py-1 text-left transition-colors duration-200 ${
                      item.level === "H3" ? "ml-4 max-w-[calc(100%-1rem)]" : ""
                    } ${
                      active
                        ? "bg-[color:var(--card)] text-[color:var(--accent-ink)]"
                        : "text-[color:var(--muted)] hover:bg-[color:var(--card-soft)] hover:text-[color:var(--ink)]"
                    }`}
                  >
                    <span className="mr-2 text-[0.56rem] text-[color:var(--subtle)]">
                      {item.level}
                    </span>
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </section>
        {children}
      </div>
    </aside>
  );
}
