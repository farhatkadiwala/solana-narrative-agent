"use client";

import { Idea, Narrative } from "@/types";
import IdeaCard from "./IdeaCard";

export default function IdeaList({
  ideas,
  narratives,
}: {
  ideas: Idea[];
  narratives: Narrative[];
}) {
  const getNarrative = (id: string) => narratives.find((n) => n.id === id);

  return (
    <div className="flex flex-col">
      {ideas.map((idea) => (
        <IdeaCard
          key={idea.id}
          idea={idea}
          narrative={getNarrative(idea.narrative_id)}
        />
      ))}
    </div>
  );
}
