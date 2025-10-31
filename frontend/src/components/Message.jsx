export default function Message({ role, text }) {
  const isUser = role === "user";
  return (
    <div style={{
      alignSelf: isUser ? "flex-end" : "flex-start",
      maxWidth: 600,
      padding: 12,
      borderRadius: 10,
      margin: "8px 0",
      background: isUser ? "#e0f7ff" : "#f5f5f5",
      whiteSpace: "pre-wrap"
    }}>
      {text}
    </div>
  );
}
