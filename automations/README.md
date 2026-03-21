# Alpha Loop Capital — Automations Workflow Structure

> Full audit of current state, roadmap, and future iterations for all bots, MCP servers, n8n workflows, and integrations.

## Overview

This is the canonical operating structure for the Alpha Loop Capital (ALC) / ClawsTAK automation ecosystem. It catalogs every AI agent, integration, and bot; maps MCP servers and n8n workflows; describes the current operational state; and outlines phased roadmap for next advancements and future iterations.

**Nothing is a placeholder. Unknowns are explicitly marked and grouped into a follow-up list.**

## Directory Structure

```
automations/
├── README.md                              # This file — master overview
├── config/
│   ├── ecosystem.yml                      # Master ecosystem config & infrastructure
│   └── mcp-servers.yml                    # MCP server registry and status
├── agents/
│   ├── registry.yml                       # Complete agent/bot registry (every agent, none forgotten)
│   ├── ai-agents.yml                      # AI agent detailed capabilities
│   ├── integrations.yml                   # Platform integrations & connectors
│   └── ownership-matrix.yml               # System/agent ownership mapping
├── workflows/
│   ├── current-state.yml                  # Current operational workflows (Phase 1)
│   ├── n8n-inventory.yml                  # n8n workflow inventory
│   ├── orchestration.yml                  # Agent orchestration patterns
│   └── trigger-action-output.yml          # Trigger → Action → Output flow diagrams
├── channels/
│   └── channel-map.yml                    # Slack channel → agent routing map
├── roadmap/
│   ├── next-advancements.md               # Phase 2 — near-term roadmap
│   ├── future-iterations.md               # Phase 3+ — long-term vision
│   ├── top-10-automations.md              # Highest-impact next 10 automations
│   ├── phased-implementation-plan.md      # Dependencies, blockers, phased plan
│   └── gaps-and-risks.md                  # Gaps, risks, and follow-up list
└── architecture/
    └── canonical-architecture.md          # Recommended canonical architecture
```

## Agent Fleet — Complete Roster (28 Agents/Bots/Integrations)

### Primary Orchestration (3)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 1 | **Manus** | Autonomous multi-step tasks, workflow building, end-to-end automation | Manus | Active |
| 2 | **Computer** | Workflow scheduling, monitoring, cross-agent orchestration | Anthropic | Active |
| 3 | **Claude** | Workflow architecture, complex logic, feedback synthesis | Anthropic | Active |

### Specialized Assistants (5)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 4 | **Ellie** | Chief Fun Officer, creativity, marketing | Ellie | Active |
| 5 | **Hoags** | Master Agent / CEO | Custom | Active |
| 6 | **Kat** | Teaching, lessons, continuous improvement | Custom | Active |
| 7 | **Hailey / Danielle / Sloane** | Personalized assistant agents | Custom | Active |
| 8 | **EKT Agent** | Top-level structures, agent builder | Custom | Active |

### Code & Engineering Agents (5)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 9 | **Cursor** | Cloud agent / IDE, code gen, PR automation | Cursor | Connected |
| 10 | **Codex** | Code generation, development tasks | OpenAI | Active |
| 11 | **Replit** | Prototyping, rapid deployment, hosted envs | Replit | Active |
| 12 | **BLACKBOX Agent** | Code completion, code search, IDE AI | Blackbox AI | Active |
| 13 | **Kilo** | Cloud agent spawning for codebase work | Kilo Code | Active |

### Quality & Observability (2)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 14 | **Sourcery** | Auto-investigates Sentry issues, code quality | Sourcery | Connected |
| 15 | **LangSmith Fleet** | Trace analysis, performance monitoring | LangChain | Active |

### Knowledge & Project Management (4)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 16 | **Notion** | Knowledge base, bidirectional Obsidian sync | Notion | Connected |
| 17 | **Notion AI** | AI-powered content generation, synthesis | Notion | Connected |
| 18 | **Linear** | Issue tracking, project management, sprint planning | Linear | Connected |
| 19 | **Linear Asks** | Conversational issue triage, project queries | Linear | Connected |

### Productivity & Files (5)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 20 | **Google Drive** | File storage, document management | Google | Connected |
| 21 | **Google Sheets Workflow Steps** | Spreadsheet automation, workflow data | Google | Connected |
| 22 | **Tom - Gmail** | Email and calendar integration | Google | Connected |
| 23 | **OneDrive and SharePoint** | File storage, file search | Microsoft | Connected |
| 24 | **Outlook Calendar** | Calendar management, meeting scheduling | Microsoft | Connected |

### AI Assistants & Other (3)

| # | Agent | Role | Provider | Status |
|---|-------|------|----------|--------|
| 25 | **ChatGPT** | General conversational AI | OpenAI | Active |
| 26 | **Figma** | Design collaboration | Figma | Connected |
| 27 | **Vercel** | Deployment notifications and releases | Vercel | Connected |

### Core Infrastructure (not agents, but critical systems)

| System | Role | Status |
|--------|------|--------|
| **n8n (ClawsTAK Instance)** | Central workflow orchestration, webhook routing, API integration | Active |
| **OpenClaw Gateway** | Autonomous agent loops, cron jobs via webhook POST to n8n | Active |
| **Slack Workspace** | 41+ channels, primary human-agent and agent-to-agent interface | Active |
| **MCP Servers** | Standardized tool access (Slack, Notion, Vercel, Sentry, Linear, Supabase, Neon, Firecrawl, etc.) | Active |

## Quick Links

- [Agent Registry](agents/registry.yml) — every agent, none forgotten
- [MCP Server Map](config/mcp-servers.yml) — all MCP servers and status
- [n8n Workflow Inventory](workflows/n8n-inventory.yml) — all n8n workflows
- [Integration Matrix](agents/integrations.yml) — full integration matrix
- [Ownership Matrix](agents/ownership-matrix.yml) — system/agent ownership
- [Trigger → Action → Output Flows](workflows/trigger-action-output.yml) — flow diagrams
- [Channel Map](channels/channel-map.yml) — Slack channel routing
- [Current State](workflows/current-state.yml) — Phase 1 operational state
- [Next Advancements](roadmap/next-advancements.md) — Phase 2 roadmap
- [Future Iterations](roadmap/future-iterations.md) — Phase 3+ vision
- [Top 10 Automations](roadmap/top-10-automations.md) — highest-impact next builds
- [Phased Implementation Plan](roadmap/phased-implementation-plan.md) — dependencies, blockers, phases
- [Gaps & Risks](roadmap/gaps-and-risks.md) — known gaps with follow-up list
- [Canonical Architecture](architecture/canonical-architecture.md) — recommended target architecture
