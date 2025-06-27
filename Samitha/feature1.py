# feature_1.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os

# Import your actual logic from recycle.py
from .recycle import (
    GraniteAPIClient,
    get_sustainability_advice_api,
)

app = FastAPI()

# Load credentials
API_KEY = os.getenv("IBM_API_KEY", "your_api_key_here")  # Replace this or set as env var
PROJECT_ID = "ce2ced52-0815-4c93-9d49-6f105f4ff799"
MODEL_ID = "ibm/granite-3-2b-instruct"

# Set up the Granite API client
client = GraniteAPIClient(API_KEY)
client.set_project_id(PROJECT_ID)
if not client.authenticate():
    print("❌ IBM Granite API authentication failed. Check your API key.")
else:
    print("✅ Granite client ready.")

# Request and Response schema
class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 300
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    feature_name: str
    timestamp: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        result = get_sustainability_advice_api(
            waste_material=request.message,
            client=client,
            model_id=MODEL_ID
        )

        if result["success"]:
            return ChatResponse(
                response=result["advice"],
                feature_name="Sustainability Advisor",
                timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
