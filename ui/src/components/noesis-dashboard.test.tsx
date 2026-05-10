import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { NoesisDashboard } from "./noesis-dashboard";

describe("NoesisDashboard", () => {
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
    const chatRow = screen.getByTestId("chat-row");
    const headingReference = screen.getByTestId("heading-reference");
    const referenceRail = screen.getByTestId("reference-rail");
    const railControls = screen.getByTestId("rail-controls");

    expect(screen.queryByRole("navigation", { name: /workspace tabs/i })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /add new topic/i })).toBeInTheDocument();
    expect(screen.getByRole("main").className).toContain("h-screen");
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
    expect(dashboardShell?.className.includes("76px")).toBe(false);
    expect(dashboardShell?.className.includes("bg-white/30")).toBe(false);
    expect(dashboardShell?.className.includes("bg-transparent")).toBe(true);
    expect(screen.getByRole("main").className).toContain("pb-5");
    expect(dashboardShell?.className.includes("shadow-[0_28px_90px")).toBe(false);
    expect(dashboardShell?.classList.contains("p-3")).toBe(false);
    expect(dashboardShell?.classList.contains("rounded-[38px]")).toBe(false);
    expect(artifactList.className.includes("bg-white/50")).toBe(false);
    expect(artifactList.className.includes("bg-[#f7ff4a]")).toBe(false);
    expect(artifactList.className).not.toMatch(/\bborder\b/);
    expect(artifactList.classList.contains("border-2")).toBe(false);
    expect(artifactList.className.includes("shadow-")).toBe(false);
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
    expect(markdownFile).toBeInTheDocument();
    expect(markdownFile.className).not.toContain("shadow-");
    expect(within(markdownFile).getByText("Operational brief for reusable prompt patterns")).toBeInTheDocument();
    expect(within(markdownFile).getByRole("heading", { name: "What this artifact is for", level: 2 })).toBeInTheDocument();
    const distilledFindingsHeading = within(markdownFile).getByRole("heading", { name: "Distilled findings", level: 3 });
    expect(distilledFindingsHeading).toBeInTheDocument();
    expect(distilledFindingsHeading.className).toContain("mb-3");
    expect(within(markdownFile).getByText(/Instruction shape matters most/).closest("li")?.className).not.toContain("border-b");
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
    expect(railControls.className).toContain("absolute");
    expect(railControls.className).toContain("bottom-0");
    expect(railControls.className).toContain("w-[200px]");
    expect(within(railControls).getByRole("button", { name: /summarize artifact/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /design ppt/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /create study notes/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /export markdown/i }).className).toContain("h-[var(--button-height)]");
    expect(within(railControls).getByRole("button", { name: /export pdf/i }).className).toContain("h-[var(--button-height)]");
    expect(artifactView.querySelector(".bg-\\[\\#111111\\]")).toBeNull();
    expect(within(artifactView).queryByRole("button", { name: /audio chat/i })).not.toBeInTheDocument();
    expect(within(headingReference).getByRole("button", { name: "H1 Title" })).toHaveAttribute("aria-current", "true");
    expect(within(headingReference).getByRole("button", { name: "H2 Summary" })).toHaveAttribute("aria-current", "false");
    expect(within(headingReference).getByRole("button", { name: "H3 Distilled findings" }).className).toContain("ml-4");
    expect(chatInput.parentElement?.className.includes("bg-[color:var(--artifact)]")).toBe(true);
    expect(artifactView.className).toContain("gap-3");
    expect(artifactView.className).toContain("h-full");
    expect(chatRow.className).toContain("xl:grid-cols-[minmax(0,1fr)_200px]");
    expect(chatDock.className).toContain("bg-[color:var(--artifact)]");
    expect(chatDock.className).not.toMatch(/\bborder-t\b/);
    expect(chatDock.className).not.toMatch(/\bp-3\b/);
    expect(chatInput.className).toContain("h-[calc(var(--button-height)-1rem)]");
    expect(sendButton.className.includes("bg-[color:var(--ink)]")).toBe(true);
    expect(sendButton.className.includes("hover:bg-[color:var(--accent)]")).toBe(true);
    expect(sendButton.className).toContain("h-[calc(var(--button-height)-1rem)]");
  });

  it("keeps the artifact work area free of wrapper panel treatment", () => {
    const { container } = render(<NoesisDashboard />);
    const artifactView = screen.getByRole("region", { name: /artifact view/i });
    const artifactWorkArea = container.querySelector('[aria-label="Artifact view"] > div');

    expect(artifactView.className).not.toMatch(/\bborder\b/);
    expect(artifactView.className).not.toContain("bg-[color:var(--surface)]");
    expect(artifactView.className).not.toContain("shadow-fine");
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
