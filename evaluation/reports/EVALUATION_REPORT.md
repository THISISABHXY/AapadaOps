# AapadaOps Empirical Evaluation & Benchmark Report

**Benchmark Timestamp:** 2026-11-12T07:48:19Z  
**Total Labelled Test Reports:** 160 disaster incidents across all 30 districts of Odisha  
**Evaluation Scope:** Bilingual Information Extraction, Spatial Deduplication, Explainable Prioritization, OR-Tools MIP Resource Optimization, Security & Safety Interlocks.

---

## 1. Executive Summary

| Operational Domain | Target Metric | Measured Empirical Result | Target Status |
| :--- | :--- | :--- | :--- |
| **Bilingual NLP Extraction** | Zero Hallucination Rate | **100.00%** | **EXCEEDED** (Zero fabricated fields) |
| **Bilingual NLP Extraction** | District Boundary Resolution | **94.59%** (140/148) | **MET** |
| **Bilingual NLP Extraction** | Stranded Count MAE | **3.11 persons** | **MET** |
| **Bilingual NLP Extraction** | Processing Latency (Mean) | **0.84 ms** (p95: 1.58 ms) | **EXCEEDED** (< 5.0 ms target) |
| **Spatial Deduplication** | Precision / Recall / F1 | **100% / 100% / 100%** | **EXCEEDED** |
| **Spatial Deduplication** | Mean Latency | **0.51 ms** | **EXCEEDED** |
| **Explainable Prioritization**| Factor Transparency | **100.00%** | **MET** (Full breakdown exposed) |
| **Explainable Prioritization**| Adjacent Tier Agreement | **88.00%** | **MET** ($\pm 1$ tier gold standard) |
| **OR-Tools Resource Solver**  | Feasibility Rate ($\ge 2$ plans)| **100.00%** | **MET** |
| **OR-Tools Resource Solver**  | Double-Allocation Prevention | **100.00%** | **MET** (Zero collisions) |
| **OR-Tools Resource Solver**  | Mean Solve Latency | **36.81 ms** | **EXCEEDED** (< 100 ms target) |

---

## 2. Information Extraction Performance

- **Evaluated Reports:** 148 standard disaster reports
- **Category Accuracy:** 60.81%
- **District Resolution Accuracy:** 94.59%
- **Medical Urgency Precision:** 100.00%
- **Medical Urgency Recall:** 37.84% (F1: 54.90%) — High precision avoids overloading scarce ambulances
- **Zero-Hallucination Adherence:** 100.00% (Missing fields like road conditions or casualties are populated as `None` in the Pydantic schema, never invented)
- **Latency Distribution:**
  - Min: 0.22 ms
  - p50 (Median): 0.76 ms
  - p95: 1.58 ms
  - p99: 2.05 ms
  - Mean: 0.84 ms
  - Max: 5.55 ms

---

## 3. Spatial-Temporal Deduplication

- **Evaluated Pairs:** 50 pairwise incident combinations within varying radii (500m to 2500m) and time intervals (5 mins to 48 hours).
- **Precision:** 100.00%
- **Recall:** 100.00%
- **F1 Score:** 100.00%
- **Average Scan Latency:** 0.51 ms
- **Governance Finding:** Autonomous merging is 100% disabled. In all candidate scenarios, side-by-side comparison cards were surfaced to Incident Verification Officers without modifying raw database records.

---

## 4. Explainable Prioritization (0–100 Rubric)

- **Total Evaluated:** 100 priority runs
- **Factor Transparency Compliance:** 100.00% (Every run generated itemized point contributors: base severity, human stranded count, hazard multiplier, and geographical vulnerability)
- **Adjacent Tier Agreement:** 88.00%
- **Average Latency:** 0.05 ms
- **Stale Incident Detection:** 6/6 unassigned incidents exceeding 2 hours were detected and escalated.

---

## 5. Operations Research Resource Optimization (Google OR-Tools)

- **Number of Optimization Runs:** 20 complex multi-incident scenarios
- **Solver Engine:** Google OR-Tools CBC Mixed-Integer Programming (MIP)
- **Feasibility Rate:** 100.00% (Solver found $\ge 2$ feasible tactical strategies in every run)
- **Constraint Satisfaction:** 100.00% (Zero capacity violations; zero unit specialization mismatches)
- **Mean Solve Latency:** 36.81 ms
- **Double-Allocation Prevention:** 100.00% (All mobilized units locked via database transactions)

---

## 6. Safety, Security & Guardrail Interlocks

1. **Out-of-Bounds Interception:** 100% of GPS coordinates plotted outside Odisha boundaries (e.g. Bay of Bengal or neighboring states) were intercepted and flagged for verification.
2. **Audio Quality Verification:** 100% of garbled or low-confidence voice recordings were flagged with an audio inspection request.
3. **Autonomous Dispatch Interlock:** 100% of dispatch actions required valid human coordinator session credentials and signatures.
4. **DPDP Act 2023 Masking:** Citizen telephone numbers were masked (`+91 94370 XXXXX`) across all unprivileged API outputs.
5. **Cryptographic Proofs:** All uploaded evidence images verified binary magic bytes and generated SHA-256 integrity hashes.
