"use client";

import { useEffect, useState } from "react";
import { formatCountdown } from "@/lib/api";

export default function Hero({ generatedAt }: { generatedAt: string | null }) {
  const [countdown, setCountdown] = useState("--:--:--");

  useEffect(() => {
    const update = () => setCountdown(formatCountdown(generatedAt));
    update();
    const id = setInterval(update, 60000);
    return () => clearInterval(id);
  }, [generatedAt]);

  return (
    <div className="flex items-center justify-between bg-hero border border-hero-border rounded-[6px] px-10 py-5 h-[124px] shadow-[0_1px_0_0_#000] mb-8">
      <div>
        <div className="text-[28px] font-semibold text-white tracking-[-1.4px] leading-[1.1]">
          Build while you bear <span className="text-16px font-medium text-grey tracking-[-1.1px]"> (with the) </span>  market
        </div>
      </div>
      <div className="text-right">
        <div className="text-[22px] font-semibold text-white/85 tracking-[-0.5px] tabular-nums">
          {countdown}
        </div>
        <div className="text-xs text-white/40 mt-0.5">Ideas refresh in</div>
      </div>
    </div>
  );
}
