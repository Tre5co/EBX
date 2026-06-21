/* =============================================
   EARTHBUCKS — Shared types
   ============================================= */

export interface Cause {
  id: string;
  index: number;
  name: string;
  color: string;
  emoji?: string;
  description?: string;
}

export interface Initiative {
  id: string;
  index?: number;
  title: string;
  cause_id: string;
  cause_index: number;
  emoji?: string;
  description?: string;
  proposed_by: 'benefactor' | 'org';
  committed_ebx: number;
  pool_total?: number;
  winning_org: string | null;
  status: 'suggested' | 'debate' | 'org_vote' | 'active' | 'resolved' | string;
  phase?: string;
}

export interface Organization {
  id: string;
  name: string;
  causes: number[];
  verified: boolean;
  description?: string;
  founded?: number;
}

export interface FeedPost {
  id: string;
  type: 'editorial' | 'opinion' | 'org_update' | 'headline' | string;
  author: string;
  author_type: 'earthbux' | 'benefactor' | 'org' | string;
  cause_index: number;
  title: string | null;
  body: string;
  created_at: string;
  likes: number;
  initiative_id: string | null;
  opinion_type?: 'org' | 'initiative' | string;
  // case -> 'for' | 'against' ; evaluation(feedback) -> 'positive' | 'negative'
  stance?: 'for' | 'against' | 'positive' | 'negative' | string | null;
}

// Cycle model: seven causes, each running a 7-week debate + simultaneous org
// election. The 7 cause windows are staggered by 1 week, so every week one
// cause has its decision day. Annulus rotates 1/7 of a turn per week.
export interface CycleState {
  causeIndex: number;
  daysRemaining: number;
  hoursRemaining: number;
  rotationDeg: number;
  weekNum: number;
  dayInWeek: number;
}

// One row in a cause's vote distribution.
export interface VoteShare {
  org_id: string;
  org_name: string;
  pct: number;
  rank: number;
  isOther: boolean;
  color: string;
}

export interface CreditHolding {
  causeIndex: number;
  amount: number;
}

export interface TokenChip {
  index: number;
  title: string;
  org?: string;
  causeColor: string;
  amount?: number;
}

