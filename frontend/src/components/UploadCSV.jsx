import React from "react";

export default function UploadCSV() {
  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      console.log("Uploading file:", file.name);
      console.log("Upload URL: http://localhost:5000/api/upload");
      
      // Full backend URL ensures it hits Flask directly
      const res = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData,
      });
      
      console.log("Upload response status:", res.status);

      // Parse response safely
      let data;
      const text = await res.text();
      try {
        data = JSON.parse(text);
      } catch {
        data = { message: text || "No response from server" };
      }

      if (res.ok) {
        alert(data.message || "CSV uploaded successfully!");
      } else {
        alert(data.error || "Upload failed on server");
      }
    } catch (err) {
      console.error(err);
      alert("Upload request failed.");
    }
  };

  return (
    <div>
      <label htmlFor="csvUpload" className="block mb-2 font-semibold">
        Upload CSV:
      </label>
      <input
        id="csvUpload"
        type="file"
        accept=".csv"
        onChange={handleUpload}
        className="border p-2 rounded"
      />
    </div>
  );
}
