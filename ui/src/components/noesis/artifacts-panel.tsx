"use client";

import { CircleHelp, Plus, Search, Settings, Sparkles } from "lucide-react";
import { HeaderAction } from "./header-action";
import type { Artifact } from "./types";

type ArtifactsPanelProps = {
  artifacts: Artifact[];
  selectedTitle: string;
  onSelectArtifact: (artifact: Artifact) => void;
  onAddTopic: () => void;
};

export function ArtifactsPanel({
  artifacts,
  selectedTitle,
  onSelectArtifact,
  onAddTopic
}: ArtifactsPanelProps) {
  const grouped = artifacts.reduce<Record<string, Artifact[]>>((acc, artifact) => {
    acc[artifact.dateGroup] = [...(acc[artifact.dateGroup] ?? []), artifact];
    return acc;
  }, {});

  return (
    <section
      aria-label="Artifacts"
      className="min-h-0 overflow-hidden rounded-[30px] bg-[color:var(--surface)]/78 p-4 backdrop-blur-xl"
    >
      <div className="mb-4 flex items-start justify-between gap-4 border-b border-[color:var(--line)] pb-4">
        <div className="flex items-center gap-3">
          <div className="grid h-[var(--brand-icon-size)] w-[var(--brand-icon-size)] place-items-center rounded-2xl border border-[color:var(--line)] bg-[color:var(--ink)] text-white shadow-[0_16px_40px_rgba(17,24,39,0.16)]">
            <Sparkles size={18} aria-hidden="true" />
          </div>
          <div>
            <p className="font-display text-2xl tracking-[-0.04em]">Noesis</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <HeaderAction label="Search">
            <Search size={16} aria-hidden="true" />
          </HeaderAction>
          <HeaderAction label="Help">
            <CircleHelp size={16} aria-hidden="true" />
          </HeaderAction>
          <HeaderAction label="Settings">
            <Settings size={16} aria-hidden="true" />
          </HeaderAction>
        </div>
      </div>

      <button
        type="button"
        onClick={onAddTopic}
        className="mb-5 flex h-[var(--field-height)] w-full items-center justify-center gap-2 rounded-2xl border border-[color:var(--line)] bg-[color:var(--mist)] px-4 text-sm font-black uppercase tracking-[0.16em] text-[color:var(--accent-ink)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--accent)]"
        aria-label="Add new topic"
      >
        <Plus size={16} aria-hidden="true" />
        New topic
      </button>

      <div className="space-y-7">
        {Object.entries(grouped).map(([group, items]) => (
          <div key={group}>
            <p className="mb-3 border-b border-[color:var(--line)] pb-1 text-xs font-black uppercase tracking-[0.22em] text-[color:var(--muted)]">
              {group}
            </p>
            <div className="space-y-4">
              {items.map((artifact) => {
                const active = artifact.title === selectedTitle;

                return (
                  <button
                    key={artifact.title}
                    type="button"
                    onClick={() => onSelectArtifact(artifact)}
                    className={`w-full rounded-3xl border px-4 py-3 text-left transition-colors duration-200 ${
                      active
                        ? "border-[color:var(--accent)] bg-white"
                        : "border-[color:var(--line)] bg-white/42 hover:border-[color:var(--accent)] hover:bg-white/72"
                    }`}
                  >
                    <p className="font-display text-[1.05rem] font-semibold leading-5 tracking-[-0.04em] text-[color:var(--ink)]">
                      {artifact.title}
                    </p>
                    <p className="mt-2 line-clamp-2 text-xs font-medium leading-5 text-[color:var(--muted)]">
                      {artifact.prompt}
                    </p>
                    <p className="mt-3 text-[0.68rem] font-bold uppercase tracking-[0.18em] text-[color:var(--subtle)]">
                      {artifact.detail}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
