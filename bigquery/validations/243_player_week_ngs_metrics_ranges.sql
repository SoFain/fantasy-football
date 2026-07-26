-- Expected result: invalid_metric_count = 0

SELECT COUNT(*) AS invalid_metric_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_ngs_metrics`
WHERE season < 2016
   OR week NOT BETWEEN 1 AND 23
   OR player_id_internal IS NULL
   OR (ngs_receiving_efficiency_score IS NOT NULL AND ngs_receiving_efficiency_score NOT BETWEEN 0 AND 100)
   OR (ngs_receiving_role_quality_score IS NOT NULL AND ngs_receiving_role_quality_score NOT BETWEEN 0 AND 100)
   OR (ngs_rushing_efficiency_score IS NOT NULL AND ngs_rushing_efficiency_score NOT BETWEEN 0 AND 100)
   OR (ngs_box_resilience_score IS NOT NULL AND ngs_box_resilience_score NOT BETWEEN 0 AND 100)
   OR (ngs_passing_efficiency_score IS NOT NULL AND ngs_passing_efficiency_score NOT BETWEEN 0 AND 100)
   OR ngs_missing_flags_json IS NULL
   OR source_provenance_json IS NULL;
