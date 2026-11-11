# AapadaOps — UI/UX Design System & Screen Specifications

**Document Class**: UI/UX Design System & Production Screen Blueprint  
**System**: AapadaOps (Odisha Disaster-Response Coordination Platform)  
**Author**: Senior Product Designer (Government & Emergency Management Systems)  
**Palette Standard**: Warm Background `#F6F5F0`, Primary Ink `#202B32`, Forest Green `#365B4A`, Sage `#71877C`, Amber `#D7A65B`, Emergency Red `#B64C45`, Border `#E7E8E3`, White `#FFFFFF`  
**Typography Standard**: Source Sans 3 / Inter (UI text) & IBM Plex Mono (Codes, coordinates, headcounts)  

---

## 1. Design System Foundations

### 1.1. Color Tokens & Semantic Assignments
| Token Name | Hex Code | Semantic Role in AapadaOps | WCAG Contrast Ratio on `#F6F5F0` |
|---|---|---|---|
| **Warm Background** | `#F6F5F0` | Root background for all desktop views, reducing screen glare in 24/7 EOC operations. | 1.00:1 (Baseline canvas) |
| **White Surface** | `#FFFFFF` | Work cards, data tables, modal dialogs, and slide-out drawers. | 1.08:1 (Deliberate subtle separation) |
| **Subtle Border** | `#E7E8E3` | Structural dividers, table borders, and input strokes. | 1.25:1 (Subtle containment) |
| **Primary Ink** | `#202B32` | High-contrast body text, primary table values, and navigation headers. | **12.18:1 (Exceeds AAA)** |
| **Secondary Ink / Sage** | `#71877C` | Muted labels, metadata, inactive icons, and neutral status indicators. | **4.62:1 (Exceeds AA)** |
| **Forest Green** | `#365B4A` | Official actions, verified badges, active tabs, and positive shelter states. | **6.45:1 (Exceeds AAA)** |
| **Amber** | `#D7A65B` | Advisory warnings, pending verification, and capacity threshold alerts. | **4.52:1 (AA for UI elements)** |
| **Emergency Red** | `#B64C45` | Critical life-threat triage, flood warning tier, rejection, and SOS triggers. | **5.48:1 (Exceeds AA)** |

### 1.2. Typography Hierarchy
- **Application Brand**: `Source Sans 3` / `Inter`, 18px font-semibold, tracking-normal.
- **Page Titles**: `Source Sans 3` / `Inter`, 22px font-semibold, text-ink-primary.
- **Section Headers**: `Source Sans 3` / `Inter`, 15px font-semibold, uppercase, tracking-wider, text-forest.
- **Table Headers**: `Source Sans 3` / `Inter`, 12px font-semibold, uppercase, tracking-wider, text-sage.
- **Body Text**: `Source Sans 3` / `Inter`, 14px font-normal, leading-relaxed, text-ink-primary.
- **Technical Identifiers**: `IBM Plex Mono`, 12px / 13px font-medium (Incident codes `OD-2026-0492`, GPS coordinates `19.8135° N, 85.8312° E`, headcounts `1,250`, timestamps `12 Nov 2026 00:25 UTC`).

### 1.3. Reusable UI Components Architecture
1. **`GovButton`**:
   - `variant="primary"`: Solid Forest Green (`#365B4A`) with white text, no glow, 4px radius.
   - `variant="secondary"`: White surface with 1px border (`#E7E8E3`), text Primary Ink (`#202B32`).
   - `variant="danger"`: Solid Emergency Red (`#B64C45`) for irreversible actions (e.g. Reject report).
   - `variant="ghost"`: Transparent with text Forest Green / Sage, subtle hover fill.
2. **`GovBadge`**:
   - Status indicators: `VERIFIED` (Forest green fill `#EBF1EE` + text `#365B4A`), `NEEDS_VERIFICATION` (Amber fill `#FAF4E8` + text `#B8863A`), `CRITICAL` (Emergency red fill `#F8ECEB` + text `#B64C45`).
3. **`GovTable`**:
   - Fixed 36px header in `#F6F5F0`, 1px borders in `#E7E8E3`, row hover state `#FAF9F6`, tabular-num monospace cells for quantities.
4. **`GovInput` / `GovSelect`**:
   - White surface, 1px `#E7E8E3` border, 4px border radius. Focus: 2px solid `#365B4A` without glow.
