# Phase 3+ — Future Iterations

> Long-term vision for Alpha Loop Capital automation ecosystem. These represent the endgame architecture where agents operate with maximum autonomy, self-improvement, and unified context.

## 3.1 Fully Autonomous Task Chains

**Status:** Planned (Phase 3)
**Owning Agents:** Sourcery → LangSmith Fleet → Claude → Cursor → Vercel → Sourcery
**Dependencies:** All Phase 2 items, reliable agent-to-agent handoff, approval gates

Complete end-to-end automation chains where bugs are detected, diagnosed, fixed, deployed, and verified without human intervention.

### Reference Chain: Bug-to-Fix

```
Bug Detected (Sentry)
  → LangSmith traces provide context
    → Claude scopes the fix (root cause + solution design)
      → Cursor implements on feature branch
        → Vercel deploys preview environment
          → Sourcery verifies the fix
            → Auto-merge if all checks pass
              → Production deployment
                → Slack notification: "Bug X resolved autonomously"
```

### Safeguards

- **Approval Gates:** Critical-path changes require human approval before merge.
- **Rollback Triggers:** If post-deploy metrics degrade, automatic rollback fires.
- **Audit Trail:** Every step logged to LangSmith + Notion for full traceability.
- **Confidence Scoring:** Claude assigns confidence level; low-confidence fixes routed to human review.

### Other Autonomous Chains (Planned)

| Chain | Flow | Status |
|-------|------|--------|
| Feature Request → Spec → Implementation → Deploy | Linear issue → Claude spec → Cursor code → Vercel deploy | Planned |
| Content Creation → Review → Publish | Notion draft → Claude review → Vercel CMS publish | Planned |
| Security Alert → Patch → Deploy → Verify | Sentry/Dependabot → Cursor patch → Vercel deploy → Sourcery verify | Planned |
| Data Pipeline → Analysis → Report | Google Sheets → n8n transform → Notion report → Slack summary | Planned |

---

## 3.2 Unified Context Persistence

**Status:** Planned (Phase 3)
**Owning Agents:** Notion, Notion AI, Claude, Manus
**Dependencies:** Agent memory layer, Obsidian vault infrastructure, real-time sync

Real-time shared state across all agents via Obsidian + Notion + agent memory.

### Architecture

```
┌─────────────────────────────────────────────────┐
│              Unified Context Layer               │
├──────────┬──────────────┬───────────────────────┤
│ Obsidian │   Notion DB  │   Agent Memory Store  │
│  Vault   │  (structured │   (ephemeral + long-  │
│ (Second  │   knowledge) │    term state per     │
│  Brain)  │              │    agent)             │
├──────────┴──────────────┴───────────────────────┤
│            Bidirectional Sync Layer              │
├─────────────────────────────────────────────────┤
│         All Agents Read/Write Context           │
└─────────────────────────────────────────────────┘
```

### Capabilities

- **Per-Agent Memory:** Each agent maintains short-term and long-term memory state.
- **Shared State:** Cross-agent context objects are readable by any agent in the fleet.
- **Conflict Resolution:** Last-writer-wins with version history for rollback.
- **Query Interface:** Agents query context via Notion MCP SQL or natural language.
- **Context Decay:** Stale context automatically ages out based on configurable TTL.

---

## 3.3 Universal Workflow Integration

**Status:** Planned (Phase 3)
**Owning Agents:** Manus, n8n, Claude
**Dependencies:** Unified webhook schema, channel-agnostic routing

Slack-initiated workflows should be identical to GitHub-initiated or OpenClaw-initiated ones. The entry point should not matter.

### Implementation

- **Unified Webhook Schema:** All triggers (Slack, GitHub, OpenClaw, manual) normalized to a common payload format before entering n8n.
- **Channel-Agnostic Routing:** n8n routes based on task type and priority, not source channel.
- **Idempotent Execution:** Same task triggered from multiple sources only executes once (deduplication by task hash).

### Before (Current State)

```
Slack message → Slack-specific handler → Slack-specific output
GitHub event  → GitHub-specific handler → GitHub-specific output
OpenClaw cron → OpenClaw-specific handler → OpenClaw-specific output
```

