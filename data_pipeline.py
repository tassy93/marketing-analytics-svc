from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
import os
import json

def fetch_google_analytics(property_id):
    """Fetch Google Analytics 4 data."""
    try:
        if not property_id:
            print("❌ No property ID provided")
            return {"error": "No Google Analytics property ID provided"}
        
        print(f"🔍 Fetching GA4 data for property: {property_id}")
        
        # Get credentials from environment variable or file
        service_account_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        
        if service_account_json:
            # Parse JSON from environment variable
            credentials_info = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            client = BetaAnalyticsDataClient(credentials=credentials)
            print("✓ Using credentials from environment variable")
        else:
            # Fallback to file
            print("⚠ Using file-based credentials")
            client = BetaAnalyticsDataClient.from_service_account_file('/app/GA_SERVICE_ACCOUNT_JSON')
        
        # Create request
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        )
        
        # Make API call
        print(f"📊 Making API request to GA4...")
        response = client.run_report(request)
        
        if not response or not hasattr(response, 'rows') or not response.rows:
            print("⚠ No data returned from GA4 API")
            return {"data": [], "total_users": 0, "message": "No data available"}
        
        print(f"✅ Received {len(response.rows)} rows from GA4")
        
        # Process response
        result = []
        total_users = 0
        
        for row in response.rows:
            date = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            total_users += users
            
            result.append({
                "date": date,
                "active_users": users
            })
        
        return {
            "data": result,
            "total_users": total_users,
            "property_id": property_id,
            "row_count": len(result),
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error in fetch_google_analytics: {str(e)}")
        return {"error": str(e), "property_id": property_id, "status": "error"}

def fetch_google_ads(customer_id):
    """Fetch Google Ads data (placeholder)."""
    if not customer_id:
        return {"data": [], "message": "No Google Ads customer ID provided", "status": "skipped"}
    
    print(f"🔍 Fetching Google Ads data for customer: {customer_id}")
    # This is a placeholder - implement actual Google Ads API call here
    return {"data": [], "message": "Google Ads integration not yet implemented", "status": "placeholder"}

def combine_metrics(ga: dict, meta: dict, gads: dict) -> dict:
    """Combine metrics from different sources."""
    print(f"🔗 Combining metrics...")
    
    # Handle None values
    if ga is None:
        ga = {"error": "GA data is None", "status": "error"}
    if gads is None:
        gads = {"error": "Ads data is None", "status": "error"}
    
    # If we have errors in GA data, log them
    if isinstance(ga, dict) and ga.get("status") == "error":
        print(f"⚠ GA data has error: {ga.get('error')}")
    
    # If we have errors in Ads data, log them
    if isinstance(gads, dict) and gads.get("status") == "error":
        print(f"⚠ Ads data has error: {gads.get('error')}")
    
    # Combine the data
    combined = {
        "google_analytics": ga,
        "google_ads": gads,
        "metadata": meta,
        "timestamp": datetime.now().isoformat(),
        "combined_status": "success" if ga.get("status") == "success" else "partial"
    }
    
    print(f"✅ Combined metrics successfully")
    return combined
