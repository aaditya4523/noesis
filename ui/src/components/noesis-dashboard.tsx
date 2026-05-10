"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { ArtifactView } from "./noesis/artifact-view";
import { ArtifactsPanel } from "./noesis/artifacts-panel";
import { artifacts } from "./noesis/data";
import { TopicComposer } from "./noesis/topic-composer";

export function NoesisDashboard() {
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedSources, setSelectedSources] = useState<string[]>(["Docs"]);
  const [selectedArtifact, setSelectedArtifact] = useState(artifacts[0]);

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
    <main className="relative h-screen overflow-hidden px-3 pb-5 pt-3 text-[var(--ink)] sm:px-5 sm:pb-5 sm:pt-5">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-noesis-pattern" />
      <div className="mx-auto grid h-full w-full gap-4 bg-transparent lg:grid-cols-[minmax(300px,380px)_minmax(0,1fr)]">
        <ArtifactsPanel
          artifacts={artifacts}
          selectedTitle={selectedArtifact.title}
          onSelectArtifact={setSelectedArtifact}
          onAddTopic={openComposer}
        />
        <ArtifactView artifact={selectedArtifact} />
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
