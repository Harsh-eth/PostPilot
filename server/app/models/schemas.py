"""
Pydantic schemas for API request/response models
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class BaseRequest(BaseModel):
    """Base request model with common fields"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to process")
    url: Optional[str] = Field(None, description="URL of the post (optional)")
    author: Optional[str] = Field(None, description="Author handle (optional)")
    persona: str = Field("human", description="Persona for AI responses")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('persona')
    def validate_persona(cls, v):
        allowed_personas = ['human', 'hardcore', 'curator']
        if v not in allowed_personas:
            raise ValueError(f'Persona must be one of: {", ".join(allowed_personas)}')
        return v


class SummarizeRequest(BaseRequest):
    """Request model for summarization endpoint"""
    pass


class ContextRequest(BaseRequest):
    """Request model for context building endpoint"""
    pass


class RepliesRequest(BaseRequest):
    """Request model for reply suggestions endpoint"""
    style: Optional[str] = Field("conversational", description="Reply style")
    
    @validator('style')
    def validate_style(cls, v):
        allowed_styles = ['conversational', 'professional', 'casual', 'witty']
        if v not in allowed_styles:
            raise ValueError(f'Style must be one of: {", ".join(allowed_styles)}')
        return v


class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    summary: str = Field(..., description="Generated summary")
    word_count: int = Field(..., description="Word count of summary")
    processing_time: float = Field(..., description="Processing time in seconds")


class ContextResponse(BaseModel):
    """Response model for context building"""
    context: str = Field(..., description="Generated context with bullet points")
    source_url: Optional[str] = Field(None, description="Source URL if provided")
    processing_time: float = Field(..., description="Processing time in seconds")


class RepliesResponse(BaseModel):
    """Response model for reply suggestions"""
    replies: List[str] = Field(..., description="List of reply suggestions")
    count: int = Field(..., description="Number of replies generated")
    processing_time: float = Field(..., description="Processing time in seconds")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for debugging")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="Uptime in seconds")


class RateLimitResponse(BaseModel):
    """Rate limit exceeded response"""
    error: str = Field("Rate limit exceeded", description="Error message")
    retry_after: int = Field(..., description="Seconds to wait before retrying")
    limit: int = Field(..., description="Request limit per window")
    window: int = Field(..., description="Time window in seconds")
