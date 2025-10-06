# OddsDataIngestion
Code relating to data ingestion for sports betting data analysis

## get_pinnacle.py

This script fetches odds data from the Pinnacle API and stores it in a PostgreSQL database. It's designed to be run as a cron job on Render.

### Environment Variables

- `PINNACLE_API_KEY`: Your API key for the Pinnacle API
- `DATABASE_URL`: PostgreSQL connection URL in the format `postgresql://username:password@host:port/database`

### Running on Render

1. Create a new Cron Job service on Render
2. Set the build command to install dependencies: `pip install requests psycopg2-binary`
3. Set the start command to run the script: `python get_pinnacle.py`
4. Configure the environment variables in the Render dashboard
5. Set the schedule for how often you want the script to run