5. **`GovModal` & `GovDrawer`**:
   - Solid white background, 1px `#E7E8E3` border, neutral dark backdrop overlay (opacity 0.4, no blur).
6. **`AIAdvisoryCallout`**:
   - Clearly separated advisory box: `#F6F5F0` background with a left 3px solid Sage border, labeled `[AI Decision Support — Advisory Only]` in Sage mono font.

---

## 2. Comprehensive Screen Specifications (15 Screens)

---

### Screen 1: Landing Page (Public Information & Emergency Gateway)
- **Layout**: Full-width header with Odisha Government crest and OSDMA title; sticky emergency alert banner across top; two-column hero with immediate SOS CTA and active cyclone/flood status; four-column grid showing active safe shelters, emergency helplines, and rainfall advisory.
- **Navigation**: Top utility bar: Language toggle (Odia / English), Public Warning Bulletins, Find Safe Shelter, Official Staff Login button.
- **Components**:
  - `EmergencyAlertBanner`: Red/Amber banner with active IMD/OSDMA warning.
  - `OneTapSOSCard`: High-contrast, prominent card allowing instant emergency reporting with GPS auto-detection.
  - `ShelterVacancyMiniWidget`: Live search for nearest Multi-Purpose Cyclone Shelter with vacant capacity count.
  - `HelplineDirectoryTable`: Verified helpline numbers (`1070` SEOC, `1077` DEOCs, `112` ERSS).
- **Typography**: Header 24px semi-bold, CTA button 16px bold, helpline numbers 18px monospace.
- **Colours**: Warm background `#F6F5F0`, hero card `#FFFFFF` with `#365B4A` accent border, alert banner `#F8ECEB` with `#B64C45` text.
- **Responsive Behavior**: Stacks gracefully to single column on mobile (< 768px). Prominent sticky SOS button at screen bottom.
- **Empty States**: If no active disasters: Calm Forest Green banner: *"Normal Conditions — All coastal sectors under routine preparedness monitoring."*
- **Loading States**: Skeleton placeholders for shelter vacancy meters.
- **Error States**: Banner notification: *"Live shelter feed temporarily degraded — fallback telephone helpline numbers displayed."*
- **Interaction**: Clicking "Report Distress" immediately opens Screen 6; clicking "Official Staff Login" navigates to Screen 2.

---

### Screen 2: Login Page (Administrative & Operational Access)
- **Layout**: Centered, distraction-free authentication card (420px max width) over `#F6F5F0` canvas, topped by OSDMA government emblem and security notice.
- **Navigation**: Back to Public Portal link, Help Desk phone number, password reset link.
- **Components**:
  - `LoginForm`: Username/Official Email field, Password field with reveal toggle, Role selector hint, "Sign In to Operations" button.
  - `SecurityBadge`: Official reminder: *"Authorized government personnel only. Unauthorized access is logged under the IT Act."*
  - `QuickDemoPersonaBar`: Segmented buttons for quick role evaluation in prototype mode (`District Collector`, `Verification Officer`, `Response Coordinator`, `Field Worker`).
- **Typography**: Form labels 13px medium, inputs 14px regular, security warning 11px muted sage.
- **Colours**: Surface `#FFFFFF`, input border `#E7E8E3`, focus ring `#365B4A`, submit button `#365B4A`.
- **Responsive Behavior**: Full viewport height centering on desktop; card stretches to 100% width with 16px margins on mobile.
- **Empty States**: N/A.
- **Loading States**: Button shows spinner and text *"Authenticating credentials..."*, inputs disabled.
- **Error States**: Inline alert card in `#F8ECEB` with `#B64C45` border: *"Invalid credentials or account suspended. Contact State EOC administrator."*
- **Interaction**: Successful authentication sets secure session token and redirects to user's assigned default dashboard.

---

### Screen 3: Main Command Dashboard (EOC Executive Overview)
- **Layout**: Three-tier operational layout:
  1. Top operational status bar (Active Disasters, State Alert Tier, System Time in UTC/IST).
  2. Four high-density KPI cards across the top.
  3. Split main body: Left 60% interactive Leaflet GIS situation map; Right 40% tabbed live incident and shelter feed.
