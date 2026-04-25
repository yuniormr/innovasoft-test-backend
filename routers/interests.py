from typing import List

from fastapi import APIRouter

import services.interests as interests_service
from core.dependencies import HttpClient, BearerToken
from schemas.clients import Interest

router = APIRouter(prefix="/api/Intereses", tags=["Intereses"])


@router.get("/Listado", response_model=List[Interest])
async def list_interests(token: BearerToken, http: HttpClient):
    return await interests_service.list_interests(token, http)

