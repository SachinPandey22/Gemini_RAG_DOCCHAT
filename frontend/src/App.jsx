import { useState } from "react";
import Upload from "./views/Upload";
import Chat from "./views/Chat";

export default function App() {
  const [namespace, setNamespace] = useState("default");
  const [tab, setTab] = useState("upload"); // "upload" | "chat"

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", fontFamily: "system-ui, Arial, sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", padding: "16px 0" }}>
        <h1 style={{ fontSize: 22 }}>Gemini RAG DocChat</h1>
        <nav style={{ display: "flex", gap: 12 }}>
          <button onClick={() => setTab("upload")} disabled={tab === "upload"}>Upload</button>
          <button onClick={() => setTab("chat")} disabled={tab === "chat"}>Chat</button>
        </nav>
      </header>

      {tab === "upload" && (
        <Upload
          namespace={namespace}
          setNamespace={setNamespace}
          onIndexed={() => setTab("chat")}
        />
      )}

      {tab === "chat" && <Chat namespace={namespace} />}
    </div>
  );
}
