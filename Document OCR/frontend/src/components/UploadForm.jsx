import { useState } from "react";
import api from "../services/api";

export default function UploadForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("aadhaar");

  const submit = async (e) => {
    e.preventDefault();
    const fd = new FormData();
    fd.append("file", file);
    fd.append("doc_type", docType);
    const res = await api.post("/upload", fd);
    onResult(res.data);
  };

  return (
    <form onSubmit={submit} className="bg-white p-6 shadow rounded">
      <select
        value={docType}
        onChange={(e) => setDocType(e.target.value)}
        className="mb-2"
      >
        <option value="aadhaar">Aadhaar</option>
        <option value="pan">PAN</option>
        <option value="license">Driving License</option>
      </select>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-2"
      />
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Upload
      </button>
    </form>
  );
}
