from agents.internal.config import ModelConfig
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from pr_logging.core import get_logger

_RESPONSES_API_MODELS = frozenset({"gpt-5.6-luna"})
logger = get_logger(__name__)


def build_chat_model(config: ModelConfig) -> BaseChatModel:
    """Build the configured chat model."""

    use_responses_api = (
        config.use_responses_api or config.name in _RESPONSES_API_MODELS
    )

    logger.debug(
        "Building chat model: provider='{}', model='{}', responses_api={}",
        config.provider,
        config.name,
        use_responses_api,
    )

    if config.provider != "openai":
        logger.error(
            "Unsupported chat model provider '{}'",
            config.provider,
        )
        raise ValueError(f"Unsupported model provider: {config.provider}")

    return ChatOpenAI(
        model=config.name,
        temperature=config.temperature,
        reasoning_effort=config.reasoning,
        use_responses_api=use_responses_api,
    )
