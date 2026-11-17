# P1 review and handover status

Review date: 11 November 2026 (Asia/Calcutta).

**P1 is ready for handover. No blocking implementation defect was found in the reviewed scope. P2 explanation analysis and P3 research integration remain open.**

Read [handover_p2.md](handover_p2.md) for the analysis task and [handover_p3.md](handover_p3.md) for research/writing. The original generated `outputs/p1/handover.md` and frozen experiment artifacts are preserved.

## What was checked

| Check | Result and evidence |
| --- | --- |
| Instructions and plan | Reviewed scripts, configuration, dataset audit, report text, and expected deliverables against `instructions.md`, `plan.md`, and the source JPEG inspected during implementation |
| Source/artifact integrity | All source and recorded artifact hashes passed |
| Split reproduction | Recreated the same 119,987 training and 30,013 held-out rows |
| Leakage controls | Disjoint row IDs and cleaned-profile groups; IDs/labels excluded from ten predictors; imputer statistics equal training-only medians |
| Saved preprocessing | Reconstructed both exported feature matrices and labels from the raw labelled data and saved imputer |
| Ten runs | Correct seed/condition combinations, feature ordering, finite bounded probabilities, 300 boosting rounds each |
| Saved model predictions | Reloaded every model; probabilities match the saved files within absolute tolerance 1e-7 |
| Metrics and summaries | Recomputed every model's metrics and condition means/sample SDs from disk |
| Effective settings | Checked ten actual booster configuration snapshots against the declared settings, including seed and positive loss weight |
| Fresh fitting | Refit seed 11 in each condition from saved processed training data; both reproduced saved probabilities exactly (maximum difference 0) |
| Native TreeSHAP compatibility | First eight held-out rows of every model produced 10 features plus bias; raw-margin additivity passed at absolute tolerance 1e-5, maximum observed error approximately 5.96e-6 |
| Dependencies | `pip check` reported no broken requirements in the pinned environment |

Primary verification evidence: [outputs/p1_review_verification.txt](outputs/p1_review_verification.txt). Supplementary counts, configuration checks, fresh-fit comparisons, and additivity residuals: [outputs/p1_review_checks.json](outputs/p1_review_checks.json).

The standard verifier was rerun in this review and does not fit models. Fresh-fit review checks cover one representative seed per condition, not all ten fresh fits. Native TreeSHAP checks are a compatibility smoke test, not a completed explanation-reliability study or verification of an external `shap` package installation.

Recheck P1 from the project root:

```powershell
.\.venv\Scripts\python.exe verify_p1.py
.\.venv\Scripts\python.exe -m pip check
```

## Findings that affect interpretation

1. **Performance similarity depends on the metric.** Mean ROC-AUC is 0.86504 unweighted and 0.86529 weighted, but mean log loss is 0.17658 versus 0.43289 and Brier score is 0.04864 versus 0.13681. The conditions cannot be described as equivalent in all predictive respects. Higher recall at threshold 0.5 comes with lower precision.
2. **Cleaned profiles are separated; some processed profiles overlap.** Median imputation produces 55 profiles shared across train/test, involving 96 training and 99 held-out rows. This does not demonstrate label leakage, but restricts claims about entirely unseen model-input profiles. [Affected test IDs](outputs/p1_review_overlap_test_ids.csv) are provided for a prespecified, separate sensitivity analysis if needed. Original split and primary cohort remain unchanged.
3. **Scope must remain accurate.** There is one held-out split, not five-fold model evaluation. The intervention is loss weighting, not SMOTE/bootstrap/resampling. The row IDs do not prove distinct real-person identities.
4. **The core research conclusion remains open.** P1 has predictive results. Rank stability, attribution stability, perturbation fidelity, verified literature novelty, and the final paper require P2/P3 work.

The simple code structure and existing experiment are sufficient for P2 to proceed. No model settings, split, preprocessing, raw inputs, scripts, or frozen P1 artifact contents were changed during this review. New review evidence and role-specific handover documents sit outside `outputs/p1/` so its integrity checks continue to work.
