from fastapi import FastAPI
from data_pipeline import fetch_google_analytics, fetch_google_ads, combine_metrics
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

GA_PROPERTY = os.getenv("GOOGLE_ANALYTICS_PROPERTY", "properties/522918452")

@app.get("/")
def root():
    return {"Hello": "World from Marketing Analytics!"}

@app.get("/metrics")
def get_metrics():
    try:
        ga = fetch_google_analytics(GA_PROPERTY)
        ads = fetch_google_ads(os.getenv("GOOGLE_ADS_LINKED_CUSTOMER_ID"))
        combined = combine_metrics(ga, {}, ads)
        return combined
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return {"error": str(e)}, 500
# Force redeploy - Wed Feb  4 09:41:05 SAST 2026
