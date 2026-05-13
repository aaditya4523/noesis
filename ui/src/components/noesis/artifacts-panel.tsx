"use client";

import { CircleHelp, Moon, PanelLeftClose, PanelLeftOpen, Plus, Search, Settings, Sun } from "lucide-react";
import { HeaderAction } from "./header-action";
import { NoesisLogoMark } from "./noesis-logo-mark";
import type { Artifact } from "./types";

type Theme = "light" | "dark";

type ArtifactsPanelProps = {
  artifacts: Artifact[];
  isCollapsed: boolean;
  selectedTitle: string;
  theme: Theme;
  onSelectArtifact: (artifact: Artifact) => void;
  onAddTopic: () => void;
  onToggleTheme: () => void;
  onToggleCollapsed: () => void;
};

export function ArtifactsPanel({
  artifacts,
  isCollapsed,
  selectedTitle,
  theme,
  onSelectArtifact,
  onAddTopic,
  onToggleTheme,
  onToggleCollapsed
}: ArtifactsPanelProps) {
  const grouped = artifacts.reduce<Record<string, Artifact[]>>((acc, artifact) => {
    acc[artifact.dateGroup] = [...(acc[artifact.dateGroup] ?? []), artifact];
    return acc;
  }, {});

  return (
    <section
      aria-label="Artifacts"
      data-collapsed={isCollapsed ? "true" : "false"}
      className="flex min-h-0 flex-col overflow-hidden bg-[color:var(--surface)]/78 px-0 py-0 backdrop-blur-xl transition-[background-color] duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)]"
    >
      <div className="mb-4 flex items-start justify-between gap-4 border-b border-[color:var(--line)] pb-4">
        <div className={`flex items-center gap-3 ${isCollapsed ? "w-full justify-center" : ""}`}>
          <div
            data-testid="brand-mark"
            className="grid h-[var(--icon-button-size)] w-[var(--icon-button-size)] place-items-center rounded-2xl border border-[color:var(--line)] bg-[color:var(--card)]"
          >
            <NoesisLogoMark />
          </div>
          <div className={isCollapsed ? "sr-only" : ""}>
            <p className="font-display text-2xl tracking-[-0.04em]">Noesis</p>
          </div>
        </div>
        {isCollapsed ? null : (
          <div className="flex items-center gap-2">
            <HeaderAction
              label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
              onClick={onToggleTheme}
              pressed={theme === "dark"}
            >
              {theme === "dark" ? <Sun size={16} aria-hidden="true" /> : <Moon size={16} aria-hidden="true" />}
            </HeaderAction>
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
        )}
      </div>

      {isCollapsed ? (
        <div data-testid="collapsed-actions" className="flex flex-col items-center gap-2">
          <HeaderAction label="Add new topic" onClick={onAddTopic}>
            <Plus size={16} aria-hidden="true" />
          </HeaderAction>
          <HeaderAction
            label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            onClick={onToggleTheme}
            pressed={theme === "dark"}
          >
            {theme === "dark" ? <Sun size={16} aria-hidden="true" /> : <Moon size={16} aria-hidden="true" />}
          </HeaderAction>
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
      ) : null}

      {isCollapsed ? null : (
        <>
          <button
            type="button"
            onClick={onAddTopic}
            className="mb-5 flex h-[var(--field-height)] w-full items-center justify-center gap-2 rounded-2xl border border-[color:var(--line)] bg-[color:var(--mist)] px-4 text-sm font-black uppercase tracking-[0.16em] text-[color:var(--accent-ink)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--accent)]"
            aria-label="Add new topic"
          >
            <Plus size={16} aria-hidden="true" />
            New topic
          </button>

          <div className="min-h-0 flex-1 space-y-7 overflow-y-auto scrollbar-none">
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
                            ? "border-[color:var(--accent)] bg-[color:var(--card)]"
                            : "border-[color:var(--line)] bg-[color:var(--card-soft)] hover:border-[color:var(--accent)] hover:bg-[color:var(--card)]"
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
        </>
      )}

      <button
        type="button"
        onClick={onToggleCollapsed}
        className={`mt-auto flex items-center justify-center gap-2 rounded-[var(--control-radius)] border border-[color:var(--line)] bg-[color:var(--card-soft)] text-[0.68rem] font-black uppercase tracking-[0.18em] text-[color:var(--accent-ink)] transition-colors duration-200 hover:border-[color:var(--accent)] hover:bg-[color:var(--mist)] ${
          isCollapsed
            ? "h-[var(--icon-button-size)] w-[var(--icon-button-size)]"
            : "h-[var(--button-height)] w-full px-4"
        }`}
        aria-label={isCollapsed ? "Expand artifacts panel" : "Collapse artifacts panel"}
      >
        {isCollapsed ? (
          <PanelLeftOpen size={15} aria-hidden="true" />
        ) : (
          <PanelLeftClose size={15} aria-hidden="true" />
        )}
        {isCollapsed ? null : "Collapse"}
      </button>
    </section>
  );
}
