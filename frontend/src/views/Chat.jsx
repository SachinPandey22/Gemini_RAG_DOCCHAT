import { useState } from "react";
import Message from "../components/Message";
import { ask } from "../api";

export default function Chat({ namespace }) {
  const [messages, setMessages] = useState([]);
  const [q, setQ] = useState("");
  const [alpha, setAlpha] = useState(0.6);
  const [k, setK] = useState(4);

  async function send() {
    const question = q.trim();
    if (!question) return;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setQ("");

    try {
      const res = await ask({ namespace, question, top_k: k, alpha });
      const answer = formatAnswer(res);
      setMessages((m) => [...m, { role: "assistant", text: answer }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${String(e.message || e)}` }]);
    }
  }

  function formatAnswer(res) {
    // Show the model's answer + list the citations
    const ci = (res.citations || []).map(c => `- ${c.label}`).join("\n");
    return `${res.answer}\n\nSources:\n${ci || "- (none)"}`
  }

  return (
    <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
      <h2>Chat</h2>

      <div style={{ fontSize: 14, color: "#666" }}>
        Namespace: <b>{namespace}</b>
      </div>

      <div style={{ display: "flex", gap: 12, alignItems: "center", fontSize: 14 }}>
        <label>alpha</label>
        <input
          type="number" step="0.1" min="0" max="1"
          value={alpha}
          onChange={(e) => setAlpha(parseFloat(e.target.value))}
          style={{ width: 60 }}
        />
        <label>top_k</label>
        <input
          type="number" min="1" max="8"
          value={k}
          onChange={(e) => setK(parseInt(e.target.value || "4", 10))}
          style={{ width: 60 }}
        />
      </div>

      <div style={{
        display: "flex", flexDirection: "column", gap: 6,
        border: "1px solid #ddd", borderRadius: 8, padding: 12, minHeight: 200
      }}>
        {messages.map((m, i) => <Message key={i} role={m.role} text={m.text} />)}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1 }}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Say 'hi' or ask a question about your docs…"
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button onClick={send}>Send</button>
      </div>
    </div>
  );
}
