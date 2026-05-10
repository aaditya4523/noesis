export type Artifact = {
  title: string;
  source: string;
  status: string;
  detail: string;
  dateGroup: string;
  prompt: string;
  subtitle: string;
  purpose: string;
  markdown: string;
};

export type HeadingReferenceItem = {
  id: string;
  label: string;
  level: "H1" | "H2" | "H3";
};
