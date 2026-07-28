"""Swagger UI configuration and HTML template for API documentation."""

import json
from flask import Response

from backend.docs.openapi_spec import SPEC


SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Development API - Swagger UI</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
        html {
            box-sizing: border-box;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin: 0;
            background: #fafafa;
        }
        .topbar {
            display: none;
        }
        .info-title {
            font-size: 1.5em;
        }
        .info-description {
            font-size: 1em;
        }
        .scheme-container {
            background: #f7f7f7;
            padding: 15px;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                spec: SPEC_DATA,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout",
                defaultModelsExpandDepth: -1,
                docExpansion: "list",
                filter: true,
                showExtensions: true,
                showCommonExtensions: true,
                tryItOutEnabled: true,
                requestSnippetsEnabled: true,
                tagsSorter: "alpha",
                operationsSorter: "alpha"
            });

            window.ui = ui;
        };
    </script>
</body>
</html>
""".strip()


def get_swagger_ui_html() -> str:
    """Generate Swagger UI HTML with embedded OpenAPI spec.

    Returns:
        HTML string with embedded spec data.
    """
    spec_json = json.dumps(SPEC)
    return SWAGGER_UI_HTML.replace("SPEC_DATA", spec_json)


def get_swagger_ui_response() -> Response:
    """Create Flask response for Swagger UI.

    Returns:
        Response object with HTML content type.
    """
    html = get_swagger_ui_html()
    return Response(html, mimetype="text/html")


def get_spec_json_response() -> Response:
    """Create Flask response for OpenAPI spec JSON.

    Returns:
        Response object with JSON content type.
    """
    return Response(
        json.dumps(SPEC, indent=2),
        mimetype="application/json"
    )
