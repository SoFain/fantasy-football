import os
from google.cloud import bigquery

def main():
    project_id = 'fantasy-football-498121'
    dataset_id = 'fantasy_football_brain'
    
    client = bigquery.Client(project=project_id)
    
    query = f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.analytics_player_weekly_summary` AS
    SELECT
        m.season,
        m.week,
        m.player_name,
        m.position,
        m.team,
        SUM(m.targets) as total_targets,
        SUM(m.receptions) as total_receptions,
        SUM(m.rushing_yards) as total_rushing_yards,
        SUM(m.fantasy_points_ppr) as total_fantasy_points_ppr,
        SUM(COALESCE(m.passing_epa, 0) + COALESCE(m.rushing_epa, 0) + COALESCE(m.receiving_epa, 0)) as total_epa,
        
        SUM(s.offense_snaps) as total_offense_snaps,
        AVG(s.offense_pct) as avg_offense_pct,
        
        AVG(n.avg_separation) as avg_separation,
        
        MAX(i.report_status) as injury_status
    FROM `{project_id}.{dataset_id}.weekly_metrics` m
    LEFT JOIN `{project_id}.{dataset_id}.weekly_snap_counts` s
        ON m.season = s.season AND m.week = s.week AND m.player_name = s.player AND m.team = s.team
    LEFT JOIN `{project_id}.{dataset_id}.ngs_receiving` n
        ON m.season = n.season AND m.week = n.week AND m.player_name = n.player_display_name AND m.team = n.team_abbr
    LEFT JOIN `{project_id}.{dataset_id}.injury_reports` i
        ON m.season = i.season AND m.week = i.week AND m.player_name = i.full_name AND m.team = i.team
    GROUP BY
        m.season,
        m.week,
        m.player_name,
        m.position,
        m.team
    """
    
    print("Executing query to create materialized table 'analytics_player_weekly_summary'...")
    job = client.query(query)
    job.result() # Wait for the query to finish
    print(f"Table `{project_id}.{dataset_id}.analytics_player_weekly_summary` created and populated successfully.")

if __name__ == '__main__':
    main()
