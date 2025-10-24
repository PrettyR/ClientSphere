import React, { useEffect, useState } from "react";
import axios from "axios";
import UploadCSV from "../components/UploadCSV";
import StatCard from "../components/StatCard";
import SkeletonCard from "../components/SkeletonCard";
import { Users, TrendingUp, Database } from "lucide-react";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [clients, setClients] = useState([]);
  const [showClientsModal, setShowClientsModal] = useState(false);
  const [showAvgBalanceModal, setShowAvgBalanceModal] = useState(false);
  const [avgTopClients, setAvgTopClients] = useState([]);
  const [avgBySegment, setAvgBySegment] = useState([]);
  const [showAssetsModal, setShowAssetsModal] = useState(false);
  const [assetsBySegment, setAssetsBySegment] = useState([]);
  const [assetsTopClients, setAssetsTopClients] = useState([]);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        if (!token) return (window.location.href = "/");
        const res = await axios.get("http://localhost:5000/api/dashboard/overview", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSummary(res.data);
      } catch (e) {
        console.error("Failed to load summary for Data page", e);
      } finally {
        setLoading(false);
      }
    };
    loadSummary();
  }, []);

  const fetchAllClients = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await axios.get("http://localhost:5000/api/clients/all", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rows = Array.isArray(res.data)
        ? res.data
        : (Array.isArray(res.data?.value) ? res.data.value : []);
      setClients(rows);
      setShowClientsModal(true);
    } catch (e) {
      console.error("Failed to fetch clients", e);
    }
  };

  const openAvgBalanceView = async () => {
    try {
      let rows = clients;
      if (!rows || rows.length === 0) {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get("http://localhost:5000/api/clients/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        rows = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.value) ? res.data.value : []);
        setClients(rows);
      }
      const sorted = [...rows].sort((a, b) => Number((b.balance ?? b.Account_Balance) || 0) - Number((a.balance ?? a.Account_Balance) || 0));
      setAvgTopClients(sorted.slice(0, 20));
      const bySeg = {};
      for (const r of rows) {
        const seg = (r.cluster_label ?? r.Cluster) ?? "Unknown";
        if (!bySeg[seg]) bySeg[seg] = { segment: seg, count: 0, total: 0 };
        bySeg[seg].count += 1;
        bySeg[seg].total += Number(r.balance ?? r.Account_Balance ?? 0);
      }
      const segArr = Object.values(bySeg).map((s) => ({ segment: s.segment, count: s.count, avg_balance: s.count ? s.total / s.count : 0 })).sort((a, b) => b.avg_balance - a.avg_balance);
      setAvgBySegment(segArr);
      setShowAvgBalanceModal(true);
    } catch (e) {
      console.error("Failed to build avg balance view", e);
    }
  };

  const openTotalAssetsView = async () => {
    try {
      let rows = clients;
      if (!rows || rows.length === 0) {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get("http://localhost:5000/api/clients/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        rows = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.value) ? res.data.value : []);
        setClients(rows);
      }
      const getAsset = (r) => Number((r.predicted_value ?? r.balance ?? r.Account_Balance) || 0);
      const top = [...rows].sort((a, b) => getAsset(b) - getAsset(a)).slice(0, 20);
      setAssetsTopClients(top);
      const bySeg = {};
      for (const r of rows) {
        const seg = (r.cluster_label ?? r.Cluster) ?? "Unknown";
        if (!bySeg[seg]) bySeg[seg] = { segment: seg, total_assets: 0, count: 0 };
        bySeg[seg].total_assets += getAsset(r);
        bySeg[seg].count += 1;
      }
      const segArr = Object.values(bySeg).sort((a, b) => b.total_assets - a.total_assets);
      setAssetsBySegment(segArr);
      setShowAssetsModal(true);
    } catch (e) {
      console.error("Failed to build assets view", e);
    }
  };

  const statCards = summary
    ? [
        {
          title: "Total Clients",
          value: summary.total_clients.toLocaleString(),
          icon: Users,
          color: "bg-red-600",
          description: "Banking clients analyzed",
          onClick: () => fetchAllClients(),
        },
        {
          title: "Avg Balance",
          value: `$${summary.avg_balance.toFixed(2)}`,
          icon: TrendingUp,
          color: "bg-red-600",
          description: "Average account balance",
          onClick: () => openAvgBalanceView(),
        },
        {
          title: "Total Assets",
          value: `$${summary.total_assets.toLocaleString()}`,
          icon: Database,
          color: "bg-blue-900",
          description: "Total asset value",
          onClick: () => openTotalAssetsView(),
        },
      ]
    : [];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-red-700">Data Workspace</h1>
        <p className="text-blue-900">Manage datasets and review key metrics.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {loading && [1,2,3].map((k) => <SkeletonCard key={k} />)}
        {!loading && summary && statCards.map((stat) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            Icon={stat.icon}
            color={stat.color}
            description={stat.description}
            onClick={stat.onClick}
          />
        ))}
      </div>

      <div className="rounded-xl bg-gradient-to-br from-white to-gray-50 p-4 shadow">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-blue-900">Upload & Refresh Data</h2>
          <button
            className="px-3 py-1 rounded bg-blue-900 text-white"
            onClick={() => window.location.reload()}
          >
            Refresh
          </button>
        </div>
        <UploadCSV />
      </div>

      {/* Clients Modal */}
      {showClientsModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-11/12 max-w-5xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-blue-900">All Clients</h3>
              <button
                className="px-3 py-1 rounded bg-red-600 text-white"
                onClick={() => setShowClientsModal(false)}
              >
                Close
              </button>
            </div>
            <div className="overflow-auto max-h-[70vh]">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="p-2">Client ID</th>
                    <th className="p-2">Age</th>
                    <th className="p-2">Balance</th>
                    <th className="p-2">Tx Count</th>
                    <th className="p-2">Cluster</th>
                  </tr>
                </thead>
                <tbody>
                  {(Array.isArray(clients) ? clients : []).map((c) => (
                    <tr key={c.id ?? c.client_id ?? c.CIFs} className="border-b">
                      <td className="p-2">{c.client_id ?? c.CIFs}</td>
                      <td className="p-2">{c.age ?? c.Age ?? "-"}</td>
                      <td className="p-2">{c.balance ?? c.Account_Balance}</td>
                      <td className="p-2">{c.tx_count ?? c.Transaction_Frequency ?? c.products_owned ?? "-"}</td>
                      <td className="p-2">{c.cluster_label ?? c.Cluster}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Avg Balance Modal */}
      {showAvgBalanceModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-11/12 max-w-5xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-blue-900">Average Balance Details</h3>
              <button
                className="px-3 py-1 rounded bg-red-600 text-white"
                onClick={() => setShowAvgBalanceModal(false)}
              >
                Close
              </button>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="overflow-auto max-h-[70vh]">
                <h4 className="font-semibold text-blue-900 mb-2">By Segment</h4>
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left border-b">
                      <th className="p-2">Segment</th>
                      <th className="p-2">Count</th>
                      <th className="p-2">Avg Balance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(avgBySegment || []).map((s) => (
                      <tr key={s.segment} className="border-b">
                        <td className="p-2">{s.segment}</td>
                        <td className="p-2">{s.count}</td>
                        <td className="p-2">${s.avg_balance.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="overflow-auto max-h-[70vh]">
                <h4 className="font-semibold text-blue-900 mb-2">Top 20 Clients by Balance</h4>
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left border-b">
                      <th className="p-2">Client ID</th>
                      <th className="p-2">Balance</th>
                      <th className="p-2">Segment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(avgTopClients || []).map((c) => (
                      <tr key={c.id ?? c.client_id} className="border-b">
                        <td className="p-2">{c.client_id ?? c.CIFs}</td>
                        <td className="p-2">{c.balance ?? c.Account_Balance}</td>
                        <td className="p-2">{c.cluster_label ?? c.Cluster}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Total Assets Modal */}
      {showAssetsModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-11/12 max-w-5xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-blue-900">Total Assets Breakdown</h3>
              <button
                className="px-3 py-1 rounded bg-red-600 text-white"
                onClick={() => setShowAssetsModal(false)}
              >
                Close
              </button>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="overflow-auto max-h-[70vh]">
                <h4 className="font-semibold text-blue-900 mb-2">By Segment</h4>
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left border-b">
                      <th className="p-2">Segment</th>
                      <th className="p-2">Clients</th>
                      <th className="p-2">Total Assets</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(assetsBySegment || []).map((s) => (
                      <tr key={s.segment} className="border-b">
                        <td className="p-2">{s.segment}</td>
                        <td className="p-2">{s.count}</td>
                        <td className="p-2">${s.total_assets.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="overflow-auto max-h-[70vh]">
                <h4 className="font-semibold text-blue-900 mb-2">Top 20 Clients by Assets</h4>
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left border-b">
                      <th className="p-2">Client ID</th>
                      <th className="p-2">Assets</th>
                      <th className="p-2">Segment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(assetsTopClients || []).map((c) => (
                      <tr key={c.id ?? c.client_id} className="border-b">
                        <td className="p-2">{c.client_id ?? c.CIFs}</td>
                        <td className="p-2">{(c.predicted_value ?? c.balance ?? c.Account_Balance)?.toLocaleString?.() ?? (c.predicted_value ?? c.balance ?? c.Account_Balance)}</td>
                        <td className="p-2">{c.cluster_label ?? c.Cluster}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
