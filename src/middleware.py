from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger("uvicorn.access")
logger.disabled = False

def register_middlewares(app: FastAPI):
    # @app.middleware("http")
    # async def custom_logging(request: Request, call_next):
    #     start_time = time.time()

    #     response = await call_next(request)
    #     processing_time = time.time() - start_time

    #     message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

    #     print(message)
    #     return response
       # Add this
       
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "192.168.5.189"],
    )