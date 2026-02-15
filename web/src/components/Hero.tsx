"use client";

import { useEffect, useState } from "react";
import { formatCountdown } from "@/lib/api";

function randomPrice() {
  return (Math.random() * 50 + 0.5).toFixed(2);
}

export default function Hero({ generatedAt }: { generatedAt: string | null }) {
  const [countdown, setCountdown] = useState("--:--:--");
  const [price, setPrice] = useState("--");

  useEffect(() => {
    const update = () => setCountdown(formatCountdown(generatedAt));
    update();
    const id = setInterval(update, 60000);
    return () => clearInterval(id);
  }, [generatedAt]);

  useEffect(() => {
    setPrice(randomPrice());
  }, []);

  return (
    <div className="flex items-center justify-between bg-hero border border-hero-border rounded-[6px] px-10 py-5 h-[124px] shadow-[0_1px_0_0_#000] mb-8">
      <div>
        <div className="text-[28px] font-semibold text-white tracking-[-1.4px] leading-[1.1]">
          Build while you bear{" "}
          <span className="text-[13px] font-normal text-white/40 tracking-[-0.3px]">
            (with the) <span className="text-[12px] font-normal text-[#E5484D] tracking-[-0.3px]">
            ${price}K &#9660;
          </span>
          </span>{" "}
          market{" "}

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
