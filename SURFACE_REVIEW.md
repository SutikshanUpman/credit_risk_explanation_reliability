# Surface review and cleanup

Date: 17 November 2026. Scope: source/layout inspection, existing small reports and summaries, syntax/CLI checks, and small synthetic checks. No model training, full SHAP calculation, bootstrap analysis, or full P1/P2 verifier rerun was requested or performed in this pass. Earlier numerical audit reports remain historical evidence, not new validation.

## Simplifications made

- Moved P2's scripts and saved outputs out of the double-nested export folder. Active scripts now share the project root; results are at `outputs/p1/` and `outputs/p2/`. This fixes their script-relative P1 paths and the supplementary script's project-root calculation.
- Removed the emptied export tree and its macOS `__MACOSX`, `._*`, and `.DS_Store` metadata. Original data and saved research results were retained.
- Read the P2 feature schema once; the supplementary script now also reads feature names from it instead of repeating ten names.
- Replaced repeated hard-coded seed counts with `len(SEEDS)`, removed an unused summary argument, and reused one feature-order calculation in the supplementary script.
- Close explanation archives after reading and check borrower order before using cached arrays for analysis.
- Load `shap` only in the stages that need it. Command help and analysis helpers no longer require that package just to import the pipeline.
- Handle empty bootstrap inputs explicitly and include remainder batches if the configured bootstrap count is not divisible by 200. The current 2,000-resample setting retains its existing batching and random sequence.
- Require `--overwrite` before replacing existing P2 analysis tables/plots. Explain-only cache reuse still requires care, as noted below.
- Made `README.md` the current starting point and labelled old handovers as historical. P1's source files were left intact because their exact hashes are part of the saved experiment provenance.

The supplied P2 scripts were archived before edits in `outputs/p2_source_before_cleanup.zip`. Existing P1/P2 manifests were not regenerated to make edited code appear to be the original generating code. The supplementary script was simplified, but its previously generated CSVs were not rerun.

## P1 gaps and qualifications

| Finding | Why it matters | Next action |
| --- | --- | --- |
| Imputation produces 55 processed profiles shared between train and test, affecting 99 test rows | Original cleaned profiles are separated, but an entirely unseen processed-profile claim would be inaccurate | Retain this limitation; P2 supplies overlap-excluded sensitivity summaries |
| One dataset, one split, five seeds, and weighting only | Does not establish robustness across splits, resampling methods, populations, or time | Describe the actual scope; extra experiments are optional extensions, not missing required P1 work |
| Extreme ratios and delinquency values 96/98 are retained | Their meaning/effect remains uncertain from the dictionary | State the cleaning policy; any recoding comparison would be a new labelled sensitivity experiment |
| Similar ROC-AUC accompanies much worse weighted log loss/Brier score | Ranking similarity is not overall predictive equivalence or formal proof of calibration quality | P3 should identify the performance metric when discussing H1 |
| The P1 verifier reuses the pipeline's loading/evaluation helpers | Good artifact reproduction, but not a wholly independent validation of the methodology | Keep the verification claim limited to what was actually checked |

## P2 gaps and qualifications

| Priority | Finding visible from code/reports | Next action |
| --- | --- | --- |
| Important | High/low median-replacement arms change different numbers of features; requiring both arms to change something does not match their changed counts | Qualify H3 as sensitivity under this replacement rule. A random-k comparator and matched-change-count analysis would strengthen it, but are extensions beyond the original top-versus-low requirement |
| Important | Existing explanation files are skipped by filename alone; background/cohort files are written before those skips | Do not reuse the cache after changing inputs/settings without explicit invalidation. The added borrower-order check catches cohort ordering mismatches, not stale models/backgrounds/features |
| Important | `verify_p2.py` can write a P2 hash manifest but does not check that saved manifest during its normal verification path | Add read-only P2 artifact-hash validation before relying on it as an integrity check; record source/configuration hashes for future runs |
| Important | P2's Linux/Python 3.12 environment differs from P1's Windows/Python 3.13 environment | Use a separate environment; full installation/verification on this machine remains untested in this pass |
| Interpretation | H1 cannot be treated as equivalence of predictive performance | Say ranking metrics are close; include probability-score differences and keep explanation comparisons descriptive |
| Interpretation | H2's reference-mode sensitivity is metric-specific | Path-dependent Spearman gap is small, top-5 ordering reverses, but the weighted/unweighted top-3 difference remains. Avoid saying every within-condition result reverses/disappears |
| Interpretation | Row bootstrap intervals condition on these fixed models, and repeated records/profile groups may reduce row independence | Do not interpret the intervals as uncertainty over seeds/splits/populations; consider group-aware intervals if inferential claims require them |
| Interpretation | The near-zero cutoff has a numerical rationale, but the protocol's claim that it is below lending-relevant effects lacks domain validation | Call it an analysis threshold, not a validated financial materiality threshold |
| Provenance | File modification times are used to infer that the protocol preceded explanations | Archive/extraction can change timestamps; mtime is not strong evidence of preregistration |
| Presentation | The dedicated attribution-stability figure, compact three-dimension results table, and borrower-across-runs visual identified by the earlier report are not apparent in the existing figure inventory | P3 can add these from existing results. Existing figure layout complaints were not visually rechecked in this surface pass |

## Current status

Lightweight checks passed: syntax of all five Python scripts; both P2 CLI help commands without installing SHAP; rejection of accidental analysis overwrites; unchanged default bootstrap/attribution helper results on synthetic inputs; empty/remainder bootstrap handling; borrower-order mismatch rejection; correct local P1/P2 paths; and unchanged frozen P1 source/result hashes and recorded P2 result hashes. These are code/integrity checks, not a fresh numerical validation of the research findings.

P1 and P2 implementations and saved result families are present. The cleanup repairs their local integration and removes obvious repetition; it does not newly certify all numerical results. P3 still needs verified literature, restrained novelty/claim wording, and the integrated research write-up.

For the working layout and commands use `README.md`. For existing P2 results read `outputs/p2/handover.md` and `analysis_protocol.md`, applying the qualifications above. Preserve the original result files if performing any later rerun.
