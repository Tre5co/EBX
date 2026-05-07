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
}

export interface CycleState {
  causeIndex: number;
  causePhase: 'debate' | 'vote' | 'recap';
  dayInCause: number;
  daysRemaining: number;
  hoursRemaining: number;
  rotationDeg: number;
  isRecap: boolean;
  cycleDay: number;
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

export interface Opinion {
  type: 'org' | 'initiative' | 'other' | string;
  body: string;
  author_handle: string;
  feedback: number;
  created_at: string;
}
