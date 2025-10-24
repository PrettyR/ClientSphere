import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart3, Users, TrendingUp, Database } from "lucide-react";
import Logo from "../assets/CBZ-LOGOS-01.png";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from "recharts";

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState({
    balance_by_cluster: [],
    avg_balance_by_cluster: [],
    tx_distribution: [],
    cluster_counts: [],
    scatter_points: [],
  });
  const [clients, setClients] = useState([]);
  const [showClientsModal, setShowClientsModal] = useState(false);
  const [showSegmentsModal, setShowSegmentsModal] = useState(false);
  const [segmentsData, setSegmentsData] = useState([]);
  const [clientsFilterSegment, setClientsFilterSegment] = useState(null);
  const [showAvgBalanceModal, setShowAvgBalanceModal] = useState(false);
  const [avgTopClients, setAvgTopClients] = useState([]);
  const [avgBySegment, setAvgBySegment] = useState([]);
  const [showAssetsModal, setShowAssetsModal] = useState(false);
  const [assetsBySegment, setAssetsBySegment] = useState([]);
  const [assetsTopClients, setAssetsTopClients] = useState([]);
  const [activeView, setActiveView] = useState(null); // "segments" | "avg_balance" | null
  const [loading, setLoading] = useState(true);
  const [chartsLoading, setChartsLoading] = useState(false);
  const [chartsError, setChartsError] = useState("");
  const [clientsCache, setClientsCache] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) return (window.location.href = "/");


      const summaryRes = await axios.get("http://localhost:5000/api/dashboard/overview", {
        headers: { Authorization: `Bearer ${token}` },
      });

      setSummary(summaryRes.data);
      // Load dynamic chart-ready datasets
      setChartsLoading(true);
      setChartsError("");
      try {
        const chartsRes = await axios.get("http://localhost:5000/api/charts/summary");
        const data = chartsRes.data;
        const isEmpty = !data || [
          data.balance_by_cluster?.length,
          data.avg_balance_by_cluster?.length,
          data.tx_distribution?.length,
          data.cluster_counts?.length,
        ].every((v) => !v);

        if (isEmpty) {
          const derived = await deriveChartsFromClients();
          setCharts(derived);
        } else {
          setCharts(data);
        }
      } catch (ce) {
        setChartsError("Failed to load charts");
        const derived = await deriveChartsFromClients();
        setCharts(derived);
      } finally {
        setChartsLoading(false);
      }

      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setLoading(false);
    }
  };

  const regenerateAndReloadCharts = async () => {
    try {
      setChartsLoading(true);
      setChartsError("");
      await axios.get("http://localhost:5000/api/charts/regenerate");
      const chartsRes = await axios.get("http://localhost:5000/api/charts/summary");
      setCharts(chartsRes.data);
    } catch (e) {
      console.error("Failed to regenerate charts", e);
      setChartsError("Failed to regenerate charts");
    } finally {
      setChartsLoading(false);
    }
  };

  const deriveChartsFromClients = async () => {
    try {
      // reuse cached rows if available
      let rows = clientsCache;
      if (!rows || rows.length === 0) {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get("http://localhost:5000/api/clients/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const raw = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.value) ? res.data.value : []);
        const normalizeRow = (r) => ({
          id: r.id ?? r.CIFs ?? r.client_id,
          client_id: r.client_id ?? r.CIFs,
          balance: Number(r.balance ?? r.Account_Balance ?? 0),
          tx_count: Number(r.tx_count ?? r.Transaction_Frequency ?? 0),
          risk_score: Number(r.risk_score ?? 0),
          cluster_label: r.cluster_label ?? r.Cluster ?? "Unknown",
        });
        rows = raw.map(normalizeRow);
        setClientsCache(rows);
      }

      const group = {};
      for (const r of rows) {
        const k = r.cluster_label ?? "Unknown";
        if (!group[k]) group[k] = { sum: 0, count: 0 };
        group[k].sum += Number(r.balance || 0);
        group[k].count += 1;
      }
      const balance_by_cluster = Object.entries(group).map(([cluster, g]) => ({ cluster, total_balance: g.sum }));
      const avg_balance_by_cluster = Object.entries(group).map(([cluster, g]) => ({ cluster, avg_balance: g.count ? g.sum / g.count : 0 }));

      // tx_distribution buckets
      const series = rows.map((r) => Number(r.tx_count ?? 0));
      const bins = [0, 1, 2, 3, 5, 10, 20, 50, 100, Math.max(100, ...series)];
      const labels = ["0", "1", "2", "3-5", "6-10", "11-20", "21-50", "51-100", ">100"];
      const counts = new Array(labels.length).fill(0);
      for (const v of series) {
        const i = v <= 0 ? 0 : v <= 1 ? 1 : v <= 2 ? 2 : v <= 5 ? 3 : v <= 10 ? 4 : v <= 20 ? 5 : v <= 50 ? 6 : v <= 100 ? 7 : 8;
        counts[i] += 1;
      }
      const tx_distribution = labels.map((label, i) => ({ tx_bucket: label, count: counts[i] }));

      const cluster_counts_map = {};
      for (const r of rows) {
        const k = r.cluster_label ?? "Unknown";
        cluster_counts_map[k] = (cluster_counts_map[k] || 0) + 1;
      }
      const cluster_counts = Object.entries(cluster_counts_map).map(([cluster, count]) => ({ cluster, count }));

      const scatter_points = rows.slice(0, 1000).map((r) => ({ balance: r.balance, risk_score: r.risk_score, cluster: r.cluster_label }));

      return { balance_by_cluster, avg_balance_by_cluster, tx_distribution, age_boxplot: [], cluster_counts, scatter_points };
    } catch (e) {
      console.error("Failed deriving charts from clients", e);
      return { balance_by_cluster: [], avg_balance_by_cluster: [], tx_distribution: [], age_boxplot: [], cluster_counts: [], scatter_points: [] };
    }
  };

  const fetchAllClients = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await axios.get("http://localhost:5000/api/clients/all", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rawRows = Array.isArray(res.data)
        ? res.data
        : (Array.isArray(res.data?.value) ? res.data.value : []);

      // Normalize incoming rows to expected keys regardless of CSV header casing
      const normalizeRow = (r) => {
        if (!r || typeof r !== "object") return r;
        // Detect new schema headers from processed_clients.csv
        const hasNewHeaders =
          r.CIFs !== undefined ||
          r.Account_Balance !== undefined ||
          r.Transaction_Frequency !== undefined ||
          r.Cluster !== undefined;

        if (!hasNewHeaders) return r;

        return {
          // Preserve any existing id/client_id for keys
          id: r.id ?? r.CIFs,
          client_id: r.client_id ?? r.CIFs,
          age: r.age ?? r.Age,
          balance: r.balance ?? r.Account_Balance,
          tx_count: r.tx_count ?? r.Transaction_Frequency,
          cluster_label: r.cluster_label ?? r.Cluster,
          // Pass through other fields for metadata consumers
          ...r,
        };
      };

      const rows = rawRows.map(normalizeRow);
      setClients(rows);
      setShowClientsModal(true);
      setClientsFilterSegment(null);
    } catch (e) {
      console.error("Failed to fetch clients", e);
    }
  };

  const openSegmentsView = async () => {
    try {
      // Ensure we have clients; reuse existing if already loaded
      let rows = clients;
      if (!rows || rows.length === 0) {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get("http://localhost:5000/api/clients/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const rawRows = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.value) ? res.data.value : []);
        const normalizeRow = (r) => ({
          id: r.id ?? r.CIFs ?? r.client_id,
          client_id: r.client_id ?? r.CIFs,
          age: r.age ?? r.Age,
          balance: r.balance ?? r.Account_Balance,
          tx_count: r.tx_count ?? r.Transaction_Frequency,
          cluster_label: r.cluster_label ?? r.Cluster,
          ...r,
        });
        rows = rawRows.map(normalizeRow);
        setClients(rows);
      }

      // Group by cluster_label and compute counts and avg balance
      const bySegment = {};
      for (const r of rows) {
        const seg = (r.cluster_label ?? r.Cluster) ?? "Unknown";
        if (!bySegment[seg]) bySegment[seg] = { segment: seg, count: 0, totalBalance: 0 };
        bySegment[seg].count += 1;
        bySegment[seg].totalBalance += Number((r.balance ?? r.Account_Balance) || 0);
      }
      const segmentsArr = Object.values(bySegment).map((s) => ({
        segment: s.segment,
        count: s.count,
        avg_balance: s.count > 0 ? s.totalBalance / s.count : 0,
      }));
      setSegmentsData(segmentsArr);
      setShowSegmentsModal(true);
      setActiveView("segments");
    } catch (e) {
      console.error("Failed to build segments view", e);
    }
  };

  const openAvgBalanceView = async () => {
    try {
      // Ensure we have client rows
      let rows = clients;
      if (!rows || rows.length === 0) {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get("http://localhost:5000/api/clients/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const rawRows = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.value) ? res.data.value : []);
        const normalizeRow = (r) => ({
          id: r.id ?? r.CIFs ?? r.client_id,
          client_id: r.client_id ?? r.CIFs,
          age: r.age ?? r.Age,
          balance: r.balance ?? r.Account_Balance,
          tx_count: r.tx_count ?? r.Transaction_Frequency,
          cluster_label: r.cluster_label ?? r.Cluster,
          ...r,
        });
        rows = rawRows.map(normalizeRow);
        setClients(rows);
      }

      // Top 20 clients by balance
      const sorted = [...rows].sort((a, b) => Number(b.balance || 0) - Number(a.balance || 0));
      setAvgTopClients(sorted.slice(0, 20));

      // Average by segment
      const bySeg = {};
      for (const r of rows) {
        const seg = r.cluster_label ?? "Unknown";
        if (!bySeg[seg]) bySeg[seg] = { segment: seg, count: 0, total: 0 };
        bySeg[seg].count += 1;
        bySeg[seg].total += Number(r.balance || 0);
      }
      const segArr = Object.values(bySeg).map((s) => ({
        segment: s.segment,
        count: s.count,
        avg_balance: s.count ? s.total / s.count : 0,
      })).sort((a, b) => b.avg_balance - a.avg_balance);
      setAvgBySegment(segArr);

      setShowAvgBalanceModal(true);
      setActiveView("avg_balance");
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
        const rawRows = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.value) ? res.data.value : []);
        const normalizeRow = (r) => ({
          id: r.id ?? r.CIFs ?? r.client_id,
          client_id: r.client_id ?? r.CIFs,
          age: r.age ?? r.Age,
          balance: r.balance ?? r.Account_Balance,
          tx_count: r.tx_count ?? r.Transaction_Frequency,
          cluster_label: r.cluster_label ?? r.Cluster,
          predicted_value: r.predicted_value,
          ...r,
        });
        rows = rawRows.map(normalizeRow);
        setClients(rows);
      }

      // Choose asset metric: prefer predicted_value if available, else balance
      const getAsset = (r) => Number((r.predicted_value ?? r.balance ?? r.Account_Balance) || 0);

      // Top 20 by asset value
      const top = [...rows].sort((a, b) => getAsset(b) - getAsset(a)).slice(0, 20);
      setAssetsTopClients(top);

      // Sum by segment
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

  if (loading) return <div className="flex justify-center items-center h-64">Loading dashboard...</div>;

  if (!summary) return <div className="text-center text-red-600">Failed to load dashboard data.</div>;

  const statCards = [
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
  ];

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      {/* Intro Section */}
      <div className="mb-8 text-center">
        <div className="flex justify-center mb-2"><img src={Logo} alt="ClientSphere Logo" className="h-10 w-auto" /></div>
        <h1 className="text-3xl font-bold text-red-700 mb-2">ClientSphere Dashboard</h1>
        <h2 className="text-xl font-semibold text-blue-900 mb-4">
          AI-Powered Client Segmentation Analytics
        </h2>
        <p className="text-gray-700 text-lg">
          Explore insights from K-Means, DBSCAN, and PCA clustering with real financial data.
        </p>
        <div className="mt-4  flex items-center justify-center gap-3">
          <button className="px-3 py-1 rounded bg-blue-900 text-white" onClick={fetchDashboardData}>Reload Data</button>
          <button className="px-3 py-1 rounded bg-red-600 text-white" onClick={regenerateAndReloadCharts} disabled={chartsLoading}>
            {chartsLoading ? "Refreshing Charts..." : "Refresh Charts"}
          </button>
        </div>
        {chartsError && (
          <div className="mt-2 text-sm text-red-600">{chartsError}</div>
        )}
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.title}
              className="p-4 rounded-lg shadow bg-white flex flex-col justify-between cursor-pointer hover:shadow-md"
              onClick={stat.onClick}
            >
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-sm font-medium text-blue-900">{stat.title}</h2>
                <div className={`p-2 rounded-full ${stat.color} text-white`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <div className="text-2xl font-bold text-red-600">{stat.value}</div>
              <p className="text-sm text-gray-600 mt-1">{stat.description}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Section (Dynamic) */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Total Balance by Segment</h3>
          <div className="w-full h-80">
            {chartsLoading ? (
              <div className="h-full flex items-center justify-center text-gray-500">Loading…</div>
            ) : (charts.balance_by_cluster?.length ? (
              <ResponsiveContainer>
                <BarChart data={charts.balance_by_cluster}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="cluster" label={{ value: "Segment", position: "insideBottom", offset: -5 }} />
                  <YAxis label={{ value: "Total Balance", angle: -90, position: "insideLeft" }} />
                  <Tooltip />
                  <Bar dataKey="total_balance" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">No data</div>
            ))}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Average Balance by Segment</h3>
          <div className="w-full h-80">
            {chartsLoading ? (
              <div className="h-full flex items-center justify-center text-gray-500">Loading…</div>
            ) : (charts.avg_balance_by_cluster?.length ? (
              <ResponsiveContainer>
                <BarChart data={charts.avg_balance_by_cluster}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="cluster" label={{ value: "Segment", position: "insideBottom", offset: -5 }} />
                  <YAxis label={{ value: "Average Balance", angle: -90, position: "insideLeft" }} />
                  <Tooltip />
                  <Bar dataKey="avg_balance" fill="#1e3a8a" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">No data</div>
            ))}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 md:col-span-2">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Transaction Count Distribution</h3>
          <div className="w-full h-80">
            {chartsLoading ? (
              <div className="h-full flex items-center justify-center text-gray-500">Loading…</div>
            ) : (charts.tx_distribution?.length ? (
              <ResponsiveContainer>
                <BarChart data={charts.tx_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="tx_bucket" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">No data</div>
            ))}
          </div>
        </div>

        {/* Segment Pie Chart */}
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Segment Distribution</h3>
          <div className="w-full h-80">
            {chartsLoading ? (
              <div className="h-full flex items-center justify-center text-gray-500">Loading…</div>
            ) : (charts.cluster_counts?.length ? (
              <ResponsiveContainer>
                <PieChart>
                  <Tooltip />
                  <Pie data={charts.cluster_counts} dataKey="count" nameKey="cluster" outerRadius={120}>
                    {(charts.cluster_counts || []).map((entry, idx) => (
                      <Cell key={entry.cluster} fill={["#ef4444", "#1e3a8a", "#10b981", "#f59e0b"][idx % 4]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">No data</div>
            ))}
          </div>
        </div>

        {/* Interactive Scatter (Balance vs Predicted Value) */}
        <div className="bg-white shadow rounded-lg p-4 md:col-span-2">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Balance vs Predicted Value (Interactive)</h3>
          <div className="w-full h-[560px]">
            <iframe
              title="interactive-scatter"
              src="http://localhost:5000/api/charts/interactive_scatter.html"
              className="w-full h-full border-0 rounded"
            />
          </div>
        </div>

        {/* Interactive Scatter (Income vs Balance) */}
        <div className="bg-white shadow rounded-lg p-4 md:col-span-2">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Income vs Balance (Interactive)</h3>
          <div className="w-full h-[520px]">
            <iframe
              title="interactive-income-balance"
              src="http://localhost:5000/api/charts/interactive_income_balance.html"
              className="w-full h-full border-0 rounded"
            />
          </div>
        </div>

        {/* Interactive Scatter (Transactions vs Predicted Value) */}
        <div className="bg-white shadow rounded-lg p-4 md:col-span-2">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Transactions vs Predicted Value (Interactive)</h3>
          <div className="w-full h-[520px]">
            <iframe
              title="interactive-tx-pred"
              src="http://localhost:5000/api/charts/interactive_tx_pred.html"
              className="w-full h-full border-0 rounded"
            />
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-6 rounded-lg bg-white shadow">
        <h3 className="text-lg font-semibold text-red-600 mb-2">Summary:</h3>
        <p className="text-gray-800">
          Export completed on:{" "}
          <span className="font-semibold text-blue-900">
            {summary.export_timestamp || "N/A"}
          </span>
        </p>
        <p className="text-gray-800">
          Segment Breakdown:
          {Object.entries(summary.segment_breakdown || {}).map(([segment, count]) => (
            <span key={segment} className="ml-2">
              <strong>{segment}</strong>: {count}
            </span>
          ))}
        </p>
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
                  {(Array.isArray(clients) ? clients : [])
                    .filter((c) => !clientsFilterSegment || c.cluster_label === clientsFilterSegment)
                    .map((c) => (
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
                        <td className="p-2">{c.client_id}</td>
                        <td className="p-2">{c.balance}</td>
                        <td className="p-2">{c.cluster_label}</td>
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
                        <td className="p-2">{c.client_id}</td>
                        <td className="p-2">{(c.predicted_value ?? c.balance)?.toLocaleString?.() ?? (c.predicted_value ?? c.balance)}</td>
                        <td className="p-2">{c.cluster_label}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Segments Modal */}
      {showSegmentsModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-11/12 max-w-3xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-blue-900">Segments</h3>
              <button
                className="px-3 py-1 rounded bg-red-600 text-white"
                onClick={() => setShowSegmentsModal(false)}
              >
                Close
              </button>
            </div>
            <div className="overflow-auto max-h-[70vh]">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="p-2">Segment</th>
                    <th className="p-2">Count</th>
                    <th className="p-2">Avg Balance</th>
                    <th className="p-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(segmentsData || []).map((s) => (
                    <tr key={s.segment} className="border-b">
                      <td className="p-2">{s.segment}</td>
                      <td className="p-2">{s.count}</td>
                      <td className="p-2">${s.avg_balance.toFixed(2)}</td>
                      <td className="p-2">
                        <button
                          className="px-2 py-1 rounded bg-blue-900 text-white"
                          onClick={() => {
                            setClientsFilterSegment(s.segment);
                            setShowSegmentsModal(false);
                            setShowClientsModal(true);
                          }}
                        >
                          View Clients
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
