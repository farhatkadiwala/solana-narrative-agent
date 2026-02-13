"use client";

import { Narrative } from "@/types";

export default function Sidebar({
  narratives,
}: {
  narratives: Narrative[];
}) {
  if (narratives.length === 0) return null;

  return (
    <div className="w-80 shrink-0 sticky top-10">
      <div className="bg-narrative-bg border border-narrative-border rounded shadow-[0_1px_0_0_#F7F7F7] p-4">
        <div className="text-[17px] font-medium text-title tracking-[-0.85px] leading-none mb-3">
          Narratives this week
        </div>
        <div className="flex flex-wrap gap-1.5">
          {narratives.map((n) => (
            <span
              key={n.id}
              className="text-xs font-medium text-pill tracking-[-0.24px] px-2.5 py-1 rounded bg-[#E8E8E8] border border-narrative-border hover:bg-[#DFDFDF] transition-colors cursor-default"
            >
              {n.category}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
