import React from "react";

export default function StatCard({ title, value, Icon, color = "bg-blue-900", description, onClick }) {
  return (
    <div
      className="p-4 rounded-lg shadow bg-white flex flex-col justify-between cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-sm font-medium text-blue-900">{title}</h2>
        <div className={`p-2 rounded-full ${color} text-white`}>
          {Icon && <Icon className="h-5 w-5" />}
        </div>
      </div>
      <div className="text-2xl font-bold text-red-600">{value}</div>
      {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
    </div>
  );
}


