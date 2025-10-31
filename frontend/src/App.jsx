import { useState } from "react";
import Upload from "./views/Upload";
import Chat from "./views/Chat";

export default function App() {
  const [namespace, setNamespace] = useState("default");
  const [tab, setTab] = useState("upload");

  return (
    <>
      <header>
        <h1>Gemini RAG DocChat</h1>
        <nav>
          <button onClick={() => setTab("upload")} disabled={tab === "upload"}>
            Upload
          </button>
          <button onClick={() => setTab("chat")} disabled={tab === "chat"}>
            Chat
          </button>
        </nav>
      </header>

      <div className="view-container">
        {tab === "upload" && (
          <Upload
            namespace={namespace}
            setNamespace={setNamespace}
            onIndexed={() => setTab("chat")}
          />
        )}

        {tab === "chat" && <Chat namespace={namespace} />}
      </div>
    </>
  );
}