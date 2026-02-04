import os
import json
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2 import service_account
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        row = next(iter(response), None)
        if row:
            return {
                "cost": row.metrics.cost_micros / 1_000_000,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
            }
        return {"cost": 0, "clicks": 0, "conversions": 0}
    except GoogleAdsException as ex:
        return {"error": str(ex)}

def fetch_google_analytics(property_id: str) -> dict:
    json_string = os.getenv("GA_SERVICE_ACCOUNT_JSON")
    if not json_string:
        return {"error": "No GA JSON provided"}
    try:
        info = json.loads(json_string)
    except json.JSONDecodeError:
        return {"error": "Invalid GA JSON format"}
    credentials = service_account.Credentials.from_service_account_info(info)
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=property_id,
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="bounceRate"),
        ],
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
    )
    response = client.run_report(request)
    if not response.rows:
        return {"error": "No data for yesterday"}
    row = response.rows[0]
    return {
        "sessions": int(row.metric_values[0].value),
        "users": int(row.metric_values[1].value),
        "bounce_rate": float(row.metric_values[2].value) / 100,
    }

def combine_metrics(ga: dict, meta: dict, gads: dict) -> dict:
    return {
        "date": "yesterday",
        "sessions": ga.get("sessions", 0),
        "users": ga.get("users", 0),
        "bounce_rate": ga.get("bounce_rate", 0),
        "ad_spend": gads.get("cost", 0),
        "clicks": gads.get("clicks", 0),
        "conversions": gads.get("conversions", 0),
    }
