from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse


from routers.router import router as root


app = FastAPI(title="Demo")
app.include_router(root)


@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
