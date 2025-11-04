"""
Swagger/OpenAPI configuration for API documentation
"""

from flasgger import Swagger

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs/"
}

# OpenAPI template
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "LittleBeliever Quran Analysis API",
        "description": "Comprehensive API for Quran learning with AI-powered recitation analysis, Tajweed guidance, user management, and progress tracking",
        "version": "2.0.0",
        "contact": {
            "name": "API Support",
            "url": "https://github.com/OmarBoshnak/quran-analysis-backend"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
        },
        "ApiKey": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
            "description": "API Key for basic endpoint access"
        }
    },
    "tags": [
        {
            "name": "Analysis",
            "description": "Quran recitation analysis endpoints"
        },
        {
            "name": "Quran Data",
            "description": "Endpoints for accessing Quran metadata"
        },
        {
            "name": "Audio & Reciters",
            "description": "Audio recitation and reciter information"
        },
        {
            "name": "Authentication",
            "description": "User authentication and token management"
        },
        {
            "name": "User Profile",
            "description": "User profile and preferences management"
        },
        {
            "name": "Progress Tracking",
            "description": "Track user reading and memorization progress"
        },
        {
            "name": "Bookmarks",
            "description": "Bookmark management for verses"
        },
        {
            "name": "Health & Monitoring",
            "description": "System health and status checks"
        }
    ]
}


def init_swagger(app):
    """
    Initialize Swagger documentation for FastAPI app
    
    Note: Flasgger is designed for Flask, not FastAPI.
    For FastAPI, use the built-in OpenAPI documentation at /docs and /redoc
    
    This function is a placeholder for future custom documentation needs.
    """
    # FastAPI has built-in OpenAPI support
    # The /docs endpoint provides interactive Swagger UI
    # The /redoc endpoint provides ReDoc documentation
    pass
