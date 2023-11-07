import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from socialmedia.database import database
from socialmedia.logging_conf import configure_logging
from socialmedia.routers.post import router as post_router
from socialmedia.routers.user import router as user_router
from socialmedia.routers.upload import router as upload_router

logger = logging.getLogger(__name__)


# async context manager is just pool that create object based on singleton pattern to control connection to dbs ..etc based on async behavior
# based on what fastAPI need it can give it connection or run it in background or stopped mimic behavior of serverless function by using yield ---> indicator that after connection stop execution of function and just be ready when application shutdown to continue execution
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting up...")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router)
app.include_router(user_router)
app.include_router(upload_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)
