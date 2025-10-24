import { Link } from "react-router-dom";
import Logo from "../assets/CBZ-LOGOS-01.png";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50 flex items-center justify-center px-6">
      <div className="max-w-3xl w-full text-center">
        <div className="mb-6 flex justify-center">
          <img src={Logo} alt="ClientSphere Logo" className="h-14 w-auto" />
        </div>
        <h1 className="text-4xl font-extrabold text-blue-900 mb-3">Welcome to ClientSphere</h1>
        <p className="text-gray-700 mb-8">
          AI-Powered Client Segmentation and Analytics for modern banking teams. Explore insights, visualize clusters,
          and make data-driven decisions.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/login"
            className="px-5 py-3 rounded-lg bg-blue-900 text-white hover:bg-blue-800 w-full sm:w-auto text-center"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="px-5 py-3 rounded-lg border border-blue-900 text-blue-900 hover:bg-blue-50 w-full sm:w-auto text-center"
          >
            Register
          </Link>
        </div>
        <p className="text-xs text-gray-500 mt-8">
          Designed and developed by Pretty Raradza (R211618e), Midlands State University.
        </p>
      </div>
    </div>
  );
}


