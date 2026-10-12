# Flux Design Implementation Notes: Warm Editorial Minimalism

Derived from `design (1).md`.

## 1. Aesthetic Vision
- **Theme:** Warm Editorial Minimalism. Feels like a high-end product catalog or Japanese architectural publication (uncoated paper, structured typography, generous whitespace).
- **Default Mode:** Light & warm canvas. No dark mode default. No SaaS dashboard tropes (no purple sidebars, no neon badges, no glowing gradient cards, no glassmorphism).

## 2. Color Tokens & Streamlit Mapping

| Design Token | Hex Code | Semantic Role | Streamlit / CSS Application |
|---|---|---|---|
| **Canvas** | `#F7F5F0` | Primary app background | Applied to `[data-testid="stAppViewContainer"]`, `body`, `.stApp` |
| **Alternate Canvas** | `#F2F0EA` | Subtle panel / secondary background | Sidebar background `[data-testid="stSidebar"]` |
| **Card Surface** | `#FFFFFF` | Metric cards, container surfaces | `.flux-card`, metric containers |
| **Elevated Surface** | `#FAFAF9` | Filter trays, highlight panels | Filter bars, preview boxes |
| **Border Default** | `#E7E5E4` | Component borders | Card borders, table borders, dividers |
| **Border Subtle** | `#F5F5F4` | Row dividers | Subtle table separators |
| **Text Primary** | `#1C1917` | Headings, main numbers, key labels | Headings `h1..h4`, primary copy, metric values |
| **Text Secondary** | `#78716C` | Captions, descriptions, metadata | Metric labels, subheaders, chart subtitles |
| **Text Muted / Hint**| `#A8A29E` | Inactive text, helper hints | Tooltips, placeholders, notes |
| **Accent Primary** | `#BFDBFE` | Soft sky blue accent (sparingly) | Active tab underline, key stat badge, focus indicator |
| **Action Accent** | `#93C5FD` | Button outlines, hover highlights | Secondary button hover, active pills |
| **Text on Accent** | `#1E40AF` | High-contrast blue text on accent | Badges, callout text |
| **Focus Accent** | `#60A5FA` | Focus rings | Input focus state |

## 3. Typography Stack & Hierarchy
- **Primary Font Stack:** `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Editorial Serif Accent:** `'Playfair Display', 'DM Serif Display', Georgia, serif` (used for key hero titles / pull statistics, max 1 per screen)
- **Monospace:** `'JetBrains Mono', 'Fira Code', monospace` (used for order IDs, stock codes, metric parameters)
- **Scale:**
  - Hero display: 40–56px, weight 800–900, tracking -0.02em
  - Section heading: 24–32px, weight 700, tracking -0.02em
  - Card/Component title: 16–20px, weight 600, tracking -0.01em
  - Section Tag / UI Label: 11–12px, weight 600, uppercase, tracking +0.08em (`text-stone-500`)
  - Body: 14–15px, weight 400, line-height 1.6
  - Caption / Footnote: 11–12px, weight 400, `#78716C`

## 4. Component Rules
- **Buttons:**
  - Primary button: Dark stone `#1C1917`, white text, border radius 4px (`rounded-sm`), never pill-shaped (`rounded-full`).
  - Secondary button: White/transparent with `#E7E5E4` border, stone text, 4px radius.
- **Cards & Containers:**
  - Background `#FFFFFF`, border `1px solid #E7E5E4`, border-radius 8px, soft box shadow `0 1px 3px rgba(0,0,0,0.04)`.
- **Inputs & Selectors:**
  - White background, `#E7E5E4` border, radius 4px, focus border `#93C5FD`.
- **Charts (Plotly):**
  - Transparent or `#FFFFFF` plot/paper background.
  - Palette: Neutral slate/stone `#1C1917`, `#78716C`, `#93C5FD`, `#3B82F6`, `#D97706`, `#059669`.
  - Gridlines: `#E7E5E4` at 0.5px.
  - Font: Inter.
- **Tables:**
  - Header: `#FAFAF9`, uppercase stone-500 text, 11px.
  - Rows: `#FFFFFF`, border-bottom `#F5F5F4`.

## 5. Layout & Spacing
- Max-width: 1200px centered.
- Ample negative space; breathing room around cards.
