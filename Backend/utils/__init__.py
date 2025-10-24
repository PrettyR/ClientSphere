"""
Utilities package for ClientSphere API

This package contains utility modules for error handling, response formatting,
and other common functionality.
"""

from .response_templates import (
    ResponseTemplate,
    ErrorHandler,
    ValidationHelper,
    success_response,
    error_response,
    validation_error_response,
    not_found_response
)

from .error_middleware import (
    setup_error_handling,
    DatabaseErrorHandler,
    FileUploadErrorHandler
)

from .email_service import (
    EmailService,
    send_verification_code_email,
    send_welcome_email,
    send_account_approved_email
)

__all__ = [
    'ResponseTemplate',
    'ErrorHandler', 
    'ValidationHelper',
    'success_response',
    'error_response',
    'validation_error_response',
    'not_found_response',
    'setup_error_handling',
    'DatabaseErrorHandler',
    'FileUploadErrorHandler',
    'EmailService',
    'send_verification_code_email',
    'send_welcome_email',
    'send_account_approved_email'
]
