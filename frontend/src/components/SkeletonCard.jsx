import React from "react";

export default function SkeletonCard() {
  return (
    <div className="p-4 rounded-lg shadow bg-white animate-pulse">
      <div className="flex justify-between items-center mb-2">
        <div className="h-4 bg-gray-200 rounded w-24" />
        <div className="h-8 w-8 bg-gray-200 rounded-full" />
      </div>
      <div className="h-7 bg-gray-200 rounded w-32" />
      <div className="h-4 bg-gray-100 rounded w-40 mt-2" />
    </div>
  );
}


