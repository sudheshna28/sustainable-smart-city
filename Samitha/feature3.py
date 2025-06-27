# feature_3.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from samitha.problem_solution import SmartCityRAGSolver  # Import your main class

# Initialize FastAPI app
app = FastAPI(title="Smart City Problem Solver")

# Load the RAG Solver
try:
    solver = SmartCityRAGSolver(
        index_path=r"C:\Users\DELL\Desktop\sustainble\sustainable-smart-city\problems_index",
        use_t5=True  # Set to True if you want T5 generation
        # models_cache_dir="your_cache_path"  # Optional if needed
    )
    print("✅ SmartCityRAGSolver loaded successfully.")
except Exception as e:
    print(f"❌ Failed to initialize SmartCityRAGSolver: {e}")
    raise RuntimeError("Could not load SmartCityRAGSolver.")

# Request & Response Models
class SmartCityQueryRequest(BaseModel):
    query: str

class SmartCitySolutionResponse(BaseModel):
    is_smart_city_related: bool
    query: str
    category: str
    confidence_score: float
    steps: List[str]
    original_solutions: List[dict]
    timestamp: str

# Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Main Endpoint: Solve a Smart City Problem
@app.post("/solve", response_model=SmartCitySolutionResponse)
def solve_problem(request: SmartCityQueryRequest):
    try:
        result = solver.solve_smart_city_problem(request.query)

        if not result['is_smart_city_related']:
            raise HTTPException(
                status_code=400,
                detail=result['message']
            )

        return SmartCitySolutionResponse(
            is_smart_city_related=result['is_smart_city_related'],
            query=result['query'],
            category=result['category'],
            confidence_score=result['confidence_score'],
            steps=result['steps'],
            original_solutions=result['original_solutions'],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
