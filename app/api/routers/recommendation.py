from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app import crud
router = APIRouter(tags=["recommendation"])

@router.get("/get_recommendation/{_id}", response_class=HTMLResponse)
def get_recommendation() -> Any:
    """
    Get recommendation list for user
    """
    sample_list = [10, 20, 30]
    return HTMLResponse(content=sample_list, status_code=200)
