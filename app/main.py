from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, admin, teacher, student, constants, health
from .utils.constants import APP_NAME, APP_VERSION, APP_DESCRIPTION, DEBUG

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app with configuration from environment
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    debug=DEBUG,
    docs_url="/docs" if DEBUG else "/docs",  # Can disable docs in production
    redoc_url="/redoc" if DEBUG else "/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="", tags=["health"])  # No prefix for health endpoints
app.include_router(constants.router, prefix="/app", tags=["constants"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(teacher.router, prefix="/teacher", tags=["teacher"])
app.include_router(student.router, prefix="/student", tags=["student"])


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - health check"""
    return {
        "message": f"{APP_NAME} is running!",
        "version": APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
        "health": "/health",
        "status_detailed": "/status"
    }


# Optional: Add startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 Starting {APP_NAME} v{APP_VERSION}")

    # Validate configuration
    try:
        validate_configuration()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"👋 Shutting down {APP_NAME}")

    # Optional: Clean up resources
    # Close database connections, etc.