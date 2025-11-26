import time
import logging
import os
from datetime import datetime
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger("api_profiling")
logger.setLevel(logging.INFO)

# Create console handler if not exists
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ProfilingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for profiling API requests and logging response times.
    Similar to Morgan middleware in Node.js.
    
    Logs:
    - HTTP method
    - Request path
    - Status code
    - Response time (in milliseconds)
    - Request size (if available)
    - Response size (if available)
    """
    
    def __init__(self, app: ASGIApp, log_format: Optional[str] = None):
        """
        Initialize profiling middleware.
        
        Args:
            app: ASGI application
            log_format: Log format style (similar to Morgan formats). 
                       If None, reads from PROFILE_LOG_FORMAT env variable.
                       - "combined": Full log with all details (IP, method, path, status, size, referrer, user-agent, time)
                       - "dev": Short format for development (method, path, status, time)
                       - "short": Short format with IP (IP, method, path, status, time)
                       - "tiny": Minimal format (method, status, time)
        """
        super().__init__(app)
        # Get log format from parameter or environment variable, default to "combined"
        self.log_format = log_format or os.getenv("PROFILE_LOG_FORMAT", "combined")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log profiling information.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler
            
        Returns:
            Response object
        """
        # Start timing
        start_time = time.time()
        
        # Get request information
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        full_path = f"{path}?{query_params}" if query_params else path
        
        # Get client IP (check for forwarded headers)
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
            request.headers.get("x-real-ip", "") or
            (request.client.host if request.client else "unknown")
        )
        
        # Get user agent
        user_agent = request.headers.get("user-agent", "-")
        
        # Get referrer
        referrer = request.headers.get("referer", request.headers.get("referrer", "-"))
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            # Get response information
            status_code = response.status_code
            
            # Get response size from header or calculate from body if possible
            response_size = response.headers.get("content-length", "-")
            
            # Log based on format
            if self.log_format == "dev":
                # Short format: METHOD PATH STATUS TIME (similar to Morgan dev)
                log_message = f"{method} {path} {status_code} {process_time_ms}ms"
            elif self.log_format == "tiny":
                # Minimal format: METHOD STATUS TIME
                log_message = f"{method} {status_code} {process_time_ms}ms"
            elif self.log_format == "short":
                # Short format with IP: IP METHOD PATH STATUS TIME
                log_message = f"{client_ip} {method} {path} {status_code} {process_time_ms}ms"
            else:
                # Combined format (default): Full details (similar to Morgan combined)
                # Format: IP - - [DATE] "METHOD PATH HTTP/VERSION" STATUS SIZE "REFERRER" "USER-AGENT" TIME
                try:
                    # Try to get timezone-aware timestamp
                    now = datetime.now()
                    timestamp = now.strftime('%d/%b/%Y:%H:%M:%S')
                    # Add timezone offset if available
                    if hasattr(now, 'astimezone'):
                        tz_offset = now.astimezone().strftime('%z')
                        if tz_offset:
                            timestamp = f"{timestamp} {tz_offset}"
                        else:
                            timestamp = f"{timestamp} +0000"
                    else:
                        timestamp = f"{timestamp} +0000"
                except Exception:
                    # Fallback to simple timestamp
                    timestamp = datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')
                
                log_message = (
                    f"{client_ip} - - [{timestamp}] "
                    f"\"{method} {full_path} HTTP/1.1\" "
                    f"{status_code} {response_size} "
                    f"\"{referrer}\" \"{user_agent}\" "
                    f"{process_time_ms}ms"
                )
            
            # Log the request
            logger.info(log_message)
            
            # Add custom headers for response time (useful for monitoring)
            response.headers["X-Process-Time"] = f"{process_time_ms}ms"
            response.headers["X-Response-Time"] = f"{process_time_ms}ms"
            
            return response
            
        except Exception as e:
            # Calculate response time even for errors
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            # Log error
            error_message = (
                f"{client_ip} - {method} {full_path} "
                f"ERROR {process_time_ms}ms - {str(e)}"
            )
            logger.error(error_message)
            
            # Re-raise the exception
            raise

