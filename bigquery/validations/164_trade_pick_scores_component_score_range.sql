-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_component_score_rows = 0

SELECT COUNT(*) AS invalid_component_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE market_score IS NULL OR market_score < 0 OR market_score > 100
    OR slot_capital_score IS NULL OR slot_capital_score < 0 OR slot_capital_score > 100
    OR time_discount_score IS NULL OR time_discount_score < 0 OR time_discount_score > 100
    OR liquidity_certainty_score IS NULL OR liquidity_certainty_score < 0 OR liquidity_certainty_score > 100
    OR college_context_score IS NULL OR college_context_score < 0 OR college_context_score > 100
    OR uncertainty_risk_score IS NULL OR uncertainty_risk_score < 0 OR uncertainty_risk_score > 100;
