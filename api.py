from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.SmartBinDB  

def serialize_doc(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc

def fetch_collection(
    collection_name: str, sort_field: Optional[str], limit: int
) -> List[dict]:
    if collection_name not in db.list_collection_names():
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    
    collection = db[collection_name]
    
    if sort_field:
        sample_doc = collection.find_one({sort_field: {"$exists": True}})
        if not sample_doc:
            sort_field = None  
    
    if sort_field:
        docs = list(collection.find().sort(sort_field, -1).limit(limit))
    else:
        docs = list(collection.find().limit(limit))
    
    return [serialize_doc(d) for d in docs]

@app.get("/api/readings")
def get_readings(limit: int = 50):
    return fetch_collection("capacity_updates", "timestamp", limit)

@app.get("/api/alerts")
def get_alerts(limit: int = 20):
    return fetch_collection("alerts", "alert_timestamp", limit)

@app.get("/api/reports")
def get_reports(limit: int = 20):
    return fetch_collection("minute_reports", "report_generated_at", limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
