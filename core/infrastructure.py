import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# 1. Structured Logging Setup
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger("jan_ai")
    logger.info("Structured logging initialized.")
    return logger

logger = setup_logging()

# 2. Rate Limiting and Error Catching Middleware
class InfrastructureMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 200, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_records = {} # Format: { ip: [timestamp1, timestamp2] }

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up records
        if client_ip not in self.ip_records:
            self.ip_records[client_ip] = []
            
        self.ip_records[client_ip] = [
            ts for ts in self.ip_records[client_ip] if now - ts < self.window_seconds
        ]
        
        # Check rate limit
        if len(self.ip_records[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Try again later."}
            )
            
        self.ip_records[client_ip].append(now)
        
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            if response.status_code >= 400:
                logger.warning(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
            return response
        except Exception as e:
            logger.error(f"Internal structure error on {request.method} {request.url.path}: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "An internal error occurred."}
            )
