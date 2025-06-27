# feature_2.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .query_rag import SmartVillageComparator

# Initialize FastAPI app
app = FastAPI()

# Load comparator
try:
    comparator = SmartVillageComparator()
    print("✅ SmartVillageComparator loaded.")
except Exception as e:
    print(f"❌ Initialization error: {e}")
    raise RuntimeError("Failed to load SmartVillageComparator.")

# Request Models
class ComparisonRequest(BaseModel):
    village1: str
    village2: str
    criteria: Optional[str] = None

class VillageRequest(BaseModel):
    village: str

class RecommendationRequest(BaseModel):
    village1: str
    village2: str

# Response Models
class ComparisonResponse(BaseModel):
    comparison: str
    timestamp: str
    feature_name: str = "Village Sustainability Comparator"

class DataResponse(BaseModel):
    village: str
    chunks: list
    timestamp: str

class RecommendationResponse(BaseModel):
    recommendations: str
    timestamp: str

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Endpoint: Compare two villages
@app.post("/compare", response_model=ComparisonResponse)
def compare_villages(request: ComparisonRequest):
    try:
        chunks1, _ = comparator.retrieve_village_data(request.village1)
        chunks2, _ = comparator.retrieve_village_data(request.village2)

        if not chunks1:
            raise HTTPException(status_code=404, detail=f"No data for {request.village1}")
        if not chunks2:
            raise HTTPException(status_code=404, detail=f"No data for {request.village2}")

        comparison = comparator.generate_comparison(
            request.village1, request.village2, chunks1, chunks2
        )

        return ComparisonResponse(
            comparison=comparison,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: Get village data
@app.post("/data", response_model=DataResponse)
def get_village_data(request: VillageRequest):
    try:
        chunks, _ = comparator.retrieve_village_data(request.village)
        if not chunks:
            raise HTTPException(status_code=404, detail=f"No data found for '{request.village}'")
        return DataResponse(
            village=request.village,
            chunks=chunks,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: Generate sustainability recommendations
@app.post("/recommend", response_model=RecommendationResponse)
def recommend_solutions(request: RecommendationRequest):
    try:
        chunks1, _ = comparator.retrieve_village_data(request.village1)
        chunks2, _ = comparator.retrieve_village_data(request.village2)

        if not chunks1 or not chunks2:
            raise HTTPException(status_code=404, detail="Village data missing.")

        recommendations = comparator._generate_recommendations(
            request.village1, request.village2, chunks1, chunks2
        )

        return RecommendationResponse(
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: CLI Interactive Mode (Run manually if needed)
def main():
    try:
        comparator = SmartVillageComparator()
        comparator.run_interactive_session()
    except Exception as e:
        print(f"❌ Error launching CLI mode: {e}")

if __name__ == "__main__":
    main()
