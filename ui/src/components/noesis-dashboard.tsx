"use client";

import type { CSSProperties, FormEvent } from "react";
import { useEffect, useState } from "react";
import { ArtifactView } from "./noesis/artifact-view";
import { ArtifactsPanel } from "./noesis/artifacts-panel";
import { artifacts } from "./noesis/data";
import { TopicComposer } from "./noesis/topic-composer";

type Theme = "light" | "dark";

export function NoesisDashboard() {
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const [isArtifactsCollapsed, setIsArtifactsCollapsed] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedSources, setSelectedSources] = useState<string[]>(["Docs"]);
  const [selectedArtifact, setSelectedArtifact] = useState(artifacts[0]);
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === "undefined") {
      return "light";
    }

    return window.localStorage.getItem("noesis-theme") === "dark" ? "dark" : "light";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem("noesis-theme", theme);
  }, [theme]);

  function toggleSource(source: string) {
    setSelectedSources((current) =>
      current.includes(source)
        ? current.filter((item) => item !== source)
        : [...current, source]
    );
  }

  function openComposer() {
    setIsGenerating(false);
    setSelectedSources(["Docs"]);
    setIsComposerOpen(true);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsGenerating(true);
  }

  return (
    <main className="relative h-screen overflow-hidden p-5 text-[var(--ink)] sm:p-8">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-noesis-pattern" />
      <div
        className="mx-auto grid h-full w-full gap-6 bg-transparent transition-[grid-template-columns] duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] lg:grid-cols-[var(--artifacts-column)_minmax(0,1fr)] xl:gap-8"
        style={{
          "--artifacts-column": isArtifactsCollapsed
            ? "var(--icon-button-size)"
            : "clamp(280px,22vw,340px)"
        } as CSSProperties}
      >
        <ArtifactsPanel
          artifacts={artifacts}
          isCollapsed={isArtifactsCollapsed}
          selectedTitle={selectedArtifact.title}
          theme={theme}
          onSelectArtifact={setSelectedArtifact}
          onAddTopic={openComposer}
          onToggleTheme={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
          onToggleCollapsed={() => setIsArtifactsCollapsed((current) => !current)}
        />
        <ArtifactView artifact={selectedArtifact} isArtifactsCollapsed={isArtifactsCollapsed} />
      </div>

      {isComposerOpen ? (
        <TopicComposer
          isGenerating={isGenerating}
          selectedSources={selectedSources}
          onClose={() => setIsComposerOpen(false)}
          onSubmit={handleSubmit}
          onToggleSource={toggleSource}
        />
      ) : null}
    </main>
  );
}