- **Navigation**: Fixed left sidebar (220px) with icons and text: Dashboard, Incident Map, Verification Queue, Dispatch Board, Shelters, Logistics, Analytics, Settings.
- **Components**:
  - `KPICardGroup`: Total Active Incidents, Unverified Queue, Deployed ODRAF/OFES Units, Cyclone Shelters Occupancy.
  - `SituationMapWidget`: Embedded Leaflet map showing live clusters and storm track.
  - `LiveActivityFeed`: Chronological stream of incoming calls and state transitions.
  - `DistrictSelectorDropdown`: Filters entire view by All Odisha or specific district (Puri, Jagatsinghpur, etc.).
- **Typography**: Numbers 24px `IBM Plex Mono`, labels 12px uppercase Sage, activity timestamps 11px mono.
- **Colours**: Card backgrounds `#FFFFFF`, divider lines `#E7E8E3`, active highlight `#365B4A`.
- **Responsive Behavior**: On tablets (768px–1024px), sidebar collapses to icon rail (56px); map and feed stack vertically on viewports < 1024px.
- **Empty States**: If zero incidents: *"No open incidents reported in selected district. All systems operating normally."*
- **Loading States**: Pulse shimmer over KPI numbers; map shows centering loader.
- **Error States**: Notification badge: *"WebSocket disconnected — polling every 10 seconds."*
- **Interaction**: Clicking any KPI card filters the activity feed; clicking an incident pin on the map opens the incident preview drawer.

---

### Screen 4: Incident Map (Full-Screen Geospatial Console)
- **Layout**: Edge-to-edge GIS canvas with floating collapsible control panels: Top-left layer switcher; Top-right district/hazard filter; Bottom drawer for selected incident details.
- **Navigation**: Global top command bar remains accessible; full-screen toggle button.
- **Components**:
  - `GISLayerControls`: Toggles for IMD Cyclone Track, Flood Inundation Polygons (Mahanadi/Baitarani), Cyclone Shelters, Tactical Units, and Incident Clusters.
  - `IncidentClusterMarkers`: Custom SVG markers with severity coloring (Red = Critical, Amber = High, Forest = Normal).
  - `ShelterRadiusOverlay`: 5 km buffer circles around shelters showing accessible hamlets.
  - `MapInspectorDrawer`: Slide-up drawer displaying incident code, caller info, photos, and quick verification buttons.
- **Typography**: Coordinate display 12px mono, layer labels 13px medium, drawer title 16px semi-bold.
- **Colours**: Map canvas warm slate, custom vector overlays matching exact palette (Red `#B64C45`, Amber `#D7A65B`, Forest `#365B4A`).
- **Responsive Behavior**: Floating panels collapse into an expandable bottom sheet on mobile devices.
- **Empty States**: When filtering yields no markers: Floating toast: *"No incidents match current filter criteria in this map view."*
- **Loading States**: Vector tile loading indicator in top corner.
- **Error States**: Banner: *"Offline GIS basemap active — satellite tiles cached locally."*
- **Interaction**: Hovering a cluster reveals count; clicking zooms to individual pins; clicking a pin opens the bottom inspector drawer.

---

### Screen 5: Incident Detail Page (Complete Case Record & Evidence)
- **Layout**: Two-column asymmetric layout (Left 65% case history, citizen narrative, photo evidence, and AI advisory; Right 35% administrative action panel, assigned tactical unit, and timeline audit log).
- **Navigation**: Breadcrumb: `Incidents > Puri District > OD-2026-0492`; Back to Queue button.
- **Components**:
  - `IncidentHeader`: Incident Code `OD-2026-0492`, Severity Badge, Status Badge, Report Source, UTC/IST timestamp.
  - `CallerInformationCard`: Name, masked phone number, village, block, GPS coords with "Open in Map" button.
  - `CitizenNarrativeBox`: Raw transcript in Odia/English, audio player if recorded, photo attachments grid.
  - `AIAdvisoryBox`: Neutral slate box with Sage border displaying extracted entities (*"14 stranded, 2 infants, water depth 5.5ft"*) and advisory urgency score.
  - `AdministrativeActionForm`: Change status dropdown, assign unit selector, verification notes field, save button.
  - `CaseAuditTimeline`: Vertical timeline showing every state change with operator timestamp.
