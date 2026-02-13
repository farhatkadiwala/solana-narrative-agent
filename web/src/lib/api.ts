import { Report } from "@/types";

export async function fetchReport(): Promise<Report> {
  const res = await fetch("/report.json");
  return res.json();
}

export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "yesterday";
  return `${days}d ago`;
}

export function formatCountdown(generatedAt: string | null): string {
  if (!generatedAt) return "--:--:--";
  const generated = new Date(generatedAt).getTime();
  const next = generated + 14 * 24 * 60 * 60 * 1000;
  const diff = Math.max(0, next - Date.now());
  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  return `${d}d:${String(h).padStart(2, "0")}h:${String(m).padStart(2, "0")}m`;
}
