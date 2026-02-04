import os
import json
import logging
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2 import service_account
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def fetch_google_ads(customer_id: str) -> dict:
    credentials = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LINKED_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    try:
        client = GoogleAdsClient.load_from_dict(credentials)
        ga_service = client.get_service("GoogleAdsService")
        query = """
        SELECT
          metrics.cost_micros,
          metrics.clicks,
          metrics.conversions
        FROM campaign
        WHERE segments.date DURING YESTERDAY
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        row = next(iter(response), None)
        if row:
            return {
                "cost": row.metrics.cost_micros / 1_000_000,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
            }
        return {"cost": 0, "clicks": 0, "conversions": 0}
    except Exception as e:
        logger.error(f"Ads fetch failed: {str(e)}", exc_info=True)
        return {"error": str(e)}

def fetch_google_analytics(property_id):
    import os
    import json
    from google.oauth2 import service_account
    
    # Try environment variable first
    service_account_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    
    if service_account_json:
        # Parse JSON from environment variable
        credentials_info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = BetaAnalyticsDataClient(credentials=credentials)
        print("✓ Using credentials from environment variable")
    else:
        # Fallback to file (for local development)
        print("⚠ Using file-based credentials")
        # Try multiple possible locations
        possible_paths = [
            'GA_SERVICE_ACCOUNT_JSON',
            '/app/GA_SERVICE_ACCOUNT_JSON',
            './GA_SERVICE_ACCOUNT_JSON'
        ]
        
        for file_path in possible_paths:
            try:
                client = BetaAnalyticsDataClient.from_service_account_file(file_path)
                print(f"✓ Found file at: {file_path}")
                break
            except:
                continue
        else:
            raise FileNotFoundError("GA_SERVICE_ACCOUNT_JSON not found in any location")
    
    # Rest of your existing code continues here...

def combine_metrics(ga: dict, meta: dict, gads: dict) -> dict:
    return {
        "date": "yesterday",
        "sessions": ga.get("sessions", 0),
        "users": ga.get("users", 0),
        "bounce_rate": ga.get("bounce_rate", 0),
        "ad_spend": gads.get("cost", 0),
        "clicks": gads.get("clicks", 0),
        "conversions": gads.get("conversions", 0),
        "error": ga.get("error") or gads.get("error")
    }
