export function NoesisLogoMark() {
  return (
    <svg
      data-testid="noesis-logo-mark"
      aria-hidden="true"
      viewBox="0 0 40 40"
      className="h-7 w-7"
      fill="none"
    >
      <path
        d="M20 8.2c5.7 0 10.3 5.2 10.3 11.8S25.7 31.8 20 31.8 9.7 26.6 9.7 20 14.3 8.2 20 8.2Z"
        stroke="var(--accent)"
        strokeWidth="2"
      />
      <path
        d="M11.4 15.4c3.7-3.1 9.3-3.1 13 0 3.9 3.2 4.7 8.4 2 12.5"
        stroke="var(--chartreuse)"
        strokeLinecap="round"
        strokeWidth="2"
      />
      <path
        d="M15.3 23.4 20 16.1l4.7 7.3"
        stroke="var(--ink)"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2.35"
      />
      <circle cx="20" cy="16.1" r="2.45" fill="var(--accent)" />
      <circle cx="15.3" cy="23.4" r="2.1" fill="var(--chartreuse)" />
      <circle cx="24.7" cy="23.4" r="2.1" fill="var(--terracotta)" />
    </svg>
  );
}
