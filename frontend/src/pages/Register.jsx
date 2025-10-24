import { useState } from "react";
import axios from "axios";
import { Sparkles } from "lucide-react";
import Logo from "../assets/CBZ-LOGOS-01.png";
import { handleApiResponse, handleApiError, showLoading, hideLoading } from "../utils/apiResponseHandler";

const Register = () => {
  const [formData, setFormData] = useState({
    employee_id: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "employee",
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    showLoading("Submitting registration...");
    
    try {
      const response = await axios.post(
        "http://localhost:5000/api/register",
        formData
      );

      // Handle standardized response
      const result = handleApiResponse(response, {
        showSuccessToast: true,
        successTitle: "Registration Successful",
        onSuccess: () => {
          window.location.href = "/login";
        }
      });
      
    } catch (error) {
      hideLoading();
      handleApiError(error, {
        errorTitle: "Registration Failed"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left panel */}
        <div className="hidden md:block space-y-6">
          <div className="flex items-center gap-2 mb-8">
            <img src={Logo} alt="ClientSphere Logo" className="h-10 w-auto" />
            <h1 className="text-2xl font-bold text-blue-900">ClientSphere</h1>
          </div>
          <h2 className="text-4xl font-bold leading-tight text-blue-900">
            Transform client data into <span className="text-red-600">actionable insights</span>
          </h2>
          <p className="text-gray-600">
            Segment private banking clients with ML and drive personalized strategies.
          </p>
        </div>

        {/* Registration Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-6 text-center text-blue-900">Create Account</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              name="employee_id"
              placeholder="Employee ID Number"
              value={formData.employee_id}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
            />
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
            <input
              type="password"
              name="confirm_password"
              placeholder="Confirm Password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
            />
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
            >
              <option value="employee">Employee</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              {loading ? "Submitting..." : "Submit for Approval"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
