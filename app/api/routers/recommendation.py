from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import HTMLResponse
import json
from app.services.recommendation import RecommendationService

router = APIRouter(tags=["recommendation"])

@router.get("/get_recommendation/{userID}/{stationID}", response_class=HTMLResponse)
def get_recommendation(userID: int = Path(..., gt=0, description="The userID to get recommendations for"), 
                       stationID: int = Path(..., gt=0, description="The stationID to get recommendations for"),
                       n_recommendations: int = Query(5, gt=0, le=20, description="Number of recommendations to return")
                       ) -> Any:
    """
    Get recommendation list for user
    """
    recommendation_service = RecommendationService()
    try:
        recommendation_service.refresh_model()
        recommendation_list = recommendation_service.get_recommendations_for_user(userID, stationID, n_recommendations=n_recommendations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return HTMLResponse(content=json.dumps(recommendation_list), status_code=200)

