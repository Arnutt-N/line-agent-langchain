from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from .template_crud import get_message_templates, log_template_usage
from .models import MessageTemplate
from .schemas import TemplateSelectionRequest
import random
import re
import re

class TemplateSelector:
    """AI-powered template selector สำหรับเลือก template ที่เหมาะสม"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def select_template(
        self, 
        request: TemplateSelectionRequest,
        fallback_type: str = "text"
    ) -> Optional[MessageTemplate]:
        """เลือก template ที่เหมาะสมตาม context"""
        
        # 1. Filter by criteria
        templates = get_message_templates(
            self.db,
            category_id=None,  # TODO: Map category name to ID
            message_type=request.message_type,
            is_active=True,
            search=None
        )
        
        if not templates:
            # Fallback to any active template
            templates = get_message_templates(
                self.db,
                message_type=fallback_type,
                is_active=True
            )
        
        if not templates:
            return None
        
        # 2. Score templates based on context
        scored_templates = []
        for template in templates:
            score = self._calculate_score(template, request)
            scored_templates.append((template, score))
        
        # 3. Sort by score and select
        scored_templates.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Weighted random selection from top candidates
        top_templates = scored_templates[:min(3, len(scored_templates))]
        weights = [score for _, score in top_templates]
        
        if sum(weights) > 0:
            selected_template = self._weighted_random_choice(
                [template for template, _ in top_templates],
                weights
            )
        else:
            selected_template = random.choice([template for template, _ in scored_templates])
        
        return selected_template
    
    def _calculate_score(self, template: MessageTemplate, request: TemplateSelectionRequest) -> float:
        """คำนวณคะแนนความเหมาะสมของ template"""
        score = 0.0
        
        # Base priority score
        score += template.priority * 0.3
        
        # Usage frequency (popular templates get higher score)
        score += min(template.usage_count * 0.1, 5.0)
        
        # Tag matching
        if template.tags and request.tags:
            template_tags = set(tag.strip().lower() for tag in template.tags.split(","))
            request_tags = set(tag.lower() for tag in request.tags)
            tag_overlap = len(template_tags.intersection(request_tags))
            score += tag_overlap * 2.0
        
        # Context keyword matching
        if template.description:
            context_words = set(request.context.lower().split())
            description_words = set(template.description.lower().split())
            keyword_overlap = len(context_words.intersection(description_words))
            score += keyword_overlap * 0.5
        
        # Message content analysis
        if hasattr(template, 'content') and template.content:
            content_score = self._analyze_content_relevance(template.content, request)
            score += content_score
        
        return score
    
    def _analyze_content_relevance(self, content: Dict[str, Any], request: TemplateSelectionRequest) -> float:
        """วิเคราะห์ความเกี่ยวข้องของเนื้อหา template"""
        score = 0.0
        
        # Text content analysis
        if content.get("text"):
            text = content["text"].lower()
            user_message = request.user_message.lower()
            
            # Simple keyword matching
            user_words = set(user_message.split())
            template_words = set(text.split())
            word_overlap = len(user_words.intersection(template_words))
            score += word_overlap * 0.2
        
        return score
    
    def _weighted_random_choice(self, choices: List[Any], weights: List[float]) -> Any:
        """Weighted random selection"""
        if not choices or not weights:
            return random.choice(choices) if choices else None
        
        total = sum(weights)
        if total <= 0:
            return random.choice(choices)
        
        r = random.uniform(0, total)
        cumulative = 0
        for choice, weight in zip(choices, weights):
            cumulative += weight
            if r <= cumulative:
                return choice
        
        return choices[-1]  # Fallback
    
    def log_usage(self, template_id: int, line_user_id: str, context: str, success: bool = True):
        """บันทึกการใช้งาน template"""
        return log_template_usage(self.db, template_id, line_user_id, context, success)
