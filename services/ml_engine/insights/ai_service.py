from typing import Protocol
from .schemas import InsightContext, InsightResponse

class AIAssistantService(Protocol):
    def generate_insights(self, context: InsightContext) -> InsightResponse:
        ...

class StubProvider:
    """
    A deterministic stub provider for testing and MVP without API keys.
    """
    def generate_insights(self, context: InsightContext) -> InsightResponse:
        target = context.dataset.target_column
        sensitive = context.dataset.sensitive_attribute
        
        # Simple rule-based mock insights
        summary = f"Analysis completed for target '{target}' using sensitive attribute '{sensitive}'."
        
        strengths = [
            "Model was successfully trained and evaluated.",
            "Global feature importance was computed."
        ]
        
        risks = []
        fairness_findings = []
        if any(m.get("metric_name") == "DisparateImpact" and m.get("metric_value", 1) < 0.8 for m in context.fairness.metrics):
            risks.append(f"Potential disparate impact detected for '{sensitive}'.")
            fairness_findings.append("Disparate impact ratio is below the 0.8 threshold (80% rule).")
        else:
            fairness_findings.append("No critical fairness violations detected by standard thresholds.")
            
        explainability_findings = []
        if context.explainability.top_features:
            top_feat = context.explainability.top_features[0].get("feature", "unknown")
            explainability_findings.append(f"The most important feature driving predictions is '{top_feat}'.")
            
        recommendations = [rec.get("recommendedAction", "Review results.") for rec in context.recommendations]
        if not recommendations:
            recommendations.append("Continue monitoring model performance.")
            
        follow_up_questions = [
            f"Why is {context.explainability.top_features[0].get('feature', 'this feature')} so important?",
            "What mitigation strategies can I apply?",
            "Can you explain Disparate Impact?"
        ] if context.explainability.top_features else ["What mitigation strategies can I apply?"]

        return InsightResponse(
            summary=summary,
            strengths=strengths,
            risks=risks,
            fairness_findings=fairness_findings,
            explainability_findings=explainability_findings,
            recommendations=recommendations,
            follow_up_questions=follow_up_questions
        )

class OpenAIProvider:
    def generate_insights(self, context: InsightContext) -> InsightResponse:
        raise NotImplementedError("OpenAI integration pending")

class GeminiProvider:
    def generate_insights(self, context: InsightContext) -> InsightResponse:
        raise NotImplementedError("Gemini integration pending")

class FallbackAIProvider:
    """Wraps the primary provider and falls back to StubProvider on error."""
    def __init__(self, primary_provider: AIAssistantService):
        self.primary = primary_provider
        self.fallback = StubProvider()
        
    def generate_insights(self, context: InsightContext) -> InsightResponse:
        try:
            return self.primary.generate_insights(context)
        except Exception as e:
            # Log error and gracefully degrade
            import structlog
            logger = structlog.get_logger(__name__)
            logger.error("ai_provider_failed", error=str(e), fallback="StubProvider")
            return self.fallback.generate_insights(context)

def get_ai_service() -> AIAssistantService:
    from apps.api.core.config import settings
    provider_name = settings.AI_PROVIDER.lower()
    
    if provider_name == "openai":
        primary = OpenAIProvider()
    elif provider_name == "gemini":
        primary = GeminiProvider()
    else:
        primary = StubProvider()
        
    return FallbackAIProvider(primary)