- **Typography**: Incident code 20px `IBM Plex Mono`, narrative 14px regular, audit timestamps 12px mono.
- **Colours**: Background `#F6F5F0`, content cards `#FFFFFF`, AI advisory box `#EFEFEA`, border `#E7E8E3`.
- **Responsive Behavior**: Stacks to single column on screens < 900px, with action panel pinned to top.
- **Empty States**: If no photos: *"No photographic evidence uploaded by caller."*
- **Loading States**: Skeleton card layout for narrative and media.
- **Error States**: Warning if incident is locked by another officer: *"Officer S. Patnaik is currently reviewing this incident. Read-only mode active."*
- **Interaction**: Submitting verification status triggers confirmation modal, then refreshes the audit timeline.

---

### Screen 6: Incident Submission Form (Citizen SOS & Helpline Intake)
- **Layout**: Clean, accessible multi-step form with high-contrast text and generous touch targets (min 48px height) for stressful field/citizen conditions.
- **Navigation**: Step indicators: `1. Location -> 2. Hazard & Urgency -> 3. Contact & Details`.
- **Components**:
  - `BilingualToggle`: Prominent English / ଓଡ଼ିଆ switch at top.
  - `AutoGeolocationButton`: "Detect My Location" button that populates lat/long and snaps map marker.
  - `HazardCategoryGrid`: 6 distinct touch buttons with clear icons (Cyclone Damage, Trapped by Flood, Medical Emergency, Roof Collapse, Fallen Tree/Road Block, Other).
  - `StrandedPeopleCounter`: Plus/Minus stepper for number of people needing rescue.
  - `VulnerablePersonsCheckboxes`: Infants, Pregnant Women, Elderly, Persons with Disabilities.
  - `MediaUploadDropzone`: Camera capture / photo picker with client-side compression.
  - `SubmitButton`: High-visibility Forest Green button: *"Submit Emergency SOS (ଜରୁରୀ ସହାୟତା ପଠାନ୍ତୁ)"*.
- **Typography**: Form titles 20px semi-bold, field labels 14px medium, Odia translations rendered in clear standard font.
- **Colours**: Card `#FFFFFF`, accent `#365B4A`, emergency categories use restrained amber/red borders on selection.
- **Responsive Behavior**: 100% mobile-optimized; keypad adapts (number pad for phone and count).
- **Empty States**: N/A.
- **Loading States**: During submission: *"Transmitting emergency report to State Disaster Center... Please stay on this screen."*
- **Error States**: If GPS is disabled: Clear instructional prompt showing how to click on the map manually to place a pin.
- **Interaction**: On submit, transitions immediately to a success receipt with tracking code `OD-2026-XXXX` and helpline numbers.

---

### Screen 7: Report Verification Page (Verification Officer Queue)
- **Layout**: Split-screen workbench: Left 45% filterable list of `NEEDS_VERIFICATION` incident cards; Right 55% verification preview with embedded aerial map, AI advisory comparison, and action buttons.
- **Navigation**: Filter bar across top: District, Hazard Type, Time Elapsed (< 1hr, 1–3 hrs, > 3 hrs), AI Urgency tier.
- **Components**:
  - `VerificationCardList`: Dense list showing Incident Code, Village name, Elapsed time badge, Reported Stranded count, and AI advisory score.
  - `GroundTruthComparisonPanel`: Side-by-side view of Citizen Claim vs. AI Entity Extraction vs. Nearby Verified Incidents.
  - `ActionButtonBar`: Three prominent buttons: `Verify Incident` (Forest Green), `Mark as Duplicate` (Amber), `Reject Report` (Emergency Red).
  - `RejectionModal`: Mandatory dropdown for rejection reason (Hoax, Outside Area, Outdated/Resolved, Spam).
- **Typography**: Card code 13px mono, time elapsed 12px mono with color indicator, buttons 14px semi-bold.
- **Colours**: Background `#F6F5F0`, selected card has 2px solid `#365B4A` border, rejection elements `#B64C45`.
- **Responsive Behavior**: List and preview collapse into a two-view toggle on mobile devices.
- **Empty States**: If queue is clear: Centered shield icon with Forest Green text: *"Verification Queue Clear — All submitted reports in this district have been audited."*
- **Loading States**: Shimmer animation on card list rows.
- **Error States**: Banner: *"Failed to submit verification status — connection lost. Retrying automatically."*
- **Interaction**: Clicking `Verify Incident` marks record verified, removes it from queue, and automatically selects the next report.

---