### After (Phase 3)

```
Any Source → Normalize to Unified Schema → n8n Universal Router → Agent Dispatch → Unified Output
```

---

## 3.4 Self-Improving Workflows (l8p Protocol Maturity)

**Status:** Planned (Phase 3)
**Owning Agents:** Claude, Manus, n8n
**Dependencies:** l8p protocol documentation, workflow metrics collection, n8n API access

l8p protocol auto-evaluates and optimizes n8n workflows with minimal human oversight.

### Implementation

- **Metrics Collection:** Every n8n workflow execution logs duration, success/failure, token usage, and output quality score.
- **Weekly Evaluation:** l8p protocol analyzes metrics, identifies bottlenecks, and scores each workflow.
- **Optimization Generation:** Claude generates specific optimization recommendations (node reordering, parallelization, caching, pruning).
- **Auto-Apply (with guardrails):** Low-risk optimizations apply automatically. High-risk changes require human approval.
- **A/B Testing:** New workflow versions run in shadow mode alongside existing ones; promoted if metrics improve.

### Evaluation Criteria

| Metric | Weight | Target |
|--------|--------|--------|
| Execution Time | 25% | < 5s for simple, < 30s for complex |
| Token Efficiency | 25% | Zero waste on routing, minimal on execution |
| Success Rate | 30% | > 99% for critical, > 95% for standard |
| Output Quality | 20% | Measured by downstream agent satisfaction |

---

## 3.5 A2A Protocol Maturity

**Status:** In Development → Phase 3
**Owning Agents:** Manus, Claude, Computer
**Dependencies:** Structured context format, handoff protocol spec, agent capability registry

Full agent-to-agent handoff protocols with structured context passing.

### Protocol Specification

```yaml
a2a_handoff:
  version: "1.0"
  fields:
    task_id: "unique identifier"
    source_agent: "agent initiating handoff"
    target_agent: "agent receiving handoff"
    context:
      summary: "natural language task summary"
      structured_data: "JSON payload with relevant data"
      conversation_history: "relevant prior messages"
      constraints: "time, budget, quality requirements"
    expected_output:
      format: "description of expected deliverable"
      destination: "where to post results"
    priority: "critical | normal | low"
    deadline: "ISO timestamp or null"
    callback:
      channel: "where to report completion"
      mention: "who to notify"
```

### Handoff Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Sequential** | Agent A finishes, hands to Agent B | Claude scopes → Cursor implements |
| **Parallel** | Agent A dispatches to B and C simultaneously | Manus dispatches to Cursor + Sourcery |
| **Callback** | Agent A starts work, calls back Agent B when done | Cursor implements, notifies Manus on PR |
| **Escalation** | Agent A can't complete, escalates to Agent B | Codex escalates complex task to Claude |
| **Broadcast** | Agent A notifies all relevant agents | n8n broadcasts deployment to all |

---

## Phase 3+ Summary

| Iteration | Status | Key Agents | Critical Dependency |
|-----------|--------|------------|---------------------|
| Fully Autonomous Task Chains | Planned | All engineering + quality agents | Reliable handoff, approval gates |
| Unified Context Persistence | Planned | Notion, Claude, Manus | Memory layer, real-time sync |
| Universal Workflow Integration | Planned | Manus, n8n, Claude | Unified webhook schema |
| Self-Improving Workflows (l8p) | Planned | Claude, Manus, n8n | Metrics collection, n8n API |
| A2A Protocol Maturity | In Dev | Manus, Claude, Computer | Handoff spec, capability registry |

---

## Vision Statement

The endgame is an autonomous agent ecosystem where:

1. **Bugs fix themselves** — detection through deployment without human touch.
2. **Workflows improve themselves** — l8p protocol continuously optimizes execution.
3. **Context is universal** — every agent has access to the full state of the system.
4. **Entry point doesn't matter** — same workflow runs regardless of trigger source.
5. **Agents hand off seamlessly** — structured A2A protocol ensures zero context loss.
