#!/usr/bin/env python3
# Script to fetch odds data from Pinnacle API and store it in a PostgreSQL database
# Designed to run as a cron job on GitHub Actions

# Import required libraries
import os          # For accessing environment variables
import requests    # For making HTTP requests
import psycopg2    # For PostgreSQL database connection
import logging     # For logging information and errors
import sys         # For system-level operations
import datetime    # For timestamp generation

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def round_to_30_minutes(dt):
    """Round datetime to the nearest 30-minute interval"""
    # Get minutes and determine if we should round up or down
    minutes = dt.minute
    if minutes < 15:
        # Round down to :00
        rounded_dt = dt.replace(minute=0, second=0, microsecond=0)
    elif minutes < 45:
        # Round to :30
        rounded_dt = dt.replace(minute=30, second=0, microsecond=0)
    else:
        # Round up to next hour :00
        rounded_dt = (dt.replace(minute=0, second=0, microsecond=0) + 
                     datetime.timedelta(hours=1))
    return rounded_dt

def get_pinnacle_odds():
    # Get API key from environment variable
    api_key = os.environ.get('PINNACLE_API_KEY')
    if not api_key:
        logger.error("PINNACLE_API_KEY not set")
        return 1

    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not set")
        return 1

    # Define API endpoint and parameters
    url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/markets"
    querystring = {"league_ids": "1980", "event_type": "prematch", "sport_id": "1", "is_have_odds": "true"}
    headers = {"X-RapidAPI-Key": api_key}

    try:
        # Request data from API
        logger.info("Requesting data from Pinnacle API")
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        # Connect to database using the URL
        logger.info("Connecting to database")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Get current timestamp rounded to nearest 30 minutes
        current_time = datetime.datetime.now(datetime.timezone.utc)
        logged_time = round_to_30_minutes(current_time).isoformat()

        # Process events data
        events_count = 0
        for event in data.get('events', []):
            # Extract event details
            event_id = event.get('event_id')
            sport_id = event.get('sport_id')
            league_id = event.get('league_id')
            league_name = event.get('league_name')
            starts = event.get('starts')
            home_team = event.get('home')
            away_team = event.get('away')

            # Extract odds data
            periods = event.get('periods', {})
            match_period = periods.get('num_0', {})

            money_line = match_period.get('money_line', {})
            home_odds = money_line.get('home')
            draw_odds = money_line.get('draw')
            away_odds = money_line.get('away')

            # SQL query for inserting or updating data using ON CONFLICT
            insert_query = """
                INSERT INTO odds1x2 (
                    event_id, logged_time, sport_id, league_id, league_name, starts, 
                    home_team, away_team, home_odds, draw_odds, away_odds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id, logged_time) 
                DO UPDATE SET
                    sport_id = EXCLUDED.sport_id,
                    league_id = EXCLUDED.league_id,
                    league_name = EXCLUDED.league_name,
                    starts = EXCLUDED.starts,
                    home_team = EXCLUDED.home_team,
                    away_team = EXCLUDED.away_team,
                    home_odds = EXCLUDED.home_odds,
                    draw_odds = EXCLUDED.draw_odds,
                    away_odds = EXCLUDED.away_odds
            """

            # Execute query with data
            cursor.execute(insert_query, (
                event_id, logged_time, sport_id, league_id, league_name, starts,
                home_team, away_team, home_odds, draw_odds, away_odds
            ))
            events_count += 1

        # Save changes to database
        conn.commit()
        logger.info(f"Processed {events_count} events")

    except requests.exceptions.RequestException as e:
        # Handle API request errors
        logger.error(f"API error: {e}")
        return 1
    except psycopg2.Error as e:
        # Handle database errors
        logger.error(f"Database error: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return 1
    except Exception as e:
        # Handle any other errors
        logger.error(f"Error: {e}")
        return 1
    finally:
        # Close database connections
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

    # If we got here, everything went well
    logger.info("Script completed successfully")
    return 0

# Run the main function if script is executed directly
if __name__ == "__main__":
    sys.exit(get_pinnacle_odds())