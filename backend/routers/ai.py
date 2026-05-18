from fastapi import APIRouter, Depends, HTTPException

from ai import call_ai
from routers.auth import get_token

router = APIRouter()


@router.get("/api/ai/test")
def ai_test(token: str = Depends(get_token)) -> dict:
    try:
        result = call_ai([{"role": "user", "content": "What is 2+2?"}])
        return {"response": result}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
