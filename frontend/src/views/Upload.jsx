import { useState } from "react";
import FileList from "../components/FileList";
import { uploadFiles, indexNamespace } from "../api";

export default function Upload({ namespace, setNamespace, onIndexed }) {
  const [files, setFiles] = useState([]);
  const [log, setLog] = useState("");

  async function handleUpload() {
    try {
      setLog("Uploading…");
      const res = await uploadFiles({ namespace, files });
      setLog(`Uploaded ${res.count} files to ${res.namespace}. Now indexing…`);
      const idx = await indexNamespace(namespace);
      setLog(
        `Indexed: ${idx.points_upserted} points from ${idx.files_indexed} files.`
      );
      onIndexed?.(idx);
    } catch (e) {
      setLog(String(e.message || e));
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Upload Documents</h2>

      <div style={{ marginTop: 12 }}>
        <label style={{ marginRight: 8 }}>Namespace:</label>
        <input
          value={namespace}
          onChange={(e) => setNamespace(e.target.value)}
          placeholder="default"
        />
      </div>

      <div style={{ marginTop: 12, border: "1px dashed #aaa", padding: 12 }}>
        <input
          type="file"
          accept=".pdf,.txt,.md"
          multiple
          onChange={(e) => setFiles(Array.from(e.target.files || []))}
        />
        <FileList files={files} />
      </div>

      <button onClick={handleUpload} style={{ marginTop: 12 }}>
        Upload & Index
      </button>

      <div style={{ marginTop: 12, fontSize: 14, color: "#555" }}>{log}</div>
    </div>
  );
}
