"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import admin, auth, exports, projects, runs
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(
    projects.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["projects"]
)
app.include_router(runs.router, prefix=f"{settings.API_V1_PREFIX}/runs", tags=["runs"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"])
app.include_router(
    exports.router, prefix=f"{settings.API_V1_PREFIX}/exports", tags=["exports"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
