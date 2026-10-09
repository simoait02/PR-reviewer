import os

from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pr_logging.core import get_logger

_configured = False
logger = get_logger(__name__)


def configure_tracing() -> None:
    global _configured

    if _configured:
        logger.debug("Phoenix tracing is already configured")
        return

    if os.getenv("PHOENIX_ENABLED", "true").lower() != "true":
        logger.debug("Phoenix tracing is disabled")
        return

    try:
        phoenix_host = os.getenv("PHOENIX_HOST", "http://localhost:6006").rstrip("/")
        endpoint = f"{phoenix_host}/v1/traces"
        api_key = os.getenv("PHOENIX_API_KEY", "")
        project_name = os.getenv("PHOENIX_PROJECT_NAME", "pr-reviewer")
        headers = {"authorization": f"Bearer {api_key}"} if api_key else None

        tracer_provider = trace_sdk.TracerProvider(
            resource=Resource.create(
                {
                    "service.name": "pr-reviewer-api",
                    "openinference.project.name": project_name,
                }
            )
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=endpoint,
                    headers=headers,
                )
            )
        )
        trace_api.set_tracer_provider(tracer_provider)
        LangChainInstrumentor().instrument()
        _configured = True

        logger.info(
            "Phoenix tracing configured: endpoint='{}' project='{}' authenticated={}",
            endpoint,
            project_name,
            bool(api_key),
        )
    except Exception:  # noqa: BLE001 - tracing must not stop API startup
        logger.opt(exception=True).warning("Phoenix tracing setup failed")
