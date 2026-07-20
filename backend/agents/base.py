from abc import ABC, abstractmethod
from typing import Optional
from core.logging import logger


class BaseAgent(ABC):
    name: str = "base_agent"

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    @abstractmethod
    def process(self, input_data: dict) -> dict:
        pass


class AgentOrchestrator:
    _agents: dict = {}

    @classmethod
    def register(cls, agent: BaseAgent):
        cls._agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name}")

    @classmethod
    def get(cls, name: str) -> Optional[BaseAgent]:
        return cls._agents.get(name)

    @classmethod
    def run_pipeline(cls, pipeline: list[str], input_data: dict) -> dict:
        context = {"input": input_data, "intermediate": {}}
        for agent_name in pipeline:
            agent = cls.get(agent_name)
            if not agent:
                logger.warning(f"Agent not found: {agent_name}")
                continue
            logger.info(f"Running agent: {agent_name}")
            result = agent.process(context)
            context["intermediate"][agent_name] = result
        context["output"] = context["intermediate"].get(pipeline[-1], {})
        return context


orchestrator = AgentOrchestrator()
