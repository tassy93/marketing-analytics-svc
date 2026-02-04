from fastapi import FastAPI
from data_pipeline import fetch_google_analytics, fetch_google_ads, combine_metrics
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

GA_PROPERTY = os.getenv("GOOGLE_ANALYTICS_PROPERTY", "properties/522918452")

@app.get("/")
def root():
    return {"Hello": "World from Marketing Analytics!"}

@app.get("/metrics")
def get_metrics():
    ga = fetch_google_analytics(GA_PROPERTY)
    ads = fetch_google_ads(os.getenv("GOOGLE_ADS_LINKED_CUSTOMER_ID"))
    combined = combine_metrics(ga, {}, ads)
    return combined
