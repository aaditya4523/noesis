import { RefObject } from "react";
import { MarkdownRenderer } from "./markdown-renderer";

type MarkdownDocumentProps = {
  markdown: string;
  scrollRef: RefObject<HTMLDivElement | null>;
};

export function MarkdownDocument({ markdown, scrollRef }: MarkdownDocumentProps) {
  return (
    <article
      aria-label="Markdown file"
      className="flex min-h-0 flex-col overflow-hidden rounded-[34px] border border-[color:var(--line)] bg-[color:var(--artifact-shell)]"
    >
      <div data-testid="markdown-frame" className="relative min-h-0 flex-1">
        <div
          ref={scrollRef}
          data-testid="markdown-scroll"
          className="scrollbar-none h-full overflow-y-auto bg-[color:var(--artifact)] px-5 py-7 md:px-7"
        >
          <MarkdownRenderer markdown={markdown} />
        </div>
      </div>
    </article>
  );
}
