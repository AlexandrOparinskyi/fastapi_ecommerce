from fastapi import FastAPI, Request, status
from loguru import logger
from uuid import uuid4
from fastapi.responses import JSONResponse

from app.routers import category, products, auth, permission, review

app = FastAPI()
logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message} ", level="INFO", enqueue=True)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to '{request.url.path}' failed")
            else:
                logger.info("Successfully accessed '" + request.url.path + "'")
        except Exception as ex:
            logger.error(f"Request to '{request.url.path}' failed: {ex}")
            response = JSONResponse(content={"Success": False}, status_code=500)
        return response


@app.get('/')
async def welcome() -> dict:
    return {"message": "Welcome"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(review.router)
