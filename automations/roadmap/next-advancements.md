# Phase 2 — Next Advancements / Roadmap

> Near-term roadmap for Alpha Loop Capital automations. Each item includes scope, owning agents, dependencies, and implementation details.

## 2.1 Proactive Agent Activation

**Status:** Planned
**Owning Agents:** Manus, Computer, Claude
**Dependencies:** n8n cron infrastructure, market data API access, Obsidian vault write access

Scheduled n8n triggers for autonomous workflows that run without human initiation.

### Implementation

- **Daily 8AM Briefings:** n8n cron fires at `0 8 * * *`. HTTP nodes gather market data, portfolio status, and agent activity from the previous 24 hours. Code node synthesizes into structured briefing. Posts to `#daily-log` and syncs to Obsidian vault via Notion API.
- **Autonomous Market Research:** n8n cron fires every 4 hours. Fetches from financial news APIs, runs basic sentiment analysis in Code node, logs findings to Notion research database. Only alerts `#investment-ops` if sentiment exceeds configured thresholds.
- **Agent Status Roll-up:** Weekly automated check of all agent health, response rates, and error counts. Posted to `#bot-notifications`.

### Trigger → Action → Output

```
Cron (8AM) → Gather Data → Synthesize Briefing → Slack #daily-log + Obsidian
Cron (4h)  → Fetch News → Sentiment Analysis → Slack #investment-ops (if critical) + Notion
Cron (Mon) → Agent Health Check → Status Report → Slack #bot-notifications
```

---

## 2.2 Immersive Layers — Real-Time Financial News Analysis

**Status:** Planned
**Owning Agents:** Computer, Claude, Manus
**Dependencies:** OpenClaw Gateway, financial news API subscriptions, sentiment analysis model

Real-time financial news analysis layer powered by OpenClaw.

### Implementation

- OpenClaw Gateway monitors financial data feeds continuously.
- Sentiment analysis runs on every incoming article/event.
- Results scored and classified: **Critical** (market-moving), **Notable** (worth tracking), **Background** (log only).
- Critical alerts double-posted to `#investment-ops` with @mentions.
- All results logged to Notion research database for historical analysis.
- Claude synthesizes weekly trend reports from accumulated data.

### Trigger → Action → Output

```
OpenClaw Feed → Sentiment Analysis → Score/Classify → Route by Priority
  Critical → Slack #investment-ops (@mentions) + Notion
  Notable → Notion + weekly digest
  Background → Notion (log only)
```

---

## 2.3 Protocol Synthesis — BDI + l8p + MCE

**Status:** In Development
**Owning Agents:** Claude, Hoags, Manus
**Dependencies:** `#goals-and-objectives` channel, protocol documentation, agent memory layer

Apply the three core protocols to all new workflows for self-improving automation.

### Protocols

| Protocol | Full Name | Purpose | Channel |
|----------|-----------|---------|---------|
| **BDI** | Beliefs-Desires-Intentions | Agent goal alignment and decision framework | `#goals-and-objectives` |
| **l8p** | l8p Protocol | Self-evaluation and optimization of workflows | n8n + Slack |
| **MCE** | Meta-Context Engineering | Cross-agent context synthesis for coherent multi-agent work | All channels |

### Implementation

- Every new n8n workflow includes a BDI alignment check node (reads current goals from `#goals-and-objectives`).
- l8p evaluation runs weekly on all active workflows, scoring efficiency and recommending optimizations.
- MCE context objects are attached to every cross-agent handoff, ensuring receiving agents have full context.

---

## 2.4 Canonical Folder Architecture

**Status:** Planned
**Owning Agents:** Manus, EKT Agent, Notion
**Dependencies:** Notion workspace structure, Obsidian vault structure, file naming conventions

Standardized folder structure per application for resilient ingestion and vectorization.

### Implementation

- Define canonical folder template per app type (web app, API, agent, documentation).
- Each app gets: `/docs`, `/config`, `/workflows`, `/agents`, `/data`.
- Ingestion pipeline reads canonical paths for vectorization.
- Notion databases mirror the structure for discoverability.
- Template enforced by EKT Agent on new project creation.

### Folder Template

```
{app}/
├── docs/           # Documentation and specs
├── config/         # Configuration files
├── workflows/      # n8n workflow exports
├── agents/         # Agent configs and prompts
└── data/           # Data assets and schemas
```

---

## 2.5 Priority-Based Routing

**Status:** Partially Active
**Owning Agents:** n8n, Manus
**Dependencies:** n8n switch node, priority field in webhook payloads

Route messages based on urgency level.

### Implementation

| Priority | Routing Rule | Mentions |
|----------|-------------|----------|
| **Critical** | Double-post to `#investment-ops` + standard fan-out | `@channel` + targeted agent `@mentions` |
| **Normal** | Standard fan-out to relevant channel | Targeted agent `@mentions` only |
| **Low** | Post to relevant channel | No `@mentions` |

### Trigger → Action → Output

```
Inbound webhook (with priority field)
  → n8n Switch Node
    → Critical: POST to #investment-ops + fan-out channels (with @channel)
    → Normal: POST to relevant channel (with @agent mentions)
    → Low: POST to relevant channel (no mentions)
```

---

## Phase 2 Summary

| Advancement | Status | Owning Agents | Key Dependency |
|-------------|--------|---------------|----------------|
| Proactive Agent Activation | Planned | Manus, Computer, Claude | n8n cron, market APIs |
| Immersive Financial Layers | Planned | Computer, Claude, Manus | OpenClaw, sentiment model |
| Protocol Synthesis (BDI/l8p/MCE) | In Dev | Claude, Hoags, Manus | Protocol docs, memory layer |
| Canonical Folder Architecture | Planned | Manus, EKT Agent, Notion | Folder templates, ingestion pipeline |
| Priority-Based Routing | Partial | n8n, Manus | Switch node, priority field |
