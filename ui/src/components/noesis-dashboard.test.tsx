import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { NoesisDashboard } from "./noesis-dashboard";

describe("NoesisDashboard", () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
  });

  it("shows the sidebar tabs, artifact list, and artifact viewer by default", () => {
    const { container } = render(<NoesisDashboard />);
    const dashboardShell = container.querySelector("main > div.mx-auto");
    const artifactList = screen.getByRole("region", { name: /artifacts/i });
    const artifactView = screen.getByRole("region", { name: /artifact view/i });
    const markdownFile = within(artifactView).getByRole("article", { name: /markdown file/i });
    const markdownFrame = within(markdownFile).getByTestId("markdown-frame");
    const markdownScroll = within(markdownFile).getByTestId("markdown-scroll");
    const chatInput = screen.getByLabelText("Artifact chat");
    const sendButton = screen.getByRole("button", { name: /send chat message/i });
    const chatDock = screen.getByTestId("chat-dock");
    const headingReference = screen.getByTestId("heading-reference");
    const referenceRail = screen.getByTestId("reference-rail");
    const railControls = screen.getByTestId("rail-controls");
    const collapseArtifactsButton = within(artifactList).getByRole("button", { name: /collapse artifacts panel/i });
    const brandMark = within(artifactList).getByTestId("brand-mark");

    expect(screen.queryByRole("navigation", { name: /workspace tabs/i })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /add new topic/i })).toBeInTheDocument();
    expect(screen.getByRole("main").className).toContain("h-screen");
    expect(screen.getByRole("main").className).toContain("p-5");
    expect(screen.getByRole("main").className).toContain("sm:p-8");
    expect(artifactList).toBeInTheDocument();
    expect(artifactView).toBeInTheDocument();
    expect(within(artifactList).getByText("Noesis")).toBeInTheDocument();
    expect(within(artifactList).queryByText("Recent generated topics")).not.toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /search/i })).toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /help/i })).toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /settings/i })).toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /search/i }).className).toContain("h-[var(--icon-button-size)]");
    expect(screen.getByRole("button", { name: /add new topic/i }).className).toContain("h-[var(--field-height)]");
    expect(within(artifactList).getByText("Prompt Engineering Handbook")).toBeInTheDocument();
    expect(within(artifactList).getByText("Retrieval Quality Notes")).toBeInTheDocument();
    expect(within(artifactList).getByText("24 minutes ago")).toBeInTheDocument();
    expect(within(artifactList).queryByText(/docs \+ papers/i)).not.toBeInTheDocument();
    expect(within(artifactList).queryByText(/web \+ notes/i)).not.toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ask about this artifact/i)).toBeInTheDocument();
    expect(container.querySelector('[aria-label="Artifact view"] .max-w-3xl')).toBeNull();
    expect(dashboardShell?.className.includes("max-w-")).toBe(false);
    expect(dashboardShell?.className).toContain("lg:grid-cols-[var(--artifacts-column)_minmax(0,1fr)]");
    expect(dashboardShell?.className).toContain("transition-[grid-template-columns]");
    expect(dashboardShell?.getAttribute("style")).toContain("--artifacts-column: clamp(280px,22vw,340px)");
    expect(dashboardShell?.className).toContain("gap-6");
    expect(dashboardShell?.className).toContain("xl:gap-8");
    expect(dashboardShell?.className.includes("76px")).toBe(false);
    expect(dashboardShell?.className.includes("bg-white/30")).toBe(false);
    expect(dashboardShell?.className.includes("bg-transparent")).toBe(true);
    expect(screen.getByRole("main").className).not.toContain("px-3");
    expect(dashboardShell?.className.includes("shadow-[0_28px_90px")).toBe(false);
    expect(dashboardShell?.classList.contains("p-3")).toBe(false);
    expect(dashboardShell?.classList.contains("rounded-[38px]")).toBe(false);
    expect(artifactList.className.includes("bg-white/50")).toBe(false);
    expect(artifactList.className.includes("bg-[#f7ff4a]")).toBe(false);
    expect(artifactList.className).not.toMatch(/\bborder\b/);
    expect(artifactList.classList.contains("border-2")).toBe(false);
    expect(artifactList.className.includes("shadow-")).toBe(false);
    expect(artifactList.className.includes("rounded-")).toBe(false);
    expect(artifactList.className).toContain("px-0");
    expect(artifactList.className).toContain("py-0");
    expect(artifactList.className).toContain("flex-col");
    expect(artifactList.className).toContain("duration-300");
    expect(artifactList.className).not.toMatch(/\bp-4\b/);
    expect(collapseArtifactsButton.className).toContain("mt-auto");
    expect(brandMark.className).not.toContain("shadow-");
    expect(brandMark.className).toContain("h-[var(--icon-button-size)]");
    expect(brandMark.className).toContain("w-[var(--icon-button-size)]");
    expect(brandMark.className).not.toContain("brand-icon-size");
    expect(brandMark.className).not.toContain("text-white");
    expect(within(brandMark).getByTestId("noesis-logo-mark")).toBeInTheDocument();
    expect(artifactView.className.includes("0_20px_70px")).toBe(false);
    expect(artifactView.className.includes("bg-[#e9e5dc]")).toBe(false);
    expect(artifactView.classList.contains("border-2")).toBe(false);
    expect(artifactView.className.includes("p-5")).toBe(false);
    expect(artifactView.className.includes("sm:p-7")).toBe(false);
    expect(artifactView.className.includes("rounded-[38px]")).toBe(false);
    expect(within(artifactView).queryByText("Prompt Engineering Handbook.md")).not.toBeInTheDocument();
    expect(within(artifactView).queryByText("Markdown file")).not.toBeInTheDocument();
    expect(within(artifactView).queryByText("Ready")).not.toBeInTheDocument();
    expect(within(artifactView).queryByText("Artifact view")).not.toBeInTheDocument();
    expect(within(artifactView).queryByTestId("markdown-accordion")).not.toBeInTheDocument();
    expect(markdownFile).toBeInTheDocument();
    expect(markdownFile.className).not.toContain("shadow-");
    expect(within(markdownFile).getByText("Operational brief for reusable prompt patterns")).toBeInTheDocument();
    expect(within(markdownFile).getByRole("heading", { name: "What this artifact is for", level: 2 })).toBeInTheDocument();
    const distilledFindingsHeading = within(markdownFile).getByRole("heading", { name: "Distilled findings", level: 3 });
    expect(distilledFindingsHeading).toBeInTheDocument();
    expect(distilledFindingsHeading.className).toContain("mb-3");
    expect(within(markdownFile).getByText(/Instruction shape matters most/).closest("li")?.className).not.toContain("border-b");
    const orderedList = within(markdownFile).getByText(/Instruction shape matters most/).closest("ol");
    expect(orderedList?.className).toContain("w-full");
    expect(orderedList?.className).not.toContain("max-w-[48rem]");
    expect(within(markdownFile).getByText(/Prompt Files/).closest("ul")?.className).toContain("w-full");
    expect(within(markdownFile).getByText(/Prompt Files/).closest("ul")?.className).not.toContain("max-w-[48rem]");
    expect(markdownScroll.className).toContain("overflow-y-auto");
    expect(markdownScroll.className).toContain("scrollbar-none");
    expect(markdownScroll.className).toContain("bg-[color:var(--artifact)]");
    expect(markdownFrame.className).not.toContain("after:shadow");
    expect(markdownFile.classList.contains("border-2")).toBe(false);
    const artifactHeading = within(markdownFile).getByRole("heading", { name: "Prompt Engineering Handbook", level: 1 });
    expect(artifactHeading).toBeInTheDocument();
    expect(artifactHeading.className).toContain("font-artifact");
    expect(artifactHeading.className).toContain("text-5xl");
    expect(artifactHeading.className).toContain("font-extrabold");
    expect(artifactHeading.className).not.toContain("text-6xl");
    expect(within(markdownFile).getByRole("heading", { name: "Sources", level: 2 })).toBeInTheDocument();
    expect(within(markdownFile).getByRole("heading", { name: "Recommendations", level: 2 })).toBeInTheDocument();
    expect(within(markdownFile).getByRole("heading", { name: "Evaluation checklist", level: 2 })).toBeInTheDocument();
    expect(within(markdownFile).getByRole("link", { name: "Prompt Files" })).toHaveAttribute("href", "#prompt-files");
    expect(within(markdownFile).queryByText("Verified source")).not.toBeInTheDocument();
    expect(within(markdownFile).queryByText("## Export")).not.toBeInTheDocument();
    expect(within(markdownFile).queryByRole("button", { name: /export markdown/i })).not.toBeInTheDocument();
    expect(within(markdownFile).queryByRole("button", { name: /export pdf/i })).not.toBeInTheDocument();
    expect(within(artifactView).queryByText("Headings")).not.toBeInTheDocument();
    expect(within(artifactView).queryByText("Export options")).not.toBeInTheDocument();
    expect(within(referenceRail).queryByRole("region", { name: /artifact sources/i })).not.toBeInTheDocument();
    const headingAccordion = screen.getByTestId("heading-accordion");
    expect(headingAccordion.tagName.toLowerCase()).toBe("section");
    expect(headingAccordion.className).toContain("border");
    expect(headingAccordion.className).toContain("top-0");
    expect(headingAccordion.className).not.toContain("top-5");
    expect(within(headingAccordion).getByText("Outline")).toBeInTheDocument();
    expect(within(headingAccordion).getByRole("button", { name: /open outline/i })).toHaveAttribute("aria-expanded", "false");
    expect(screen.getByText("Open")).toBeInTheDocument();
    expect(headingAccordion.querySelector("#heading-reference-panel")?.className).toContain("grid-rows-[0fr]");
    expect(headingAccordion.querySelector("#heading-reference-panel")?.className).toContain("overflow-hidden");
    expect(headingAccordion.querySelector("#heading-reference-panel")?.className).toContain("pointer-events-none");
    expect(headingAccordion.querySelector("#heading-reference-panel")?.className).toContain("duration-300");
    expect(headingReference.className).toContain("border-t-0");
    expect(headingReference.className).toContain("py-0");
    expect(referenceRail.className).toContain("justify-between");
    expect(referenceRail.className).toContain("flex-col");
    expect(referenceRail).toContainElement(railControls);
    expect(referenceRail).toContainElement(chatDock);
    expect(within(railControls).getByRole("region", { name: /artifact actions/i }).className).toContain("grid-cols-2");
    expect(within(railControls).getByTestId("export-controls").className).toContain("grid-cols-2");
    expect(within(railControls).getByRole("button", { name: /summarize artifact/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /summarize artifact/i }).className).toContain("rounded-[var(--control-radius)]");
    expect(within(railControls).getByRole("button", { name: /design ppt/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).queryByRole("button", { name: /create study notes/i })).not.toBeInTheDocument();
    expect(within(railControls).getByRole("button", { name: /export markdown/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /export pdf/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /export pdf/i }).className).toContain("text-[color:var(--action-strong-ink)]");
    expect(within(railControls).getByRole("button", { name: /export pdf/i }).className).not.toContain("text-white");
    expect(artifactView.querySelector(".bg-\\[\\#111111\\]")).toBeNull();
    expect(within(artifactView).queryByRole("button", { name: /audio chat/i })).not.toBeInTheDocument();
    expect(within(headingReference).getByRole("button", { name: "H1 Title", hidden: true })).toHaveAttribute("aria-current", "true");
    expect(within(headingReference).getByRole("button", { name: "H2 Summary", hidden: true })).toHaveAttribute("aria-current", "false");
    expect(within(headingReference).getByRole("button", { name: "H3 Distilled findings", hidden: true }).className).toContain("ml-4");
    expect(chatInput.parentElement?.className.includes("bg-[color:var(--artifact)]")).toBe(true);
    expect(artifactView.className).toContain("gap-3");
    expect(artifactView.className).toContain("h-full");
    expect(chatDock.className).toContain("bg-[color:var(--artifact)]");
    expect(chatDock.className).not.toMatch(/\bborder-t\b/);
    expect(chatDock.className).not.toMatch(/\bp-3\b/);
    expect(chatInput.className).toContain("h-[calc(var(--button-height)-1rem)]");
    expect(chatInput.className).toContain("artifact-chat-input");
    expect(chatInput.className).toContain("border-0");
    expect(chatInput.className).toContain("outline-none");
    expect(sendButton.className.includes("bg-[color:var(--ink)]")).toBe(true);
    expect(sendButton.className.includes("hover:bg-[color:var(--accent)]")).toBe(true);
    expect(sendButton.className).toContain("h-[calc(var(--button-height)-1rem)]");
    expect(sendButton.className).toContain("rounded-[var(--control-radius)]");
  });

  it("keeps the artifact work area free of wrapper panel treatment", () => {
    const { container } = render(<NoesisDashboard />);
    const artifactView = screen.getByRole("region", { name: /artifact view/i });
    const artifactWorkArea = container.querySelector('[aria-label="Artifact view"] > div');

    expect(artifactView.className).not.toMatch(/\bborder\b/);
    expect(artifactView.className).not.toContain("bg-[color:var(--surface)]");
    expect(artifactView.className).not.toContain("shadow-fine");
    expect(artifactWorkArea?.className).toContain("xl:grid-cols-[minmax(0,1fr)_var(--rail-width)]");
    expect(artifactWorkArea?.className).toContain("transition-[grid-template-columns]");
    expect(artifactWorkArea?.className).toContain("gap-6");
    expect(artifactWorkArea?.className).toContain("xl:gap-8");
    expect(artifactWorkArea?.className).not.toMatch(/\bp-3\b/);
    expect(artifactWorkArea?.className).not.toMatch(/\bbg-\[/);
  });

  it("uses color-only hover and focus states without moving dashboard boxes", () => {
    const { container } = render(<NoesisDashboard />);
    const classNames = Array.from(container.querySelectorAll<HTMLElement>("[class]"))
      .map((element) => element.className)
      .join(" ");

    expect(classNames).not.toMatch(/(?:hover|focus):-(?:translate|scale)/);
    expect(classNames).not.toMatch(/(?:hover|focus):(?:translate|scale)-/);
  });

  it("toggles and persists dark mode from the sidebar control", async () => {
    const user = userEvent.setup();
    render(<NoesisDashboard />);

    expect(document.documentElement).toHaveAttribute("data-theme", "light");

    await user.click(screen.getByRole("button", { name: /switch to dark mode/i }));

    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    expect(window.localStorage.getItem("noesis-theme")).toBe("dark");
    expect(screen.getByRole("button", { name: /switch to light mode/i })).toBeInTheDocument();
  });

  it("collapses the artifacts panel into a compact rail", async () => {
    const user = userEvent.setup();
    const { container } = render(<NoesisDashboard />);
    const dashboardShell = container.querySelector("main > div.mx-auto");

    await user.click(screen.getByRole("button", { name: /collapse artifacts panel/i }));

    const artifactList = screen.getByRole("region", { name: /artifacts/i });
    expect(dashboardShell?.className).toContain("lg:grid-cols-[var(--artifacts-column)_minmax(0,1fr)]");
    expect(dashboardShell?.getAttribute("style")).toContain("--artifacts-column: var(--icon-button-size)");
    expect(screen.getByRole("region", { name: /artifact view/i }).getAttribute("style")).toContain("--rail-width: calc(22rem + clamp(280px,22vw,340px) - var(--icon-button-size))");
    expect(artifactList).toHaveAttribute("data-collapsed", "true");
    expect(within(artifactList).getByRole("button", { name: /add new topic/i }).className).toContain("h-[var(--icon-button-size)]");
    expect(within(artifactList).getByRole("button", { name: /add new topic/i }).className).toContain("w-[var(--icon-button-size)]");
    expect(within(artifactList).queryByText("Prompt Engineering Handbook")).not.toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /expand artifacts panel/i })).toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /search/i })).toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /help/i })).toBeInTheDocument();
    expect(within(artifactList).getByRole("button", { name: /settings/i })).toBeInTheDocument();
    expect(within(artifactList).getByTestId("collapsed-actions").className).not.toContain("px-");
    expect(within(artifactList).getByTestId("brand-mark").className).toContain("h-[var(--icon-button-size)]");
    expect(within(artifactList).getByTestId("brand-mark").className).toContain("w-[var(--icon-button-size)]");
    expect(within(artifactList).getByRole("button", { name: /expand artifacts panel/i }).className).toContain("h-[var(--icon-button-size)]");
    expect(within(artifactList).getByRole("button", { name: /expand artifacts panel/i }).className).toContain("w-[var(--icon-button-size)]");
    expect(within(artifactList).getByRole("button", { name: /expand artifacts panel/i }).className).not.toContain("w-full");
    expect(within(artifactList).getByRole("button", { name: /expand artifacts panel/i }).className).not.toContain("mx-");
  });

  it("opens a topic form with suggestions, upload, and link evidence sections", async () => {
    const user = userEvent.setup();
    render(<NoesisDashboard />);

    await user.click(screen.getByRole("button", { name: /add new topic/i }));

    const dialog = screen.getByRole("dialog", { name: /new topic/i });
    expect(within(dialog).getByLabelText("Topic").className).toContain("h-[var(--field-height)]");
    expect(within(dialog).getByLabelText("Additional suggestions").className).toContain("h-[var(--textarea-height)]");
    expect(within(dialog).getByText("Source presets")).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: "Docs" })).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: "Web" })).toBeInTheDocument();
    expect(within(dialog).getByText("Optional evidence")).toBeInTheDocument();
    expect(within(dialog).getByText("Sources upload from local device")).toBeInTheDocument();
    expect(within(dialog).getByLabelText("Upload source files")).toBeInTheDocument();
    expect(within(dialog).getByText("Give links")).toBeInTheDocument();
    expect(within(dialog).getByLabelText("Evidence links")).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: /generate artifact/i }).className).toContain("h-[var(--field-height)]");
  });

  it("selects source tags and replaces the form with process logs on submit", async () => {
    const user = userEvent.setup();
    render(<NoesisDashboard />);

    await user.click(screen.getByRole("button", { name: /add new topic/i }));
    await user.type(screen.getByLabelText("Topic"), "Knowledge Graphs");
    await user.click(screen.getByRole("button", { name: "Docs" }));
    await user.click(screen.getByRole("button", { name: "Papers" }));
    await user.click(screen.getByRole("button", { name: /generate artifact/i }));

    expect(screen.queryByLabelText("Topic")).not.toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: /generation progress/i })).toBeInTheDocument();
    expect(screen.getByText("Collecting sources")).toBeInTheDocument();
    expect(screen.getByText("Normalizing material")).toBeInTheDocument();
    expect(screen.getByText("Preparing evidence")).toBeInTheDocument();
    expect(screen.getByText("Drafting handbook")).toBeInTheDocument();
    expect(screen.getByText("Finalizing artifact")).toBeInTheDocument();
    expect(screen.getByText("Handbook ready")).toBeInTheDocument();
  });
});
