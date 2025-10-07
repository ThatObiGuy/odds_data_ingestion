# OddsDataIngestion
Code relating to data ingestion for sports betting data analysis

## get_pinnacle.py

This script fetches odds data from the Pinnacle API and stores it in a PostgreSQL database. It's designed to be run as a cron job on GitHub Actions.

### Environment Variables

- `PINNACLE_API_KEY`: Your API key for the Pinnacle API
- `DATABASE_URL`: PostgreSQL connection URL in the format `postgresql://username:password@host:port/database`

### Running on GitHub Actions

The repository includes a GitHub Actions workflow that automatically runs the script every 6 hours. To set it up:

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Add the following repository secrets:
   - `PINNACLE_API_KEY`: Your API key for the Pinnacle API
   - `DATABASE_URL`: Your PostgreSQL connection URL

### Manual Execution

You can also manually trigger the workflow:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Fetch Pinnacle Odds" workflow
3. Click "Run workflow" and confirm

### Local Execution

To run the script locally:

1. Install dependencies: `pip install -r requirements.txt`
2. Set the required environment variables
3. Run the script: `python get_pinnacle.py`
