## 2026-09-30 - Scrollable Code/Preview Regions Keyboard Accessibility
**Learning:** Scrollable containers with `overflow-y: auto` (like preview areas) must have `tabindex="0"`, `role="region"`, and an `aria-labelledby` or `aria-label` attribute to ensure keyboard users can focus and scroll through content using arrow keys or Page Up/Down.
**Action:** Always make scrollable preview boxes keyboard-focusable with proper ARIA region semantics and visible focus indicators.
