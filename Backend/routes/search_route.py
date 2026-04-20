from fastapi import APIRouter, HTTPException, Query, status

from core.query_engine import search_atlas_direct


router = APIRouter()


@router.get("/")
def search_query(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Max results"),
    mode: str = Query("auto", description="Search mode: auto | search | vector (legacy)"),
):
    try:
        result = search_atlas_direct(query=q, top_k=top_k, mode=mode)
        return {
            "status": "success",
            "query": q,
            "mode": result.get("mode", mode),
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Atlas direct search failed: {str(e)}",
        )
