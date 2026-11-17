# Dataset card

Source: [Give Me Some Credit](https://www.kaggle.com/c/GiveMeSomeCredit/data), Credit Fusion and Will Cukierski, Kaggle (2011). Use is subject to competition rules. Variable definitions below were read from `Data/Data Dictionary.xls`.

The target `SeriousDlqin2yrs` is a binary indicator of 90-day delinquency or worse within the prediction horizon of two years. It is an operational credit-risk outcome, not a universal definition of default.

Labelled rows: 150,000. Predictors: 10. Positive rate: 6.6840%. Class counts: {'0': 139974, '1': 10026}.

| Variable | Dictionary definition | Type |
| --- | --- | --- |
| SeriousDlqin2yrs | Person experienced 90 days past due delinquency or worse | Y/N |
| RevolvingUtilizationOfUnsecuredLines | Total balance on credit cards and personal lines of credit except real estate and no installment debt like car loans divided by the sum of credit limits | percentage |
| age | Age of borrower in years | integer |
| NumberOfTime30-59DaysPastDueNotWorse | Number of times borrower has been 30-59 days past due but no worse in the last 2 years. | integer |
| DebtRatio | Monthly debt payments, alimony,living costs divided by monthy gross income | percentage |
| MonthlyIncome | Monthly income | real |
| NumberOfOpenCreditLinesAndLoans | Number of Open loans (installment like car loan or mortgage) and Lines of credit (e.g. credit cards) | integer |
| NumberOfTimes90DaysLate | Number of times borrower has been 90 days or more past due. | integer |
| NumberRealEstateLoansOrLines | Number of mortgage and real estate loans including home equity lines of credit | integer |
| NumberOfTime60-89DaysPastDueNotWorse | Number of times borrower has been 60-89 days past due but no worse in the last 2 years. | integer |
| NumberOfDependents | Number of dependents in family excluding themselves (spouse, children etc.) | integer |

`borrower_id` is the original row index, retained only for joining artifacts. It is not a predictor or proof of a real person identity. The competition test file is unlabelled; the sample submission is not ground truth. Both are excluded from modelling and evaluation.

## Audit and cleaning

Missing counts: {'RevolvingUtilizationOfUnsecuredLines': 0, 'age': 0, 'NumberOfTime30-59DaysPastDueNotWorse': 0, 'DebtRatio': 0, 'MonthlyIncome': 29731, 'NumberOfOpenCreditLinesAndLoans': 0, 'NumberOfTimes90DaysLate': 0, 'NumberRealEstateLoansOrLines': 0, 'NumberOfTime60-89DaysPastDueNotWorse': 0, 'NumberOfDependents': 3924}.

There are 609 duplicate observations beyond the first when IDs are excluded, 354 repeated predictor-profile groups, and 37 profiles with conflicting labels. Rows are retained; identical cleaned predictor profiles are grouped into one split partition. Do not interpret this as confirmed borrower-level identity grouping.

Nonpositive ages set to missing: 1. Fit median imputation only on training data. Keep all ten original predictors; no scaling, clipping, or extra indicators. Large ratios and delinquency counts (including 96/98 if present) remain because the dictionary does not document a reliable replacement rule. Their possible artifact/sentinel meaning is a limitation, not an established fact.

## Leakage review and limitations

The ID and label are excluded from inputs. Listed predictors describe borrower financial status/history; their precise collection timestamps are not available here, so temporal availability cannot be independently verified. No target-derived features are created. Imputation and loss weights use training rows only; test rows never fit a transformation or select model settings.

This historical competition sample has incomplete provenance and no usable timestamps for temporal validation. Generalization to current borrowers, other lenders, or future periods is untested. Remaining unusual values, missingness, retained repeated observations, and class imbalance can influence the models and explanations. A profile grouping policy cannot guarantee distinct real people across partitions. Post-imputation collisions between previously different profiles are reported separately.
