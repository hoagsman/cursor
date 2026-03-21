# Phased Implementation Plan

> Dependencies, blockers, and sequenced execution plan for all phases.

## Phase Overview

| Phase | Name | Focus | Prerequisites |
|-------|------|-------|---------------|
| **1** | Current State | Operational foundation | *(Complete)* |
| **2** | Next Advancements | Proactive automation, routing, protocols | Phase 1 stable |
| **3** | Future Iterations | Full autonomy, self-improvement, unified context | Phase 2 complete |

---

## Phase 1 — Current State (Complete)

### Delivered

- [x] n8n (ClawsTAK Instance) operational
- [x] OpenClaw Gateway operational with webhook dispatch
- [x] Slack workspace with 41+ channels
- [x] 12 MCP servers connected
- [x] 28 agents/bots/integrations active or connected
- [x] Webhook Reply Pattern (zero token waste)
- [x] Agent-to-Agent dispatch via `#agent-to-agent`
- [x] Sourcery auto-investigation of Sentry issues
- [x] Code development pipeline (Cursor → PR → Vercel)
- [x] Obsidian ↔ Notion bidirectional sync
- [x] BDI protocol active in `#goals-and-objectives`
- [x] l8p and MCE protocols active

### Known Gaps (Phase 1)

See [Gaps & Risks](gaps-and-risks.md) for full detail.

---

## Phase 2 — Next Advancements

### Sprint 2A: Foundation (Build First)

| Item | Automation | Owning Agents | Blockers |
|------|-----------|---------------|----------|
| 2A-1 | Daily 8AM Briefing | Manus, Claude, Computer | Market data API access |
| 2A-2 | Priority-Based Routing (Full) | n8n, Manus | Standardized priority field |
| 2A-3 | n8n Workflow Metrics Collector | n8n, LangSmith Fleet | Metrics storage destination |

**Blockers for Sprint 2A:**
- Market data API subscription or free tier setup
- Decision on metrics storage (Notion DB vs. Google Sheets vs. dedicated DB)
- Priority field schema agreed across all webhook sources

### Sprint 2B: Intelligence Layer

| Item | Automation | Owning Agents | Blockers |
|------|-----------|---------------|----------|
| 2B-1 | Sentry + LangSmith Enhanced Investigation | Sourcery, LangSmith Fleet | LangSmith API key/access |
| 2B-2 | Agent Health Monitor | Computer, Manus | Agent activity log aggregation |
| 2B-3 | Autonomous Market Research | Computer, Claude, Manus | Financial news API, sentiment model |

**Blockers for Sprint 2B:**
- LangSmith API access configured and tested
- Sentiment analysis model selected (local vs. API)
- Financial news data sources identified and API keys provisioned

### Sprint 2C: Protocol & Architecture

| Item | Automation | Owning Agents | Blockers |
|------|-----------|---------------|----------|
| 2C-1 | BDI Goal Alignment Check Node | Claude, Hoags | Structured BDI data format |
| 2C-2 | Canonical Folder Architecture | Manus, EKT Agent, Notion | Folder template finalized |
| 2C-3 | Unified Webhook Schema Normalizer | n8n, Manus | Schema spec, per-source adapters |

**Blockers for Sprint 2C:**
- BDI data needs to be structured (currently in Slack channel, needs Notion DB)
- Canonical folder template needs sign-off from Hoags
- Webhook schema requires input from all trigger sources

---

## Phase 3 — Future Iterations

### Sprint 3A: Handoff & Context

| Item | Automation | Owning Agents | Blockers |
|------|-----------|---------------|----------|
| 3A-1 | A2A Structured Handoff v1 | Manus, Claude | Handoff schema spec |
| 3A-2 | Obsidian Vault Ingestion Pipeline | Notion, Notion AI, Manus | Vectorization service, file watcher |
| 3A-3 | Unified Context Persistence | Notion, Claude, Manus | Agent memory layer design |

**Blockers for Sprint 3A:**
- A2A handoff schema needs protocol design (Claude + Manus)
- Vectorization service needs selection (OpenAI embeddings, Cohere, local)
- Agent memory layer architecture needs design doc

