from typing import Dict, List
from enum import Enum

class Persona(Enum):
    HUMAN = "human"
    HARDCORE = "hardcore"
    CURSOR = "curator"

class PromptBuilder:
    def __init__(self):
        self.personas = self._load_personas()
        self.safety_guardrails = self._load_safety_guardrails()
    
    def _load_personas(self) -> Dict[str, Dict[str, str]]:
        return {
            "human": {
                "name": "Human",
                "description": "Friendly, conversational, relatable responses",
                "style": "conversational",
                "tone": "warm and friendly",
                "personality": "approachable, empathetic, genuine"
            },
            "hardcore": {
                "name": "Hardcore",
                "description": "Direct, no-nonsense, straight to the point",
                "style": "direct",
                "tone": "blunt and straightforward",
                "personality": "confident, direct, no fluff"
            },
            "curator": {
                "name": "Curator",
                "description": "Thoughtful, insightful, expert perspective",
                "style": "analytical",
                "tone": "intelligent and thoughtful",
                "personality": "wise, insightful, well-informed"
            }
        }
    
    def _load_safety_guardrails(self) -> List[str]:
        return [
            "Do not provide financial advice",
            "Do not provide medical advice",
            "Do not provide legal advice",
            "Do not echo or repeat personal information",
            "Do not generate harmful, offensive, or inappropriate content",
            "Do not impersonate specific individuals",
            "Be respectful and professional in all responses"
        ]
    
    def build_summarize_prompt(self, text: str, persona: str = "human", url: str = None, author: str = None) -> str:
        prompt = f"""Create a summary with EXACT formatting.

Tweet: {text}

FORMATTING RULES:
- Write 2-3 complete sentences
- Each sentence on its own line
- Blank line between sentences
- NO metadata, URLs, or author names
- NO labels or prefixes

EXAMPLE FORMAT:
This is the first sentence.

This is the second sentence.

This is the third sentence.

RESPONSE:"""

        if url:
            prompt += f"\n\nSource URL: {url}"
        
        if author:
            prompt += f"\n\nAuthor: {author}"
        
        return prompt
    
    def build_context_prompt(self, text: str, persona: str = "human", url: str = None, author: str = None) -> str:
        prompt = f"""Create context with EXACT formatting.

Tweet: {text}

FORMATTING RULES:
- Write 3-4 complete sentences
- Each sentence on its own line
- Blank line between sentences
- NO metadata, URLs, or author names
- NO labels or prefixes

EXAMPLE FORMAT:
This is the first sentence.

This is the second sentence.

This is the third sentence.

RESPONSE:"""

        if url:
            prompt += f"\n\nSource URL: {url}"
        
        if author:
            prompt += f"\n\nAuthor: {author}"
        
        return prompt
    
    def build_replies_prompt(self, text: str, persona: str = "human", style: str = "conversational", url: str = None, author: str = None) -> str:
        persona_config = self.personas.get(persona, self.personas["human"])
        
        prompt = f"""Generate 3 replies with EXACT formatting.

Tweet: {text}

Persona: {persona_config['name']} - {persona_config['description']}
Tone: {persona_config['tone']}
Style: {persona_config['style']}

FORMATTING RULES:
- Generate exactly 3 replies
- Each reply on its own line
- Blank line between replies
- NO metadata, URLs, or author names
- NO labels or prefixes

EXAMPLE FORMAT:
1. First reply here.

2. Second reply here.

3. Third reply here.

RESPONSE:"""

        if url:
            prompt += f"\n\nSource URL: {url}"
        
        if author:
            prompt += f"\n\nAuthor: {author}"
        
        return prompt
    
    def get_persona_info(self, persona: str) -> Dict[str, str]:
        return self.personas.get(persona, self.personas["human"])
    
    def list_personas(self) -> List[Dict[str, str]]:
        return [
            {
                "key": key,
                "name": config["name"],
                "description": config["description"]
            }
            for key, config in self.personas.items()
        ]
    
    def validate_persona(self, persona: str) -> bool:
        return persona in self.personas
    
    def get_safety_guardrails(self) -> List[str]:
        return self.safety_guardrails.copy()

prompt_builder = PromptBuilder()