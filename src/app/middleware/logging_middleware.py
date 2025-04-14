from fastapi import Request
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request received: {request.method} {request.url.path}", 
                   {"query_params": str(request.query_params)})
        
        try:
            # Process the request and get response
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log the response
            logger.log_request(
                method=request.method,
                url=request.url.path,
                status_code=response.status_code,
                processing_time=process_time
            )
            
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                {
                    "error": str(e),
                    "processing_time_ms": process_time * 1000
                },
                exc_info=True
            )
            raise 