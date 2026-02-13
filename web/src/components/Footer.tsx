"use client";

import { timeAgo } from "@/lib/api";

export default function Footer({
  generatedAt,
}: {
  generatedAt: string | null;
}) {
  return (
    <div className="fixed bottom-0 left-0 right-0 h-[38px] bg-footer-bg border-t border-footer-border backdrop-blur-[62px] flex items-center justify-between px-12 z-50">
      <div className="flex items-center gap-4 text-xs font-medium text-desc tracking-[-0.3px]">
        {generatedAt && <span>Updated {timeAgo(generatedAt)}</span>}
      </div>
      <div className="flex items-center gap-1.5 text-xs text-desc tracking-[-0.3px]">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" />
        <span>Made by an LLM</span>
      </div>
    </div>
  );
}
