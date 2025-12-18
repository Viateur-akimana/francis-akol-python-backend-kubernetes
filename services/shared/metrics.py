"""Prometheus metrics configuration for FastAPI."""

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info


def setup_metrics(app, service_name: str):
    """
    Configure Prometheus metrics for a FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for metric labels
    """
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/ready", "/metrics"],
        inprogress_name=f"{service_name}_inprogress",
        inprogress_labels=True,
    )
    
    # Add default metrics
    instrumentator.add(
        Info(
            name=f"{service_name}_info",
            description=f"Information about {service_name}",
        )
    )
    
    # Instrument the app
    instrumentator.instrument(app)
    
    # Expose metrics endpoint
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=True)
    
    return instrumentator
