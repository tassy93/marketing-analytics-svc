from fastapi import FastAPI
import os
import logging
from data_pipeline import fetch_google_analytics, fetch_google_ads, combine_metrics
from datetime import datetime

app = FastAPI()
logger = logging.getLogger(__name__)

# Get environment variables
GA_PROPERTY = os.getenv("GA_PROPERTY", "")
GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_LINKED_CUSTOMER_ID", "")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {
        "service": "Marketing Analytics API",
        "status": "running",
        "endpoints": {
            "/": "This information",
            "/metrics": "Get combined analytics metrics",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment_variables": {
            "GA_PROPERTY_set": bool(GA_PROPERTY),
            "GOOGLE_ADS_CUSTOMER_ID_set": bool(GOOGLE_ADS_CUSTOMER_ID)
        }
    }

@app.get("/metrics")
def get_metrics():
    """Get combined marketing metrics."""
    try:
        logger.info("=== Starting metrics collection ===")
        
        # Check required environment variables
        if not GA_PROPERTY:
            error_msg = "GA_PROPERTY environment variable is not set"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}, 500
        
        # Fetch data from sources
        logger.info(f"Fetching Google Analytics for property: {GA_PROPERTY}")
        ga_data = fetch_google_analytics(GA_PROPERTY)
        
        logger.info(f"Fetching Google Ads for customer: {GOOGLE_ADS_CUSTOMER_ID}")
        ads_data = fetch_google_ads(GOOGLE_ADS_CUSTOMER_ID)
        
        # Log what we received
        logger.info(f"GA data type: {type(ga_data)}, keys: {list(ga_data.keys()) if isinstance(ga_data, dict) else 'N/A'}")
        logger.info(f"Ads data type: {type(ads_data)}")
        
        # Combine metrics
        meta_data = {
            "ga_property": GA_PROPERTY,
            "ads_customer": GOOGLE_ADS_CUSTOMER_ID,
            "collection_time": datetime.now().isoformat()
        }
        
        combined = combine_metrics(ga_data, meta_data, ads_data)
        
        logger.info("=== Metrics collection complete ===")
        return combined
        
    except Exception as e:
        error_msg = f"Error in get_metrics: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg, "success": False}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
# Redeploy trigger - Thu Feb  5 10:35:09 SAST 2026
