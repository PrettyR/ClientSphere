import axios from "axios";
import { handleApiResponse, handleApiError } from "./utils/apiResponseHandler";

// Use Vite's import.meta.env instead of process.env
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api",
});

// Add request interceptor for authentication
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for standardized error handling
API.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("userRole");
      localStorage.removeItem("userName");
      localStorage.removeItem("userEmail");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/**
 * Enhanced API call with standardized response handling
 * @param {Function} apiCall - Axios call function
 * @param {Object} options - Response handling options
 * @returns {Promise} - Promise that resolves with processed response
 */
export const apiCall = async (apiCall, options = {}) => {
  try {
    const response = await apiCall();
    return handleApiResponse(response, options);
  } catch (error) {
    return handleApiError(error, options);
  }
};

export default API;
