from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.license_middleware import LicenseMiddleware
from services.license_service import LicenseService
from routes.license_routes import router as license_router
from routes.agent_routes import router as agent_router

app = FastAPI(title="Client Chat App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

license_service = LicenseService()
app.add_middleware(LicenseMiddleware, license_service=license_service)

app.include_router(license_router)
app.include_router(agent_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)