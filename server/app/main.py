import time
import structlog
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .deps import (
    log_request, 
    handle_cors_preflight, 
    handle_rate_limit_exceeded,
    verify_api_key,
    get_request_id,
    get_client_ip
)
from .models.schemas import (
    SummarizeRequest, SummarizeResponse,
    ContextRequest, ContextResponse,
    RepliesRequest, RepliesResponse,
    ErrorResponse, HealthResponse, RateLimitResponse
)
from .services.normalize import normalizer
from .services.prompts import prompt_builder
from .services.llm_client import llm_client
from .services.ratelimit import rate_limiter

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
startup_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("PostPilot backend starting up", version="1.0.0")
    yield
    logger.info("PostPilot backend shutting down")

app = FastAPI(
    title="PostPilot API",
    description="AI-powered X/Twitter post summarization and reply suggestions",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.middleware("http")(log_request)
app.middleware("http")(handle_rate_limit_exceeded)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    uptime = time.time() - startup_time
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=uptime
    )

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_post(
    request: SummarizeRequest,
    api_key: str = Depends(verify_api_key),
    request_id: str = Depends(get_request_id)
):
    start_time = time.time()
    
    try:
        client_ip = "127.0.0.1"
        is_allowed, retry_after = rate_limiter.is_allowed(client_ip, "summarize")
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {retry_after:.0f} seconds"
            )
        
        normalized = normalizer.normalize(
            request.text,
            strip_urls=False,
            strip_mentions=False
        )
        
        if not normalizer.is_valid_text(normalized['text']):
            raise HTTPException(
                status_code=400,
                detail="Invalid or too short text for processing"
            )
        
        prompt = prompt_builder.build_summarize_prompt(
            normalized['text'],
            request.persona,
            request.url,
            request.author
        )
        llm_result = await llm_client.generate(
            prompt,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        if not llm_result['success']:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate summary"
            )
        
        summary = llm_result['text'].strip()
        word_count = len(summary.split())
        processing_time = time.time() - start_time
        
        logger.info(
            "Summary generated",
            request_id=request_id,
            word_count=word_count,
            processing_time=processing_time
        )
        
        return SummarizeResponse(
            summary=summary,
            word_count=word_count,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Summarize error", request_id=request_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post("/context", response_model=ContextResponse)
async def build_context(
    request: ContextRequest,
    api_key: str = Depends(verify_api_key),
    request_id: str = Depends(get_request_id)
):
    start_time = time.time()
    
    try:
        client_ip = "127.0.0.1"
        is_allowed, retry_after = rate_limiter.is_allowed(client_ip, "context")
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {retry_after:.0f} seconds"
            )
        
        normalized = normalizer.normalize(request.text)
        
        if not normalizer.is_valid_text(normalized['text']):
            raise HTTPException(
                status_code=400,
                detail="Invalid or too short text for processing"
            )
        
        prompt = prompt_builder.build_context_prompt(
            normalized['text'],
            request.persona,
            request.url,
            request.author
        )
        llm_result = await llm_client.generate(
            prompt,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        if not llm_result['success']:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate context"
            )
        
        context = llm_result['text'].strip()
        processing_time = time.time() - start_time
        
        logger.info(
            "Context generated",
            request_id=request_id,
            processing_time=processing_time
        )
        
        return ContextResponse(
            context=context,
            source_url=request.url,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Context error", request_id=request_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post("/replies", response_model=RepliesResponse)
async def generate_replies(
    request: RepliesRequest,
    api_key: str = Depends(verify_api_key),
    request_id: str = Depends(get_request_id)
):
    start_time = time.time()
    
    try:
        client_ip = "127.0.0.1"
        is_allowed, retry_after = rate_limiter.is_allowed(client_ip, "replies")
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {retry_after:.0f} seconds"
            )
        
        normalized = normalizer.normalize(request.text)
        
        if not normalizer.is_valid_text(normalized['text']):
            raise HTTPException(
                status_code=400,
                detail="Invalid or too short text for processing"
            )
        
        prompt = prompt_builder.build_replies_prompt(
            normalized['text'],
            request.persona,
            request.style or "conversational",
            request.url,
            request.author
        )
        
        llm_result = await llm_client.generate(
            prompt,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        if not llm_result['success']:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate replies"
            )
        
        replies_text = llm_result['text'].strip()
        replies = []
        
        lines = replies_text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                line = line.lstrip('0123456789. -•')
                if line:
                    replies.append(line)
        
        if not replies:
            sentences = replies_text.split('. ')
            replies = [s.strip() + '.' for s in sentences if s.strip()]
        
        replies = replies[:3]
        processing_time = time.time() - start_time
        
        logger.info(
            "Replies generated",
            request_id=request_id,
            count=len(replies),
            processing_time=processing_time
        )
        
        return RepliesResponse(
            replies=replies,
            count=len(replies),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Replies error", request_id=request_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": getattr(request.state, 'request_id', None)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug
    )