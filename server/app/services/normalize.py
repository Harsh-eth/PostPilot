"""
Text normalization and preprocessing utilities
"""

import re
import unicodedata
from typing import Optional
import langdetect
from langdetect import LangDetectException


class TextNormalizer:
    """Text normalization and preprocessing"""
    
    def __init__(self):
        self.max_length = 10000  # Maximum text length
        self.min_length = 10     # Minimum text length
    
    def normalize(self, text: str, strip_urls: bool = False, strip_mentions: bool = False) -> dict:
        """
        Normalize text with various preprocessing options
        
        Args:
            text: Input text to normalize
            strip_urls: Whether to remove URLs
            strip_mentions: Whether to remove @mentions
            
        Returns:
            dict: Normalized text and metadata
        """
        if not text or not isinstance(text, str):
            return {
                'text': '',
                'language': 'unknown',
                'word_count': 0,
                'char_count': 0,
                'normalized': False
            }
        
        # Start with original text
        normalized = text
        
        # Strip URLs if requested
        if strip_urls:
            normalized = self._strip_urls(normalized)
        
        # Strip mentions if requested
        if strip_mentions:
            normalized = self._strip_mentions(normalized)
        
        # Basic normalization
        normalized = self._basic_normalize(normalized)
        
        # Truncate if too long
        if len(normalized) > self.max_length:
            normalized = normalized[:self.max_length] + "..."
        
        # Detect language
        language = self._detect_language(normalized)
        
        # Calculate metrics
        word_count = len(normalized.split())
        char_count = len(normalized)
        
        return {
            'text': normalized,
            'language': language,
            'word_count': word_count,
            'char_count': char_count,
            'normalized': True,
            'original_length': len(text),
            'truncated': len(text) > self.max_length
        }
    
    def _basic_normalize(self, text: str) -> str:
        """Basic text normalization"""
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def _strip_urls(self, text: str) -> str:
        """Remove URLs from text"""
        # Common URL patterns
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        ]
        
        for pattern in url_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def _strip_mentions(self, text: str) -> str:
        """Remove @mentions from text"""
        # Remove @mentions
        text = re.sub(r'@\w+', '', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            if len(text.strip()) < 10:
                return 'unknown'
            
            # Use langdetect library
            detected = langdetect.detect(text)
            return detected if detected else 'unknown'
            
        except LangDetectException:
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def is_valid_text(self, text: str) -> bool:
        """Check if text is valid for processing"""
        if not text or not isinstance(text, str):
            return False
        
        normalized = self._basic_normalize(text)
        
        # Check minimum length
        if len(normalized) < self.min_length:
            return False
        
        # Check if text is mostly whitespace
        if len(normalized.strip()) < self.min_length:
            return False
        
        return True
    
    def extract_hashtags(self, text: str) -> list:
        """Extract hashtags from text"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> list:
        """Extract @mentions from text"""
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        return [mention.lower() for mention in mentions]
    
    def extract_urls(self, text: str) -> list:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls


# Global normalizer instance
normalizer = TextNormalizer()
