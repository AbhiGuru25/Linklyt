-- =============================================
-- Linklyt AI — Supabase Database Schema
-- Run this in your Supabase SQL Editor
-- =============================================

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. Documents table (for LangChain SupabaseVectorStore)
create table if not exists documents (
  id          bigserial primary key,
  content     text not null,
  metadata    jsonb,
  embedding   vector (384)   -- all-MiniLM-L6-v2 produces 384-dim vectors
);

-- 3. URL Cache table (replaces Redis for tracking indexed URLs)
create table if not exists url_cache (
  url         text primary key,
  title       text default '',
  created_at  timestamptz default now()
);

-- 4. Create the match_documents function (required by LangChain SupabaseVectorStore)
create or replace function match_documents (
  query_embedding vector(384),
  match_count     int     default 4,
  filter          jsonb   default '{}'
)
returns table (
  id        bigint,
  content   text,
  metadata  jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where documents.metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- 5. Enable Row Level Security (RLS) with open policies for service role
alter table documents  enable row level security;
alter table url_cache  enable row level security;

-- Allow service role full access
create policy "Service role full access on documents"
  on documents for all using (true);

create policy "Service role full access on url_cache"
  on url_cache for all using (true);
