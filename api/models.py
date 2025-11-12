"""
Pydantic Models for API Request/Response
Matches the exact format from your screenshots
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., example="healthy")


class RecommendRequest(BaseModel):
    """Request model for /recommend endpoint"""
    query: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="Job description or query string",
        example="I am hiring for Java developers who can also collaborate effectively with my business teams"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Python developer with 5 years experience in API development"
            }
        }


class AssessmentItem(BaseModel):
    """
    Single assessment recommendation
    Matches exact format from your screenshot
    """
    url: str = Field(
        ...,
        description="Valid URL to the assessment resource",
        example="https://www.shl.com/solutions/products/product-catalog/view/python-new/"
    )
    
    name: str = Field(
        ...,
        description="Name of the assessment",
        example="Python (New)"
    )
    
    adaptive_support: str = Field(
        ...,
        description='Either "Yes" or "No" indicating if the assessment supports adaptive testing',
        example="No"
    )
    
    description: str = Field(
        ...,
        description="Detailed description of the assessment",
        example="Multi-choice test that measures the knowledge of Python programming, databases, modules and library. For..."
    )
    
    duration: int = Field(
        ...,
        description="Duration of the assessment in minutes",
        example=11,
        ge=0
    )
    
    remote_support: str = Field(
        ...,
        description='Either "Yes" or "No" indicating if the assessment can be taken remotely',
        example="Yes"
    )
    
    test_type: List[str] = Field(
        ...,
        description="Categories or types of the assessment",
        example=["Knowledge & Skills"]
    )
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.shl.com/solutions/products/product-catalog/view/python-new/",
                "name": "Python (New)",
                "adaptive_support": "No",
                "description": "Multi-choice test that measures the knowledge of Python programming, databases, modules and library.",
                "duration": 11,
                "remote_support": "Yes",
                "test_type": ["Knowledge & Skills"]
            }
        }


class RecommendResponse(BaseModel):
    """
    Response model for /recommend endpoint
    Returns list of recommended assessments (max 10, min 1)
    """
    recommended_assessments: List[AssessmentItem] = Field(
        ...,
        description="List of recommended assessments (at most 10, minimum 1)",
        min_items=0,
        max_items=10
    )
    
    class Config:
        schema_extra = {
            "example": {
                "recommended_assessments": [
                    {
                        "url": "https://www.shl.com/solutions/products/product-catalog/view/python-new/",
                        "name": "Python (New)",
                        "adaptive_support": "No",
                        "description": "Multi-choice test that measures the knowledge of Python programming, databases, modules and library.",
                        "duration": 11,
                        "remote_support": "Yes",
                        "test_type": ["Knowledge & Skills"]
                    },
                    {
                        "url": "https://www.shl.com/solutions/products/product-catalog/view/technology-professional-8-8-job-focused-assessment/",
                        "name": "Technology Professional 8.8 Job Focused Assessment",
                        "adaptive_support": "No",
                        "description": "The Technology Job Focused Assessment assesses key behavioral attributes required for success in fast-paced roles.",
                        "duration": 16,
                        "remote_support": "Yes",
                        "test_type": ["Competencies", "Personality & Behaviour"]
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Query must be at least 3 characters long"
            }
        }