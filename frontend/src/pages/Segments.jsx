import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { BarChart3, Lightbulb, Users, Target, Crown, Star, TrendingUp, Shield } from "lucide-react";

const Segments = () => {
  console.log("Segments component initializing...");
  
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [segmentsData, setSegmentsData] = useState([]);
  const [showSegmentsModal, setShowSegmentsModal] = useState(false);
  const [clients, setClients] = useState([]);
  const [selectedSegment, setSelectedSegment] = useState("");
  const [recommendationName, setRecommendationName] = useState("");
  const [recommendationMessage, setRecommendationMessage] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Known system segments fallback (used if API hasn't provided segments yet)
  const systemSegments = ["bronze", "silver", "gold", "platinum"];
  const segmentOptions = useMemo(() => {
    const fromData = Array.from(new Set((segmentsData || []).map((s) => s.segment))).filter(Boolean);
    if (fromData.length > 0) {
      // If we have data segments, use them
      return fromData;
    }
    
    // If no data segments, check if we have clients with numeric cluster labels
    if (clients.length > 0) {
      const uniqueSegments = Array.from(new Set(clients.map(c => c.cluster_label).filter(Boolean)));
      if (uniqueSegments.length > 0) {
        return uniqueSegments;
      }
    }
    
    return systemSegments;
  }, [segmentsData, clients]);

  useEffect(() => {
    const load = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        if (!token) return (window.location.href = "/");
        
        // Load summary data
        const summaryRes = await axios.get("http://localhost:5000/api/dashboard/overview", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSummary(summaryRes.data);

        // Load clients data for recommendation mechanism
        const clientsRes = await axios.get("http://localhost:5000/api/clients/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const rows = Array.isArray(clientsRes.data)
          ? clientsRes.data
          : (Array.isArray(clientsRes.data?.value) ? clientsRes.data.value : []);

        // Normalize potential new headers
        const normalizeRow = (r) => ({
          id: r.id ?? r.CIFs ?? r.client_id,
          client_id: r.client_id ?? r.CIFs,
          balance: r.balance ?? r.Account_Balance,
          cluster_label: r.cluster_label ?? r.Cluster,
        });
        const normalized = rows.map(normalizeRow);
        console.log("Loaded clients:", normalized.length, "clients");
        console.log("Sample client:", normalized[0]);
        console.log("Unique cluster labels:", Array.from(new Set(normalized.map(c => c.cluster_label))));
        setClients(normalized);

        // Build segments data
        const bySegment = {};
        for (const r of normalized) {
          const seg = r.cluster_label ?? "Unknown";
          if (!bySegment[seg]) bySegment[seg] = { segment: seg, count: 0, totalBalance: 0 };
          bySegment[seg].count += 1;
          bySegment[seg].totalBalance += Number(r.balance || 0);
        }
        const segmentsArr = Object.values(bySegment).map((s) => ({
          segment: s.segment,
          count: s.count,
          avg_balance: s.count > 0 ? s.totalBalance / s.count : 0,
        }));
        setSegmentsData(segmentsArr);
        
        // Set default selected segment
        if (segmentsArr.length > 0) {
          setSelectedSegment(segmentsArr[0].segment);
        }
        
        setLoading(false);
      } catch (e) {
        console.error("Failed to load segments data", e);
        setLoading(false);
      }
    };
    load();
  }, []);

  const openSegmentsView = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await axios.get("http://localhost:5000/api/clients/all", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rows = Array.isArray(res.data)
        ? res.data
        : (Array.isArray(res.data?.value) ? res.data.value : []);

      // Normalize potential new headers
      const normalizeRow = (r) => ({
        id: r.id ?? r.CIFs ?? r.client_id,
        client_id: r.client_id ?? r.CIFs,
        balance: r.balance ?? r.Account_Balance,
        cluster_label: r.cluster_label ?? r.Cluster,
      });
      const normalized = rows.map(normalizeRow);
      setClients(normalized);
      const bySegment = {};
      for (const r of normalized) {
        const seg = r.cluster_label ?? "Unknown";
        if (!bySegment[seg]) bySegment[seg] = { segment: seg, count: 0, totalBalance: 0 };
        bySegment[seg].count += 1;
        bySegment[seg].totalBalance += Number(r.balance || 0);
      }
      const segmentsArr = Object.values(bySegment).map((s) => ({
        segment: s.segment,
        count: s.count,
        avg_balance: s.count > 0 ? s.totalBalance / s.count : 0,
      }));
      setSegmentsData(segmentsArr);
      if (!selectedSegment && segmentsArr.length > 0) setSelectedSegment(segmentsArr[0].segment);
      setShowSegmentsModal(true);
    } catch (e) {
      console.error("Failed to build segments view", e);
    }
  };

  const targetedClients = useMemo(() => {
    if (!selectedSegment) return [];
    const filtered = (clients || []).filter((c) => {
      const clientSegment = c.cluster_label ?? "Unknown";
      // Handle both string and numeric comparisons
      return clientSegment.toString() === selectedSegment.toString() || 
             clientSegment === selectedSegment;
    });
    console.log("Selected segment:", selectedSegment);
    console.log("Targeted clients count:", filtered.length);
    console.log("Sample targeted client:", filtered[0]);
    return filtered;
  }, [clients, selectedSegment]);

  const avgEngagement = useMemo(() => {
    if (targetedClients.length === 0) return 0;
    const scores = targetedClients.map((c) => {
      const bal = Number(c.balance || 0);
      const score = Math.max(10, Math.min(95, Math.round(bal / 1000)));
      return score;
    });
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    return Math.round(avg);
  }, [targetedClients]);

  // Helper functions - define before useMemo
  const getSegmentCharacteristics = (segment, avgBalance, count) => {
    switch (segment.toLowerCase()) {
      case 'platinum':
        return {
          title: "High-Value Premium Customers",
          description: "Your most valuable clients with highest balances and premium service needs",
          icon: Crown,
          color: "text-purple-600",
          bgColor: "bg-purple-50"
        };
      case 'gold':
        return {
          title: "Medium Activity Clients",
          description: "Clients with moderate activity and average account balances",
          icon: Star,
          color: "text-yellow-600",
          bgColor: "bg-yellow-50"
        };
      case 'silver':
        return {
          title: "High Transaction Clients",
          description: "Engaged customers with frequent transactions but moderate balances",
          icon: TrendingUp,
          color: "text-gray-600",
          bgColor: "bg-gray-50"
        };
      case 'bronze':
        return {
          title: "Emerging Clients",
          description: "New or developing clients with lower balances and transaction activity",
          icon: Shield,
          color: "text-orange-600",
          bgColor: "bg-orange-50"
        };
      default:
        return {
          title: "Unknown Segment",
          description: "Clients in an unidentified segment",
          icon: Users,
          color: "text-gray-600",
          bgColor: "bg-gray-50"
        };
    }
  };

  const getSegmentRecommendations = (segment, avgBalance, count) => {
    switch (segment.toLowerCase()) {
      case 'platinum':
        return [
          "Premium Investment Advisory Services",
          "Exclusive Wealth Management Packages",
          "Priority Relationship Manager Assignment",
          "High-Yield Investment Opportunities",
          "Exclusive Banking Products"
        ];
      case 'gold':
        return [
          "Balanced Investment Portfolios",
          "Retirement Planning Services",
          "Moderate Risk Investment Options",
          "Enhanced Savings Products",
          "Financial Planning Consultation"
        ];
      case 'silver':
        return [
          "Business Banking Solutions",
          "Transaction Optimization Services",
          "Cash Management Products",
          "Payment Processing Solutions",
          "Working Capital Financing"
        ];
      case 'bronze':
        return [
          "Basic Savings Accounts",
          "Financial Literacy Programs",
          "Low-Risk Investment Options",
          "Credit Building Products",
          "Educational Financial Services"
        ];
      default:
        return ["General Banking Services"];
    }
  };

  // Calculate high-value customers separately
  const highValueCustomers = useMemo(() => {
    if (!clients.length) return [];
    const allBalances = clients.map(c => Number(c.balance || 0)).sort((a, b) => b - a);
    const totalClients = clients.length;
    const highValueThreshold = allBalances[Math.floor(totalClients * 0.1)] || 0; // Top 10%
    return clients.filter(c => Number(c.balance || 0) >= highValueThreshold);
  }, [clients]);

  // Segment analysis and recommendation logic
  const segmentAnalysis = useMemo(() => {
    if (!clients.length) return {};
    
    const analysis = {};
    const allBalances = clients.map(c => Number(c.balance || 0)).sort((a, b) => b - a);
    const totalClients = clients.length;
    const highValueThreshold = allBalances[Math.floor(totalClients * 0.1)] || 0; // Top 10%

    // Analyze each segment - handle both numeric and string cluster labels
    const segments = ["bronze", "silver", "gold", "platinum"];
    const numericSegments = [0, 1, 2, 3]; // Common numeric cluster labels
    
    segments.forEach((segment, index) => {
      const segmentClients = clients.filter(c => {
        const clientSegment = c.cluster_label ?? "Unknown";
        // Check both string and numeric matches
        return clientSegment.toString().toLowerCase() === segment.toLowerCase() ||
               (numericSegments[index] !== undefined && clientSegment === numericSegments[index]);
      });
      if (segmentClients.length === 0) return;

      const balances = segmentClients.map(c => Number(c.balance || 0));
      const avgBalance = balances.reduce((a, b) => a + b, 0) / balances.length;
      const maxBalance = Math.max(...balances);
      const minBalance = Math.min(...balances);

      analysis[segment] = {
        count: segmentClients.length,
        avgBalance,
        maxBalance,
        minBalance,
        highValueCount: segmentClients.filter(c => Number(c.balance || 0) >= highValueThreshold).length,
        characteristics: getSegmentCharacteristics(segment, avgBalance, segmentClients.length),
        recommendations: getSegmentRecommendations(segment, avgBalance, segmentClients.length)
      };
    });

    return analysis;
  }, [clients]);

  const handleGenerateRecommendation = () => {
    setSuccessMsg("");
    if (!selectedSegment) {
      alert("Please choose a segment to analyze.");
      return;
    }
    
    const analysis = segmentAnalysis[selectedSegment.toLowerCase()];
    if (!analysis) {
      alert("No analysis available for the selected segment.");
      return;
    }

    const segmentInfo = analysis.characteristics;
    const recommendations = analysis.recommendations;
    
    setRecommendationName(segmentInfo.title);
    setRecommendationMessage(
      `Based on analysis of ${analysis.count} clients in the ${selectedSegment} segment:\n\n` +
      `Average Balance: $${analysis.avgBalance.toFixed(2)}\n` +
      `High-Value Clients: ${analysis.highValueCount}\n\n` +
      `Recommended Products/Services:\n` +
      recommendations.map(rec => `• ${rec}`).join('\n') +
      `\n\nThis segment represents ${segmentInfo.description.toLowerCase()} and would benefit from the above personalized recommendations.`
    );
    
    setSuccessMsg(`Recommendation analysis generated for ${selectedSegment} segment with ${analysis.count} clients.`);
  };

  if (loading) {
    console.log("Component is loading...");
    return <div className="p-6">Loading...</div>;
  }

  // Error boundary - if there's an issue, show a fallback
  if (!clients || clients.length === 0) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Segments</h1>
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">No client data available. Please ensure data has been uploaded.</p>
        </div>
      </div>
    );
  }

  console.log("Rendering Segments component with:", { 
    clients: clients.length, 
    selectedSegment, 
    loading, 
    summary: !!summary 
  });

  try {
    return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Segments</h1>

      {/* Stat Card: Segments */}
      <div
        className="p-4 rounded-lg shadow bg-white flex flex-col justify-between cursor-pointer hover:shadow-md max-w-sm"
        onClick={openSegmentsView}
      >
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-sm font-medium text-blue-900">Segments</h2>
          <div className={`p-2 rounded-full bg-blue-900 text-white`}>
            <BarChart3 className="h-5 w-5" />
          </div>
        </div>
        <div className="text-2xl font-bold text-red-600">{summary?.segments_count ?? "-"}</div>
        <p className="text-sm text-gray-600 mt-1">Distinct client clusters</p>
      </div>

      {/* High-Value Customers Overview */}
      <div className="mt-8 mb-6">
        <div className="rounded-xl bg-gradient-to-r from-purple-50 to-blue-50 shadow p-4">
          <div className="flex items-center gap-2 mb-2">
            <Crown className="h-5 w-5 text-purple-600" />
            <h2 className="text-lg font-semibold text-blue-900">High-Value Customers</h2>
          </div>
          <p className="text-sm text-gray-600 mb-3">Your most valuable clients identified through balance analysis</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-600">{highValueCustomers.length}</div>
              <div className="text-sm text-gray-600">High-Value Clients</div>
            </div>
            <div className="bg-white rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-600">
                ${highValueCustomers.length > 0 ? (highValueCustomers.reduce((sum, c) => sum + Number(c.balance || 0), 0) / highValueCustomers.length).toFixed(0) : 0}
              </div>
              <div className="text-sm text-gray-600">Avg Balance</div>
            </div>
            <div className="bg-white rounded-lg p-3">
              <div className="text-2xl font-bold text-green-600">
                {clients.length > 0 ? Math.round((highValueCustomers.length / clients.length) * 100) : 0}%
              </div>
              <div className="text-sm text-gray-600">Of Total Clients</div>
            </div>
          </div>
        </div>
      </div>

      {/* Segment Overview */}
      <div className="mt-8">
        <div className="rounded-xl bg-white shadow p-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-blue-900">Segment Analysis Overview</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(segmentAnalysis).map(([segment, analysis]) => {
              const IconComponent = analysis.characteristics.icon;
              return (
                <div key={segment} className={`rounded-lg p-4 ${analysis.characteristics.bgColor} border`}>
                  <div className="flex items-center gap-2 mb-2">
                    <IconComponent className={`h-4 w-4 ${analysis.characteristics.color}`} />
                    <span className={`text-sm font-medium ${analysis.characteristics.color}`}>
                      {segment.charAt(0).toUpperCase() + segment.slice(1)}
                    </span>
                  </div>
                  <div className="text-lg font-bold text-gray-800">{analysis.count}</div>
                  <div className="text-xs text-gray-600">Clients</div>
                  <div className="text-sm text-gray-700 mt-1">${analysis.avgBalance.toFixed(0)} avg</div>
                  <div className="text-xs text-gray-500 mt-1">{analysis.characteristics.title}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recommendation Mechanism */}
      <div className="mt-8">
        <div className="rounded-xl bg-white shadow p-4">
          <div className="flex items-center gap-2 mb-1">
            <Lightbulb className="h-5 w-5 text-red-600" />
            <h2 className="text-lg font-semibold text-blue-900">Recommendation Mechanism</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4">Analyze client segments and generate personalized recommendations</p>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-blue-900">Target Segment</label>
              <select
                className="border rounded px-3 py-2 w-full bg-white text-blue-900"
                value={selectedSegment}
                onChange={(e) => setSelectedSegment(e.target.value)}
              >
                {segmentOptions.map((seg) => (
                  <option key={seg} value={seg}>{seg}</option>
                ))}
              </select>
              <p className="text-sm text-gray-500">Choose which client segment to target.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-gray-500" />
                <div>
                  <p className="text-sm font-medium">{targetedClients.length} Clients</p>
                  <p className="text-xs text-gray-500">Will receive this offer</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-gray-500" />
                <div>
                  <p className="text-sm font-medium">{avgEngagement}%</p>
                  <p className="text-xs text-gray-500">Avg. engagement (proxy)</p>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="recommendationName" className="text-sm font-medium text-blue-900">Recommendation Name</label>
              <input
                id="recommendationName"
                className="border rounded px-3 py-2 w-full bg-white text-blue-900 placeholder:text-gray-400"
                placeholder="e.g., High-Value Premium Customers"
                value={recommendationName}
                onChange={(e) => setRecommendationName(e.target.value)}
                readOnly
              />
              <p className="text-xs text-gray-500">Auto-generated based on segment analysis</p>
            </div>

            <div className="space-y-2">
              <label htmlFor="recommendationMessage" className="text-sm font-medium text-blue-900">Personalized Recommendation</label>
              <textarea
                id="recommendationMessage"
                className="border rounded px-3 py-2 w-full bg-white text-blue-900 placeholder:text-gray-400"
                placeholder="Click 'Generate Recommendation' to analyze the selected segment..."
                rows={6}
                value={recommendationMessage}
                onChange={(e) => setRecommendationMessage(e.target.value)}
                readOnly
              />
              <p className="text-xs text-gray-500">System-generated recommendations based on segment characteristics</p>
            </div>

            {successMsg && (
              <div className="p-3 rounded bg-green-50 text-green-700 text-sm">{successMsg}</div>
            )}

            <button
              className="w-full px-3 py-2 rounded bg-blue-900 text-white hover:bg-blue-800 disabled:bg-gray-400"
              onClick={handleGenerateRecommendation}
              disabled={!selectedSegment}
            >
              Generate Recommendation Analysis
            </button>
          </div>
        </div>
      </div>

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
                  </tr>
                </thead>
                <tbody>
                  {(segmentsData || []).map((s) => (
                    <tr key={s.segment} className="border-b">
                      <td className="p-2">{s.segment}</td>
                      <td className="p-2">{s.count}</td>
                      <td className="p-2">${s.avg_balance.toFixed(2)}</td>
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
  } catch (error) {
    console.error("Error rendering Segments component:", error);
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Segments</h1>
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">Error loading segments. Please refresh the page.</p>
          <p className="text-red-600 text-sm mt-2">Error: {error.message}</p>
        </div>
      </div>
    );
  }
};

export default Segments;