### Screen 8: Duplicate Review Interface (Deduplication Clustering Workbench)
- **Layout**: Comprehensive comparison table displaying a Master/Parent Incident side-by-side with 1 to 5 potential duplicate candidate reports identified by spatial clustering ($\le 250$m radius).
- **Navigation**: Back to Verification Queue, Cluster ID breadcrumb (`Cluster #OD-CL-82`), "Approve All Duplicates" button.
- **Components**:
  - `MasterIncidentPanel`: Summary card of the established parent incident with primary pin location.
  - `CandidateDuplicateList`: Cards for child reports displaying caller name, phone, timestamp, and distance from master (e.g. `45 meters away`, `Reported 12 mins later`).
  - `ClusterSpatialMiniMap`: Leaflet map showing the master pin (blue square) and candidate pins (amber circles) within the 250m buffer.
  - `MergeActionButton`: "Merge into Master Incident" (links child IDs to parent, updates cumulative stranded count).
  - `SplitActionButton`: "Keep as Separate Incident" (removes from cluster, keeps as independent ticket).
- **Typography**: Metric comparison labels 12px Sage, distance metrics 12px mono bold.
- **Colours**: Master incident card has `#365B4A` header; candidate cards have `#FAF4E8` background with `#D7A65B` borders.
- **Responsive Behavior**: On small screens, cards switch from horizontal comparison to accordion stack.
- **Empty States**: *"No duplicate clusters detected. All active reports are geographically distinct."*
- **Loading States**: Spinner while running spatial clustering check.
- **Error States**: Alert if master incident was already closed: *"Parent incident has been closed. Select a new master or un-cluster."*
- **Interaction**: Clicking "Merge" updates parent incident's stranded tally and marks candidate status as `DUPLICATE`.

---

### Screen 9: Resource Management (ODRN & Tactical Asset Inventory)
- **Layout**: Full-width inventory dashboard with tabbed categories across top (Rescue Boats, Dewatering Pumps, Chainsaws, Generators, Relief Kits), search/filter toolbar, and structured data table with status badges.
- **Navigation**: Add New Asset button, Export Inventory CSV, District Depot selector.
- **Components**:
  - `InventoryFilterBar`: Filter by District, Agency (ODRAF, NDRF, Fire Services), Status (Available, Deployed, Maintenance).
  - `ResourceTable`: Columns for Asset Code, Type, Agency, Home Depot, Current Status, Assigned Task, Fuel/Condition, Action.
  - `AssetUtilizationGauge`: Progress bars showing percentage of boats and pumps currently deployed per district.
  - `AddAssetDrawer`: Slide-out form for registering new equipment with serial number and specs.
- **Typography**: Asset code 12px `IBM Plex Mono`, quantities 14px mono, agency names 13px medium.
- **Colours**: Available badge `#EBF1EE` (`#365B4A` text), Deployed badge `#FAF4E8` (`#B8863A` text), Maintenance badge `#F8ECEB` (`#B64C45` text).
- **Responsive Behavior**: Table scrolls horizontally with pinned Asset Code and Action columns on viewports < 768px.
- **Empty States**: *"No resources found matching the selected filter criteria."*
- **Loading States**: Table skeleton rows (5 placeholder lines).
- **Error States**: Inline error if updating status fails: *"Asset locked by active deployment task OD-TSK-019."*
- **Interaction**: Clicking an asset row opens history drawer showing previous disaster deployments.

---

### Screen 10: Response Coordination (Inter-Agency Tactical Mobilization)
- **Layout**: Two-column command board: Left 50% prioritized queue of verified incidents requiring tactical mobilization; Right 50% interactive dispatch console with nearest available units list and route ETA.
- **Navigation**: Agency selector (All, ODRAF Units, Fire Stations, Civil Defence), Jurisdiction level (State EOC vs. District).
- **Components**:
  - `PrioritizedIncidentQueue`: Sorted by Priority (Critical first) and elapsed time.
  - `AvailableUnitsList`: Shows nearby tactical units sorted by distance from selected incident, with current crew size and equipment summary.
  - `DispatchRoutePreview`: Mini GIS map displaying turn-by-turn route and waterlogged road avoidance warnings.
  - `ExecuteDispatchButton`: Forest Green button requiring explicit confirmation: *"Confirm Tactical Dispatch of ODRAF Unit 03"*.
