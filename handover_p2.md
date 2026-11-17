# Handover to P2: SHAP reliability analysis

> Historical P1-to-P2 brief. P2 results have since been imported into `outputs/p2/`. See `README.md` and `SURFACE_REVIEW.md` for the current layout and outstanding gaps.

Reviewed on 11 November 2026. Read `instructions.md`, `plan.md`, and [review.md](review.md) first.

**P1 is complete and checked. Your task is to explain all ten saved models for the same held-out borrowers, then measure rank stability, attribution stability, and perturbation fidelity.** Full P2 analysis has not been performed.

## 1. What you receive

All paths below are relative to the project root. Keep `outputs/p1/` unchanged and save your work under `outputs/p2/`.

| Input | Purpose |
| --- | --- |
| `outputs/p1/feature_schema.json` | Ordered ten predictors, dictionary meanings, and training medians |
| `outputs/p1/processed/X_test.csv` | 30,013 fixed, processed held-out borrower rows |
| `outputs/p1/processed/y_test.csv` | Labels: 1,991 positives and 28,022 negatives |
| `outputs/p1/processed/X_train.csv` | 119,987 processed training rows; use for any background/replacement statistics |
| `outputs/p1/processed/y_train.csv` | Training labels: 8,035 positives and 111,952 negatives |
| `outputs/p1/processed/preprocessor.joblib` | Training-fitted median imputer; exported matrices are already imputed |
| `outputs/p1/splits/` | Original split IDs and cleaned-profile group IDs |
| `outputs/p1/runs/<run_id>/model.ubj` | Native XGBoost model |
| Each run's `config.json`, `effective_config.json` | Requested settings and actual training configuration |
| Each run's `predictions.csv`, `metrics.json` | Frozen probabilities, labels, predicted classes, and predictive metrics |
| `outputs/p1/metrics_all_runs.csv`, `metrics_summary.csv` | Model-level performance for comparison with explanation stability |
| `outputs/p1/manifest.json` | Source/artifact hashes, seeds, versions, and completion metadata |
| `outputs/p1_review_verification.txt`, `p1_review_checks.json` | Review verification evidence |
| `outputs/p1_review_overlap_test_ids.csv` | 99 test rows whose processed profiles also occur in training |

Run IDs are `unweighted_seed11`, `unweighted_seed22`, `unweighted_seed33`, `unweighted_seed44`, `unweighted_seed55`, and the corresponding five `weighted_seed...` runs. Never select only the best predictive model.

The same training rows, imputer, feature order, and held-out rows are used throughout. The weighted models use `scale_pos_weight=13.933042937149969`; the unweighted models use 1. This changes the loss, not the sample. There is no SMOTE/bootstrap experiment.

## 2. Environment and loading

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe verify_p1.py
```

Reuse the existing `.venv` if it is available. Python 3.13 and XGBoost 3.0.2 are the tested versions. Creating the virtual environment again is unnecessary when reusing it.

Minimal loading example, run from the project root:

```python
import json
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

p1 = Path("outputs/p1")
features = json.loads((p1 / "feature_schema.json").read_text())["features"]
X = pd.read_csv(p1 / "processed/X_test.csv",
                index_col="borrower_id", float_precision="round_trip")
assert list(X.columns) == features
folder = p1 / "runs/unweighted_seed11"
model = XGBClassifier()
model.load_model(folder / "model.ubj")
saved = pd.read_csv(folder / "predictions.csv", float_precision="round_trip")
assert X.index.tolist() == saved["borrower_id"].tolist()
np.testing.assert_allclose(model.predict_proba(X)[:, 1],
                           saved["probability"], rtol=0, atol=1e-7)
