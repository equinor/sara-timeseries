from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter as OTLPGrpcLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGrpcSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter as OTLPHttpLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHttpSpanExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from fastapi import FastAPI
from typing import Optional

from sara_timeseries.core.settings import settings

logger = logging.getLogger(__name__)


def setup_open_telemetry(app: Optional[FastAPI] = None) -> None:
    service_name = settings.OTEL_SERVICE_NAME
    endpoint = settings.OTEL_EXPORTER_OTLP_ENDPOINT
    protocol = settings.OTEL_EXPORTER_OTLP_PROTOCOL.lower()

    logger.info(
        f"Setting up open telemetry with endpoint {endpoint} and protocol {protocol}"
    )

    resource = Resource.create({"service.name": service_name})

    span_exporter: SpanExporter
    log_exporter: LogExporter

    if protocol == "http":
        base = endpoint.rstrip("/")
        span_exporter = OTLPHttpSpanExporter(endpoint=f"{base}/v1/traces")
        log_exporter = OTLPHttpLogExporter(endpoint=f"{base}/v1/logs")  # type: ignore
    elif protocol == "grpc":
        span_exporter = OTLPGrpcSpanExporter(
            endpoint=endpoint,
            insecure=True,  # insecure=True is ok for non-public traffic
        )
        log_exporter = OTLPGrpcLogExporter(
            endpoint=endpoint,
            insecure=True,
        )  # type: ignore
    else:
        raise ValueError(
            f"Unknown OTLP protocol: {protocol!r} (expected 'grpc' or 'http')"
        )

    # --- Traces ---
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)

    # --- Logs ---
    log_provider = LoggerProvider(resource=resource)
    log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    set_logger_provider(log_provider)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(
        LoggingHandler(level=logging.INFO, logger_provider=log_provider)
    )

    # --- Auto Instrumentation ---
    RequestsInstrumentor().instrument()
    if app:
        FastAPIInstrumentor.instrument_app(app)
    else:
        # Fallback if app not provided, though precise instrumentation is preferred
        FastAPIInstrumentor().instrument()
