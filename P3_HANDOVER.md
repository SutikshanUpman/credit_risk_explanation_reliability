# P3 research integration handover

Date: 17 November 2026

## Deliverables
- The full research paper is supplied as an editable DOCX and PDF companion.
- `research/literature_matrix.md` — selected literature verification matrix and positioning.
- `research/claim_audit.md` — claim-to-evidence map and wording boundaries.
- `presentations/slide_content.md` — content and order for the 20-slide presentation.
- `presentations/speaker_notes.md` — suggested 12–15 minute delivery notes.
- The editable PowerPoint and PDF companion are supplied with the P3 handover.

The branch tracks the research-supporting text sources for review and version control. The polished office-format deliverables are provided separately.

## Scope and findings
P1's ten XGBoost models and P2's saved TreeSHAP results were integrated without refitting models or recomputing explanations. The study uses the Give Me Some Credit labelled set (150,000 rows), one fixed group-aware split (119,987 train / 30,013 held out), five seeds in each of two conditions, and one fixed interventional 100-row training background. The positive-class weighted condition uses `scale_pos_weight=13.933042937149969`; it changes the loss, not the training sample.

- Mean borrower-level rank Spearman: 0.959 within unweighted, 0.949 within weighted, 0.924 between matched weighting conditions.
- Mean top-3 agreement: 0.950, 0.931, and 0.898 in the same order.
- Sign consistency is high among non-near-zero attributions, while magnitude CV is higher for DebtRatio and MonthlyIncome than for delinquency-count features.
- High-ranked median substitution has a larger mean raw-margin effect than low-ranked substitution, but the test has no random-k or matched-changed-count baseline; low-ranked arms also include no-op cases. H3 is an average directional sensitivity result, not causal or definitive fidelity evidence.
- ROC-AUC is close across conditions (0.86504 vs 0.86529), but log loss (0.17658 vs 0.43289) and Brier score (0.04864 vs 0.13681) differ materially. H1 is qualified to ranking discrimination only.

## Required interpretation qualifications
1. One historical dataset and one fixed held-out split; no temporal, external, or population generalisation.
2. Five seeds describe limited run-to-run variation. Borrower-bootstrap intervals condition on the ten fitted models and do not quantify seed, split, dataset, or population uncertainty.
3. Post-imputation representations include 55 profiles shared across train/test (96 training and 99 held-out records); this does not establish label leakage but restricts claims of entirely unseen processed profiles.
4. The within-condition H2 difference is reference-mode/metric sensitive under path-dependent SHAP. The between-condition Spearman gap persists.
5. Median-replacement perturbation measures model sensitivity, not causality, feasible applicant action, or the formal infidelity metric in Yeh et al. High/low arms can change unequal feature counts.
6. P1/P2 execution environments differ (Windows/Python 3.13 and Linux/Python 3.12.3). P2's saved verification passed; this integration did not rerun model training or full SHAP computation.
7. P2's analysis protocol preceded full-cohort explanation computation, but P1 predictive results already existed. Do not claim whole-study preregistration.
8. The final author list, affiliations, and contribution statement must be confirmed by the project team before external submission.

## Reproducibility
Use the original repository's `README.md`, `outputs/p1/experiment_protocol.md`, `outputs/p1/metrics_summary.csv`, `outputs/p2/analysis_protocol.md`, `outputs/p2/verification_p2.txt`, and `outputs/p2/handover.md`. Preserve all original P1/P2 model and result artifacts. P2's verifier reports passing checks for artifact hashes, SHAP additivity, selected independent recomputations, and output completeness.

## Next research steps
Prioritise a random-k baseline and a matched-changed-count perturbation analysis; repeat the protocol over multiple group-aware splits, more seeds, and external/temporal datasets; then separately assess calibration, fairness, and recourse under appropriate data and governance controls.


## Revised IEEE companion deliverables (17 November 2026)
The initial document and deck were replaced by a five-page IEEEtran conference-style two-column manuscript and a 19-slide 16:9 presentation. The manuscript source is LaTeX using IEEEtran; the deck has an editable PPTX and PDF companion. Numerical claims were rechecked against P1 `metrics_summary.csv`, P2 `rank_stability_summary.csv`, `attribution_stability_summary.csv`, `fidelity_summary.csv`, and `outputs/p2/handover.md`. The revised presentation uses larger data visualisations and the three pre-specified borrower examples. The perturbation result is explicitly qualified because high/low arms change unequal feature counts and have low-arm no-op cases. Author names/affiliations remain pending project-team confirmation.
