import os
import time
import logging
import urllib.error
import requests
import pandas as pd
import nflreadpy as nfl
from datetime import datetime

# Configure Logger
logger = logging.getLogger(__name__)


def filter_supported_seasons(seasons, min_season, max_season, dataset_name):
    supported = [season for season in seasons if min_season <= season <= max_season]
    skipped = [season for season in seasons if season not in supported]
    if skipped:
        logger.warning(
            f"Skipping unsupported {dataset_name} seasons {skipped}. "
            f"Supported range is {min_season}-{max_season}."
        )
    return supported

def execute_with_backoff(func, *args, max_retries=5, initial_backoff=2, backoff_factor=2, **kwargs):
    """
    Executes a callable with exponential backoff on HTTP 429/5xx status codes and connection errors.
    """
    retries = 0
    backoff = initial_backoff
    while True:
        try:
            return func(*args, **kwargs)
        except (urllib.error.HTTPError, requests.exceptions.HTTPError, requests.exceptions.ConnectionError, ConnectionError) as e:
            err_str = str(e).lower()
            if "404" in err_str:
                logger.error(f"Non-retryable 404 HTTP error calling {func.__name__}. Raising immediately.")
                raise e
            
            status_code = None
            if hasattr(e, 'code'):  # urllib.error.HTTPError
                status_code = e.code
            elif hasattr(e, 'response') and e.response is not None:  # requests.exceptions.HTTPError
                status_code = e.response.status_code

            retries += 1
            if retries > max_retries:
                logger.error(f"Failed executing {func.__name__} after {max_retries} retries. Raising error.")
                raise e

            # Retry on 429, 5xx server issues, or general connection/network drops (status_code is None)
            if status_code in [429, 500, 502, 503, 504] or status_code is None:
                logger.warning(
                    f"Transient network/HTTP error (status: {status_code}) calling {func.__name__}. "
                    f"Retrying in {backoff} seconds (Attempt {retries}/{max_retries})... Error: {e}"
                )
                time.sleep(backoff)
                backoff *= backoff_factor
            else:
                logger.error(f"Non-retryable HTTP error (status: {status_code}) calling {func.__name__}. Raising immediately.")
                raise e
        except Exception as e:
            # Catch-all for string-based check if requests wraps exceptions differently
            err_str = str(e).lower()
            if "429" in err_str or "too many requests" in err_str or "connection" in err_str or "timeout" in err_str:
                retries += 1
                if retries > max_retries:
                    logger.error(f"Failed executing {func.__name__} after {max_retries} retries. Raising error.")
                    raise e
                logger.warning(
                    f"Potential transient error calling {func.__name__}. "
                    f"Retrying in {backoff} seconds (Attempt {retries}/{max_retries})... Error: {e}"
                )
                time.sleep(backoff)
                backoff *= backoff_factor
            else:
                if not isinstance(e, ValueError):
                    logger.error(f"Unexpected exception calling {func.__name__}. Raising immediately.")
                raise e

def get_pbp_data(seasons):
    """
    Extracts NFL play-by-play data for the given list of seasons.
    nflreadpy handles internal caching natively.
    """
    dataframes = []

    for season in seasons:
        logger.info(f"Fetching play-by-play data for season {season} from nflreadpy")
        try:
            # Fetch using exponential backoff wrapper
            df = execute_with_backoff(nfl.load_pbp, [season])
            dataframes.append(df.to_pandas())
        except ValueError as e:
            logger.warning(
                f"🏈 Play-by-play data for season {season} is not available (typically a future/unstarted season or invalid year). "
                f"Skipping this season. Error details: {e}"
            )
        except Exception as e:
            err_str = str(e).lower()
            if "404" in err_str or "not found" in err_str:
                logger.warning(
                    f"🏈 Play-by-play data for season {season} is not available (typically a future/unstarted season or invalid year). "
                    f"Skipping this season. Error details: 404 Not Found"
                )
            else:
                logger.error(f"Unexpected error fetching play-by-play data for season {season}: {e}")
                raise e

    if not dataframes:
        logger.warning("No play-by-play data was successfully loaded.")
        return pd.DataFrame()
        
    return pd.concat(dataframes, ignore_index=True)

