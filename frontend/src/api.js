// Simple API client for your FastAPI endpoints.
// Change BASE if your backend runs elsewhere.
export const BASE = "http://127.0.0.1:8000";

export async function uploadFiles({ namespace, files }) {
  const form = new FormData();
  form.append("namespace", namespace || "default");
  for (const f of files) form.append("files", f);
  const res = await fetch(`${BASE}/upload/`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export async function indexNamespace(namespace) {
  const url = new URL(`${BASE}/index/`);
  url.searchParams.set("namespace", namespace || "default");
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error(`Index failed: ${res.status}`);
  return res.json();
}

export async function ask({ namespace, question, top_k = 4, alpha = 0.6 }) {
  const res = await fetch(`${BASE}/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ namespace: namespace || "default", question, top_k, alpha })
  });
  if (!res.ok) throw new Error(`Ask failed: ${res.status}`);
  return res.json();
}
