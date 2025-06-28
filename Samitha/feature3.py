from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import traceback
import logging
import numpy as np
import os

# Enforce offline mode for transformers
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Set logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Smart City Problem Solver")

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

# Helper to convert numpy types to native Python types
def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

# Load RAG Solver
try:
    from samitha.problem_solution import SmartCityRAGSolver

    solver = SmartCityRAGSolver(
        index_path=r"C:\Users\DELL\Desktop\sustainble\sustainable-smart-city\problems_index",
        use_t5=True,
        models_cache_dir=r"C:\Users\Shamitha kondapalli\.cache\huggingface\hub"
    )
    logger.info("✅ SmartCityRAGSolver loaded successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize SmartCityRAGSolver: {e}")
    solver = None

# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "solver_loaded": solver is not None
    }

# Debug Endpoint
@app.post("/debug")
def debug_solve(request: SmartCityQueryRequest):
    try:
        logger.info(f"Debug request: {request.query}")

        if solver is None:
            return {"error": "Solver not initialized", "query": request.query}

        result = solver.solve_smart_city_problem(request.query)
        result = convert_numpy_types(result)

        return {
            "debug": True,
            "query": request.query,
            "raw_result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "query": request.query
        }

# Main Problem Solver Endpoint
@app.post("/solve", response_model=SmartCitySolutionResponse)
def solve_problem(request: SmartCityQueryRequest):
    try:
        logger.info(f"Solve request: {request.query}")

        if solver is None:
            raise HTTPException(status_code=503, detail="Smart City solver is not available")

        result = solver.solve_smart_city_problem(request.query)
        result = convert_numpy_types(result)

        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid response from solver")

        if not result.get('is_smart_city_related', False):
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Query is not related to smart city problems')
            )

        response_data = {
            "is_smart_city_related": result.get('is_smart_city_related', False),
            "query": result.get('query', request.query),
            "category": result.get('category', 'Unknown'),
            "confidence_score": float(result.get('confidence_score', 0.0)),
            "steps": result.get('steps', []) if isinstance(result.get('steps'), list) else [str(result.get('steps'))],
            "original_solutions": result.get('original_solutions', []) if isinstance(result.get('original_solutions'), list) else [],
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Response: {response_data}")
        return SmartCitySolutionResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Solve error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
