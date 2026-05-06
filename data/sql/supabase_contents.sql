-- ============================================================
-- EARTHBUCKS — Supabase Schema
-- Run this in your Supabase project: SQL Editor → New query
-- ============================================================

-- ── 0. Extensions ──────────────────────────────────────────
create extension if not exists "uuid-ossp";

-- ── 1. Users (shared row for benefactors + orgs) ───────────
-- Auth is handled by Supabase Auth (auth.users).
-- This table extends it with EBX-specific profile data.

create table public.users (
  id            uuid primary key references auth.users(id) on delete cascade,
  user_type     text not null check (user_type in ('benefactor','org')) default 'benefactor',
  handle        text unique not null,          -- @username
  display_name  text not null,
  bio           text,
  avatar_url    text,
  -- Benefactor fields (null for orgs)
  ebx_balance   numeric(18,6) default 0,       -- liquid EBX balance
  credit_score  numeric(5,2)  default 100,     -- 0–200, tracks mission success
  -- Org fields (null for benefactors)
  org_verified  boolean default false,
  org_website   text,
  org_mission   text,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

alter table public.users enable row level security;

create policy "Users can view all profiles"
  on public.users for select using (true);

create policy "Users can update own profile"
  on public.users for update using (auth.uid() = id);

create policy "Users can insert own profile"
  on public.users for insert with check (auth.uid() = id);


-- ── 2. Posts (opinions, reviews, updates, editorial) ───────
create table public.posts (
  id            uuid primary key default uuid_generate_v4(),
  author_id     uuid not null references public.users(id) on delete cascade,
  cause_index   int  not null check (cause_index between 0 and 6),
  initiative_id text,                          -- matches initiatives.json id field
  mission_id    text,                          -- for mission-scoped posts
  type          text not null check (type in (
                  'opinion',
                  'initiative_review',
                  'org_review',
                  'update',
                  'editorial'
                )),
  title         text,
  body          text not null,
  likes         int  not null default 0,
  created_at    timestamptz default now()
);

alter table public.posts enable row level security;

create policy "Anyone can read posts"
  on public.posts for select using (true);

create policy "Authenticated users can post"
  on public.posts for insert
  with check (auth.uid() = author_id);

create policy "Authors can update own posts"
  on public.posts for update
  using (auth.uid() = author_id);

-- Index for cause feed queries
create index posts_cause_idx on public.posts (cause_index, created_at desc);
create index posts_initiative_idx on public.posts (initiative_id, created_at desc);


-- ── 3. Votes (on initiatives) ───────────────────────────────
create table public.votes (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references public.users(id) on delete cascade,
  initiative_id text not null,
  direction     text not null check (direction in ('up','down')),
  created_at    timestamptz default now(),
  unique (user_id, initiative_id)              -- one vote per user per initiative
);

alter table public.votes enable row level security;

create policy "Anyone can read vote counts"
  on public.votes for select using (true);

create policy "Authenticated users can vote"
  on public.votes for insert
  with check (auth.uid() = user_id);

create policy "Users can change own vote"
  on public.votes for update
  using (auth.uid() = user_id);

create index votes_initiative_idx on public.votes (initiative_id);


-- ── 4. Commits (EBX pledged to initiatives) ────────────────
-- The balance debit is handled atomically by the Edge Function.
-- Direct INSERT is blocked; only the Edge Function can write here.

create table public.commits (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references public.users(id) on delete cascade,
  initiative_id text not null,
  amount_ebx    numeric(18,6) not null check (amount_ebx > 0),
  status        text not null default 'active'
                  check (status in ('active','withdrawn','converted')),
  created_at    timestamptz default now()
);

alter table public.commits enable row level security;

create policy "Users can view own commits"
  on public.commits for select
  using (auth.uid() = user_id);

create policy "Earthbux service role can insert commits"
  on public.commits for insert
  with check (auth.role() = 'service_role');   -- only Edge Function

create index commits_initiative_idx on public.commits (initiative_id);
create index commits_user_idx       on public.commits (user_id);


-- ── 5. Credit coins ────────────────────────────────────────
-- One row per cause per user. A user can hold coins from
-- multiple missions (multiple rows, different cause_index).

create table public.credit_coins (
  id               uuid primary key default uuid_generate_v4(),
  owner_id         uuid not null references public.users(id) on delete cascade,
  cause_index      int  not null check (cause_index between 0 and 6),
  mission_id       text not null,              -- the mission this coin came from
  face_value_ebx   numeric(18,6) not null,     -- original committed amount
  current_value    numeric(18,6) not null,     -- modulated by credit score
  credit_score_snap numeric(5,2),              -- score at time of last update
  -- Transaction history stored as JSONB for flexibility
  -- Shape: [{ type, amount, from_mission?, to_mission?, ts }]
  tx_history       jsonb not null default '[]',
  -- Key mission stats snapshot (updated by Edge Function on each release)
  stats_snapshot   jsonb not null default '{}',
  created_at       timestamptz default now(),
  updated_at       timestamptz default now(),
  unique (owner_id, mission_id)
);

alter table public.credit_coins enable row level security;

create policy "Users can view own coins"
  on public.credit_coins for select
  using (auth.uid() = owner_id);

create policy "Service role manages coins"
  on public.credit_coins for all
  using (auth.role() = 'service_role');


-- ── 6. Credit coin conversions ─────────────────────────────
-- Tracks 100%-value conversions between cause coins.
-- Rate is derived from the source coin's credit score at conversion time.

create table public.coin_conversions (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references public.users(id),
  from_mission_id text not null,
  to_mission_id   text not null,
  amount_ebx      numeric(18,6) not null,
  rate            numeric(8,6) not null,       -- e.g. 0.94 = 94 cents per EBX
  credit_score_at_conversion numeric(5,2),
  created_at      timestamptz default now()
);

alter table public.coin_conversions enable row level security;

create policy "Users can view own conversions"
  on public.coin_conversions for select
  using (auth.uid() = user_id);

create policy "Service role inserts conversions"
  on public.coin_conversions for insert
  with check (auth.role() = 'service_role');


-- ── 7. Mission release stages ──────────────────────────────
-- Org submits this form; determines how the 11/16 pot is split.
-- Minimum 7 stages required.

create table public.mission_release_stages (
  id            uuid primary key default uuid_generate_v4(),
  mission_id    text not null,
  org_id        uuid not null references public.users(id),
  stage_number  int  not null check (stage_number >= 1),
  label         text not null,                -- e.g. "Phase 1 fieldwork"
  description   text,
  pct_of_pot    numeric(5,2) not null         -- must sum to 100 across all stages
                  check (pct_of_pot > 0 and pct_of_pot <= 100),
  condition     text,                         -- release condition description
  status        text not null default 'pending'
                  check (status in ('pending','approved','released','missed')),
  amount_ebx    numeric(18,6),               -- computed: pct_of_pot × (11/16 × total_committed)
  released_at   timestamptz,
  created_at    timestamptz default now(),
  unique (mission_id, stage_number)
);

alter table public.mission_release_stages enable row level security;

create policy "Anyone can view release stages"
  on public.mission_release_stages for select using (true);

create policy "Org can insert their mission stages"
  on public.mission_release_stages for insert
  with check (auth.uid() = org_id);

create policy "Org can update their mission stages"
  on public.mission_release_stages for update
  using (auth.uid() = org_id);

-- ── 8. Helpful views ───────────────────────────────────────

-- Vote tallies per initiative
create or replace view public.initiative_vote_counts as
  select
    initiative_id,
    count(*) filter (where direction = 'up')   as up_votes,
    count(*) filter (where direction = 'down') as down_votes,
    count(*) as total_votes
  from public.votes
  group by initiative_id;

-- Commit totals per initiative
create or replace view public.initiative_commit_totals as
  select
    initiative_id,
    count(distinct user_id) as committer_count,
    sum(amount_ebx)         as total_committed_ebx
  from public.commits
  where status = 'active'
  group by initiative_id;

-- ── 9. Updated_at trigger ──────────────────────────────────
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger users_updated_at
  before update on public.users
  for each row execute function public.touch_updated_at();

create trigger coins_updated_at
  before update on public.credit_coins
  for each row execute function public.touch_updated_at();