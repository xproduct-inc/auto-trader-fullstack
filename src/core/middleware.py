from fastapi import Request
from prometheus_client import Counter, Histogram
import time
from typing import Callable
from starlette.types import ASGIApp

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

class PrometheusMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope["path"]
        method = scope["method"]
        
        start_time = time.time()

        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=status_code
                ).inc()
                
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
            
            await send(message)

        await self.app(scope, receive, wrapped_send) 