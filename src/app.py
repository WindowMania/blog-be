from fastapi import FastAPI
import logging
from src.user.routers.user import router as user_router
from src.infra.orm import start_mappers


def create_app() -> FastAPI:
    app_ = FastAPI()
    return app_


app = create_app()
logger = logging.getLogger(__name__)
app.include_router(user_router, prefix='/api/v1/user')


@app.on_event('startup')
async def on_start_app():
    logger.info("start server")
    start_mappers()


@app.on_event('shutdown')
async def on_shutdown_app():
    logger.info("shutdown server")
