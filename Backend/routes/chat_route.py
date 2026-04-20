from fastapi import APIRouter, Query, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.chat_engine import legal_chat
from middleware.token_jwt import create_jwt_token, verify_jwt_token
from middleware.mongo_session_manager import mongo_session_manager

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_or_create_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> tuple[str, str]:
    token = credentials.credentials if credentials else None
    token_status = "new"

    if not token:
        token = create_jwt_token()
    else:
        payload = verify_jwt_token(token)
        if payload is None:
            token = create_jwt_token()
            token_status = "regenerated"
        else:
            token_status = "existing"

    mongo_session_manager.create_session(token)
    return token, token_status


@router.get("/history")
def get_chat_history(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token is required.",
            )

        token = credentials.credentials
        payload = verify_jwt_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            )

        history = mongo_session_manager.get_history(token)

        return {
            "token": token,
            "token_status": "existing",
            "history": history,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}",
        )

@router.get("/")
def chat_query(
    q: str = Query(..., description="User query to retrieve information"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    try:
        token, token_status = _resolve_or_create_token(credentials)

        history = mongo_session_manager.get_history(token)
        response_text = legal_chat(query=q, history=history)
        mongo_session_manager.store_message(token, "User Query", q)
        mongo_session_manager.store_message(token, "AI Response", response_text.get("answer", ""))

        history = mongo_session_manager.get_history(token)
        return {
            "query": q,
            "response": response_text,
            "token": token,
            "token_status": token_status,
            "history": history,
        }

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )
