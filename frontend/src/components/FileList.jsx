export default function FileList({ files = [] }) {
  if (!files.length) return null;
  return (
    <ul style={{ marginTop: 8 }}>
      {files.map((f, i) => (
        <li key={i} style={{ fontSize: 14 }}>
          • {f.name} ({Math.round(f.size / 1024)} KB)
        </li>
      ))}
    </ul>
  );
}
