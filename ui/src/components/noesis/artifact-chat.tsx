import { ArrowUp, MessageCircle } from "lucide-react";

export function ArtifactChat() {
  return (
    <div
      data-testid="chat-row"
      className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_200px]"
    >
      <div data-testid="chat-dock" className="rounded-3xl bg-[color:var(--artifact)]">
        <div className="flex items-center gap-2 rounded-3xl border border-[color:var(--line)] bg-[color:var(--artifact)] p-2">
          <MessageCircle size={17} className="ml-2 text-[color:var(--accent)]" aria-hidden="true" />
          <input
            aria-label="Artifact chat"
            placeholder="Ask about this artifact ..."
            className="h-[calc(var(--button-height)-1rem)] min-w-0 flex-1 bg-transparent px-2 text-sm font-semibold text-[color:var(--ink)] placeholder:text-[color:var(--subtle)]"
          />
          <button
            type="button"
            className="grid h-[calc(var(--button-height)-1rem)] w-[calc(var(--button-height)-1rem)] place-items-center rounded-2xl border border-[color:var(--line)] bg-[color:var(--ink)] text-white transition-colors duration-200 hover:bg-[color:var(--accent)] hover:text-[color:var(--accent-ink)]"
            aria-label="Send chat message"
          >
            <ArrowUp size={17} aria-hidden="true" />
          </button>
        </div>
      </div>
      <div aria-hidden="true" className="hidden xl:block" />
    </div>
  );
}
