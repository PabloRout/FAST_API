from fastapi import FastAPI  # type: ignore

from storeapi.routers.post import router as post_router

app = FastAPI()

app.include_router(post_router)
# app.include_router(post_router, prefix="/posts") // makes /posts/post
