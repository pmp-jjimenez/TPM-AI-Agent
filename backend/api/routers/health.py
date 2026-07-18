from fastapi import APIRouter

from backend.api.compat import APPLICATION_VERSION


router = APIRouter(tags=["health"])


@router.get("/health")
def get_health():
    return {"status": "healthy", "version": APPLICATION_VERSION}