def get_weekly_data(seasons):
    """
    Extracts NFL weekly player metrics data for the given list of seasons.
    nflreadpy handles internal caching natively.
    """
    dataframes = []

    for season in seasons:
        logger.info(f"Fetching weekly player metrics for season {season} from nflreadpy")
        try:
            # Fetch using exponential backoff wrapper
            df = execute_with_backoff(nfl.load_player_stats, [season])
            dataframes.append(df.to_pandas())
        except ValueError as e:
            logger.warning(
                f"🏈 Weekly metrics data for season {season} is not available (typically a future/unstarted season or invalid year). "
                f"Skipping this season. Error details: {e}"
            )
        except Exception as e:
            err_str = str(e).lower()
            if "404" in err_str or "not found" in err_str:
                logger.warning(
                    f"🏈 Weekly metrics data for season {season} is not available (typically a future/unstarted season or invalid year). "
                    f"Skipping this season. Error details: 404 Not Found"
                )
            else:
                logger.error(f"Unexpected error fetching weekly metrics data for season {season}: {e}")
                raise e

    if not dataframes:
        logger.warning("No weekly metrics data was successfully loaded.")
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)

def get_team_data():
    """
    Extracts NFL team description/metadata.
    """
    logger.info("Fetching team descriptions from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_teams)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching team data: {e}")
        return pd.DataFrame()

def get_draft_picks_data():
    """
    Extracts NFL draft picks data.
    """
    logger.info("Fetching draft picks data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_draft_picks)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching draft picks data: {e}")
        return pd.DataFrame()

def get_players_data():
    """
    Extracts NFL player roster data.
    """
    logger.info("Fetching players data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_players)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching players data: {e}")
        return pd.DataFrame()

def get_contracts_data():
    """
    Extracts NFL player contracts data.
    """
    logger.info("Fetching contracts data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_contracts)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching contracts data: {e}")
        return pd.DataFrame()

def get_ngs_passing_data(seasons):
    """
    Extracts NFL Next Gen Stats passing data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2016, current_year, "NGS passing")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching NGS passing data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_nextgen_stats, seasons, stat_type="passing")
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching NGS passing data: {e}")
        return pd.DataFrame()

def get_ngs_rushing_data(seasons):
    """
    Extracts NFL Next Gen Stats rushing data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2016, current_year, "NGS rushing")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching NGS rushing data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_nextgen_stats, seasons, stat_type="rushing")
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching NGS rushing data: {e}")
        return pd.DataFrame()

def get_ngs_receiving_data(seasons):
    """
    Extracts NFL Next Gen Stats receiving data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2016, current_year, "NGS receiving")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching NGS receiving data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_nextgen_stats, seasons, stat_type="receiving")
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching NGS receiving data: {e}")
        return pd.DataFrame()

def get_ftn_charting_data(seasons):
    """
    Extracts NFL FTN charting data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2022, current_year, "FTN charting")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching FTN charting data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_ftn_charting, seasons)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching FTN charting data: {e}")
        return pd.DataFrame()

def get_snap_counts_data(seasons):
    """
    Extracts NFL weekly snap counts data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2012, current_year, "snap counts")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching snap counts data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_snap_counts, seasons)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching snap counts data: {e}")
        return pd.DataFrame()

def get_injury_reports_data(seasons):
    """
    Extracts NFL weekly injury reports data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2009, current_year, "injury reports")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching injury reports data from nflreadpy")
    try:
        df = execute_with_backoff(nfl.load_injuries, seasons)
        return df.to_pandas()
    except Exception as e:
        logger.error(f"Error fetching injury reports data: {e}")
        return pd.DataFrame()

def get_depth_charts_data(seasons):
    """
    Extracts NFL depth charts data.
    """
    current_year = datetime.now().year
    seasons = filter_supported_seasons(seasons, 2001, current_year, "depth charts")
    if not seasons:
        return pd.DataFrame()

    logger.info("Fetching depth charts data from nflreadpy")
    dfs = []
    for season in seasons:
        try:
            df = execute_with_backoff(nfl.load_depth_charts, [season])
            pdf = df.to_pandas()
            pdf['season'] = int(season)
            dfs.append(pdf)
        except Exception as e:
            logger.error(f"Error fetching depth charts data for season {season}: {e}")

    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


