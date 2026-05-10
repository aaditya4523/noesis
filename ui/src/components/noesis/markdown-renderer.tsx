import type { ReactNode } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";

function slugify(value: ReactNode) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

const markdownComponents: Components = {
  h1: ({ children }) => (
    <h1
      id="title"
      data-heading-id="title"
      className="font-artifact text-5xl font-extrabold leading-[0.9] tracking-[-0.08em] text-[color:var(--ink)]"
    >
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2
      id={slugify(children)}
      data-heading-id={slugify(children)}
      className="mt-10 font-artifact text-[2rem] font-extrabold tracking-[-0.065em] text-[color:var(--ink)]"
    >
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3
      id={slugify(children)}
      data-heading-id={slugify(children)}
      className="mb-3 mt-5 font-artifact text-[1.15rem] font-bold tracking-[-0.055em] text-[color:var(--muted)]"
    >
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p className="max-w-[48rem] text-sm font-medium leading-7 text-[color:var(--muted)]">
      {children}
    </p>
  ),
  strong: ({ children }) => (
    <strong className="block font-mono text-[0.68rem] font-bold uppercase tracking-[0.24em] text-[color:var(--subtle)]">
      {children}
    </strong>
  ),
  blockquote: ({ children }) => (
    <blockquote className="max-w-[48rem] border-l-2 border-[color:var(--terracotta)] bg-white/58 px-4 py-3 text-[color:var(--muted)]">
      {children}
    </blockquote>
  ),
  ol: ({ children }) => (
    <ol className="max-w-[48rem] list-decimal space-y-2 pl-5">{children}</ol>
  ),
  ul: ({ children }) => (
    <ul className="max-w-[48rem] space-y-2 text-sm font-medium leading-7 text-[color:var(--muted)]">
      {children}
    </ul>
  ),
  li: ({ children }) => (
    <li className="text-sm font-medium leading-7 text-[color:var(--muted)]">
      {children}
    </li>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      className="font-bold text-[color:var(--accent-ink)] underline decoration-[color:var(--accent)] decoration-2 underline-offset-4 transition-colors duration-200 hover:text-[color:var(--terracotta)]"
    >
      {children}
    </a>
  )
};

export function MarkdownRenderer({ markdown }: { markdown: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeSanitize]}
      components={markdownComponents}
    >
      {markdown}
    </ReactMarkdown>
  );
}
