import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def clean_column_names(df):
    """
    Sanitizes column names to be compatible with Google BigQuery rules:
    - Only alphanumeric characters and underscores are allowed.
    - Column names must not start with a digit.
    - Column names must be unique.
    """
    cleaned_columns = []
    seen = {}
    for col in df.columns:
        # Convert to string and strip
        name = str(col).strip()
        # Replace non-alphanumeric/non-underscore characters with an underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # If column starts with a digit, prefix it
        if name and name[0].isdigit():
            name = f"col_{name}"
        # Ensure column name is not empty
        if not name:
            name = "unnamed_field"
        
        # Deduplicate column names
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
            
        cleaned_columns.append(name)
        
    df.columns = cleaned_columns
    return df

def transform_pbp_data(df):
    """
    Transforms play-by-play data:
    - Cleans column names
    - Verifies 'season' column is integer type and drops invalid seasons
    """
    if df.empty:
        return df
        
    logger.info("Transforming Play-by-Play data...")
    df = clean_column_names(df)
    
    # Ensure season column exists and is cast to integer
    if 'season' in df.columns:
        df = df.dropna(subset=['season'])
        df['season'] = df['season'].astype('int64')
    else:
        raise ValueError("Play-by-play data is missing the 'season' column.")
        
    logger.info(f"PBP Transformation complete. Rows: {len(df)}")
    return df

def transform_weekly_data(df):
    """
    Transforms weekly player metrics data:
    - Cleans column names
    - Verifies 'season' column is integer type and drops invalid seasons
    """
    if df.empty:
        return df
        
    logger.info("Transforming Weekly player metrics data...")
    df = clean_column_names(df)
    
    if 'season' in df.columns:
        df = df.dropna(subset=['season'])
        df['season'] = df['season'].astype('int64')
    else:
        raise ValueError("Weekly player metrics data is missing the 'season' column.")
        
    logger.info(f"Weekly Transformation complete. Rows: {len(df)}")
    return df

def transform_team_data(df, seasons):
    """
    Transforms team description data:
    - Cleans column names
    - Replicates/maps static team descriptions for each season in `seasons` 
      to enable table partitioning by 'season'.
    """
    if df.empty:
        return df
        
    logger.info("Transforming Team Description data...")
    df = clean_column_names(df)
    
    # Replicate the team description rows for each requested season to enforce the 'season' partitioning requirement
    replicated_dfs = []
    for season in seasons:
        season_df = df.copy()
        season_df['season'] = int(season)
        replicated_dfs.append(season_df)
        
    final_df = pd.concat(replicated_dfs, ignore_index=True)
    logger.info(f"Team data replicated for seasons {seasons}. Rows: {len(final_df)}")
    return final_df

def transform_draft_picks_data(df, seasons):
    """
    Transforms draft picks data:
    - Cleans column names
    - Filters to only the requested seasons
    """
    if df.empty:
        return df
        
    logger.info("Transforming Draft Picks data...")
    df = clean_column_names(df)
    
    if 'season' in df.columns:
        df = df.dropna(subset=['season'])
        df['season'] = df['season'].astype('int64')
        df = df[df['season'].isin(seasons)]
    else:
        raise ValueError("Draft picks missing season")
        
    logger.info(f"Draft Picks Transformation complete. Rows: {len(df)}")
    return df

def transform_players_data(df, seasons):
    """
    Transforms players data:
    - Cleans column names
    - Replicates data for each season to enable partitioning by 'season'
    """
    if df.empty:
        return df
        
    logger.info("Transforming Players data...")
    df = clean_column_names(df)
    
    replicated_dfs = []
    for season in seasons:
        season_df = df.copy()
        season_df['season'] = int(season)
        replicated_dfs.append(season_df)
        
    final_df = pd.concat(replicated_dfs, ignore_index=True)
    logger.info(f"Players data replicated for seasons {seasons}. Rows: {len(final_df)}")
    return final_df

def transform_contracts_data(df, seasons):
    """
    Transforms contracts data:
    - Cleans column names
    - Replicates data for each season to enable partitioning by 'season'
    """
    if df.empty:
        return df
        
    logger.info("Transforming Contracts data...")
    df = clean_column_names(df)
    
    replicated_dfs = []
    for season in seasons:
        season_df = df.copy()
        season_df['season'] = int(season)
        replicated_dfs.append(season_df)
        
    final_df = pd.concat(replicated_dfs, ignore_index=True)
    logger.info(f"Contracts data replicated for seasons {seasons}. Rows: {len(final_df)}")
    return final_df

def transform_standard_seasonal_data(df, seasons, dataset_name):
    """
    Transforms seasonal data (NGS and FTN):
    - Cleans column names
    - Filters to only the requested seasons
    """
    if df.empty:
        return df
        
    logger.info(f"Transforming {dataset_name} data...")
    df = clean_column_names(df)
    
    if 'season' in df.columns:
        df = df.dropna(subset=['season'])
        df['season'] = df['season'].astype('int64')
        df = df[df['season'].isin(seasons)]
    else:
        raise ValueError(f"{dataset_name} missing season")
        
    logger.info(f"{dataset_name} Transformation complete. Rows: {len(df)}")
    return df

def transform_depth_charts_data(df, seasons):
    """
    Transforms depth charts data:
    - Cleans column names
    - Filters to only the requested seasons
    """
    if df.empty:
        return df

    logger.info("Transforming Depth Charts data...")
    df = clean_column_names(df)

    if 'season' in df.columns:
        df = df.dropna(subset=['season'])
        df['season'] = df['season'].astype('int64')
        df = df[df['season'].isin(seasons)]
    else:
        raise ValueError("Depth charts data is missing the 'season' column.")

    logger.info(f"Depth Charts Transformation complete. Rows: {len(df)}")
    return df

