from agents.internal.config import ModelConfig
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

_RESPONSES_API_MODELS = frozenset({"gpt-5.6-luna"})


def build_chat_model(config: ModelConfig) -> BaseChatModel:
    """Build the configured chat model."""

    if config.provider != "openai":
        raise ValueError(f"Unsupported model provider: {config.provider}")

    return ChatOpenAI(
        model=config.name,
        temperature=config.temperature,
        reasoning_effort=config.reasoning,
        use_responses_api=(
            config.use_responses_api or config.name in _RESPONSES_API_MODELS
        ),
    )
