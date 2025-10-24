"""
Error Handling Middleware for ClientSphere API

This module provides centralized error handling and logging for the Flask application.
"""

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import traceback
import logging
from typing import Dict, Any
from .response_templates import ResponseTemplate, ErrorHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_error_handlers(app: Flask) -> None:
    """Register error handlers with the Flask application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return ResponseTemplate.validation_error(
            message="Invalid request data",
            user_action="Please check your input and try again"
        )
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return ResponseTemplate.authentication_error(
            message="Authentication required",
            user_action="Please log in to continue"
        )
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return ResponseTemplate.authorization_error(
            message="Access denied",
            user_action="Contact your administrator for access"
        )
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return ResponseTemplate.not_found_error(
            message="The requested resource was not found",
            user_action="Please check the URL and try again"
        )
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return ResponseTemplate.error(
            message="Method not allowed",
            error_code="METHOD_NOT_ALLOWED",
            status_code=405,
            user_action="Please use the correct HTTP method"
        )
    
    @app.errorhandler(413)
    def payload_too_large(error):
        """Handle 413 Payload Too Large errors."""
        return ResponseTemplate.error(
            message="File too large",
            error_code="FILE_TOO_LARGE",
            status_code=413,
            user_action="Please choose a smaller file"
        )
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        return ResponseTemplate.validation_error(
            message="Unable to process the request",
            user_action="Please check your data and try again"
        )
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests errors."""
        return ResponseTemplate.error(
            message="Too many requests",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            user_action="Please wait a moment before trying again"
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        return ResponseTemplate.server_error(
            message="Internal server error",
            user_action="Please try again later or contact support if the problem persists"
        )
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway errors."""
        return ResponseTemplate.error(
            message="Service temporarily unavailable",
            error_code="BAD_GATEWAY",
            status_code=502,
            user_action="Please try again later"
        )
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        return ResponseTemplate.error(
            message="Service temporarily unavailable",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            user_action="Please try again later"
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle generic HTTP exceptions."""
        return ResponseTemplate.error(
            message=error.description or "HTTP error occurred",
            error_code=f"HTTP_{error.code}",
            status_code=error.code,
            user_action="Please try again"
        )
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other exceptions."""
        return ErrorHandler.handle_exception(error, f"Request to {request.endpoint}")


class RequestLogger:
    """Middleware for logging requests and responses."""
    
    @staticmethod
    def log_request():
        """Log incoming requests."""
        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    @staticmethod
    def log_response(response):
        """Log outgoing responses."""
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response


def setup_error_handling(app: Flask) -> None:
    """Set up comprehensive error handling for the Flask application."""
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add request/response logging
    app.before_request(RequestLogger.log_request)
    app.after_request(RequestLogger.log_response)
    
    # CORS is already handled by flask-cors in app.py
    # No need for additional CORS headers here


class DatabaseErrorHandler:
    """Specialized error handler for database-related errors."""
    
    @staticmethod
    def handle_database_error(exception: Exception, operation: str = "database operation") -> tuple:
        """Handle database-specific errors with user-friendly messages."""
        error_type = type(exception).__name__
        
        if "IntegrityError" in error_type:
            return ResponseTemplate.error(
                message="Data conflict detected",
                error_code="DATA_INTEGRITY_ERROR",
                status_code=409,
                user_action="The data you're trying to save conflicts with existing records. Please check for duplicates."
            )
        elif "OperationalError" in error_type:
            return ResponseTemplate.error(
                message="Database connection issue",
                error_code="DATABASE_CONNECTION_ERROR",
                status_code=503,
                user_action="Please try again in a few moments"
            )
        elif "ProgrammingError" in error_type:
            return ResponseTemplate.error(
                message="Database query error",
                error_code="DATABASE_QUERY_ERROR",
                status_code=500,
                user_action="Please contact support if this problem persists"
            )
        else:
            return ResponseTemplate.server_error(
                message="Database operation failed",
                error_code="DATABASE_ERROR",
                details={"operation": operation, "error_type": error_type}
            )


class FileUploadErrorHandler:
    """Specialized error handler for file upload errors."""
    
    @staticmethod
    def handle_upload_error(exception: Exception, filename: str = None) -> tuple:
        """Handle file upload errors with user-friendly messages."""
        error_type = type(exception).__name__
        
        if "FileNotFoundError" in error_type:
            return ResponseTemplate.error(
                message="File not found",
                error_code="FILE_NOT_FOUND",
                status_code=404,
                user_action="Please select a file to upload"
            )
        elif "PermissionError" in error_type:
            return ResponseTemplate.error(
                message="File access denied",
                error_code="FILE_PERMISSION_ERROR",
                status_code=403,
                user_action="Please check file permissions and try again"
            )
        elif "UnicodeDecodeError" in error_type:
            return ResponseTemplate.error(
                message="File encoding error",
                error_code="FILE_ENCODING_ERROR",
                status_code=400,
                user_action="Please save the file as UTF-8 encoded CSV and try again"
            )
        else:
            return ResponseTemplate.error(
                message="File upload failed",
                error_code="FILE_UPLOAD_ERROR",
                status_code=500,
                user_action="Please try uploading the file again"
            )
