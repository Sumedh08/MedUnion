from collections import defaultdict
from typing import Callable, Any
from core.logging import logger


class ImportEvents:
    IMPORT_STARTED = "import.started"
    IMPORT_COMPLETED = "import.completed"
    IMPORT_FAILED = "import.failed"
    BATCH_STARTED = "batch.started"
    BATCH_COMPLETED = "batch.completed"
    BATCH_FAILED = "batch.failed"


class EventBus:
    _handlers: dict[str, list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event: str, handler: Callable):
        if handler not in cls._handlers[event]:
            cls._handlers[event].append(handler)
            logger.debug(f"Subscribed {handler.__name__} to {event}")

    @classmethod
    def unsubscribe(cls, event: str, handler: Callable):
        cls._handlers[event] = [h for h in cls._handlers[event] if h != handler]

    @classmethod
    def publish(cls, event: str, **data):
        logger.debug(f"Event: {event}")
        for handler in cls._handlers.get(event, []):
            try:
                handler(**data)
            except Exception as e:
                logger.error(f"Event handler {handler.__name__} failed for {event}: {e}")

    @classmethod
    def clear(cls):
        cls._handlers.clear()
