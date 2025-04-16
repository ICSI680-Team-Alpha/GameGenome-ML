from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import HTMLResponse
import json

router = APIRouter(tags=["recommendation"])

@router.get("/get_recommendation/{userID}", response_class=HTMLResponse)
def get_recommendation(userID: int = Path(..., gt=0, description="The userID to get recommendations for")) -> Any:
    """
    Get recommendation list for user
    """
    ## TODO: Implement recommendation logic
    sample_list = [10, 20, 30]
    
    return HTMLResponse(content=json.dumps(sample_list), status_code=200)
