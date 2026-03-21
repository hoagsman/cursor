# Recommended Canonical Architecture

> Target architecture for the Alpha Loop Capital automation ecosystem. This is the endgame structure that all phased work converges toward.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TRIGGER LAYER                                     │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Slack    │  │  GitHub  │  │ OpenClaw │  │  Sentry  │  │  Manual  │ │
│  │ Messages  │  │  Events  │  │   Cron   │  │  Alerts  │  │ Webhooks │ │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘ │
│        │              │              │              │              │      │
└────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     NORMALIZATION LAYER                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              Unified Webhook Schema Normalizer                    │   │
│  │    (All triggers normalized to canonical payload format)          │   │
│  └──────────────────────────┬───────────────────────────────────────┘   │
│                              │                                           │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                                 │
│                                                                          │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────────────┐  │
│  │    n8n Engine   │   │  Priority       │   │  BDI Alignment Check  │  │
│  │  (Workflow      │◄─►│  Router         │   │  (Goals validation    │  │
│  │   Execution)    │   │  (Crit/Norm/Lo) │   │   before execution)   │  │
│  └───────┬────────┘   └────────────────┘   └────────────────────────┘  │
│          │                                                               │
│  ┌───────▼────────┐   ┌────────────────┐   ┌────────────────────────┐  │
│  │  Manus         │   │  l8p Protocol  │   │  Metrics Collector     │  │
│  │  (Task         │   │  (Self-eval &  │   │  (Execution logging    │  │
│  │   Decomposer)  │   │   optimization)│   │   & analytics)         │  │
│  └───────┬────────┘   └────────────────┘   └────────────────────────┘  │
│          │                                                               │
└──────────┼──────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       A2A HANDOFF LAYER                                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              A2A Protocol (Structured Context Passing)            │   │
│  │                                                                    │   │
│  │  { task_id, source_agent, target_agent, context, expected_output, │   │
│  │    priority, deadline, callback }                                  │   │
│  └──────────────────────────┬───────────────────────────────────────┘   │
│                              │                                           │
└──────────────────────────────┼──────────────────────────────────────────┘
           ┌───────────────────┼──────────────────────┐
           │                   │                      │
           ▼                   ▼                      ▼
┌─────────────────┐ ┌─────────────────┐ ┌────────────────────────────────┐
│  AGENT LAYER    │ │  AGENT LAYER    │ │  AGENT LAYER                   │
│  (Engineering)  │ │  (Knowledge)    │ │  (Specialized)                 │
│                 │ │                 │ │                                 │
│ Cursor          │ │ Notion/Notion AI│ │ Ellie (Creative)               │
│ Codex           │ │ Linear/Asks     │ │ Hoags (Strategy)               │
│ Replit          │ │ Obsidian Vault  │ │ Kat (Improvement)              │
│ BLACKBOX Agent  │ │                 │ │ Hailey/Danielle/Sloane (PA)    │
│ Kilo            │ │                 │ │ EKT Agent (Architecture)       │
│ Sourcery        │ │                 │ │ Claude (Reasoning)             │
│ LangSmith Fleet │ │                 │ │ Computer (UI/Browser)          │
│                 │ │                 │ │ ChatGPT (General)              │
└────────┬────────┘ └────────┬────────┘ └─────────────────┬──────────────┘
         │                   │                             │
         ▼                   ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      TOOL LAYER (MCP Servers)                            │
│                                                                          │
│  Slack │ Notion │ GitHub │ Vercel │ Sentry │ Linear │ Supabase │ Neon  │
│  Firecrawl │ Context7 │ Cloudflare │ AWS                                │
│                                                                          │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER                                      │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Obsidian   │  │  Notion     │  │  Agent       │  │  Google     │  │
│  │  Vault      │◄─►  Databases  │  │  Memory      │  │  Sheets     │  │
│  │  (Second    │  │  (Structured │  │  Store       │  │  (Workflow  │  │
│  │   Brain)    │  │   Knowledge) │  │  (Per-agent) │  │   Data)     │  │
│  └─────────────┘  └─────────────┘  └──────────────┘  └─────────────┘  │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐                    │
│  │  Google     │  │  OneDrive / │  │  Supabase /  │                    │
│  │  Drive      │  │  SharePoint │  │  Neon DBs    │                    │
│  └─────────────┘  └─────────────┘  └──────────────┘                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                                           │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Slack   │  │  GitHub  │  │  Vercel  │  │  Notion  │  │  Email   │ │
│  │ Channels │  │   PRs    │  │  Deploy  │  │  Pages   │  │ (Gmail)  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Trigger Layer

