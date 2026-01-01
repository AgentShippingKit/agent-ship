# AgentShip Brand Guidelines

> Ship AI agents to production in minutes, not weeks.

---

## Brand Overview

AgentShip is a developer platform that helps engineers deploy AI agents to production quickly and securely. Our brand reflects **speed**, **reliability**, and **developer-first thinking**.

### Brand Personality
- **Confident** — We know what we're doing
- **Fast** — Ship in minutes, not weeks  
- **Trustworthy** — Production-ready, secure by default
- **Developer-friendly** — Clean, no-nonsense, professional

---

## Logo

The AgentShip logo consists of two elements:

1. **Icon** — A tilted rocket in launch trajectory with an AI agent core (indigo circle) and verified badge (teal checkmark). The motion trail conveys speed and deployment.

2. **Wordmark** — "Agent" in slate + "Ship" in indigo, bold geometric sans-serif.

### Logo Versions

| File | Use Case |
|------|----------|
| `logo-full.svg` | Primary logo for light backgrounds |
| `logo-full-dark.svg` | Primary logo for dark backgrounds |
| `logo-icon.svg` | Icon only (64px square) |
| `wordmark.svg` | Text only for light backgrounds |
| `wordmark-dark.svg` | Text only for dark backgrounds |

### Clear Space

Maintain clear space around the logo equal to the height of the "A" in AgentShip.

### Minimum Sizes

- Full logo: 120px wide minimum
- Icon only: 24px minimum
- Favicon: 16px (use `favicon-16.svg`)

---

## Color Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Slate 800** | `#1E293B` | Primary text, rocket body |
| **Indigo 500** | `#6366F1` | Agent core, "Ship" text, accents |
| **Teal 600** | `#0D9488` | Verified badge, CTAs, success states |

### Secondary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Slate 900** | `#0F172A` | Dark backgrounds |
| **Slate 700** | `#334155` | Secondary text |
| **Slate 500** | `#64748B` | Muted text, borders |
| **Slate 400** | `#94A3B8` | Placeholder, disabled |
| **Indigo 300** | `#A5B4FC` | Agent inner glow |
| **Indigo 400** | `#818CF8` | "Ship" on dark backgrounds |
| **Teal 300** | `#5EEAD4` | Flame highlight |

### Background Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **White** | `#FFFFFF` | Page backgrounds |
| **Slate 50** | `#F8FAFC` | Cards, subtle backgrounds |
| **Slate 100** | `#F1F5F9` | Section backgrounds |
| **Slate 900** | `#0F172A` | Dark mode backgrounds |
| **Slate 800** | `#1E293B` | Dark mode cards |

---

## Typography

### Font Stack

```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

For a more distinctive look, consider:
- **Inter** — Clean, highly legible
- **Geist** — Modern, Vercel-inspired
- **Plus Jakarta Sans** — Friendly, professional

### Weights

- **800 (Extra Bold)** — Logo wordmark, hero headlines
- **700 (Bold)** — Section headings
- **600 (Semi Bold)** — Subheadings, buttons
- **500 (Medium)** — Body text emphasis
- **400 (Regular)** — Body text

### Letter Spacing

- Headlines: `-0.02em` to `-0.03em` (tight)
- Body: `0` (normal)
- Code: `0` (normal)

---

## Iconography

Use simple, geometric icons that match our clean aesthetic.

**Recommended icon libraries:**
- Lucide Icons
- Heroicons
- Phosphor Icons

**Icon style:**
- 1.5-2px stroke weight
- Rounded caps and joins
- Consistent 24px base size

---

## Assets Included

### Logos
- `logo-full.svg` — Full logo, light background
- `logo-full-dark.svg` — Full logo, dark background
- `logo-icon.svg` — Icon only (64x64)
- `wordmark.svg` — Text only, light
- `wordmark-dark.svg` — Text only, dark

### Favicons
- `favicon-32.svg` — 32x32 favicon
- `favicon-16.svg` — 16x16 favicon

### Banners
- `github-banner.svg` — GitHub README header (1280x320)
- `social-preview.svg` — Open Graph image (1200x630)
- `docs-header.svg` — Documentation header (960x200)

---

## Usage Examples

### GitHub README

```markdown
<p align="center">
  <img src="./assets/github-banner.svg" alt="AgentShip" width="100%">
</p>
```

### Favicon (HTML)

```html
<link rel="icon" type="image/svg+xml" href="/favicon-32.svg">
<link rel="icon" type="image/svg+xml" sizes="16x16" href="/favicon-16.svg">
```

### Open Graph (HTML)

```html
<meta property="og:image" content="https://agentship.dev/social-preview.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
```

---

## Don'ts

- ❌ Don't rotate the logo (it's already tilted by design)
- ❌ Don't change the logo colors
- ❌ Don't add effects like shadows or gradients
- ❌ Don't stretch or distort the logo
- ❌ Don't place on busy backgrounds without contrast
- ❌ Don't remove the verified badge from the icon

---

## File Formats

All source files are SVG for maximum flexibility. Export to PNG at 2x or 3x for raster needs.

**Recommended exports:**
- Favicon: `.ico` (multi-resolution) or `.png`
- Social: `.png` at 1200x630
- Print: `.pdf` or high-res `.png`

---

## Contact

Questions about brand usage? Open an issue on GitHub or reach out to the maintainers.

---

**AgentShip** — Ship AI agents to production in minutes, not weeks.
