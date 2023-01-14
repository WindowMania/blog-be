from fastapi import FastAPI
import logging
from src.routers.user import router as user_router
from src.routers.post import router as post_router
from src.infra.orm import start_mappers
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app_ = FastAPI()
    return app_


app = create_app()

# cors 임시..
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

logger = logging.getLogger(__name__)
app.include_router(user_router, prefix='/api/v1/user')
app.include_router(post_router, prefix="/api/v1/post")


@app.on_event('startup')
async def on_start_app():
    logger.info("start server")
    start_mappers()


@app.on_event('shutdown')
async def on_shutdown_app():
    logger.info("shutdown server")