```

`borrower_id` is a row identifier, not a feature. Do not impute the exported matrices again, scale them, reorder features, or recreate the split. Save borrower IDs alongside every explanation array.

## 3. Freeze your analysis choices first

Write `outputs/p2/analysis_protocol.md` before producing the full explanation results. P1 predictive results already exist; do not claim that the complete study was preregistered.

| Decision | Recommended starting choice to record |
| --- | --- |
| Cohort | All 30,013 held-out rows, in saved order; use batches if necessary |
| Output scale | Raw XGBoost margin (log odds), consistently across all runs |
| Reference handling | Prefer explicit interventional TreeSHAP with one fixed training-only background if computationally feasible |
| Background for that mode | Sample 100 processed training rows once with a recorded seed; save their IDs and reuse them for every model |
| Alternative | Explicit tree-path-dependent TreeSHAP; record that the implied reference is model-specific |
| Feature ranking | Descending absolute SHAP values, excluding the bias/base term |
| Top-k | 3 and 5 |
| Ties | Average ranks for Spearman; stable feature-schema order to break top-k ties |
| Numerical-zero handling | Record a small threshold in raw-margin units and the reason for it before computing sign/CV summaries |
| Perturbation | Replace k highest- or k lowest-ranked features jointly with the same training medians; use equal k in both arms |
| Fidelity output | Absolute probability change; retain raw-margin change too if interpreting comparisons across conditions |

The choice between interventional and tree-path-dependent explanations is a methodological decision. Keep the selected mode explicit and constant, and do not choose it based on whichever produces nicer stability results. Tree-path-dependent references can differ across learned models, so observed changes include that reference effect. With interventional mode, use an identical background matrix for every model.

The external `shap` package has not been installed or version-tested in P1. If you use it, test compatibility on a small fixed batch, pin the working version separately for P2, and record its dependencies without changing the frozen P1 `requirements.txt`. `shap.TreeExplainer` documents the raw-margin scale and explicit reference modes in its [official API](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html).

XGBoost's native `Booster.predict(DMatrix(X), pred_contribs=True, approx_contribs=False)` is another available route for its native tree-path-dependent contributions. P1 review checked shape and additivity for the first eight held-out rows of every model; it did not compute stability/fidelity results. This returns ten feature columns plus one bias column, which together sum to the raw margin. Exclude the bias from feature rankings, but save it for additivity and baseline comparisons. See the [XGBoost 3.0 API](https://xgboost.readthedocs.io/en/release_3.0.0/python/python_api.html#xgboost.Booster.predict).

## 4. Perform these comparisons

Keep two comparison families separate:

1. **Within condition:** all ten distinct pairs among five seeds, separately for unweighted and weighted models. Total: 20 model pairs.
2. **Between conditions:** match the same seed, unweighted versus weighted. Total: five model pairs.

Pair every explanation comparison by borrower ID and feature name. The 25 comparisons are dependent because they share models and borrowers. They are not 25 independent repetitions of the experiment.

| Measure | Computation and interpretation |
| --- | --- |
| Rank stability | Per borrower/model pair, Spearman correlation of the ten absolute SHAP values. Mark undefined constant-vector correlations as missing and report their count. |
| Top-k agreement | Intersection size of the two top-k feature sets divided by k; 1 means full agreement. |
| Signed variability | Per borrower/feature, sample standard deviation of signed SHAP values across the five seeds within each condition. |
| Sign consistency | Report positive, negative, and near-zero frequencies across seeds. State the formula used for any single consistency score; do not equate all-near-zero attribution with strong importance. |
| Magnitude CV | A simple option is sample SD of absolute SHAP values divided by their mean. Mask near-zero denominators and report masked counts. Distinguish this explicitly from a CV calculated on signed means. |
| Weighting change | Per matched seed/borrower/feature, signed and absolute SHAP differences; do not mix these with within-condition CV. |
| Perturbation fidelity | Compare the absolute prediction change from replacing high-ranked features against replacing low-ranked features. Save both changes and their paired difference for each borrower/model/k. |

Report distributions as well as means. For within-condition rank results, one useful summary is each borrower's average over its ten seed pairs, then summaries across borrowers. Preserve feature-level attribution results. If adding statistical intervals, justify the sampling unit and account for repeated borrowers/models; avoid naive tests over flattened pairs.

Retain the same full cohort as the primary analysis. The review identified 55 post-imputation profiles shared across partitions, affecting 99 test rows (and 96 training rows). The original pre-imputation cleaned-profile groups do not cross partitions. This does not show test-label leakage, but it limits a claim of unseen processed profiles. If reporting an overlap-exclusion sensitivity analysis, specify it in your protocol, use the supplied 99-row ID list, and label it separately. Do not silently remove these rows from the primary results.

A median replacement can equal a borrower's existing value, making a perturbation a no-op. Retain those cases and report their frequency. Correlated features may form unrealistic combinations after replacement. Perturbation measures model sensitivity, not causality. Because weighted models have different probability calibration, compare fidelity within each model and interpret cross-condition probability-change magnitudes carefully.

## 5. Deliver to P3

Keep the code simple, for example one `run_p2.py` and a short verification step. Supply:

- Frozen analysis protocol and exact environment versions.
- Borrower/feature/run order, cohort and background IDs, and references to the P1 manifest.
- Signed explanation arrays, base values, and raw predictions for every run; check reconstruction of raw margins.
- `rank_stability.csv`: borrower ID, comparison family, run A/B, Spearman, top-3 and top-5 agreement.
- `attribution_stability.csv`: borrower, feature, condition, signed SD, sign frequencies, magnitude CV, and its validity mask.
- `fidelity.csv`: borrower, run, k, high/low probability changes, paired difference, and no-op indicators/counts.
- Clear summaries and a few figures combining predictive performance with reliability metrics.
- Borrower examples selected by a recorded rule, including mixed/negative findings rather than only striking cases.
- Checks, limitations, and a short plain-language explanation of what the results do and do not show.

P2 is complete when P3 can trace every table/figure back to the same frozen P1 borrowers and saved explanation arrays, and all three reliability dimensions have been evaluated.
