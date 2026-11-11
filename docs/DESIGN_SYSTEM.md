# AapadaOps — Government Operations Design System

## 1. Design Philosophy
AapadaOps is designed for high-stress, mission-critical government operations under extreme conditions (low bandwidth, outdoor sunlight, high-fatigue shifts, multi-agency coordination).

The interface prioritizes:
- **Maximum Data Density & Clarity**: Operations personnel must grasp critical indicators at a single glance without unnecessary animation or decoration.
- **Sober, Professional Government Aesthetic**: Warm neutral backgrounds, clean slate surfaces, crisp typography, practical structured data tables.
- **Zero Gimmicks**: Strictly NO purple gradients, NO neon effects, NO glowing borders, NO glassmorphism or translucent backdrop blurs, NO generic AI sparkle illustrations.
- **Accessibility & Contrast**: Built to meet or exceed WCAG 2.1 Level AA standards, ensuring legibility on varied display hardware from rugged field tablets to high-resolution EOC video walls.

---

## 2. Color Specification

### Canvas & Neutral Hierarchy
| Token | Hex | Role |
|-------|-----|------|
| `bg-gov-surface` | `#F8FAFC` | Main application background (Warm Slate 50) |
| `bg-gov-panel` | `#FFFFFF` | Cards, operational tables, modal dialogs |
| `border-gov-border` | `#E2E8F0` | Default structural divider lines (Slate 200) |
| `border-gov-border-strong` | `#CBD5E1` | Interactive elements, active card outlines (Slate 300) |
| `text-gov-text` | `#0F172A` | Primary typography (Slate 900) — High contrast |
| `text-gov-muted` | `#475569` | Secondary metadata, labels, timestamps (Slate 600) |
| `bg-gov-header` | `#0F172A` | Top operational command bar |

### Government Olive & Forest Green Accents
Used for system confirmation, official brand marks, safe indicators, and affirmative actions.
| Token | Hex | Usage |
|-------|-----|-------|
| `emeraldgov-50` | `#F0FDF4` | Table highlight rows, success badges |
| `emeraldgov-100` | `#DCFCE7` | Mild notification background |
| `emeraldgov-700` | `#15803D` | Primary action buttons, verified badge |
| `emeraldgov-800` | `#166534` | Primary active navigation, header elements |
| `emeraldgov-950` | `#052E16` | Deep accent accents |

### Official Disaster Alert Status Tiers
Conforms precisely to standard IMD / NDMA / OSDMA four-stage early warning system:
| Alert Tier | Background | Border | Text | Operational Definition |
|------------|------------|--------|------|------------------------|
| **Green (All Clear / Normal)** | `#F0FDF4` | `#BBF7D0` | `#166534` | Normal situation, routine monitoring |
| **Yellow (Watch / Advisory)** | `#FEFCE8` | `#FEF08A` | `#854D0E` | Be updated, standby mode, monitor forecast |
| **Orange (Warning / Alert)** | `#FFF7ED` | `#FED7AA` | `#9A3412` | Be prepared, pre-position teams, initiate evacuation |
| **Red (Severe / Action)** | `#FEF2F2` | `#FECACA` | `#991B1B` | Take action, full evacuation, round-the-clock control |

---

## 3. Typography & Hierarchy

- **Primary Typeface**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, sans-serif.
- **Monospace Typeface**: `JetBrains Mono`, `Consolas`, monospace (used for GPS coordinates, timestamps, unit serials, phone numbers).
- **Type Scale**:
  - `Display / KPI`: 28px - 32px / font-semibold / tracking-tight
  - `Section Header`: 18px - 20px / font-semibold / tracking-tight
  - `Card Header / Table Header`: 13px - 14px / font-medium / uppercase / tracking-wider
  - `Body / Cell Text`: 14px / font-normal / leading-relaxed
  - `Metadata / Captions`: 12px / font-medium

---

## 4. Operational Components Specification

### 4.1. Practical Data Tables
- Strict border containment (`border border-gov-border`).
- Fixed header rows with subtle contrasting slate fill (`bg-slate-50`).
- Row zebra striping or explicit hover state (`hover:bg-slate-50/75`).
- Pinned action columns for immediate dispatch / edit actions.
- Tabular figures (`font-mono text-xs`) for quantities, capacities, and phone numbers.

### 4.2. Metric & Status Cards
- Solid white surface, 1px slate-200 border, rounded 6px or 8px corners (no exaggerated rounded-2xl or pill designs).
- Clean label at top with muted color, large crisp integer, trend/delta badge, and baseline comparison.

### 4.3. Interactive GIS Map
- Dedicated dark or clean satellite/street tile set with muted boundaries.
- High-visibility vector markers with distinct shapes:
  - Shelter: Square with bed icon
  - Incident/SOS: Circle with warning symbol
  - Field Team: Diamond with shield icon
- Standard Leaflet popups with structured key-value tables rather than bloated modal wrappers.

### 4.4. Form Elements & Inputs
- Standard rectangular fields with 1px border (`border-slate-300`).
- Focus state: Clear 2px outline in deep green/slate (`focus:ring-2 focus:ring-emeraldgov-700/20 focus:border-emeraldgov-700`).
- Prominent required indicator and clear helper text.

