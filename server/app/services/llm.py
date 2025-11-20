from __future__ import annotations

import random
from typing import List

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
except ImportError:
    genai = None
    google_exceptions = None

from ..config import get_settings
from ..models import DocType


settings = get_settings()


class LLMService:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = None
        self.use_api = False
        if self.api_key and genai:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.use_api = True
            except Exception:
                self.use_api = False

    def _call_model(self, prompt: str) -> str:
        if self.model and self.use_api:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass
        return self._generate_fallback_content(prompt)

    def _generate_fallback_content(self, prompt: str) -> str:
        topic_keywords = self._extract_topic_keywords(prompt)
        section_type = self._detect_section_type(prompt)
        
        paragraphs = []
        
        if "overview" in prompt.lower() or "introduction" in prompt.lower():
            paragraphs.append(
                f"This comprehensive analysis provides an in-depth examination of {topic_keywords}. "
                f"The current market landscape presents both significant opportunities and notable challenges "
                f"that require careful strategic consideration. Understanding the fundamental dynamics at play "
                f"is essential for making informed decisions and developing effective approaches."
            )
            paragraphs.append(
                f"Recent developments in this sector have reshaped traditional expectations and created "
                f"new pathways for growth and innovation. Key factors driving change include technological "
                f"advancements, evolving consumer preferences, regulatory shifts, and competitive pressures. "
                f"These elements combine to form a complex ecosystem that demands nuanced understanding."
            )
            paragraphs.append(
                f"Stakeholders across the industry are increasingly recognizing the importance of "
                f"data-driven insights and evidence-based strategies. Organizations that successfully "
                f"navigate this environment will be those that can adapt quickly, leverage emerging "
                f"opportunities, and mitigate potential risks through proactive planning."
            )
        
        elif "insight" in prompt.lower() or "analysis" in prompt.lower():
            paragraphs.append(
                f"Critical insights reveal several important patterns and trends within {topic_keywords}. "
                f"Analysis of current data indicates that organizations are experiencing both unprecedented "
                f"opportunities and complex challenges. The most successful approaches combine strategic "
                f"vision with practical implementation capabilities."
            )
            paragraphs.append(
                f"Market research suggests that key success factors include understanding customer needs, "
                f"maintaining competitive advantages, and building sustainable operational models. "
                f"Companies that invest in innovation and adapt to changing conditions tend to outperform "
                f"those that maintain rigid, traditional approaches."
            )
            paragraphs.append(
                f"Emerging trends point toward increased emphasis on digital transformation, "
                f"sustainability initiatives, and customer-centric strategies. These developments "
                f"require organizations to rethink their business models and operational frameworks. "
                f"Early adopters of these approaches are positioning themselves for long-term success."
            )
        
        elif "next step" in prompt.lower() or "recommendation" in prompt.lower() or "action" in prompt.lower():
            paragraphs.append(
                f"Based on comprehensive analysis of {topic_keywords}, several strategic next steps "
                f"emerge as priorities for forward-looking organizations. These recommendations are "
                f"designed to address current challenges while positioning for future growth and success."
            )
            paragraphs.append(
                f"Immediate actions should focus on establishing clear objectives, allocating appropriate "
                f"resources, and building necessary capabilities. Short-term initiatives might include "
                f"pilot programs, stakeholder engagement, and process improvements that deliver "
                f"measurable results within defined timeframes."
            )
            paragraphs.append(
                f"Long-term strategic planning requires consideration of market evolution, competitive "
                f"dynamics, and emerging opportunities. Organizations should develop flexible roadmaps "
                f"that allow for adaptation as conditions change. Success will depend on consistent "
                f"execution, continuous monitoring, and willingness to adjust strategies based on "
                f"performance data and market feedback."
            )
        
        else:
            paragraphs.append(
                f"This section examines important aspects of {topic_keywords} that are critical for "
                f"understanding the broader context and implications. The subject matter encompasses "
                f"multiple dimensions that require careful analysis and thoughtful consideration."
            )
            paragraphs.append(
                f"Key considerations include the interplay between various factors, the impact of "
                f"external forces, and the potential outcomes of different strategic choices. "
                f"Organizations must balance competing priorities while maintaining focus on core "
                f"objectives and long-term sustainability."
            )
            paragraphs.append(
                f"Effective approaches typically involve comprehensive planning, stakeholder alignment, "
                f"and systematic implementation. Success requires not only sound strategy but also "
                f"strong execution capabilities and the ability to adapt to changing circumstances. "
                f"Organizations that master these elements are well-positioned to achieve their goals."
            )
        
        return " ".join(paragraphs)

    def _extract_topic_keywords(self, prompt: str) -> str:
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                       "of", "with", "by", "about", "section", "heading", "document", "write", 
                       "detailed", "concise", "business", "ready", "focus", "titled"}
        words = prompt.lower().split()
        keywords = [w for w in words if w not in common_words and len(w) > 3]
        if keywords:
            return " ".join(keywords[:5])
        return "the subject matter"

    def _detect_section_type(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "overview" in prompt_lower or "introduction" in prompt_lower:
            return "overview"
        elif "insight" in prompt_lower or "analysis" in prompt_lower:
            return "insights"
        elif "next step" in prompt_lower or "recommendation" in prompt_lower or "action" in prompt_lower:
            return "next_steps"
        return "general"

    def generate_outline(self, topic: str, doc_type: DocType, item_count: int) -> List[str]:
        if not self.use_api:
            default_templates = [
                "Overview",
                "Key Insights",
                "Analysis",
                "Recommendations",
                "Next Steps",
                "Conclusion",
                "Background",
                "Current State",
                "Future Outlook",
                "Implementation",
            ]
            titles = []
            for i in range(item_count):
                if i < len(default_templates):
                    titles.append(f"{default_templates[i]}: {topic}")
                else:
                    titles.append(f"{topic} - Section {i + 1}")
            return titles

        prompt = (
            f"Create {item_count} concise headings for a {doc_type.value.upper()} document "
            f"about {topic}. Provide only the headings separated by newline."
        )
        try:
            raw = self._call_model(prompt)
            if raw and len(raw) > 20:
                titles = [line.strip("- ").strip() for line in raw.splitlines() if line.strip() and len(line.strip()) > 3]
                if len(titles) >= item_count:
                    return titles[:item_count]
        except Exception:
            pass

        default_templates = [
            "Overview",
            "Key Insights",
            "Analysis",
            "Recommendations",
            "Next Steps",
            "Conclusion",
            "Background",
            "Current State",
            "Future Outlook",
            "Implementation",
        ]
        titles = []
        for i in range(item_count):
            if i < len(default_templates):
                titles.append(f"{default_templates[i]}: {topic}")
            else:
                titles.append(f"{topic} - Section {i + 1}")
        return titles

    def generate_section(self, topic: str, section_title: str) -> str:
        prompt = (
            f"Write a comprehensive, detailed business-ready section (at least 300 words) for the document titled "
            f"'{topic}'. Focus specifically on the section heading '{section_title}'. "
            f"Use professional tone, include relevant details, examples, and actionable insights. "
            f"Make the content substantial and informative."
        )
        return self._call_model(prompt)

    def refine_section(self, topic: str, section_title: str, current_text: str, refinement_prompt: str) -> str:
        prompt = (
            f"You are improving a section named '{section_title}' in a document about {topic}. "
            f"Current text:\n{current_text}\n\nApply this instruction: {refinement_prompt}. "
            "Return the updated section text only."
        )
        return self._call_model(prompt)


llm_service = LLMService()

