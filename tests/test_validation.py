import unittest

import pandas as pd

from src.validation import (
    TRIVIAL_BASELINE_NAME,
    build_report,
    evaluate_trivial_baseline,
    summarize_fold_metrics,
)


class ValidationTests(unittest.TestCase):
    def test_evaluate_trivial_baseline_returns_one_row_per_fold(self):
        df = pd.DataFrame(
            {
                'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'y': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                'price_m2': [100, 110, 120, 130, 140, 150, 160, 170, 180, 190],
            }
        )
        rows = evaluate_trivial_baseline(df, ['x', 'y'])

        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row['experiment'] == TRIVIAL_BASELINE_NAME for row in rows))
        self.assertTrue(all(row['model_type'] == 'trivial_baseline' for row in rows))

    def test_summarize_fold_metrics_marks_selected_and_trivial_rows(self):
        fold_metrics = pd.DataFrame(
            [
                {'model_type': 'knn', 'experiment': 'B_metric_no_norm', 'description': 'B', 'feature_columns': 'x,y', 'use_scaler': False, 'k': 5, 'model_label': 'B_metric_no_norm_k5', 'fold': 1, 'mae': 1.0, 'rmse': 2.0, 'r2': 0.5},
                {'model_type': 'knn', 'experiment': 'B_metric_no_norm', 'description': 'B', 'feature_columns': 'x,y', 'use_scaler': False, 'k': 5, 'model_label': 'B_metric_no_norm_k5', 'fold': 2, 'mae': 1.5, 'rmse': 2.5, 'r2': 0.4},
                {'model_type': 'trivial_baseline', 'experiment': TRIVIAL_BASELINE_NAME, 'description': 'baseline', 'feature_columns': 'x,y', 'use_scaler': False, 'k': '', 'model_label': TRIVIAL_BASELINE_NAME, 'fold': 1, 'mae': 3.0, 'rmse': 4.0, 'r2': 0.1},
                {'model_type': 'trivial_baseline', 'experiment': TRIVIAL_BASELINE_NAME, 'description': 'baseline', 'feature_columns': 'x,y', 'use_scaler': False, 'k': '', 'model_label': TRIVIAL_BASELINE_NAME, 'fold': 2, 'mae': 3.5, 'rmse': 4.5, 'r2': 0.0},
            ]
        )

        summary = summarize_fold_metrics(fold_metrics, 'B_metric_no_norm', 5)

        selected_row = summary.loc[summary['model_label'].eq('B_metric_no_norm_k5')].iloc[0]
        trivial_row = summary.loc[summary['model_label'].eq(TRIVIAL_BASELINE_NAME)].iloc[0]

        self.assertTrue(bool(selected_row['is_selected_solution']))
        self.assertFalse(bool(selected_row['is_trivial_baseline']))
        self.assertTrue(bool(trivial_row['is_trivial_baseline']))

    def test_build_report_mentions_stability_and_trivial_baseline(self):
        summary = pd.DataFrame(
            [
                {
                    'model_label': 'B_metric_no_norm_k5',
                    'model_type': 'knn',
                    'mae_mean': 1.1,
                    'mae_std': 0.1,
                    'mae_min': 1.0,
                    'mae_max': 1.2,
                    'rmse_mean': 2.1,
                    'rmse_std': 0.1,
                    'rmse_min': 2.0,
                    'rmse_max': 2.2,
                    'r2_mean': 0.6,
                    'r2_std': 0.05,
                    'r2_min': 0.55,
                    'r2_max': 0.65,
                },
                {
                    'model_label': TRIVIAL_BASELINE_NAME,
                    'model_type': 'trivial_baseline',
                    'mae_mean': 3.1,
                    'mae_std': 0.2,
                    'mae_min': 2.9,
                    'mae_max': 3.3,
                    'rmse_mean': 4.1,
                    'rmse_std': 0.2,
                    'rmse_min': 3.9,
                    'rmse_max': 4.3,
                    'r2_mean': 0.1,
                    'r2_std': 0.03,
                    'r2_min': 0.07,
                    'r2_max': 0.13,
                },
            ]
        )
        selected_row = summary.iloc[0]
        trivial_row = summary.iloc[1]
        preprocess_metadata = {'rows_after_invalid_geo_filter': 6014}

        report = build_report(preprocess_metadata, summary, selected_row, trivial_row)

        self.assertIn('fold-by-fold', report)
        self.assertIn('trivial baseline', report.lower())
        self.assertIn('stable', report.lower())


if __name__ == '__main__':
    unittest.main()
