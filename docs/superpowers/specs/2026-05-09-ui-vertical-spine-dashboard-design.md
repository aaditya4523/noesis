# Noesis Vertical Spine Dashboard Design

## Goal

Design the first Noesis UI screen as a calm, local-first dashboard for general learning and personal research.

The screen should let a user:

- enter a topic they want to understand deeply
- select predefined source families such as official documentation, Wikipedia, Medium, or GeeksforGeeks
- optionally upload files
- optionally paste URLs
- generate a handbook artifact
- watch the system progress on the same screen

This design is for the first dashboard only. It does not define the broader multi-screen app shell.

## Product Positioning

This first screen is for users doing general learning and personal research, not exam-specific prep and not a power-user control panel.

The experience should feel:

- calm
- guided
- local-first
- document-oriented

It should not feel like:

- a chatbot conversation
- a generic SaaS admin dashboard
- a noisy research workbench
- a terminal-themed gimmick

## Core Interaction Model

The entire page is organized around a single vertical spine: one continuous line running down the page with step markers.

The spine is the governing interaction model for both user input and system execution.

The same line should cover the entire flow:

1. user-entered setup steps
2. the generate transition
3. runtime processing steps
4. final artifact reveal

This avoids a split between "form UI" and "progress UI." The page should feel like one uninterrupted research path.

## Primary Screen Structure

The first screen should be a single page with three vertical bands of attention:

1. `Masthead`
2. `Vertical spine workflow`
3. `Expanded artifact endpoint`

### Masthead

The top area should be restrained and compact.

It contains:

- the Noesis product name
- a short descriptor such as `Local-first handbook generation`
- a small local-status indicator

The masthead establishes identity but should not dominate the page.

### Vertical Spine Workflow

The main body is the spine.

Each step appears as:

- a dot or status marker on the line
- a content card anchored to that marker

The cards sit to the right of the spine and expand or collapse as the run progresses.

### Expanded Artifact Endpoint

The final artifact appears as the last major step on the same vertical line.

When complete, the artifact card expands larger than other cards, but remains visually anchored to the final step marker so the whole run still reads as one continuous flow.

## Step Sequence

The first version should use this spine sequence:

1. `Topic`
2. `Source presets`
3. `Optional evidence`
4. `Generate handbook`
5. `Collecting sources`
6. `Normalizing material`
7. `Preparing evidence`
8. `Drafting handbook`
9. `Finalizing artifact`
10. `Handbook ready`

The first four steps are user-facing intake and transition steps.
The next five are runtime system steps.
The last step is the artifact output state.

## Setup Step Behavior

### Topic

This opens first and contains the primary prompt asking what the user wants to understand deeply.

It should use a large, clear input with strong typographic emphasis.

### Source Presets

This becomes active only after the topic is meaningful.

It should present a predefined set of source-family options, including:

- `Official docs`
- `Wikipedia`
- `Medium`
- `GeeksforGeeks`

The design should support a selectable set of chips or segmented options rather than a raw checkbox list.

### Optional Evidence

This becomes active after source presets are chosen or skipped.

It should support:

- file uploads
- pasted URLs

Both inputs are optional. The step should clearly communicate that it can be skipped.

### Generate Handbook

This is the final intake step and the transition into execution.

The `Generate handbook` action must remain in the main reading flow on the spine, not isolated in a separate side column or secondary rail.

## Progressive Reveal

The page should progressively reveal only the next relevant step during intake.

Behavior:

1. `Topic` is open first.
2. Once topic input is meaningful, `Source presets` becomes active.
3. Once presets are selected or intentionally skipped, `Optional evidence` becomes active.
4. Once required inputs are satisfied, `Generate handbook` becomes active.

Completed intake steps should collapse into compact summaries:

- topic becomes a one-line topic summary
- source presets become a compact chip row
- optional evidence becomes `Skipped` or a short count summary such as `2 files, 3 links`

This keeps the upper part of the spine readable once runtime execution begins.

## Execution on the Same Spine

After the user triggers generation:

- intake steps remain visible as completed compact summaries
- runtime steps appear below on the same vertical line
- the active runtime step pulses
- completed runtime steps convert to checkmarked archive states

This is the key behavior that defines the design. The system does not switch to a separate status panel or bottom section.

## Runtime Step Content

Each runtime step should include:

- a step title
- a short status phrase
- active, complete, or error visual state
- an optional concise machine note below the step while active

