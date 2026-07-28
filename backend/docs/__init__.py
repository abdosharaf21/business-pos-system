"""OpenAPI documentation package for the Business Development Web App."""

from backend.docs.openapi_spec import SPEC
from backend.docs.swagger_ui import get_swagger_ui_response, get_spec_json_response

__all__ = ["SPEC", "get_swagger_ui_response", "get_spec_json_response"]
