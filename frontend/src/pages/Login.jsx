import { useState, useEffect } from "react";
import axios from "axios";
import { Sparkles } from "lucide-react";
import Logo from "../assets/CBZ-LOGOS-01.png";
import { handleApiResponse, handleApiError, showLoading, hideLoading } from "../utils/apiResponseHandler";

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (token) window.location.href = "/dashboard";
  }, []);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    showLoading("Logging in...");
    
    try {
      const response = await axios.post("http://localhost:5000/api/login", formData);
      
      // Handle standardized response
      const result = handleApiResponse(response, {
        showSuccessToast: false, // We'll handle success manually
        onSuccess: (responseData) => {
          // Store authentication data
          if (responseData.data?.access_token) {
            localStorage.setItem("accessToken", responseData.data.access_token);
          }
          
          // Store user info
          if (responseData.data?.role) {
            localStorage.setItem("userRole", responseData.data.role);
          }
          
          if (formData?.email && !localStorage.getItem("userEmail")) {
            localStorage.setItem("userEmail", formData.email);
          }
          
          // Extract user name from message
          const message = responseData.message || "";
          const extracted = (message.match(/Welcome back,\s*(.+)!/i) || [])[1];
          if (extracted) localStorage.setItem("userName", extracted);
          
          // Redirect based on role
          const redirectUrl = responseData.data?.role === "admin" ? "/admin" : "/dashboard";
          window.location.href = redirectUrl;
        }
      });
      
      if (result.success) {
        hideLoading();
        // Success is handled in onSuccess callback
      }
      
    } catch (error) {
      hideLoading();
      handleApiError(error, {
        errorTitle: "Login Failed"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left panel */}
        <div className="hidden md:block space-y-6">
          <div className="flex items-center gap-2 mb-8">
            <img src={Logo} alt="ClientSphere Logo" className="h-10 w-auto" />
            <h1 className="text-2xl font-bold text-blue-900">ClientSphere</h1>
          </div>
          <h2 className="text-4xl font-bold leading-tight text-blue-900">
            Welcome back to <span className="text-red-600">ClientSphere</span>
          </h2>
          <p className="text-gray-600">
            Continue managing client segments and driving personalized engagement.
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-6 text-center text-blue-900">Login</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