All events that can initiate an automation. The canonical architecture normalizes these to a common format.

| Trigger Source | Examples |
|----------------|----------|
| Slack Messages | Human @mention, agent message, reaction |
| GitHub Events | Push, PR created, issue opened, review requested |
| OpenClaw Cron | Scheduled agent loops, periodic tasks |
| Sentry Alerts | Error detection, performance threshold breach |
| Manual Webhooks | API calls from external systems, CLI triggers |

### 2. Normalization Layer

Converts all trigger payloads to a unified schema before routing. Eliminates source-specific handler sprawl.

**Unified Payload Schema:**
```json
{
  "id": "unique-task-id",
  "source": "slack | github | openclaw | sentry | manual",
  "timestamp": "ISO-8601",
  "priority": "critical | normal | low",
  "task_type": "code | research | deploy | monitor | report | ...",
  "payload": { },
  "routing_hints": {
    "target_agents": ["agent-id-1", "agent-id-2"],
    "target_channels": ["#channel-1"],
    "callback": { "channel": "...", "mention": "..." }
  }
}
```

### 3. Orchestration Layer

The brain of the system. Contains n8n for workflow execution, Manus for task decomposition, priority routing, BDI alignment, l8p self-improvement, and metrics collection.

**Key Principle:** Zero token waste. Routing and orchestration consume minimal tokens. Agents only consume tokens when executing actual work.

### 4. A2A Handoff Layer

Structured protocol for agent-to-agent context passing. Ensures no context is lost when work moves between agents.

**Key Principle:** Every handoff includes full context, expected output format, priority, deadline, and callback instructions.

### 5. Agent Layer

The fleet of 28 agents organized by specialty. Each agent has defined capabilities, routing rules, and escalation paths.

**Key Principle:** Agents are specialists. They do one thing well. Complex tasks are decomposed and distributed.

### 6. Tool Layer (MCP Servers)

Standardized tool access via 12 MCP servers. Agents don't implement integrations directly — they use MCP tools.

**Key Principle:** New tools are added as MCP servers, instantly available to all agents.

### 7. Persistence Layer

All state is persisted across three tiers:
- **Obsidian Vault:** Long-form knowledge, notes, Second Brain
- **Notion Databases:** Structured data, project tracking, searchable knowledge
- **Agent Memory Store:** Per-agent short-term and long-term state

### 8. Output Layer

Where results are delivered: Slack messages, GitHub PRs, Vercel deployments, Notion pages, emails.

---

## Design Principles

1. **Zero Token Waste:** Routing consumes zero agent tokens. Agents activate only when directly needed.
2. **Source Agnostic:** The same workflow runs regardless of whether it was triggered by Slack, GitHub, OpenClaw, or API.
3. **Structured Handoffs:** Every agent-to-agent transfer includes full structured context.
4. **Goal Aligned:** BDI protocol validates all actions against current strategic goals.
5. **Self-Improving:** l8p protocol continuously evaluates and optimizes workflow efficiency.
6. **Observable:** Every execution is logged, traced, and measurable (LangSmith + n8n metrics).
7. **Fail Safe:** Critical paths have approval gates; all deployments have rollback capability.
8. **Single Orchestrator:** Manus is the single point of task decomposition, preventing conflicting parallel actions.

---

## Migration Path

The current architecture (Phase 1) evolves to this canonical architecture through Phase 2 and Phase 3 work:

| Component | Phase 1 (Now) | Phase 2 | Phase 3 (Target) |
|-----------|---------------|---------|-------------------|
| Triggers | Source-specific handlers | Priority routing added | Unified schema normalizer |
| Orchestration | n8n + Manus via Slack | + BDI alignment, metrics | + l8p self-optimization |
| Handoffs | Unstructured Slack messages | A2A schema designed | Full A2A protocol |
| Agents | 28 active, manual dispatch | Health monitoring, proactive | Autonomous chains |
| Tools | 12 MCP servers | Same + metrics MCP | Same + memory MCP |
| Persistence | Notion + Obsidian sync | + structured BDI data | + agent memory store |
| Outputs | Slack + GitHub + Vercel | + priority-routed alerts | Universal output routing |
