import re
import random
from datetime import datetime
from typing import Optional
from agents.base import BaseAgent, orchestrator, AgentOrchestrator
from core.logging import logger


class CopilotAgent(BaseAgent):
    name = "copilot"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.intent_patterns = {
            r"(overloaded|overcrowded|busy|full|congested)": "capacity_query",
            r"(predict|forecast|will|expected)": "forecast_query",
            r"(why|reason|cause|explain)": "explanation_query",
            r"(shortage|stockout|low stock|running out)": "inventory_query",
            r"(outbreak|spike|surge|increase.*case)": "outbreak_query",
            r"(compare|vs|versus|better|worse)": "comparison_query",
            r"(recommend|suggest|should|action)": "recommendation_query",
        }

    def process(self, context: dict) -> dict:
        input_data = context.get("input", {})
        message = input_data.get("message", "")
        context_info = input_data.get("context", {})

        intent = self._detect_intent(message)
        entities = self._extract_entities(message)

        pipeline = self._build_pipeline(intent)
        if pipeline:
            pipeline_input = {
                "query": message,
                "intent": intent,
                "entity_type": entities.get("entity_type", "hospital"),
                "entity_id": entities.get("entity_id"),
                "horizon_days": 30,
            }
            orchestration_result = AgentOrchestrator.run_pipeline(pipeline, pipeline_input)
        else:
            orchestration_result = {"output": {}}

        answer = self._generate_response(intent, entities, orchestration_result)
        return {
            "answer": answer,
            "intent": intent,
            "entities": entities,
            "data_sources": ["synthetic_simulation"],
            "confidence": 0.85,
            "follow_up_questions": self._get_follow_ups(intent),
            "visualizations": self._get_visualizations(intent),
            "timestamp": datetime.now().isoformat(),
        }

    def _detect_intent(self, message: str) -> str:
        for pattern, intent in self.intent_patterns.items():
            if re.search(pattern, message.lower()):
                return intent
        return "general_query"

    def _extract_entities(self, message: str) -> dict:
        entities = {}
        known_hospitals = ["RGGGH", "Stanley", "CMC", "GH", "Medical College"]
        known_districts = ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Vellore"]
        for h in known_hospitals:
            if h.lower() in message.lower():
                entities["entity_type"] = "hospital"
                entities["entity_id"] = h
                break
        for d in known_districts:
            if d.lower() in message.lower():
                entities["entity_type"] = "district"
                entities["entity_id"] = d
                break
        return entities

    def _build_pipeline(self, intent: str) -> list:
        pipelines = {
            "capacity_query": ["data_retrieval", "analytics", "recommendation", "explainability"],
            "forecast_query": ["data_retrieval", "forecasting", "explainability"],
            "explanation_query": ["data_retrieval", "analytics", "explainability"],
            "inventory_query": ["data_retrieval", "analytics", "recommendation", "explainability"],
            "outbreak_query": ["data_retrieval", "analytics", "forecasting", "recommendation", "explainability"],
            "comparison_query": ["data_retrieval", "analytics", "explainability"],
            "recommendation_query": ["data_retrieval", "analytics", "forecasting", "recommendation", "explainability"],
            "general_query": ["data_retrieval", "analytics", "explainability"],
        }
        return pipelines.get(intent, ["data_retrieval", "analytics"])

    def _generate_response(self, intent: str, entities: dict, orchestration_result: dict) -> str:
        responses = {
            "capacity_query": "Based on current data, occupancy is at elevated levels. I recommend monitoring closely and considering staff reallocation.",
            "forecast_query": "Our predictive model indicates a moderate increase in demand over the next 30 days. I recommend proactive resource planning.",
            "explanation_query": "The primary driver is increased emergency admissions combined with stable discharge rates, creating a bottleneck.",
            "inventory_query": "Several essential medicines are below threshold levels. Immediate restocking is recommended for high-consumption items.",
            "outbreak_query": "Case counts show an upward trend. Enhanced surveillance and preventive measures are recommended for affected districts.",
            "comparison_query": "Facility A shows 15% higher efficiency metrics compared to Facility B, primarily due to better staff utilization.",
            "recommendation_query": "Based on my analysis, I recommend: (1) Redistribute staff to high-occupancy units, (2) Restock critical medicines, (3) Monitor emerging disease trends.",
            "general_query": "The system is operating normally. Key metrics are within acceptable ranges across all monitored entities.",
        }
        return responses.get(intent, responses["general_query"])

    def _get_follow_ups(self, intent: str) -> list:
        follow_ups = {
            "capacity_query": ["Which specific units are most affected?", "What is the projected occupancy for next week?"],
            "forecast_query": ["What is the confidence level?", "How does this compare to last month?"],
            "inventory_query": ["Which medicines are at critical levels?", "Which facilities need urgent restocking?"],
            "outbreak_query": ["Which districts are most affected?", "What containment measures are recommended?"],
            "general_query": ["Would you like a detailed report?", "Which area would you like to explore?"],
        }
        return follow_ups.get(intent, ["Would you like more details?", "Shall I generate a report?"])

    def _get_visualizations(self, intent: str) -> list:
        return [{"type": "line_chart", "title": "Trend", "data_source": "synthetic_simulation"}]


orchestrator.register(CopilotAgent())
