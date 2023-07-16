from fastapi import APIRouter, Depends
from app.endpoints import auth, posts, reactions
from app.core.auth import get_current_user, oauth2_scheme

api_router = APIRouter(prefix="/api", redirect_slashes=True, responses={404: {"description": "Not found"}})

api_router.include_router(auth.router, tags=["Auth"])

api_router_with_token = APIRouter(
    prefix="/api",
    redirect_slashes=True,
    dependencies=[Depends(oauth2_scheme), Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

api_router_with_token.include_router(posts.router, tags=["Posts"])
api_router_with_token.include_router(reactions.router, tags=["Reactions"])

