import type { HeadingReferenceItem } from "./types";

type HeadingReferenceProps = {
  activeHeading: string;
  items: HeadingReferenceItem[];
  onSelectHeading: (id: string) => void;
};

export function HeadingReference({
  activeHeading,
  items,
  onSelectHeading
}: HeadingReferenceProps) {
  return (
    <aside className="hidden min-h-0 xl:block">
      <div data-testid="reference-rail" className="h-full text-[color:var(--ink)]">
        <nav
          aria-label="Markdown headings"
          data-testid="heading-reference"
          className="sticky top-5 space-y-1 border-l border-[color:var(--line)] pl-3 font-mono text-[0.68rem] font-bold uppercase tracking-[0.18em]"
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
                    ? "bg-white/72 text-[color:var(--accent-ink)]"
                    : "text-[color:var(--muted)] hover:bg-white/48 hover:text-[color:var(--ink)]"
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
    </aside>
  );
}
