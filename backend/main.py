import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Climate Analysis System API",
    description="API for CO₂-Groundwater-Temperature correlation analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Climate Analysis System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import routers
from api import co2_router, temperature_router, analysis_router, groundwater_router
from api import analysis_router_fixed
app.include_router(co2_router.router, prefix="/api/co2", tags=["CO2"])
app.include_router(temperature_router.router, prefix="/api/temperature", tags=["Temperature"])
app.include_router(groundwater_router.router, prefix="/api/groundwater", tags=["Groundwater"])
app.include_router(analysis_router.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(analysis_router_fixed.router, prefix="/api/analysis", tags=["Analysis Fixed"])

# Custom exception handler for better error messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc) if str(exc) else "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "True").lower() == "true"
    )