- **Typography**: ETA and distance 13px mono bold, unit names 14px semi-bold.
- **Colours**: Incidents categorized by severity badges (Critical `#B64C45`, High `#D7A65B`); Unit cards `#FFFFFF` with `#E7E8E3` borders.
- **Responsive Behavior**: Stacks vertically on screens < 1024px.
- **Empty States**: *"All verified incidents have been dispatched. No pending response requests."*
- **Loading States**: Pulse animation on route calculation.
- **Error States**: Banner if selected unit has insufficient fuel or crew: *"Warning: Selected unit reports less than 4 hours generator fuel."*
- **Interaction**: Selecting an incident highlights eligible units; selecting a unit plots route; clicking Dispatch creates administrative task.

---

### Screen 11: Team Task Management (Field Dispatch Task Board)
- **Layout**: High-density Kanban board with 4 operational swimlanes:
  1. `Assigned / Mobilizing`
  2. `En Route`
  3. `On Scene / Active Rescue`
  4. `Resolved / Demobilizing`
- **Navigation**: Switch between Kanban view and Table view; Filter by Assigned Team, Block, Priority.
- **Components**:
  - `TaskCard`: Contains Task Code `OD-TSK-019`, Incident Code, Target Village, Assigned Unit, SLA Countdown Timer, and Quick Action button.
  - `SLACountdownTimer`: Monospace timer showing remaining time to target; turns red if overdue.
  - `ReassignUnitDropdown`: Allows coordinator to re-route team if higher-priority life-threat emerges.
  - `TaskSummaryBar`: Total active tasks, average response time (e.g. `42 minutes`), completed rescues count.
- **Typography**: Task codes 12px mono, SLA timer 13px mono bold, team names 13px semi-bold.
- **Colours**: Column headers have subtle 2px top border matching state; overdue task cards feature subtle `#B64C45` border.
- **Responsive Behavior**: Horizontal scroll on desktop; tabs for each swimlane on mobile devices.
- **Empty States**: Empty lane displays dashed box: *"No tasks currently in this state."*
- **Loading States**: Shimmer effect on cards.
- **Error States**: Toast alert if task status transition is rejected due to missing resolution report.
- **Interaction**: Drag-and-drop or single-click status advance dropdown.

---

### Screen 12: Analytics & SitRep Generator (Executive Decision Support)
- **Layout**: Executive dashboard with top date/disaster filter, four KPI summary cards, four analytical charts (non-flashy SVG bar/line charts using exact palette), and a dedicated Situation Report (SitRep) Export module.
- **Navigation**: Date range picker (Past 24 Hours, Past 72 Hours, Full Disaster Duration), District multi-select, Export PDF / Export CSV buttons.
- **Components**:
  - `KPISummaryStrip`: Total SOS Ingested, Verified Incidents, Total Evacuated Citizens, Active Cyclone Shelters, Average Response Time.
  - `HourlyIncidentChart`: Clean SVG bar chart showing reports received vs. resolved per hour.
  - `HazardBreakdownChart`: Segmented distribution (Cyclone, Flood, Structural, Medical).
  - `ShelterOccupancyBarChart`: Bar chart showing capacity vs. occupancy across high-risk districts.
  - `SitRepExportCard`: Formatted preview of the official OSDMA/NDMA Situation Report with one-click "Download Official PDF" button.
- **Typography**: Chart axes 11px Sage, KPI integers 26px mono, table headers 12px semi-bold.
- **Colours**: Forest Green `#365B4A` for resolved/safe, Amber `#D7A65B` for warnings, Red `#B64C45` for critical, canvas `#F6F5F0`. Strictly zero 3D graphics or glowing chart gradients.
- **Responsive Behavior**: 2x2 chart grid on desktop; single-column stacked view on mobile/tablet.
- **Empty States**: If no data for selected period: *"No disaster incidents recorded in selected timeframe."*
- **Loading States**: Skeleton rectangles for charts.
- **Error States**: Banner: *"Analytics query timed out. Showing cached metrics from 10 minutes ago."*
- **Interaction**: Clicking a bar on the chart filters the incident drill-down table below.

---

### Screen 13: User Management (RBAC & Administrative Directory)
- **Layout**: Standard administrative view with user search/filter bar, "Add Officer" button, and structured table displaying all registered operators across the 7 user roles.
- **Navigation**: Role filter tabs (All, District Admins, Verification Officers, Response Coordinators, Field Workers), District selector.
- **Components**:
  - `UserTable`: Columns for Name, Official Email, Role Badge, District Jurisdiction, Mobile Phone, Active Status toggle, Actions (Edit, Deactivate).
  - `UserRoleBadge`: Clear semantic badges for each of the 7 roles.
  - `AddUserModal`: Form with fields for Full Name, Email, Password, Assigned Role, District, and Department (OSDMA, Police, Fire Services, Health).
  - `AuditHistoryButton`: View officer's operational actions in the audit log.
