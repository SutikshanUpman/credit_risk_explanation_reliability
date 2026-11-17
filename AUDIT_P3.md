# Audit of P2 results (done at hand-over)

> Historical audit of the supplied P2 package. P1 is now present alongside P2; the old missing-file statements below describe the original package. See `SURFACE_REVIEW.md` for the current inspection scope and remaining gaps.

## Independently recomputed from the saved SHAP arrays (all matched `handover.md` and the summary CSVs)
- Rank stability: Spearman, top-3 and top-5 for all three comparison families (within-unweighted 0.9594 / 0.9504 / 0.9474; within-weighted 0.9490 / 0.9315 / 0.9414; between 0.9245 / 0.8984 / 0.9148). Exact to 13 decimals.
- Attribution stability: per-feature median signed SD across seeds, median magnitude CV and the number of masked CV values (1 unweighted, 0 weighted = 1 of 600,260 as stated).
- Weighting change: mean absolute same-seed difference per feature (0.006 to 0.058, largest DebtRatio, RevolvingUtilization).
- Global importance: mean |SHAP| per feature equals `attribution_stability_summary.csv` and `weighting_change_summary.csv`.
- Condition-level fidelity values in `fidelity_summary.csv` agree with the numbers quoted in `handover.md`.

## Existing checks reviewed
`verification_p2.txt`: all checks PASS (additivity max error 7.4e-6, SHAP re-computation, 3,000 rank rows and 1,500 attribution rows re-computed, fidelity re-computed one borrower at a time).

## Could NOT be re-run here
- Fidelity values (need the P1 XGBoost models, not in the zip), `verify_p2.py`, and P1 hash checks.
- Whether P2 covers every item of the original brief (`handover_p2.md`, `plan.md`): those files were not supplied. Against the frozen `analysis_protocol.md`, every promised output exists (rank, attribution, weighting, fidelity, performance vs reliability, examples, two sensitivities, figures).

## Gaps found and filled
No missing P2 result relative to the protocol. Two convenience tables were added for P3 (`p3_extras/`), both derived only from existing arrays.

## Things P3 should know
- Per-model predictive metrics (ROC-AUC, log loss, Brier) live in P1; here only pairwise gaps are stored (`performance_vs_reliability.csv`).
- The H2 within-condition result flips under path-dependent SHAP; quote it with that caveat.
- Environment differs from P1 (Linux/Py3.12 vs Windows/Py3.13), see handover.md section 9.
