# Design System: Editorial Automation & Pipeline Logic

## 1. Overview & Creative North Star
**The Creative North Star: "The Kinetic Architect"**

This design system moves beyond the "SaaS Dashboard" trope. It is a visual manifestation of logic—a high-end, editorial approach to data-driven automation. We treat the interface not as a collection of boxes, but as a fluid "pipeline" of intent. By leveraging intentional asymmetry, sophisticated tonal layering, and an aggressive rejection of traditional borders, we create an environment that feels both authoritative and ethereal. 

The system breaks the "template" look by using **Inter** for utility, **Manrope** for editorial presence, and **Space Grotesk** for technical data markers. This typographic friction, combined with a "No-Line" philosophy, ensures that the user is guided by visual weight and background shifts rather than rigid structural grids.

---

## 2. Colors & Surface Philosophy

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning. Boundaries must be defined solely through background color shifts.
*   *Implementation:* A `surface-container-low` section sitting directly on a `surface` background creates a natural, sophisticated edge.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—stacked sheets of tinted glass. 
*   **Base Layer:** `surface` (#11131c)
*   **Logical Grouping:** `surface-container` (#1d1f29)
*   **Actionable Cards:** `surface-container-high` (#282933)
*   **Modal/Floating:** `surface-container-highest` (#32343e) with backdrop-blur.

### Signature Textures
Main CTAs and hero elements must avoid flat fills. Use a subtle linear gradient from `primary` (#bbc6e2) to `primary-container` (#0f1a2e) at a 135-degree angle to provide "visual soul."

---

## 3. Typography: The Triple-Threat Scale

We use three distinct typefaces to separate "Action," "Data," and "Narrative."

*   **Editorial/Headlines (Manrope):** High-end, wide-aperture sans-serif. Use `display-lg` (3.5rem) and `headline-md` (1.75rem) to establish a dominant hierarchy.
*   **Functional/Body (Inter):** The workhorse for automation logic. Use `body-md` (0.875rem) for all pipeline descriptions.
*   **Technical/Labels (Space Grotesk):** For data density. Use `label-md` (0.75rem) for status indicators, timestamps, and machine-read parameters. This monospaced-adjacent feel reinforces the "Automation Engine" persona.

---

## 4. Elevation & Depth: Tonal Layering

### The Layering Principle
Depth is achieved by "stacking" the surface-container tiers. Place a `surface-container-lowest` card on a `surface-container-low` section to create a soft, natural lift without needing a shadow.

### Ambient Shadows
If a floating effect is required (e.g., a critical "Run Pipeline" button), shadows must be:
*   **Blur:** 24px - 40px
*   **Opacity:** 6% - 10%
*   **Color:** Use a tinted version of `on-surface` (#e1e1ef) to mimic natural light dispersion.

### Glassmorphism & Depth
For overlays and sidebars, use `surface_bright` (#373943) at 60% opacity with a `20px` backdrop-blur. This allows the underlying pipeline flow to bleed through, maintaining the user’s mental map of the engine.

---

## 5. Components

### Minimalist Cards
*   **Style:** No borders. Use `surface-container-low` for inactive states and `surface-container-high` for hover states.
*   **Corner Radius:** Use `lg` (0.5rem) for the card outer shell and `md` (0.375rem) for nested elements.
*   **Spacing:** Use `8` (1.75rem) for internal padding to ensure "breathing room" in data-dense views.

### Buttons (The Interaction Kinetic)
*   **Primary:** A gradient from `tertiary` (#4cd6ff) to `on-tertiary-container` (#008eae). Text color: `on-tertiary`.
*   **Secondary:** Ghost style. No background fill. `label-md` weight text using `primary` color.
*   **Tertiary:** `surface-container-highest` background with `on-surface-variant` text.

### The Pipeline Indicator (Custom Component)
Instead of standard progress bars, use "Kinetically Linked Nodes." Small circles using `tertiary` (#4cd6ff) for completed, `primary` (#bbc6e2) for pending, and `error` (#ffb4ab) for missed. Connect them with a 2px vertical "track" using `outline-variant` at 20% opacity.

### Input Fields
*   **Design:** Flat backgrounds using `surface-container-lowest`. 
*   **Focus State:** Do not use a border. Use a 2px bottom-accent in `tertiary` (#4cd6ff) and a subtle glow.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical layouts (e.g., a wide pipeline view next to a narrow, high-density data sidebar).
*   **Do** use `16` (3.5rem) spacing between major sections to emphasize the "minimalist" brand personality.
*   **Do** use `on-tertiary-container` for small, high-contrast labels to draw the eye to status changes.

### Don't:
*   **Don't** use 1px solid dividers. Use vertical whitespace `6` (1.3rem) or `8` (1.75rem) instead.
*   **Don't** use pure black (#000) or pure white (#FFF). Stick strictly to the neutral palette (`surface` and `on-surface`).
*   **Don't** use standard "drop shadows" on cards. Rely on color-shifting or the "Ghost Border" (10% opacity `outline-variant`) if accessibility requires it.
*   **Don't** clutter the view. If an automation step has more than 5 parameters, use a "Glassmorphic" drawer to hide complexity.