"""
FastAPI Application - SHL Assessment Recommender
Main API implementation with health check and recommendation endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
import logging

from api.models import (
    HealthResponse,
    RecommendRequest,
    RecommendResponse,
    AssessmentItem
)
from api.recommender import AssessmentRecommender
from api.config import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender API",
    description="AI-powered assessment recommendation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender system
try:
    recommender = AssessmentRecommender(
        data_path=settings.DATA_PATH,
        gemini_api_key=settings.GEMINI_API_KEY
    )
    logger.info("✅ Recommender system initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize recommender: {e}")
    recommender = None


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Starting SHL Assessment Recommender API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Documentation: http://localhost:{settings.PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Shutting down SHL Assessment Recommender API")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs"""
    return {
        "message": "SHL Assessment Recommender API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health Check Endpoint
    
    Returns the health status of the API
    """
    try:
        if recommender is None:
            raise HTTPException(
                status_code=503,
                detail="Recommender system not initialized"
            )
        
        return HealthResponse(status="healthy")
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )


@app.post(
    "/recommend",
    response_model=RecommendResponse,
    tags=["Recommendations"]
)
async def get_recommendations(request: RecommendRequest):
    """
    Assessment Recommendation Endpoint
    
    Accepts a job description or query and returns top 10 relevant assessments
    
    Args:
        request: RecommendRequest with query field
    
    Returns:
        RecommendResponse with list of recommended assessments
    
    Example:
        ```json
        {
          "query": "Python developer with 5 years experience"
        }
        ```
    """
    try:
        # Validate request
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 3 characters long"
            )
        
        # Check if recommender is initialized
        if recommender is None:
            raise HTTPException(
                status_code=503,
                detail="Recommender system not available"
            )
        
        logger.info(f"Processing recommendation request: '{request.query[:50]}...'")
        
        # Get recommendations
        recommendations = recommender.recommend(
            query=request.query,
            top_k=10  # Return top 10 as per requirements
        )
        
        # Check if we got results
        if not recommendations:
            logger.warning(f"No recommendations found for: '{request.query}'")
            return RecommendResponse(recommended_assessments=[])
        
        logger.info(f"✅ Returned {len(recommendations)} recommendations")
        
        return RecommendResponse(recommended_assessments=recommendations)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"❌ Error in recommendation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """
    Get API statistics
    
    Returns information about the loaded assessments
    """
    try:
        if recommender is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        stats = recommender.get_statistics()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )