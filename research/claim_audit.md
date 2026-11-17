# P3 claim audit and evidence map

| Claim | Evidence | Safe wording | Avoid |
|---|---|---|---|
| Dataset scope | Give Me Some Credit labelled file; `outputs/p1/dataset_card.md` | 150,000 labelled records; 10 predictors; 10,026 positives (6.684%); 90-day delinquency or worse within two years | Calling this universal default or using the unlabelled competition test set for evaluation |
| Split | `outputs/p1/experiment_protocol.md`, P1 handover | One fixed first-fold group-aware split: 119,987 train / 30,013 held out | Calling this five-fold CV performance |
| Model conditions | P1 protocol and saved configs | Five seeds in unweighted and positive-class-weighted XGBoost; weighting changes loss, not samples | Claiming SMOTE, bootstrap resampling, or instance-dependent cost sensitivity |
| Predictive performance | `outputs/p1/metrics_summary.csv` | ROC-AUC is close; log loss and Brier score differ substantially | Calling conditions equivalent overall or claiming a significant performance difference |
| Rank stability | `outputs/p2/rank_stability_summary.csv` | Within-condition agreement is high; matched-seed between-condition agreement is lower | Saying the explanations are identical or uniformly reliable |
| Attribution stability | `outputs/p2/attribution_stability_summary.csv` | Sign consistency high among non-near-zero attributions; magnitude CV is feature-dependent | Treating sign consistency as magnitude stability |
| Perturbation result | `outputs/p2/fidelity_summary.csv` | High-ranked replacement has larger absolute raw-margin effect on average under this replacement rule | Causal effects, validated faithfulness, or equal-change-count evidence |
| CIs | P2 protocol/handover | Percentile bootstrap over borrowers conditional on ten fixed models | Population, split, seed, or dataset uncertainty |
| Literature positioning | References [8]-[9] | Complementary local, multi-dimension case study | First-ever SHAP stability study in credit scoring |
| Novelty | Existing methods and close 2025 papers | Empirical integration of local rank, signed attribution, and model-sensitivity checks in this particular controlled design | New algorithm, new SHAP metric, or a proven general theory |

## Material limitations to state

- One historical dataset; one fixed group-aware split; five seeds per condition; XGBoost only.
- Post-imputation profile overlap: 55 profiles, 96 train rows and 99 held-out rows.
- No explicit timestamps or temporal validation; unusual ratios/delinquency values retained.
- P2's percentile CIs sample borrowers while conditioning on the ten fitted models.
- Perturbation high/low arms differ in realised number of changed features; low arm has no-op cases; no random-k or matched-count control.
- Path-dependent sensitivity changes some within-condition stability comparisons.
- P1 and P2 environments differ (Windows/Python 3.13 and Linux/Python 3.12.3).
- P2 protocol precedes full-cohort explanation computation, but P1 predictive results already existed; not a whole-study preregistration.
