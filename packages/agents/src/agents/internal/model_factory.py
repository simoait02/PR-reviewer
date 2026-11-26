from typing import Any

from agents.internal.config import ModelConfig
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from pr_logging.core import get_logger

logger = get_logger(__name__)


def build_chat_model(config: ModelConfig) -> BaseChatModel:
    """Build the configured chat model."""

    logger.debug(
        "Building chat model: provider='{}', model='{}', responses_api={}",
        config.provider,
        config.name,
        True,
    )

    model_options: dict[str, Any] = {
        "model": config.name,
        "model_provider": config.provider,
        "reasoning_effort": config.reasoning,
        "use_responses_api": True,
    }

    return init_chat_model(**model_options)
