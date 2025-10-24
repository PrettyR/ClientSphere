/**
 * API Response Handler for ClientSphere Frontend
 * 
 * This utility handles standardized API responses from the backend,
 * providing consistent error handling and user feedback.
 */

import Swal from 'sweetalert2';

/**
 * Standardized API response structure from backend
 * @typedef {Object} ApiResponse
 * @property {boolean} success - Whether the request was successful
 * @property {string} message - User-friendly message
 * @property {*} data - Response data payload
 * @property {number} status_code - HTTP status code
 * @property {string} [error_code] - Internal error code for debugging
 * @property {string} [user_action] - Suggested action for the user
 * @property {Object} [metadata] - Additional metadata
 */

/**
 * Handle API response and show appropriate user feedback
 * @param {Object} response - Axios response object
 * @param {Object} options - Configuration options
 * @returns {Object} - Processed response data
 */
export const handleApiResponse = (response, options = {}) => {
  const {
    showSuccessToast = true,
    showErrorToast = true,
    successTitle = 'Success',
    errorTitle = 'Error',
    onSuccess = null,
    onError = null,
    customSuccessMessage = null,
    customErrorMessage = null
  } = options;

  const responseData = response.data;

  // Handle successful responses
  if (responseData.success) {
    const message = customSuccessMessage || responseData.message || 'Operation completed successfully';
    
    if (showSuccessToast) {
      Swal.fire({
        icon: 'success',
        title: successTitle,
        text: message,
        timer: 3000,
        showConfirmButton: false
      });
    }

    if (onSuccess) {
      onSuccess(responseData);
    }

    return {
      success: true,
      data: responseData.data,
      message: responseData.message,
      metadata: responseData.metadata
    };
  }

  // Handle error responses
  const errorMessage = customErrorMessage || responseData.message || 'An error occurred';
  const userAction = responseData.user_action || 'Please try again';
  
  if (showErrorToast) {
    Swal.fire({
      icon: 'error',
      title: errorTitle,
      text: errorMessage,
      footer: userAction ? `<small>${userAction}</small>` : undefined,
      confirmButtonText: 'OK'
    });
  }

  if (onError) {
    onError(responseData);
  }

  return {
    success: false,
    error: responseData.message,
    errorCode: responseData.error_code,
    userAction: responseData.user_action
  };
};

/**
 * Handle API errors (network errors, etc.)
 * @param {Object} error - Axios error object
 * @param {Object} options - Configuration options
 */
export const handleApiError = (error, options = {}) => {
  const {
    showErrorToast = true,
    errorTitle = 'Error',
    customErrorMessage = null
  } = options;

  let errorMessage = 'An unexpected error occurred';
  let userAction = 'Please try again later';

  if (error.response) {
    // Server responded with error status
    const responseData = error.response.data;
    if (responseData && responseData.message) {
      errorMessage = responseData.message;
      userAction = responseData.user_action || 'Please try again';
    } else {
      errorMessage = `Server error (${error.response.status})`;
    }
  } else if (error.request) {
    // Network error
    errorMessage = 'Network error - please check your connection';
    userAction = 'Please check your internet connection and try again';
  } else {
    // Other error
    errorMessage = error.message || 'An unexpected error occurred';
  }

  if (showErrorToast) {
    Swal.fire({
      icon: 'error',
      title: errorTitle,
      text: customErrorMessage || errorMessage,
      footer: userAction ? `<small>${userAction}</small>` : undefined,
      confirmButtonText: 'OK'
    });
  }

  return {
    success: false,
    error: errorMessage,
    userAction: userAction
  };
};

/**
 * Enhanced axios wrapper with standardized response handling
 * @param {Function} apiCall - Axios call function
 * @param {Object} options - Response handling options
 * @returns {Promise} - Promise that resolves with processed response
 */
export const apiCallWithHandler = async (apiCall, options = {}) => {
  try {
    const response = await apiCall();
    return handleApiResponse(response, options);
  } catch (error) {
    return handleApiError(error, options);
  }
};

/**
 * Common error messages for different scenarios
 */
export const ErrorMessages = {
  NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
  SERVER_ERROR: 'Server error occurred. Please try again later.',
  AUTHENTICATION_ERROR: 'Authentication failed. Please log in again.',
  AUTHORIZATION_ERROR: 'You do not have permission to perform this action.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  NOT_FOUND_ERROR: 'The requested resource was not found.',
  FILE_UPLOAD_ERROR: 'File upload failed. Please try again.',
  DATA_PROCESSING_ERROR: 'Unable to process the data. Please check the file format.'
};

/**
 * Show loading state
 * @param {string} message - Loading message
 */
export const showLoading = (message = 'Loading...') => {
  Swal.fire({
    title: message,
    allowOutsideClick: false,
    allowEscapeKey: false,
    showConfirmButton: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });
};

/**
 * Hide loading state
 */
export const hideLoading = () => {
  Swal.close();
};

/**
 * Show confirmation dialog
 * @param {string} title - Dialog title
 * @param {string} text - Dialog text
 * @param {string} confirmButtonText - Confirm button text
 * @returns {Promise<boolean>} - User's choice
 */
export const showConfirmation = (title, text, confirmButtonText = 'Yes, proceed') => {
  return Swal.fire({
    title: title,
    text: text,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#6b7280',
    confirmButtonText: confirmButtonText,
    cancelButtonText: 'Cancel'
  }).then((result) => result.isConfirmed);
};

/**
 * Show success message
 * @param {string} title - Success title
 * @param {string} text - Success message
 * @param {Function} onConfirm - Callback when user confirms
 */
export const showSuccess = (title, text, onConfirm = null) => {
  Swal.fire({
    icon: 'success',
    title: title,
    text: text,
    confirmButtonText: 'OK'
  }).then(() => {
    if (onConfirm) onConfirm();
  });
};

/**
 * Show error message
 * @param {string} title - Error title
 * @param {string} text - Error message
 * @param {string} userAction - Suggested user action
 */
export const showError = (title, text, userAction = null) => {
  Swal.fire({
    icon: 'error',
    title: title,
    text: text,
    footer: userAction ? `<small>${userAction}</small>` : undefined,
    confirmButtonText: 'OK'
  });
};

/**
 * Handle form validation errors
 * @param {Object} errors - Validation errors object
 * @param {string} title - Error title
 */
export const handleValidationErrors = (errors, title = 'Validation Error') => {
  let errorText = 'Please correct the following errors:\n';
  
  if (typeof errors === 'object') {
    Object.entries(errors).forEach(([field, message]) => {
      errorText += `• ${field}: ${message}\n`;
    });
  } else {
    errorText = errors;
  }

  showError(title, errorText, 'Please check your input and try again');
};

/**
 * Extract user-friendly error message from API response
 * @param {Object} error - Axios error object
 * @returns {string} - User-friendly error message
 */
export const getErrorMessage = (error) => {
  if (error.response && error.response.data) {
    const responseData = error.response.data;
    return responseData.message || responseData.error || 'An error occurred';
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

/**
 * Check if response is successful
 * @param {Object} response - API response
 * @returns {boolean} - Whether response is successful
 */
export const isSuccessResponse = (response) => {
  return response && response.success === true;
};

/**
 * Check if response is an error
 * @param {Object} response - API response
 * @returns {boolean} - Whether response is an error
 */
export const isErrorResponse = (response) => {
  return response && response.success === false;
};
