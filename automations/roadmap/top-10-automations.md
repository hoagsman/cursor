# Highest-Impact Next 10 Automations

> Ranked by impact, feasibility, and dependency readiness. Each automation includes estimated complexity, owning agents, and the specific trigger → action → output chain.

## Ranking Criteria

- **Impact:** How much operational value does this unlock?
- **Feasibility:** Can it be built with current infrastructure?
- **Dependencies:** Are prerequisites in place?

---

## 1. Daily 8AM Briefing Automation

**Impact:** Very High | **Feasibility:** High | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | n8n cron at `0 8 * * *` |
| Action | Gather market data + agent status → Claude synthesizes → Post + sync |
| Output | `#daily-log` message + Obsidian vault entry |
| Owning Agents | Manus, Claude, Computer |
| Dependencies | n8n cron, market data API, Notion write access |
| Complexity | Low — straightforward n8n workflow with HTTP + Code + Slack nodes |

**Why #1:** Immediate daily value. Sets the rhythm for the entire team. Foundation for all proactive automations.

---

## 2. Priority-Based Routing (Full Implementation)

**Impact:** Very High | **Feasibility:** High | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | Any inbound webhook with priority field |
| Action | n8n Switch node routes by priority level |
| Output | Critical: `#investment-ops` + fan-out; Normal: standard; Low: no mentions |
| Owning Agents | n8n, Manus |
| Dependencies | n8n switch node, standardized priority field in payloads |
| Complexity | Low — extends existing webhook routing with priority logic |

**Why #2:** Prevents alert fatigue. Ensures critical items get immediate attention while low-priority items don't interrupt.

---

## 3. Sentry → Sourcery Auto-Investigation (Enhanced)

**Impact:** High | **Feasibility:** High | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | Sentry posts issue to Slack |
| Action | Sourcery investigates → LangSmith adds traces → Report posted |
| Output | Detailed investigation report with traces in Slack thread |
| Owning Agents | Sourcery, LangSmith Fleet |
| Dependencies | Sentry → Slack integration, LangSmith API access |
| Complexity | Medium — extends existing Sourcery auto-investigation with LangSmith trace enrichment |

**Why #3:** Already partially active. Enhancement adds trace data, making investigations actionable without human digging.

---

## 4. Agent Health Monitor

**Impact:** High | **Feasibility:** High | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | n8n cron weekly on Monday `0 9 * * 1` |
| Action | Check each agent's last response time, error rate, availability |
| Output | Health report to `#bot-notifications` with status per agent |
| Owning Agents | Computer, Manus |
| Dependencies | Agent activity logs (Slack message timestamps), n8n |
| Complexity | Medium — requires aggregating data from multiple sources |

**Why #4:** Prevents silent failures. Ensures no agent goes offline without notice.

---

## 5. Autonomous Market Research Pipeline

**Impact:** Very High | **Feasibility:** Medium | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | n8n cron every 4 hours `0 */4 * * *` |
| Action | Fetch news APIs → Sentiment analysis → Threshold check → Alert or log |
| Output | Critical: `#investment-ops` alert; All: Notion research database entry |
| Owning Agents | Computer, Claude, Manus |
| Dependencies | Financial news API subscriptions, sentiment analysis model |
| Complexity | Medium — requires API integrations and sentiment scoring |

**Why #5:** Core to ALC's investment thesis. Proactive intelligence vs. reactive research.

---

## 6. Unified Webhook Schema Normalizer

**Impact:** High | **Feasibility:** Medium | **Phase:** 2-3

| Aspect | Detail |
|--------|--------|
| Trigger | Any inbound webhook (Slack, GitHub, OpenClaw, manual) |
| Action | n8n normalizes to standard payload schema before routing |
| Output | Uniform task object fed to Universal Router |
| Owning Agents | n8n, Manus |
| Dependencies | Documented schema, adapter nodes per source type |
| Complexity | Medium — requires schema design and per-source adapters |

**Why #6:** Foundational for Universal Workflow Integration (Phase 3). Eliminates source-specific handler sprawl.

---

## 7. BDI Goal Alignment Check Node

**Impact:** High | **Feasibility:** Medium | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | Inserted into every new n8n workflow |
| Action | Node reads current BDI state from `#goals-and-objectives`, validates task alignment |
| Output | Proceed (aligned) or Flag (misaligned) with explanation |
| Owning Agents | Claude, Hoags |
| Dependencies | Structured BDI data in `#goals-and-objectives` or Notion |
| Complexity | Medium — requires BDI data structure and validation logic |

**Why #7:** Ensures all automation stays aligned to strategic goals. Prevents drift.

---

## 8. n8n Workflow Metrics Collector

**Impact:** Medium-High | **Feasibility:** High | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | Post-execution hook on every n8n workflow |
| Action | Log execution time, success/failure, node count, output destination |
| Output | Metrics database in Notion or Google Sheets |
| Owning Agents | n8n, LangSmith Fleet |
| Dependencies | n8n execution API, metrics storage |
| Complexity | Low-Medium — n8n has built-in execution logs, need to pipe to storage |

**Why #8:** Prerequisite for l8p self-improvement (Phase 3). Can't optimize what you can't measure.

---

## 9. A2A Structured Handoff (v1)

**Impact:** High | **Feasibility:** Medium | **Phase:** 2-3

| Aspect | Detail |
|--------|--------|
| Trigger | Agent completes task and needs to hand off |
| Action | Construct A2A handoff object (context, expected output, callback) → Post to target agent |
| Output | Target agent receives structured task with full context |
| Owning Agents | Manus, Claude |
| Dependencies | A2A handoff schema, agent capability registry |
| Complexity | Medium-High — requires protocol design and adoption across agents |

**Why #9:** Foundation for all autonomous task chains. Without structured handoffs, multi-agent chains break.

---

## 10. Obsidian Vault Ingestion Pipeline

**Impact:** Medium-High | **Feasibility:** Medium | **Phase:** 2

| Aspect | Detail |
|--------|--------|
| Trigger | New or updated file in Obsidian vault |
| Action | Detect change → Extract content → Vectorize → Index in Notion |
| Output | Searchable, queryable knowledge base accessible to all agents |
| Owning Agents | Notion, Notion AI, Manus |
| Dependencies | Obsidian vault sync, vectorization service, Notion API |
| Complexity | Medium — requires file watcher, content extraction, and indexing |

**Why #10:** Makes the Second Brain truly accessible to every agent. Currently sync exists but deep search/vectorization doesn't.

---

## Summary Table

| Rank | Automation | Impact | Feasibility | Phase | Complexity |
|------|-----------|--------|-------------|-------|------------|
| 1 | Daily 8AM Briefing | Very High | High | 2 | Low |
| 2 | Priority-Based Routing (Full) | Very High | High | 2 | Low |
| 3 | Sentry + LangSmith Investigation | High | High | 2 | Medium |
| 4 | Agent Health Monitor | High | High | 2 | Medium |
| 5 | Market Research Pipeline | Very High | Medium | 2 | Medium |
| 6 | Unified Webhook Schema | High | Medium | 2-3 | Medium |
| 7 | BDI Goal Alignment Node | High | Medium | 2 | Medium |
| 8 | n8n Metrics Collector | Medium-High | High | 2 | Low-Medium |
| 9 | A2A Structured Handoff v1 | High | Medium | 2-3 | Medium-High |
| 10 | Obsidian Vault Ingestion | Medium-High | Medium | 2 | Medium |

**Recommended build order:** 1 → 2 → 8 → 3 → 4 → 5 → 7 → 6 → 10 → 9

(Build #8 early because metrics collection is a prerequisite for l8p optimization later.)
