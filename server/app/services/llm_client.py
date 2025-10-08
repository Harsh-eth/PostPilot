import json
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import structlog
from ..config import settings

logger = structlog.get_logger()

class LLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

class DobbyClient(LLMClient):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.fireworks_api_key
        self.model = model or "accounts/sentientfoundation-serverless/models/dobby-mini-unhinged-plus-llama-3-1-8b"
        self.base_url = "https://api.fireworks.ai/inference/v1"
        self.timeout = 30
        
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        if not self.is_available():
            raise ValueError("Dobby client not properly configured")
        
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are Dobby, a helpful AI assistant powered by Fireworks. Provide concise, accurate, and helpful responses."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Dobby API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    processing_time = time.time() - start_time
                    
                    raw_text = result["choices"][0]["message"]["content"]
                    formatted_text = self._format_response(raw_text)
                    
                    return {
                        "text": formatted_text,
                        "model": self.model,
                        "provider": "dobby-fireworks",
                        "processing_time": processing_time,
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                        "success": True
                    }
                    
        except asyncio.TimeoutError:
            raise Exception("Dobby API timeout")
        except Exception as e:
            logger.error("Dobby API error", error=str(e))
            raise Exception(f"Dobby API error: {str(e)}")
    
    def _format_response(self, text: str) -> str:
        import re
        
        text = re.sub(r'Author:\s*[^\n]*', '', text)
        text = re.sub(r'Source URL:\s*[^\n]*', '', text)
        text = re.sub(r'Summary:\s*', '', text)
        text = re.sub(r'Context:\s*', '', text)
        text = re.sub(r'Reply Suggestions:\s*', '', text)
        
        text = text.strip()
        
        sentences = re.split(r'[.!?]+', text)
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                formatted_sentences.append(sentence)
        
        if len(formatted_sentences) > 1:
            return '.\n\n'.join(formatted_sentences) + '.'
        else:
            return text
    
    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

class LocalMockClient(LLMClient):
    def __init__(self):
        self.mock_responses = self._load_mock_responses()
    
    def _load_mock_responses(self) -> Dict[str, str]:
        return {
            "summarize": "Mock response for summarize",
            "context": "Mock response for context", 
            "replies": "Mock response for replies"
        }
    
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        start_time = time.time()
        
        await asyncio.sleep(0.1 + (temperature * 0.2))
        
        tweet_match = None
        if "Tweet:" in prompt:
            tweet_start = prompt.find("Tweet:") + 6
            tweet_end = prompt.find("\n", tweet_start)
            if tweet_end == -1:
                tweet_end = len(prompt)
            tweet_content = prompt[tweet_start:tweet_end].strip()
        else:
            tweet_content = "Sample tweet content"
        
        if "summarize" in prompt.lower():
            response_text = f"Summary of the tweet: {tweet_content[:100]}...\n\nThis tweet discusses important topics that are relevant to the audience.\n\nThe key points are clearly presented and easy to understand."
        elif "context" in prompt.lower():
            response_text = f"Context for the tweet: {tweet_content[:100]}...\n\nThis provides important background information about the topic.\n\nThe context helps readers understand the broader implications.\n\nAdditional insights are provided to enhance understanding."
        elif "reply" in prompt.lower():
            response_text = f"1. Great point about {tweet_content[:50]}...! I'd love to hear more about this.\n2. This is really interesting - what are your thoughts on the implications?\n3. Thanks for sharing this insight about {tweet_content[:30]}...!"
        else:
            response_text = f"Response to: {tweet_content[:100]}...\n\nThis is a generated response based on the input content.\n\nThe response addresses the key points mentioned in the tweet."
        
        processing_time = time.time() - start_time
        
        return {
            "text": response_text,
            "model": "mock-local",
            "provider": "local", 
            "processing_time": processing_time,
            "tokens_used": len(response_text.split()),
            "success": True
        }
    
    def is_available(self) -> bool:
        return True

class LLMClientFactory:
    @staticmethod
    def create_client() -> LLMClient:
        if settings.fireworks_api_key and len(settings.fireworks_api_key) > 10:
            try:
                client = DobbyClient()
                if client.is_available():
                    logger.info("Using Dobby LLM agent client")
                    return client
            except Exception as e:
                logger.warning("Dobby client not available, falling back to mock", error=str(e))
        
        logger.info("Using local mock client")
        return LocalMockClient()
    
    @staticmethod
    def create_dobby_client(api_key: str, model: str = None) -> DobbyClient:
        return DobbyClient(api_key, model)
    
    @staticmethod
    def create_mock_client() -> LocalMockClient:
        return LocalMockClient()

llm_client = LLMClientFactory.create_client()