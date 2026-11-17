# Presentation structure and slide content

Order follows the requested sequence: problem statement; solution with three borrower examples; literature review; proposed solution; methodology; results/discussion; conclusion; future work. The editable PowerPoint contains 20 slides. Speaker notes are in `speaker_notes.md`.

## Slide sequence
1. Title
2. Problem statement: predictive score versus explanation reliability
3. Solution: rank stability, attribution stability, model sensitivity
4. Example 1: stable local explanation (borrower row 463)
5. Example 2: weighting-dependent top-three set (borrower row 13186)
6. Example 3: borrower-level counterexample to H3 (borrower row 33756); note row 2157 for rank/top-k complementarity
7. Literature foundations: SHAP, robustness, quantitative evaluation, credit scoring
8. Closest 2025 credit-risk explanation-stability studies and careful positioning
9. Proposed solution: fixed-cohort explanation audit
10. Methodology: dataset, target, split, preprocessing
11. Methodology: ten XGBoost models, TreeSHAP reference, metric definitions
12. Results: rank stability
13. Results: signed-attribution and magnitude stability
14. Results: perturbation sensitivity and design caveat
15. Results: predictive performance and weighting trade-off
16. Discussion: hypothesis outcomes
17. Conclusion
18. Future work
19. Selected references
20. Close

## Critical presentation caveats
- Do not say that this is the first SHAP stability study in credit scoring.
- Do not say the weighted/unweighted models have equivalent predictive performance: ROC-AUC is close, log loss and Brier differ materially.
- Do not describe the perturbation test as causal or as the formal Yeh et al. infidelity metric.
- Do not say that all borrowers have stable explanations; show the tail and the counterexample.
- Bootstrap intervals are over borrowers conditional on ten fixed models.
