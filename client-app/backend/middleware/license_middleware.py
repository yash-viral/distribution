from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
import time
import json
from collections import defaultdict

class LicenseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, license_service):
        super().__init__(app)
        self.license_service = license_service
        self.agent_timestamps = defaultdict(list)
        self.protected_paths = ["/chat"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip middleware for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        if not any(request.url.path.startswith(path) for path in self.protected_paths):
            return await call_next(request)
        
        try:
            current_license = self.license_service.get_current_license()
            print(f"DEBUG: Middleware - current license: {current_license}")
            if not current_license:
                print("DEBUG: Middleware - No valid license found")
                return JSONResponse(status_code=400, content={"detail": "No valid license"})
            
            if not current_license.get("server_verified", False):
                return JSONResponse(status_code=403, content={"detail": "License not verified with server"})
            
            if self._is_license_expired(current_license):
                return JSONResponse(status_code=401, content={"detail": "License expired"})
            
            if request.url.path == "/chat" and request.method == "POST":
                body = await request.body()
                request._body = body
                
                try:
                    chat_data = json.loads(body.decode())
                    agent = chat_data.get("agent")
                    
                    if agent and not self._check_agent_access(agent, current_license):
                        return JSONResponse(status_code=403, content={"detail": f"Agent '{agent}' not available"})
                    
                    if agent and not self._check_rate_limit(agent, current_license):
                        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
                except:
                    pass
            
            return await call_next(request)
            
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": f"License validation error: {str(e)}"})
    
    def _is_license_expired(self, license_data):
        try:
            expires_str = license_data["expires_at"]
            if expires_str.endswith('+00:00'):
                expires_at = datetime.fromisoformat(expires_str)
            elif 'T' in expires_str and not expires_str.endswith('Z'):
                expires_at = datetime.fromisoformat(expires_str + '+00:00')
            else:
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            
            return datetime.now(timezone.utc) > expires_at
        except:
            return False
    
    def _check_agent_access(self, agent, license_data):
        return agent in license_data["agents"]
    
    def _check_rate_limit(self, agent, license_data):
        limit = license_data["rate_limit"]
        now = time.time()
        
        timestamps = [t for t in self.agent_timestamps[agent] if now - t < 60]
        self.agent_timestamps[agent] = timestamps
        
        if len(timestamps) >= limit:
            return False
        
        self.agent_timestamps[agent].append(now)
        return True