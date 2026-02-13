"use client";

import { useState } from "react";
import { Idea, Narrative } from "@/types";

const LINK_ICONS: Record<string, string> = {
  tweet: "𝕏",
  article: "📄",
  repo: "⌨",
  docs: "📖",
};

function copyToLLM(idea: Idea, narrative: Narrative | undefined) {
  let text = `# ${idea.title}\n\n`;
  text += `**Elevator Pitch:** ${idea.elevator_pitch || idea.description.split(".")[0] + "."}\n\n`;
  text += `## What it is\n${idea.description}\n\n`;
  text += `## Target Users\n${idea.target_users}\n\n`;
  text += `## Key Features\n`;
  (idea.key_features || []).forEach((f) => (text += `- ${f}\n`));
  text += `\n## Tech Stack\n${(idea.tech_stack || []).join(", ")}\n\n`;
  text += `## Skills Required\n${(idea.skills_required || []).join(", ")}\n\n`;
  text += `## Build Guideline\n${idea.build_guideline || "N/A"}\n\n`;
  text += `## Competitive Advantage\n${idea.competitive_advantage}\n\n`;
  text += `## Revenue Model\n${idea.revenue_model}\n\n`;
  text += `## Effort Level: ${idea.effort_level}\n`;
  if (idea.seeker_compatible)
    text += `\n## Solana Seeker Mobile\n${idea.seeker_features}\n`;
  if (idea.bounty_links?.length) {
    text += `\n## Related Bounties\n`;
    idea.bounty_links.forEach(
      (b) => (text += `- [${b.title}](${b.url}) - ${b.prize}\n`)
    );
  }
  if (idea.relevant_links?.length) {
    text += `\n## Relevant Links\n`;
    idea.relevant_links.forEach(
      (l) => (text += `- [${l.title}](${l.url}) (${l.type})\n`)
    );
  }
  if (idea.colosseum_analysis) {
    const c = idea.colosseum_analysis;
    text += `\n## Colosseum Reference\nSimilar to **${c.reference_project}** (${c.edition}, score: ${c.hackathon_score}) - ${c.insight}\n`;
  }
  if (narrative)
    text += `\n## Narrative Context\n${narrative.title} (${narrative.category}, ${narrative.trend_direction}, strength: ${(narrative.strength * 100).toFixed(0)}%)\n${narrative.summary}\n`;
  text += `\n---\nHelp me build this. Ask me clarifying questions, then create a detailed technical spec and implementation plan.`;
  return text;
}

export default function IdeaCard({
  idea,
  narrative,
}: {
  idea: Idea;
  narrative: Narrative | undefined;
}) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = copyToLLM(idea, narrative);
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="py-5 border-b border-divider last:border-b-0 first:pt-0 group hover:bg-white/40 transition-colors px-3 -mx-3 rounded-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className="text-[19px] font-medium text-title tracking-[-0.95px] leading-none">
            {idea.title}
          </span>
          <div className="flex flex-wrap gap-1.5">
            {narrative?.title && (
              <span className="text-xs font-medium text-title/70 tracking-[-0.24px] leading-[0.93] px-2 py-1 rounded bg-narrative-bg border border-narrative-border hover:bg-[#E8E8E8] transition-colors">
                {narrative.title}
              </span>
            )}
            {narrative?.category && (
              <span className="text-xs font-medium text-pill tracking-[-0.24px] leading-[0.93] px-2 py-1 rounded bg-narrative-bg border border-narrative-border hover:bg-[#E8E8E8] transition-colors">
                {narrative.category}
              </span>
            )}
            <span className="text-xs font-medium text-pill tracking-[-0.24px] leading-[0.93] px-2 py-1 rounded bg-narrative-bg border border-narrative-border hover:bg-[#E8E8E8] transition-colors">
              {idea.effort_level}
            </span>
            {idea.seeker_compatible && (
              <span className="text-xs font-medium text-pill tracking-[-0.24px] leading-[0.93] px-2 py-1 rounded bg-narrative-bg border border-narrative-border hover:bg-[#E8E8E8] transition-colors">
                Seeker
              </span>
            )}
          </div>
        </div>
        <button
          onClick={handleCopy}
          className={`shrink-0 mt-0.5 transition-opacity cursor-pointer ${copied ? "opacity-100" : "opacity-0 group-hover:opacity-35 hover:!opacity-70"}`}
          title="Copy to LLM"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"
            />
          </svg>
        </button>
      </div>

      <p className="text-[15px] text-desc tracking-[-0.75px] leading-[1.12] mt-2">
        {idea.elevator_pitch || idea.description.split(".")[0] + "."}
      </p>

      <p
        className={`text-[15px] text-desc tracking-[-0.75px] leading-[1.12] mt-1.5 ${!expanded ? "line-clamp-2" : ""}`}
      >
        {idea.description}
      </p>

      <button
        onClick={() => setExpanded(!expanded)}
        className="text-[15px] font-medium text-green tracking-[-0.75px] mt-1 cursor-pointer hover:underline"
      >
        {expanded ? "Read less" : "Read more"}
      </button>

      {/* Relevant links */}
      {idea.relevant_links?.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1">
          {idea.relevant_links.map((l, i) => (
            <a
              key={i}
              href={l.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[13px] text-desc hover:text-title transition-colors inline-flex items-center gap-1"
            >
              <span className="text-[11px] opacity-60">
                {LINK_ICONS[l.type] || "🔗"}
              </span>
              <span className="hover:underline">{l.title}</span>
            </a>
          ))}
        </div>
      )}

      {/* Bounty links */}
      {idea.bounty_links?.length > 0 && (
        <div className="mt-1.5 flex flex-wrap gap-x-2.5">
          {idea.bounty_links.map((b) => (
            <a
              key={b.url}
              href={b.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[13px] font-medium text-green hover:underline"
            >
              {b.title} {b.prize}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
