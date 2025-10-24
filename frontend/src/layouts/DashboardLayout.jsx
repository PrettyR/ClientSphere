import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Users, Table, BarChart3, LogOut, UserCircle, Home as HomeIcon, Shield } from "lucide-react";
import Logo from "../assets/CBZ-LOGOS-01.png";

const DashboardLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const isActive = (path) => {
    const current = location.pathname;
    const active = path === "/" ? current === "/" : current.startsWith(path);
    return active ? "text-red-600" : "text-blue-900 hover:text-red-600";
  };

  const handleSignOut = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("userName");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userEmail");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-30 bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          {/* Brand */}
          <Link to="/dashboard" className="flex items-center gap-2">
            <img src={Logo} alt="ClientSphere Logo" className="h-10 w-auto" />
            <span className="text-xl font-bold text-blue-900">ClientSphere</span>
          </Link>

          {/* Nav */}
          <nav className="hidden md:flex items-center gap-6">
            <Link to="/" className={`flex items-center gap-1 ${isActive("/")}`}>
              <HomeIcon className="h-5 w-5" />
              <span>Home</span>
            </Link>
            <Link to="/dashboard" className={`flex items-center gap-1 ${isActive("/dashboard")}`}>
              <BarChart3 className="h-5 w-5" />
              <span>Dashboard</span>
            </Link>
            <Link to="/segments" className={`flex items-center gap-1 ${isActive("/segments")}`}>
              <Users className="h-5 w-5" />
              <span>Segments</span>
            </Link>
            <Link to="/data" className={`flex items-center gap-1 ${isActive("/data")}`}>
              <Table className="h-5 w-5" />
              <span>Data</span>
            </Link>
            <Link to="/admin" className={`flex items-center gap-1 ${isActive("/admin")}`}>
              <Shield className="h-5 w-5" />
              <span>Admin</span>
            </Link>
          </nav>

          {/* User */}
          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2">
              <UserCircle className="h-6 w-6 text-blue-900" />
              <div>
                <p className="text-sm font-medium text-blue-900">{localStorage.getItem("userName") || "User"}</p>
                <p className="text-xs text-red-600">{localStorage.getItem("userRole") || "Employee"}</p>
              </div>
            </div>
            <button onClick={handleSignOut} className="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700">
              <span className="inline-flex items-center gap-1"><LogOut className="h-4 w-4" /> Sign Out</span>
            </button>
          </div>

          {/* Mobile menu button */}
          <button className="md:hidden px-3 py-2 rounded border text-blue-900" onClick={() => setMenuOpen(!menuOpen)}>
            Menu
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t">
            <nav className="px-4 py-2 flex flex-col gap-2">
              <Link to="/" onClick={() => setMenuOpen(false)} className={`flex items-center gap-2 ${isActive("/")}`}>
                <HomeIcon className="h-5 w-5" /> Home
              </Link>
              <Link to="/dashboard" onClick={() => setMenuOpen(false)} className={`flex items-center gap-2 ${isActive("/dashboard")}`}>
                <BarChart3 className="h-5 w-5" /> Dashboard
              </Link>
              <Link to="/segments" onClick={() => setMenuOpen(false)} className={`flex items-center gap-2 ${isActive("/segments")}`}>
                <Users className="h-5 w-5" /> Segments
              </Link>
              <Link to="/data" onClick={() => setMenuOpen(false)} className={`flex items-center gap-2 ${isActive("/data")}`}>
                <Table className="h-5 w-5" /> Data
              </Link>
              <Link to="/admin" onClick={() => setMenuOpen(false)} className={`flex items-center gap-2 ${isActive("/admin")}`}>
                <Shield className="h-5 w-5" /> Admin
              </Link>
              <button onClick={handleSignOut} className="mt-2 text-left px-2 py-2 rounded bg-red-600 text-white">
                <span className="inline-flex items-center gap-2"><LogOut className="h-4 w-4" /> Sign Out</span>
              </button>
            </nav>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto p-6 overflow-auto">{children}</div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 py-6 text-sm text-blue-900">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
            <p>
              ClientSphere — AI-Powered Client Segmentation and Analytics Platform.
              Provides insights, clustering visualizations, and data-driven tools for financial institutions.
            </p>
            <p className="text-red-700 font-medium">
              Designed and developed by Pretty Raradza (R211618e), Midlands State University.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default DashboardLayout;
