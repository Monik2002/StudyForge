# StudyForge — Design Specification

## 1. Design direction
A focused, modern learning workspace: calm, technical, high-contrast, and low-distraction. The interface should feel like a serious study tool, not a gamified social feed.

## 2. Visual language
- Dark navy/charcoal background with subtle blue-toned ambient gradients.
- Mint/green accent for primary actions, progress, and active states.
- Softly bordered cards with restrained gradients and rounded corners.
- Clear hierarchy through compact uppercase eyebrow labels, strong headlines, and readable body copy.
- Avoid excessive animation, decorative clutter, and large hero sections inside assessment flows.

## 3. Layout
- Center content in a responsive container with a maximum width around 1120px.
- Use a 12-column grid on wider screens; collapse to one column on narrow screens.
- Keep course creation and course lists visually distinct.
- Assessment screen: question content on the main column, question navigator and submission controls in a side panel.
- On mobile, stack the navigator below the question or provide a compact accessible navigation pattern.

## 4. Components
- **Primary button:** mint fill, dark text, clear hover/focus/disabled states.
- **Secondary button:** dark surface, neutral border, light text.
- **Cards:** dark panel, subtle border, consistent spacing.
- **Inputs:** full width, dark fill, clear label, visible focus ring and validation state.
- **Question options:** large click targets; selected option uses an accent border/background.
- **Status notices:** distinguish success and error using text plus color, not color alone.
- **Question navigator:** visibly distinguish current, answered, and flagged questions.
- **Progress:** concise label plus accessible progress indicator.

## 5. Typography and responsive behavior
- Use system/Inter-like sans-serif typography.
- Use `clamp()` for large headings so text scales across screen widths.
- Body text should remain comfortably readable; avoid fixed widths that cause mobile-like rendering on desktop.
- At mobile widths, reduce outer padding and stack cards. At desktop widths, preserve whitespace and use the full content width.

## 6. Interaction states
Every async action needs loading and error feedback.
Forms need required-field and length validation.
Buttons must be keyboard accessible.
Focused controls need visible focus states.
Avoid unexpected welcome flashes, delayed layout shifts, and unnecessary page reloads.
Warn before final submission when unanswered questions remain.
Show a clear timer state in exams and auto-submit/finalize on expiry.
Do not reveal exam answers until submission.

## 7. Accessibility
- Semantic headings and form labels.
- Keyboard operation for all controls.
- Visible focus rings and sufficient contrast.
- Do not communicate correctness, status, or errors through color alone.
- Support reduced motion if animation is introduced.
- Verify with automated and manual accessibility testing.

## 8. Current implementation notes
The current CSS defines a dark theme, mint accent, responsive grid, cards, options, and assessment navigation. The design has not yet had a formal visual QA or accessibility audit.


## Notes upload interaction
- The course notes form defaults to **Upload a file**, with a separate **Paste text** alternative.
- Supported uploads: PDF, DOCX, TXT, Markdown, PNG, JPG, and WEBP; maximum 20 MB.
- Show the selected filename and size only. Do not render an extracted-content preview.
- Keep upload and question generation in the same action, with a clear busy state and actionable errors.
