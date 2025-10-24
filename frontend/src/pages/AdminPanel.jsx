import { useEffect, useState } from "react";
import API from "../api";

function getToken(){
  return localStorage.getItem("accessToken");
}

export default function AdminPanel(){
  const [users, setUsers] = useState([]);
  const [pending, setPending] = useState([]);
  const [editingUser, setEditingUser] = useState(null);
  const [editForm, setEditForm] = useState({ employee_id: "", email: "", role: "" });
  const [activityLogs, setActivityLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState("users");
  useEffect(()=>{ load(); },[]);
  async function load(){
    try {
      const headers = { headers: { Authorization: `Bearer ${getToken()}` } };
      const [allRes, pendingRes, logsRes, statsRes] = await Promise.all([
        API.get("/users/", headers),
        API.get("/users/pending", headers),
        API.get("/activity/logs", headers),
        API.get("/activity/stats", headers)
      ]);
      
      // Handle standardized responses - data is in response.data.data
      setUsers(allRes.data.data || allRes.data);
      setPending(pendingRes.data.data || pendingRes.data);
      setActivityLogs(logsRes.data.data || logsRes.data);
      setStats(statsRes.data.data || statsRes.data);
    } catch (error) {
      console.error("Error loading admin data:", error);
      // Set empty arrays on error to prevent crashes
      setUsers([]);
      setPending([]);
      setActivityLogs([]);
      setStats({});
    }
  }
  async function assign(userId, role){
    try {
      await API.post("/users/assign-role", { user_id: userId, role }, { headers: { Authorization: `Bearer ${getToken()}` }});
      load();
    } catch (error) {
      console.error("Error assigning role:", error);
      alert("Failed to assign role. Please try again.");
    }
  }
  async function approve(userId){
    try {
      await API.post("/users/approve", { user_id: userId }, { headers: { Authorization: `Bearer ${getToken()}` }});
      load();
    } catch (error) {
      console.error("Error approving user:", error);
      alert("Failed to approve user. Please try again.");
    }
  }
  async function deleteUser(userId){
    if (!confirm("Are you sure you want to delete this user?")) return;
    try {
      await API.delete(`/users/delete/${userId}`, { headers: { Authorization: `Bearer ${getToken()}` }});
      load();
    } catch (error) {
      console.error("Error deleting user:", error);
      alert("Failed to delete user. Please try again.");
    }
  }
  function startEdit(u){
    setEditingUser(u.id);
    setEditForm({ employee_id: u.employee_id, email: u.email, role: u.role });
  }
  async function saveEdit(){
    await API.post("/users/assign-role", { user_id: editingUser, role: editForm.role }, { headers: { Authorization: `Bearer ${getToken()}` }});
    setEditingUser(null);
    load();
  }
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-blue-900 mb-4">Admin — User Management & Activity Tracking</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b">
        <button className={`px-4 py-2 ${activeTab === "users" ? "border-b-2 border-blue-900 text-blue-900" : "text-gray-600"}`} onClick={() => setActiveTab("users")}>Users</button>
        <button className={`px-4 py-2 ${activeTab === "activity" ? "border-b-2 border-blue-900 text-blue-900" : "text-gray-600"}`} onClick={() => setActiveTab("activity")}>Activity Logs</button>
        <button className={`px-4 py-2 ${activeTab === "stats" ? "border-b-2 border-blue-900 text-blue-900" : "text-gray-600"}`} onClick={() => setActiveTab("stats")}>Statistics</button>
      </div>

      {activeTab === "users" && (
        <>
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-red-600 mb-2">Pending Approvals</h3>
        <table className="min-w-full text-sm bg-white rounded shadow">
          <thead>
            <tr className="text-left border-b">
              <th className="p-2">Employee ID</th>
              <th className="p-2">Email</th>
              <th className="p-2">Role</th>
              <th className="p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {pending.map(u => (
              <tr key={u.id} className="border-b">
                <td className="p-2">{u.employee_id}</td>
                <td className="p-2">{u.email}</td>
                <td className="p-2">{u.role}</td>
                <td className="p-2"><button className="px-3 py-1 rounded bg-blue-900 text-white" onClick={()=>approve(u.id)}>Approve</button></td>
              </tr>
            ))}
            {pending.length === 0 && (
              <tr><td className="p-2" colSpan={4}>No pending requests</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-blue-900 mb-2">All Users</h3>
        <table className="min-w-full text-sm bg-white rounded shadow">
          <thead>
            <tr className="text-left border-b">
              <th className="p-2">Employee ID</th>
              <th className="p-2">Email</th>
              <th className="p-2">Role</th>
              <th className="p-2">Approved</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-b">
                {editingUser === u.id ? (
                  <>
                    <td className="p-2"><input className="border px-2 py-1 w-full" value={editForm.employee_id} onChange={(e)=>setEditForm({...editForm, employee_id: e.target.value})} /></td>
                    <td className="p-2"><input className="border px-2 py-1 w-full" value={editForm.email} onChange={(e)=>setEditForm({...editForm, email: e.target.value})} /></td>
                    <td className="p-2">
                      <select className="border px-2 py-1 w-full" value={editForm.role} onChange={(e)=>setEditForm({...editForm, role: e.target.value})}>
                        <option value="employee">Employee</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td className="p-2">{u.approved ? "Yes" : "No"}</td>
                    <td className="p-2">
                      <button className="px-2 py-1 mr-2 rounded bg-green-600 text-white" onClick={saveEdit}>Save</button>
                      <button className="px-2 py-1 rounded bg-gray-100" onClick={()=>setEditingUser(null)}>Cancel</button>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="p-2">{u.employee_id}</td>
                    <td className="p-2">{u.email}</td>
                    <td className="p-2">{u.role}</td>
                    <td className="p-2">{u.approved ? "Yes" : "No"}</td>
                    <td className="p-2">
                      <button className="px-2 py-1 mr-2 rounded bg-blue-900 text-white" onClick={()=>startEdit(u)}>Edit</button>
                      <button className="px-2 py-1 rounded bg-red-600 text-white" onClick={()=>deleteUser(u.id)}>Delete</button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
        </>
      )}

      {activeTab === "activity" && (
        <div>
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Recent Activity Logs</h3>
          <table className="min-w-full text-sm bg-white rounded shadow">
            <thead>
              <tr className="text-left border-b">
                <th className="p-2">User</th>
                <th className="p-2">Action</th>
                <th className="p-2">Resource</th>
                <th className="p-2">IP Address</th>
                <th className="p-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {activityLogs.map(l => (
                <tr key={l.id} className="border-b">
                  <td className="p-2">{l.user_email || "Anonymous"}</td>
                  <td className="p-2">{l.action}</td>
                  <td className="p-2">{l.resource || "-"}</td>
                  <td className="p-2">{l.ip_address || "-"}</td>
                  <td className="p-2">{l.created_at ? new Date(l.created_at).toLocaleString() : "-"}</td>
                </tr>
              ))}
              {activityLogs.length === 0 && (
                <tr><td className="p-2" colSpan={5}>No activity logs</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "stats" && stats && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded shadow p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Overall Statistics</h3>
            <div className="space-y-2">
              <p><strong>Total Logs:</strong> {stats.total_logs}</p>
              <p><strong>Unique Users:</strong> {stats.unique_users}</p>
            </div>
          </div>
          <div className="bg-white rounded shadow p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Most Active Users</h3>
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="p-2">Email</th>
                  <th className="p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_users.map((u, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{u.email}</td>
                    <td className="p-2">{u.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="bg-white rounded shadow p-4 md:col-span-2">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Most Accessed Resources</h3>
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="p-2">Resource</th>
                  <th className="p-2">Access Count</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_resources.map((r, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{r.resource}</td>
                    <td className="p-2">{r.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
