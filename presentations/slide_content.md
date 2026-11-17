# Revised P3 presentation — IEEE-style companion deck

The revised presentation is supplied as a 19-slide editable PowerPoint and rendered PDF. It uses a 16:9 research-talk format, a restrained navy/teal visual system, larger data visualisations, and borrower-level examples.

## Slide order
1. Title
2. Problem: prediction versus explanation reliability
3. Three distinct reliability checks
4. Borrower 463: stable top-three explanation
5. Borrower 13186: weighting-sensitive top-three set
6. Borrower 33756: counterexample to average H3
7. Literature foundations and positioning
8. Two closest 2025 credit-XAI studies
9. Proposed solution / controlled audit flow
10. Dataset, target and fixed split
11. Ten models and shared TreeSHAP reference
12. Local rank agreement
13. Attribution sign and magnitude stability
14. Median-replacement sensitivity and design caveat
15. Predictive performance trade-off
16. Hypothesis discussion
17. Conclusion and future experiments
18. Selected references
19. Close

## Data accuracy guardrails
- Spearman means: 0.959 within unweighted; 0.949 within weighted; 0.924 between matched weighting conditions.
- Top-3 agreement: 0.950, 0.931, 0.898. Between-condition fifth percentile: 0.667.
- Sign consistency: approximately 0.938–1.000 among non-near-zero attributions.
- Median magnitude CV: about 0.020–0.023 for delinquency counts; 0.212–0.270 for DebtRatio; 0.226–0.258 for MonthlyIncome.
- Mean high-minus-low raw-margin change: 0.956, 0.931, 1.012, 0.982 for unweighted k=3, unweighted k=5, weighted k=3, weighted k=5.
- Perturbation arms change unequal feature counts; low-arm no-op at k=3 is 11.2% unweighted and 12.7% weighted.
- ROC-AUC is close (0.86504 vs 0.86529), but log loss (0.17658 vs 0.43289) and Brier (0.04864 vs 0.13681) differ materially.
- The presentation does not claim causality, predictive equivalence, universal explanation stability, or novelty as the first credit-risk SHAP stability study.

See `speaker_notes.md` for the talk track.