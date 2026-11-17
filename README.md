# Credit-risk explanation reliability

This college research project asks whether explanations for the same borrowers remain reliable when model training changes. Read `instructions.md` for coding priorities and `plan.md` for the complete research plan.

The workspace contains **P1 modelling** and the imported **P2 SHAP analysis/results**. P3 owns literature verification and research integration. Read [SURFACE_REVIEW.md](SURFACE_REVIEW.md) for the latest lightweight inspection and open gaps. Earlier P1 handovers describe the state before P2 arrived.

## Run P1

Use Python 3.13. From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_p1.py
.\.venv\Scripts\python.exe verify_p1.py
```

No environment activation is needed. Inputs stay in `Data/`; generated results go to `outputs/p1/`. A nonempty output directory is protected against accidental overwriting. For a fresh reproduction, choose another directory:

```powershell
.\.venv\Scripts\python.exe run_p1.py --output outputs/p1_repeat
.\.venv\Scripts\python.exe verify_p1.py --output outputs/p1_repeat
```

Expect ten short CPU training runs. Run time depends on the machine. The scripts resolve relative paths from this project folder.

## Logic

1. Audit the labelled data and read its local dictionary.
2. Preserve borrower IDs for alignment and exclude them from predictors.
3. Treat nonpositive age as missing. Retain other unusual values because the dictionary does not establish a correction for them.
4. Group identical cleaned predictor profiles before splitting. Use the first fold of five-fold stratified group splitting, seed 42, as the one fixed held-out set. The other four folds form training data; this is one experiment split, not five-fold model evaluation.
5. Fit median imputation using training rows only, then reuse it for every run.
6. Train XGBoost with five seeds under unweighted and positive-class-weighted loss. All other settings stay fixed.
7. Save every model and every held-out prediction, evaluate with fixed metrics, and verify saved models reproduce their predictions.

Weighting changes the loss, not the training sample. No SMOTE, resampling experiment, tuning, or best-model selection is performed.

## Read the results

- `outputs/p2/handover.md`: P2 results and limitations; apply the wording qualifications in `SURFACE_REVIEW.md`.
- `outputs/p2/analysis_protocol.md`: P2 metric definitions and original analysis choices.
- `outputs/p2/p3_extras/key_results.csv`: compact P2 headline table.
- `outputs/p2/figures/`: existing P2 plots.
- `handover_p2.md`: checked inputs, loading example, SHAP decisions, analysis definitions, and P2 deliverables.
- `handover_p3.md`: verified predictive results, report-ready Methods facts, research tasks, and limitations.
- `review.md`: review findings and links to the latest verification evidence.
- `outputs/p1/handover.md`: results, checks, limitations, and P2/P3 next steps.
- `outputs/p1/dataset_card.md`: target, feature definitions, cleaning, and data limitations.
- `outputs/p1/data_audit.json`: detailed counts and unusual-value summaries.
- `outputs/p1/experiment_protocol.md`: choices recorded before training.
- `outputs/p1/metrics_all_runs.csv`: each model's predictive performance.
- `outputs/p1/metrics_summary.csv`: mean and sample standard deviation across seeds.
- `outputs/p1/manifest.json`: source/artifact hashes, environment, and completion status.
- `outputs/p1/runs/`: native model files, effective configurations, metrics, and predictions.

Exported matrices contain `borrower_id` for joining. Load them with `index_col="borrower_id"` so it never becomes a model feature. Use `float_precision="round_trip"` when reading numeric CSVs for strict prediction reproduction. `verify_p1.py` demonstrates loading and checking the saved models.

## P2 commands

P2 scripts now live beside P1, and their saved results live in `outputs/p2/`. The nested export directory and macOS metadata have been removed. The supplied P2 source is preserved in `outputs/p2_source_before_cleanup.zip` for provenance.

P2 originally ran on Linux/Python 3.12 with `requirements_p2.txt`. Its full environment has not been installed or revalidated on this Windows machine during the surface review. Use a separate P2 environment to avoid replacing P1's pinned dependencies. A full P2 rerun can be slow.

```powershell
python -m venv .venv-p2
.\.venv-p2\Scripts\python.exe -m pip install -r requirements_p2.txt
.\.venv-p2\Scripts\python.exe verify_p2.py
```

Inspect the saved results first. To deliberately recompute analysis from saved explanations, use `run_p2.py --stage analyze --overwrite` in that environment. This replaces analysis tables and plots; preserve a copy of the original results first. `--stage explain` computes missing explanation files and skips existing ones. Do not reuse that cache after changing models, background settings, or the cohort without invalidating it. The surface review did not run either stage or rewrite the original result manifests.

## Sources

- [Give Me Some Credit](https://www.kaggle.com/c/GiveMeSomeCredit/data): original dataset, subject to competition rules; see the local `Data/Data Dictionary.xls` for variable definitions.
- [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html): subsampling, tree settings, and positive-class weighting.
- [StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html): preserving group separation while approximating class proportions.

These sources support dataset/method choices, not a claim of research novelty. P3 must verify the literature separately.
