"use client";

import { BookOpenCheck, Check, Link2, Sparkles, Upload, X } from "lucide-react";
import type { FormEvent } from "react";
import { processLogs, sourcePresets } from "./data";

type TopicComposerProps = {
  isGenerating: boolean;
  selectedSources: string[];
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggleSource: (source: string) => void;
};

export function TopicComposer({
  isGenerating,
  selectedSources,
  onClose,
  onSubmit,
  onToggleSource
}: TopicComposerProps) {
  return (
    <div className="frost-overlay fixed inset-0 z-20 grid place-items-center px-4 py-8">
      <section
        role="dialog"
        aria-modal="true"
        aria-label={isGenerating ? "Generation progress" : "New topic"}
        className="composer-panel max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-[30px] border border-[color:var(--line)] bg-[color:var(--surface)]/90 p-5 shadow-[0_28px_80px_rgba(18,26,42,0.13)] backdrop-blur-2xl sm:p-6"
      >
        {isGenerating ? (
          <GenerationLogs />
        ) : (
          <TopicForm
            selectedSources={selectedSources}
            onClose={onClose}
            onSubmit={onSubmit}
            onToggleSource={onToggleSource}
          />
        )}
      </section>
    </div>
  );
}

function TopicForm({
  selectedSources,
  onClose,
  onSubmit,
  onToggleSource
}: Omit<TopicComposerProps, "isGenerating">) {
  return (
    <form onSubmit={onSubmit} className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="grid h-[var(--field-height)] w-[var(--field-height)] place-items-center rounded-2xl border border-[color:var(--line)] bg-[color:var(--mist)] text-[color:var(--accent)]">
            <BookOpenCheck size={18} aria-hidden="true" />
          </div>
          <p className="font-display text-base uppercase">New topic</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="grid h-[var(--icon-button-sm)] w-[var(--icon-button-sm)] place-items-center rounded-full border border-[color:var(--line)] bg-white/80 text-[color:var(--muted)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)] hover:text-[color:var(--ink)]"
          aria-label="Close"
        >
          <X size={16} aria-hidden="true" />
        </button>
      </div>

      <label className="block">
        <span className="mb-2 block text-sm font-semibold">Topic</span>
        <input
          autoFocus
          name="topic"
          required
          placeholder="e.g. Evaluation patterns for RAG"
          className="h-[var(--field-height)] w-full rounded-2xl border border-[color:var(--line)] bg-white/82 px-4 text-base text-[color:var(--ink)] transition-colors duration-200 placeholder:text-[color:var(--subtle)] focus:border-[color:var(--accent)] focus:bg-white"
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-sm font-semibold">Additional suggestions</span>
        <textarea
          name="suggestions"
          placeholder="Tone, audience, constraints, or sections to prioritize."
          className="h-[var(--textarea-height)] w-full resize-none rounded-2xl border border-[color:var(--line)] bg-white/82 px-4 py-3 text-base text-[color:var(--ink)] transition-colors duration-200 placeholder:text-[color:var(--subtle)] focus:border-[color:var(--accent)] focus:bg-white"
        />
      </label>

      <fieldset>
        <legend className="mb-2 text-sm font-semibold">Source presets</legend>
        <div className="flex flex-wrap gap-2">
          {sourcePresets.map((source) => {
            const selected = selectedSources.includes(source);

            return (
              <button
                key={source}
                type="button"
                aria-pressed={selected}
                onClick={() => onToggleSource(source)}
                className={`inline-flex h-[var(--chip-height)] items-center gap-1.5 rounded-full border px-3 text-sm font-bold transition-colors duration-200 ${
                  selected
                    ? "border-[color:var(--accent)] bg-[color:var(--ink)] text-white hover:bg-[color:var(--accent)]"
                    : "border-[color:var(--line)] bg-white/80 text-[color:var(--muted)] hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)] hover:text-[color:var(--ink)]"
                }`}
              >
                {selected ? <Check size={14} aria-hidden="true" /> : null}
                {source}
              </button>
            );
          })}
        </div>
      </fieldset>

      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold">Optional evidence</legend>
        <div className="grid gap-3 sm:grid-cols-2">
          <EvidenceUpload />
          <EvidenceLinks />
        </div>
      </fieldset>

      <button
        type="submit"
        className="flex h-[var(--field-height)] w-full items-center justify-center gap-2 rounded-2xl bg-[color:var(--ink)] px-4 text-sm font-black uppercase tracking-[0.18em] text-white transition-colors duration-200 hover:bg-[color:var(--accent)] hover:text-[color:var(--accent-ink)]"
      >
        <Sparkles size={17} aria-hidden="true" />
        Generate artifact
      </button>
    </form>
  );
}

function EvidenceUpload() {
  return (
    <div className="rounded-3xl border border-[color:var(--line)] bg-white/58 p-4">
      <div className="mb-3 flex items-center gap-2">
        <Upload size={16} aria-hidden="true" />
        <p className="text-sm font-semibold">Sources upload from local device</p>
      </div>
      <label className="block">
        <span className="sr-only">Upload source files</span>
        <input
          type="file"
          name="sourceFiles"
          multiple
          aria-label="Upload source files"
          className="h-[var(--field-height)] w-full rounded-2xl border border-[color:var(--line)] bg-white/80 px-3 text-sm file:mr-3 file:rounded-full file:border-0 file:bg-[color:var(--ink)] file:px-3 file:py-1.5 file:text-sm file:font-bold file:text-white"
        />
      </label>
    </div>
  );
}

function EvidenceLinks() {
  return (
    <div className="rounded-3xl border border-[color:var(--line)] bg-white/58 p-4">
      <div className="mb-3 flex items-center gap-2">
        <Link2 size={16} aria-hidden="true" />
        <p className="text-sm font-semibold">Give links</p>
      </div>
      <label className="block">
        <span className="sr-only">Evidence links</span>
        <textarea
          name="evidenceLinks"
          aria-label="Evidence links"
          placeholder="Paste one link per line."
          className="h-[var(--textarea-height)] w-full resize-none rounded-2xl border border-[color:var(--line)] bg-white/82 px-3 py-2 text-sm transition-colors duration-200 placeholder:text-[color:var(--subtle)] focus:border-[color:var(--accent)] focus:bg-white"
        />
      </label>
    </div>
  );
}

function GenerationLogs() {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <div className="grid h-[var(--field-height)] w-[var(--field-height)] place-items-center rounded-2xl border border-[color:var(--line)] bg-[color:var(--mist)] text-[color:var(--accent)]">
          <Sparkles size={18} aria-hidden="true" />
        </div>
        <p className="font-display text-xl tracking-[-0.04em]">Generation progress</p>
      </div>

      <ol className="space-y-3">
        {processLogs.map((log, index) => (
          <li
            key={log}
            className="flex min-h-[var(--field-height)] items-center gap-3 rounded-2xl border border-[color:var(--line)] bg-white/62 px-3 py-3"
          >
            <span
              className={`grid h-7 w-7 place-items-center rounded-full text-xs font-bold ${
                index === processLogs.length - 1
                  ? "bg-[color:var(--ink)] text-white"
                  : "bg-[color:var(--mist)] text-[color:var(--accent-ink)]"
              }`}
            >
              {index === processLogs.length - 1 ? (
                <Check size={14} aria-hidden="true" />
              ) : (
                index + 1
              )}
            </span>
            <span className="text-sm font-semibold text-[color:var(--muted)]">{log}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
