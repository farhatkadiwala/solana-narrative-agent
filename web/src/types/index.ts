export interface BountyLink {
  title: string;
  url: string;
  prize: string;
}

export interface ColosseumAnalysis {
  reference_project: string;
  edition: string;
  hackathon_score: number;
  relevance: number;
  insight: string;
}

export interface RelevantLink {
  title: string;
  url: string;
  type: "tweet" | "article" | "repo" | "docs";
}

export interface Idea {
  id: string;
  narrative_id: string;
  title: string;
  elevator_pitch: string;
  description: string;
  target_users: string;
  key_features: string[];
  tech_stack: string[];
  competitive_advantage: string;
  effort_level: string;
  revenue_model: string;
  similar_projects: string[];
  skills_required: string[];
  build_guideline: string;
  bounty_links: BountyLink[];
  colosseum_analysis: ColosseumAnalysis | null;
  seeker_compatible: boolean;
  seeker_features: string;
  relevant_links: RelevantLink[];
}

export interface Narrative {
  id: string;
  title: string;
  summary: string;
  category: string;
  strength: number;
  keywords: string[];
  trend_direction: string;
}

export interface SignalSummary {
  total: number;
  onchain: { count: number };
  github: { count: number };
  twitter: { count: number };
}

export interface Report {
  generated_at: string;
  period_days: number;
  signal_summary: SignalSummary;
  narratives: Narrative[];
  ideas: Idea[];
}

export interface Status {
  is_running: boolean;
  last_run: string | null;
  report: Report | null;
  error: string | null;
}
