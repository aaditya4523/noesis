"use client";

import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { headingReferenceItems } from "./data";
import { ArtifactChat } from "./artifact-chat";
import { HeadingReference } from "./heading-reference";
import { MarkdownDocument } from "./markdown-document";
import { RailControls } from "./rail-controls";
import type { Artifact } from "./types";

type ArtifactViewProps = {
  artifact: Artifact;
  isArtifactsCollapsed: boolean;
};

export function ArtifactView({ artifact, isArtifactsCollapsed }: ArtifactViewProps) {
  const markdownScrollRef = useRef<HTMLDivElement>(null);
  const [activeHeading, setActiveHeading] = useState("title");

  useEffect(() => {
    setActiveHeading("title");
  }, [artifact.title]);

  useEffect(() => {
    const container = markdownScrollRef.current;

    if (!container) {
      return;
    }

    function updateActiveHeading() {
      if (!container) {
        return;
      }

      if (container.scrollTop <= 0) {
        setActiveHeading("title");
        return;
      }

      const nextActive =
        headingReferenceItems.reduce((current, item) => {
          const heading = container.querySelector<HTMLElement>(
            `[data-heading-id="${item.id}"]`
          );

          if (!heading) {
            return current;
          }

          return heading.offsetTop <= container.scrollTop + 96 ? item.id : current;
        }, "title") ?? "title";

      setActiveHeading(nextActive);
    }

    updateActiveHeading();
    container.addEventListener("scroll", updateActiveHeading, { passive: true });

    return () => {
      container.removeEventListener("scroll", updateActiveHeading);
    };
  }, [artifact.markdown]);

  function scrollToHeading(id: string) {
    const container = markdownScrollRef.current;
    const heading = container?.querySelector<HTMLElement>(`[data-heading-id="${id}"]`);

    if (!container || !heading) {
      return;
    }

    container.scrollTo({
      top: Math.max(heading.offsetTop - 24, 0),
      behavior: "smooth"
    });
    setActiveHeading(id);
  }

  return (
    <section
      aria-label="Artifact view"
      className="relative flex h-full min-h-0 flex-col gap-3 overflow-hidden bg-transparent"
      style={{
        "--rail-width": isArtifactsCollapsed
          ? "calc(22rem + clamp(280px,22vw,340px) - var(--icon-button-size))"
          : "22rem"
      } as CSSProperties}
    >
      <div className="grid min-h-0 flex-1 gap-6 transition-[grid-template-columns] duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] xl:grid-cols-[minmax(0,1fr)_var(--rail-width)] xl:gap-8">
        <MarkdownDocument markdown={artifact.markdown} scrollRef={markdownScrollRef} />
        <HeadingReference
          activeHeading={activeHeading}
          items={headingReferenceItems}
          onSelectHeading={scrollToHeading}
        >
          <div className="space-y-2">
            <RailControls />
            <ArtifactChat />
          </div>
        </HeadingReference>
      </div>
    </section>
  );
}