### Sprint 3B: Autonomous Chains

| Item | Automation | Owning Agents | Blockers |
|------|-----------|---------------|----------|
| 3B-1 | Bug-to-Fix Autonomous Chain | All engineering + quality | A2A handoff working, approval gates |
| 3B-2 | Universal Workflow Integration | Manus, n8n, Claude | Unified webhook schema (from 2C-3) |
| 3B-3 | Feature Request → Deploy Chain | Linear, Claude, Cursor, Vercel | Autonomous chains working |

**Blockers for Sprint 3B:**
- Requires Sprint 3A (handoff protocol) to be complete and tested
- Approval gate mechanism needs design (Slack reaction? Linear approval?)
- Rollback triggers need implementation

### Sprint 3C: Self-Improvement

| Item | Automation | Owning Agents | Blockers |
|------|-----------|---------------|----------|
| 3C-1 | l8p Workflow Self-Optimizer | Claude, Manus, n8n | Metrics collector (from 2A-3), n8n API |
| 3C-2 | A/B Testing for Workflows | n8n, LangSmith Fleet | Shadow mode infrastructure |
| 3C-3 | Context Decay & TTL Management | Notion, Claude | Unified context layer (from 3A-3) |

**Blockers for Sprint 3C:**
- Requires metrics collection running for enough time to have meaningful data
- n8n API access for programmatic workflow modification
- Shadow mode execution needs n8n workflow duplication capability

---

## Dependency Graph

```
Phase 1 (Complete)
  │
  ├─→ 2A-1: Daily Briefing
  ├─→ 2A-2: Priority Routing
  ├─→ 2A-3: Metrics Collector ──────────────────────→ 3C-1: l8p Optimizer
  │                                                    └──→ 3C-2: A/B Testing
  ├─→ 2B-1: Enhanced Sentry Investigation
  ├─→ 2B-2: Agent Health Monitor
  ├─→ 2B-3: Market Research Pipeline
  │
  ├─→ 2C-1: BDI Alignment Node
  ├─→ 2C-2: Canonical Folders
  ├─→ 2C-3: Unified Webhook Schema ─────────────────→ 3B-2: Universal Workflows
  │
  ├─→ 3A-1: A2A Handoff v1 ──────────────────────────→ 3B-1: Bug-to-Fix Chain
  │                                                    └──→ 3B-3: Feature-to-Deploy
  ├─→ 3A-2: Obsidian Ingestion
  ├─→ 3A-3: Unified Context ────────────────────────→ 3C-3: Context Decay/TTL
  │
  └─→ All Phase 3 items require Phase 2 foundation
```

---

## Blockers Summary

| Blocker | Blocking | Owner | Status |
|---------|----------|-------|--------|
| Market data API access | 2A-1, 2B-3 | Tom / Manus | **UNKNOWN** |
| Metrics storage decision | 2A-3 | Tom / Hoags | **UNKNOWN** |
| Priority field schema | 2A-2 | Manus | **UNKNOWN** |
| LangSmith API configuration | 2B-1 | LangSmith Fleet | **UNKNOWN** |
| Sentiment analysis model selection | 2B-3 | Claude | **UNKNOWN** |
| Financial news API sources | 2B-3 | Computer | **UNKNOWN** |
| BDI structured data format | 2C-1 | Claude / Hoags | **UNKNOWN** |
| Canonical folder template sign-off | 2C-2 | Hoags | **UNKNOWN** |
| Webhook schema specification | 2C-3 | Manus | **UNKNOWN** |
| A2A handoff protocol spec | 3A-1 | Claude / Manus | **IN DEVELOPMENT** |
| Vectorization service selection | 3A-2 | Tom | **UNKNOWN** |
| Agent memory layer design | 3A-3 | Claude | **UNKNOWN** |
| Approval gate mechanism | 3B-1 | Tom / Hoags | **UNKNOWN** |
| n8n API access for modifications | 3C-1 | n8n admin | **UNKNOWN** |
