import os
import time
import logging
import urllib.error
import requests
import pandas as pd
import nflreadpy as nfl

# Configure Logger
logger = logging.getLogger(__name__)

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
