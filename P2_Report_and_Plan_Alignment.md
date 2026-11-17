# P2 report: what P2 added, and how it aligns with the Action Plan

Project: Explainable credit-risk prediction, quantitative evaluation of SHAP explanation reliability.
Role reviewed: P2 (SHAP/analysis). Review date: 17 November 2026.

## 1. Verdict
**P2 is correctly aligned with the plan and numerically sound. Estimated plan coverage for P2: about 90%.**
All four things Section 3 of the plan asks of P2 exist, and every number I could re-derive from the saved SHAP arrays matched the handover exactly. What is missing is polish and one design-strength item, not core work. Nothing found invalidates a result.

| Severity | Count | Meaning |
| --- | --- | --- |
| Critical (breaks a result or a plan item) | 0 | |
| Moderate (weakens a claim P3 will want to make) | 2 | fidelity has no random-feature baseline; H1 wording |
| Minor (presentation / paper-readiness) | 5 | see section 4 |

## 2. What P2 added (inventory)
**Explanations.** TreeSHAP (shap 0.54.1, interventional, raw log-odds, 100-row training background) for all 10 P1 XGBoost models on all 30,013 held-out borrowers; one `.npz` per model (SHAP, base value, margin, probability, borrower IDs, plus path-dependent SHAP for a sensitivity check). Additivity error at most 7.4e-6.

**Plan Section 3 items**
| Plan item | P2 deliverable | Status |
| --- | --- | --- |
| TreeSHAP for same test borrowers, every P1 run | `explanations/*.npz`, `cohort_ids.csv`, `background_ids.csv` | Done |
| Rank stability (Spearman, top-k) | `rank_stability.csv.gz`, `rank_stability_summary.csv`, fig1 | Done |
| Attribution stability (signed SHAP, variability/CV, near-zero care) | `attribution_stability.csv.gz`, `*_summary.csv`, `weighting_change*`, fig2 | Done (no dedicated figure) |
| Fidelity (perturb top vs low-ranked features) | `fidelity.csv.gz`, `fidelity_summary.csv`, fig3 | Done (see gap 1) |
| Final tables, plots, borrower examples | CSV summaries, fig1-fig4, `examples.md/csv` | Done, not paper-ready |

**Extras beyond the plan.** Frozen analysis protocol written before the full run; performance-vs-reliability table over 25 model pairs; overlap-excluded sensitivity (99 test rows also in training); path-dependent SHAP sensitivity; bootstrap CIs; rule-based borrower selection; `verify_p2.py` (independent re-computation) and a hash manifest; written P1-vs-P2 environment differences.

**Added during hand-over review:** `README_START_HERE.md`, `AUDIT_P3.md`, `outputs/p2/p3_extras/` (key results table, per-feature global importance table).

## 3. Verification performed
Independently recomputed from the saved SHAP arrays (matches handover to 13 decimals unless noted):
- Spearman, top-3, top-5 for all three families (within-unweighted 0.9594/0.9504/0.9474; within-weighted 0.9490/0.9315/0.9414; between 0.9245/0.8984/0.9148).
- Per-feature median signed SD, median magnitude CV, masked-CV count (1 of 600,260), mean |SHAP| per feature, same-seed weighting differences.
- From the summary files: sign consistency 0.94 to 1.00; all 20 per-run fidelity intervals above 0; positive/negative shares and no-op rates as quoted; performance-vs-reliability correlations (-0.75 all pairs, -0.32 within-condition ROC-AUC) and between-condition gaps (ROC-AUC at most 0.0006, log loss about 0.256).
- Existing `verification_p2.txt`: all checks pass.

Not re-runnable here (needs P1 folder, which was not supplied): fidelity recomputation, `verify_p2.py`, P1 hash checks.

## 4. Missing or weak points against the plan
**Moderate**
1. **Fidelity lacks a random-feature baseline.** The plan compares top-ranked vs low-ranked removal. P2 does that, but the high arm changes more features than the low arm (2.07 vs 1.37 at k=3 unweighted), because median replacement is a no-op when a value already equals the median. P2 admits "part of the gap is mechanical". A reviewer will ask: is a SHAP-ranked set better than a random set of k features, and does the gap survive when both arms change the same number of features? The H3 claim ("supported") is safe on direction but its size is not yet defensible.
2. **H1 wording.** The plan says "similar predictive performance". Between-condition ROC-AUC is nearly identical (at most 0.0006) but log loss differs by 0.256 and Brier by 0.088, so the two conditions are not equivalent models. P2 states this, but P3 must not write "equally accurate models give different explanations". Safe wording: "models with near-identical ranking ability (ROC-AUC) differ in explanation agreement".

**Minor**
3. **H2 text slightly overstates the reference-mode dependence.** Under path-dependent SHAP the within-condition Spearman gap disappears (0.9636 vs 0.9629) and top-5 reverses, but the top-3 gap remains (0.959 vs 0.943). Handover should say the gap shrinks or disappears for Spearman/top-5 and persists for top-3.
4. **No figure for attribution stability.** The plan lists it as one of three core measures; only a table exists (fig2 is global importance). Needed: sign consistency and magnitude CV per feature, by condition.
5. **No paper-ready core evaluation table.** The plan's Section 5 table (3 rows: dimension, question, output) has no filled-in results version.
6. **Figure quality.** fig3 has overlapping x labels, a legend over the bars, no confidence intervals, and a technical title. fig1 boxplots lack plain-language axis labels.
7. **Borrower examples are tables only.** No plot showing one borrower's SHAP across the 10 runs; viva-friendly visual is missing.

**Scope notes (not errors; P3 should word carefully)**
- P1 used loss weighting, not SMOTE. The plan says "one class-balancing method such as SMOTE", so this satisfies it, but the paper must say "class weighting".
- Five seeds on one fixed split: no resampling. CIs cover borrower sampling only.
- The plan forbids claiming novelty for SHAP stability; the handover language already respects this.

## 5. Plan Section 7 and 8 checks
- "What we are NOT doing": P2 added no second dataset, deep model, counterfactuals or fairness analysis. Compliant. The path-dependent and overlap analyses are labelled secondary.
- Definition of done (one reproducible model, same borrowers, three measures, performance comparison, concise figures/tables): met, except "concise figures/tables" needs items 4 to 6 above.

## 6. Recommended fixes (priority order)
1. Add random-k baseline and matched-changed-count fidelity analysis (needs P1 models).
2. Correct the H1 and H2 wording in `handover.md`.
3. Add attribution-stability figure and a paper-ready core results table.
4. Redraw fig3 (CIs, readable labels); add one borrower-example figure.
5. Re-run `verify_p2.py` after changes and refresh the manifest.
