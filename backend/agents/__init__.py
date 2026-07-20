from agents.base import AgentOrchestrator, orchestrator
from agents.retrieval_agent import DataRetrievalAgent
from agents.analytics_agent import AnalyticsAgent
from agents.forecasting_agent import ForecastingAgent
from agents.recommendation_agent import RecommendationAgent
from agents.explainability_agent import ExplainabilityAgent
from agents.copilot_agent import CopilotAgent


def init_agents():
    return orchestrator