Example runtime copy:

- `Collecting sources` -> `Searching selected source families`
- `Normalizing material` -> `Cleaning and structuring extracted text`
- `Preparing evidence` -> `Chunking and indexing research material`
- `Drafting handbook` -> `Composing cited handbook sections`
- `Finalizing artifact` -> `Preparing readable output`

These lines should feel like precise instrumentation, not chatty narration.

## Artifact Reveal

When the run completes, the final artifact should appear as the last major step on the spine.

The artifact step should:

- expand wider and taller than normal step cards
- feel more document-like than app-like
- clearly read as the outcome of the flow

The artifact is a handbook only for this first design.

No separate research-pack surface is required in this version.

## Visual Direction

The approved direction is a calm editorial-research aesthetic with a living signal spine.

### Tone

Use:

- warm paper-like background surfaces
- dark ink typography
- one electric cyan signal accent

Avoid:

- purple gradient SaaS styling
- glassmorphism
- terminal theater
- over-rounded playful UI
- dense dashboard chrome

### Typography

Use a serif display face for:

- major prompts
- section titles
- document-oriented surfaces

Pair it with a sharp mono or restrained sans for:

- step labels
- metadata
- machine-state copy

This contrast reinforces the distinction between user intent, machine execution, and final artifact.

### Spine Styling

The spine should be:

- thin
- continuous
- visually stable down the page
- slightly brighter around the active region

Markers should communicate state:

- hollow dot for idle
- softly pulsing dot for active
- checkmark for complete
- muted skipped marker for skipped optional steps
- distinct error marker for failed steps

Motion should be subtle and precise, closer to instrument feedback than decorative animation.

### Surfaces

Cards should feel like layered paper or archival sheets:

- off-white surfaces
- thin borders or rules
- restrained shadows
- generous spacing

The final artifact card should feel most like a reading object.

## State Model

The screen should be implemented as an explicit local state machine.

Top-level UI modes:

- `intake`
- `running`
- `complete`
- `error`

Each step should also support explicit statuses:

- `idle`
- `active`
- `complete`
- `skipped`
- `error`

This design should not rely on ad hoc booleans spread across unrelated components.

## Data Collected by the UI

The first dashboard should collect:

- `topic`
- `selected source families`
- `uploaded files`
- `pasted links`

On generate, these values become a single run payload.

Even if the first implementation uses mocked runtime progression, the UI structure should assume a later event-driven run model where backend events advance the spine.

## Error Handling

Errors must appear inline on the same vertical spine.

Failure behavior:

- the failing runtime step changes to an error marker
- a short explanation appears directly under that step
- prior completed intake and runtime steps remain visible
- the artifact step remains pending
- the user gets a clear retry action in context

The page should feel recoverable and stateful, not reset-prone.

## Implementation Boundary

The first shipped implementation does not need real backend integration.

It must prove:

- the vertical spine interaction model
- progressive reveal through intake
- transition from user steps to runtime steps on the same line
- correct rendering of active, complete, skipped, and error states
- an expanded final artifact state that feels like the earned endpoint

Mocked runtime progression is acceptable for the first slice as long as the event model is realistic enough to swap for live engine updates later.

## Testing Focus

The first implementation should verify:

- intake steps reveal in the correct order
- intake steps collapse into summaries after generation
- runtime steps append to the same spine in order
- step-state markers render correctly for `idle`, `active`, `complete`, `skipped`, and `error`
- optional file and link inputs can be omitted safely
- the final artifact card expands correctly from the last spine step
- inline error handling preserves prior progress

## Relationship to Prior UI Spec

This document supersedes the earlier intake-first layout direction in [2026-05-03-ui-intake-local-first-design.md](D:\REPOS\Projects\Noesis\docs\superpowers\specs\2026-05-03-ui-intake-local-first-design.md) for the first-screen interaction model.

The earlier spec established useful constraints:

- repo placement under `ui/`
- frontend-only first implementation
- general warm editorial aesthetic

Those remain valid.

The main change is structural:

- replace the prior split intake-plus-processing layout
- use one continuous vertical spine for intake, execution, and artifact output

## Recommended First Implementation Shape

Inside `ui/src`, the first implementation should likely separate:

- a spine state model
- step-card components
- marker/state visuals
- mock runtime progression
- artifact preview surface

The exact file map can be decided during implementation planning, but the architecture should preserve the spine as the top-level organizing primitive.
