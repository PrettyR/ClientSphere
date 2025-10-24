"""
Standardized Response Templates for ClientSphere API

This module provides consistent response formatting across the entire application,
ensuring users receive clear, actionable feedback instead of technical error messages.
"""

from flask import jsonify
from typing import Any, Dict, Optional, Union
import traceback
import logging

# Configure logging for error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseTemplate:
    """Standardized response template for all API endpoints."""
    
    @staticmethod
    def success(
        message: str = "Operation completed successfully",
        data: Optional[Union[Dict, list, Any]] = None,
        status_code: int = 200,
        metadata: Optional[Dict] = None
    ) -> tuple:
        """
        Create a standardized success response.
        
        Args:
            message: User-friendly success message
            data: Response data payload
            status_code: HTTP status code
            metadata: Additional metadata (pagination, timestamps, etc.)
        """
        response = {
            "success": True,
            "message": message,
            "status_code": status_code
        }
        
        if data is not None:
            response["data"] = data
            
        if metadata:
            response["metadata"] = metadata
            
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        error_code: str = "GENERIC_ERROR",
        status_code: int = 500,
        details: Optional[Dict] = None,
        user_action: Optional[str] = None
    ) -> tuple:
        """
        Create a standardized error response.
        
        Args:
            message: User-friendly error message
            error_code: Internal error code for debugging
            status_code: HTTP status code
            details: Additional error details (not shown to user)
            user_action: Suggested action for the user
        """
        response = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "status_code": status_code
        }
        
        if user_action:
            response["user_action"] = user_action
            
        # Log error details for debugging (not sent to client)
        if details:
            logger.error(f"Error {error_code}: {details}")
            
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        errors: Optional[Dict] = None,
        user_action: str = "Please check your input and try again"
    ) -> tuple:
        """Create a validation error response."""
        return ResponseTemplate.error(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=errors,
            user_action=user_action
        )
    
    @staticmethod
    def authentication_error(
        message: str = "Authentication required",
        user_action: str = "Please log in to continue"
    ) -> tuple:
        """Create an authentication error response."""
        return ResponseTemplate.error(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            user_action=user_action
        )
    
    @staticmethod
    def authorization_error(
        message: str = "Access denied",
        user_action: str = "Contact your administrator for access"
    ) -> tuple:
        """Create an authorization error response."""
        return ResponseTemplate.error(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            user_action=user_action
        )
    
    @staticmethod
    def not_found_error(
        message: str = "Resource not found",
        user_action: str = "Please check the resource ID and try again"
    ) -> tuple:
        """Create a not found error response."""
        return ResponseTemplate.error(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=404,
            user_action=user_action
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        error_code: str = "SERVER_ERROR",
        details: Optional[Dict] = None
    ) -> tuple:
        """Create a server error response."""
        return ResponseTemplate.error(
            message=message,
            error_code=error_code,
            status_code=500,
            details=details,
            user_action="Please try again later or contact support if the problem persists"
        )


class ErrorHandler:
    """Centralized error handling for common scenarios."""
    
    # User-friendly error messages
    ERROR_MESSAGES = {
        # Database errors
        "database_connection": "Unable to connect to the database. Please try again later.",
        "database_query": "Database operation failed. Please try again.",
        "data_integrity": "The data provided conflicts with existing records.",
        
        # Authentication errors
        "invalid_credentials": "Invalid email or password. Please check your credentials.",
        "account_pending": "Your account is pending approval. Please contact your administrator.",
        "email_not_verified": "Please verify your email address before logging in.",
        "session_expired": "Your session has expired. Please log in again.",
        
        # Authorization errors
        "insufficient_permissions": "You don't have permission to perform this action.",
        "admin_required": "This action requires administrator privileges.",
        
        # File upload errors
        "file_too_large": "File is too large. Please choose a smaller file.",
        "invalid_file_type": "Invalid file type. Please upload a CSV file.",
        "file_processing": "Unable to process the uploaded file. Please check the format.",
        
        # Data processing errors
        "data_processing": "Unable to process the data. Please check the file format.",
        "missing_columns": "Required columns are missing from the uploaded file.",
        "invalid_data_format": "Data format is invalid. Please check your file.",
        
        # ML/Analysis errors
        "model_not_found": "Analysis model not found. Please upload data first.",
        "insufficient_data": "Insufficient data for analysis. Please upload more data.",
        "analysis_failed": "Analysis failed. Please try again with different data.",
        
        # Network/External service errors
        "external_service": "External service is temporarily unavailable.",
        "network_error": "Network error occurred. Please check your connection.",
    }
    
    @classmethod
    def get_user_friendly_message(cls, error_type: str, custom_message: str = None) -> str:
        """Get user-friendly error message for common error types."""
        if custom_message:
            return custom_message
        return cls.ERROR_MESSAGES.get(error_type, "An unexpected error occurred. Please try again.")
    
    @classmethod
    def handle_exception(cls, exception: Exception, context: str = None) -> tuple:
        """Handle unexpected exceptions with user-friendly messages."""
        error_details = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "context": context,
            "traceback": traceback.format_exc()
        }
        
        # Log the full error for debugging
        logger.error(f"Unexpected error in {context}: {error_details}")
        
        # Return user-friendly response
        return ResponseTemplate.server_error(
            message="An unexpected error occurred. Our team has been notified.",
            error_code="UNEXPECTED_ERROR",
            details=error_details
        )


class ValidationHelper:
    """Helper functions for data validation with user-friendly error messages."""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: list) -> Optional[tuple]:
        """Validate that all required fields are present."""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return ResponseTemplate.validation_error(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                errors={"missing_fields": missing_fields},
                user_action="Please provide all required information"
            )
        return None
    
    @staticmethod
    def validate_email(email: str) -> Optional[tuple]:
        """Validate email format."""
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return ResponseTemplate.validation_error(
                message="Invalid email format",
                errors={"email": "Please enter a valid email address"},
                user_action="Please check your email address format"
            )
        return None
    
    @staticmethod
    def validate_password_strength(password: str) -> Optional[tuple]:
        """Validate password strength."""
        if len(password) < 8:
            return ResponseTemplate.validation_error(
                message="Password must be at least 8 characters long",
                user_action="Please choose a stronger password"
            )
        return None
    
    @staticmethod
    def validate_file_upload(file, allowed_extensions: list = ['.csv'], max_size_mb: int = 10) -> Optional[tuple]:
        """Validate file upload."""
        if not file:
            return ResponseTemplate.validation_error(
                message="No file provided",
                user_action="Please select a file to upload"
            )
        
        # Check file extension
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return ResponseTemplate.validation_error(
                message=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
                user_action="Please upload a supported file type"
            )
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return ResponseTemplate.validation_error(
                message=f"File too large. Maximum size: {max_size_mb}MB",
                user_action="Please choose a smaller file"
            )
        
        return None


# Convenience functions for common responses
def success_response(message: str = "Success", data: Any = None, **kwargs) -> tuple:
    """Quick success response."""
    return ResponseTemplate.success(message=message, data=data, **kwargs)

def error_response(message: str = "Error occurred", status_code: int = 500, **kwargs) -> tuple:
    """Quick error response."""
    return ResponseTemplate.error(message=message, status_code=status_code, **kwargs)

def validation_error_response(message: str = "Validation failed", errors: Dict = None) -> tuple:
    """Quick validation error response."""
    return ResponseTemplate.validation_error(message=message, errors=errors)

def not_found_response(message: str = "Resource not found") -> tuple:
    """Quick not found response."""
    return ResponseTemplate.not_found_error(message=message)
