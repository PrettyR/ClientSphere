import { Routes, Route } from "react-router-dom";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Segments from "./pages/Segments";
import Data from "./pages/Data";
import DashboardLayout from "./layouts/DashboardLayout";
import Home from "./pages/Home";
import AdminPanel from "./pages/AdminPanel";


function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Dashboard and nested pages */}
      <Route
        path="/admin"
        element={
          <DashboardLayout>
            <AdminPanel />
          </DashboardLayout>
        }
      />

      <Route
        path="/dashboard"
        element={
          <DashboardLayout>
            <Dashboard />
          </DashboardLayout>
        }
      />
      <Route
        path="/segments"
        element={
          <DashboardLayout>
            <Segments />
          </DashboardLayout>
        }
      />
      <Route
        path="/data"
        element={
          <DashboardLayout>
            <Data />
          </DashboardLayout>
        }
      />

      {/* catch-all */}
      <Route path="*" element={<Home />} />
    </Routes>
  );
}

export default App;