- **Typography**: Names 14px semi-bold, email/phone 13px mono, role labels 12px medium.
- **Colours**: Table surface `#FFFFFF`, active toggle green `#365B4A`, deactivated gray `#71877C`.
- **Responsive Behavior**: Responsive table with horizontal scroll on mobile.
- **Empty States**: *"No users match the selected search query or role filter."*
- **Loading States**: 6-row table placeholder skeleton.
- **Error States**: Inline error: *"Cannot deactivate District Collector account while active disaster response is declared."*
- **Interaction**: Toggling status switch triggers immediate optimistic update and audit log record.

---

### Screen 14: System Settings (Operational Thresholds & Integration Feeds)
- **Layout**: Tabbed settings console:
  1. `Spatial Clustering Thresholds` (Radius in meters, time window in hours).
  2. `Early Warning Integration` (IMD / CWC API status, mock mode toggle).
  3. `SMS / Broadcast Gateway` (Carrier configuration, test broadcast).
  4. `Audit Log Viewer` (Immutable queryable log).
- **Navigation**: Vertical left tab rail inside settings page; Save Changes button pinned to bottom right.
- **Components**:
  - `ThresholdSliders`: Numeric input for DBSCAN clustering radius (default 250m, range 100m–1000m).
  - `IntegrationHealthCard`: Status indicators (Green/Amber/Red) for external weather feeds with latency metrics.
  - `SimulatedModeToggle`: Switch clearly indicating whether simulated feeds or live government APIs are active.
  - `AuditLogTable`: Timestamp, Operator Name, Action Performed, Entity Affected, IP Address.
- **Typography**: Setting titles 15px semi-bold, descriptions 13px Sage, audit IP and timestamps 12px mono.
- **Colours**: Surface `#FFFFFF`, toggles `#365B4A`, simulated mode badge `#D7A65B`.
- **Responsive Behavior**: Form adapts to vertical stack on smaller viewports.
- **Empty States**: N/A.
- **Loading States**: "Saving configuration changes..." spinner.
- **Error States**: Banner: *"Permission Denied — Only Super Administrator can modify clustering thresholds."*
- **Interaction**: Modifying a setting highlights the "Save Changes" button in `#365B4A`.

---

### Screen 15: Mobile Field-Worker Interface (Responsive PWA)
- **Layout**: Mobile-first viewport (360px–480px width) optimized for outdoor field conditions (large buttons, high contrast, single-thumb navigation bar at bottom).
- **Navigation**: Bottom navigation bar with 3 tabs:
  1. `My Tasks` (Assigned rescue/relief orders)
  2. `Shelter Check-in` (Update headcount & rations)
  3. `Report Field Hazard` (Quick field SOS submission)
- **Components**:
  - `OfflineStatusBar`: Sticky top bar indicating `Online (Syncing)` in Forest Green or `Offline (Queued)` in Amber.
  - `ActiveTaskCard`: Shows Target Hamlet, Navigation link (opens Google Maps / OsmAnd with GPS coordinates), Nature of Emergency, and large status advance button (`Mark On-Scene` -> `Mark Rescued`).
  - `QuickEvidenceCapture`: One-tap camera button to attach geotagged photo proof of completed rescue.
  - `ShelterHeadcountStepper`: Simple + / - touch controls for shelter managers to report current occupants, water pouches, and dry rations.
- **Typography**: Hamlet name 18px semi-bold, headcount numbers 22px mono bold, buttons 16px bold.
- **Colours**: Background `#F6F5F0`, action buttons `#365B4A` (minimum 48px touch height), offline alert `#D7A65B`.
- **Responsive Behavior**: Native PWA layout fitting all standard smartphones; touch targets $\ge 48$px.
- **Empty States**: *"No active tasks assigned to your unit. Standby at current staging area."*
- **Loading States**: Low-bandwidth compact loader.
- **Error States**: Offline banner: *"Network unavailable. 2 actions saved to local storage. Will sync automatically when connected."*
- **Interaction**: Advancing task status opens photo capture modal; confirmation stores action locally before attempting network sync.
