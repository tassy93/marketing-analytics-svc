# app.py - FastAPI endpoint exposing combined GA & Ads metrics

import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables (including .env)
load_dotenv()

# Import pipeline functions
from data_pipeline import fetch_google_analytics, fetch_google_ads, combine_metrics

app = FastAPI()

# Default GA property (must be set in .env as GOOGLE_ANALYTICS_PROPERTY)
GA_PROPERTY = os.getenv("GOOGLE_ANALYTICS_PROPERTY", "properties/522918452")

@app.get("/metrics")
def get_metrics():
    """Return a combined dict of GA4 and Google Ads sandbox metrics."""
    ga = fetch_google_analytics(GA_PROPERTY)
    ads = fetch_google_ads(os.getenv("GOOGLE_ADS_LINKED_CUSTOMER_ID"))
    combined = combine_metrics(ga, {}, ads)
    return combined
