# Gaps, Risks, and Follow-Up List

> Explicit documentation of all known gaps, risks, and unknowns. Nothing is a placeholder — items are either confirmed or explicitly marked unknown with a follow-up action.

## Critical Gaps

### GAP-1: No Workflow Metrics Collection

**Severity:** High
**Impact:** Cannot measure workflow efficiency, cannot build l8p self-optimization
**Current State:** n8n workflows execute but execution data is not persisted or analyzed
**Follow-Up:**
- [ ] Decide metrics storage destination (Notion DB, Google Sheets, or dedicated DB)
- [ ] Implement post-execution hook on all n8n workflows
- [ ] Define metrics schema (duration, success/failure, token usage, output quality)
**Blocks:** l8p protocol (3C-1), A/B testing (3C-2)

### GAP-2: No Structured A2A Handoff Protocol

**Severity:** High
**Impact:** Multi-agent task chains rely on unstructured Slack messages; context is lost between agents
**Current State:** Agents communicate via Slack @mentions with free-form text
**Follow-Up:**
- [ ] Design A2A handoff schema (context, expected output, callback, priority)
- [ ] Implement handoff constructor in Manus
- [ ] Test with simple 2-agent chain (Claude → Cursor)
**Blocks:** All autonomous task chains (3B-1, 3B-2, 3B-3)

### GAP-3: BDI Data Is Unstructured

**Severity:** Medium-High
**Impact:** Agent goal alignment relies on reading Slack channel messages, not structured data
**Current State:** `#goals-and-objectives` channel has goals as conversational messages
**Follow-Up:**
- [ ] Create structured BDI Notion database (Beliefs, Desires, Intentions as separate fields)
- [ ] Migrate existing goals from Slack to Notion DB
- [ ] Build BDI check node for n8n workflows
**Blocks:** BDI alignment automation (2C-1)

### GAP-4: No Agent Health Monitoring

**Severity:** Medium-High
**Impact:** Agents can go offline silently; no proactive detection of failures
**Current State:** No automated health checks; issues discovered reactively
**Follow-Up:**
- [ ] Define health metrics per agent (last response time, error rate, uptime)
- [ ] Build weekly health check workflow in n8n
- [ ] Route alerts to `#bot-notifications`
**Blocks:** Reliable autonomous chains (Phase 3)

---

## Moderate Gaps

### GAP-5: Incomplete Channel Audit

**Severity:** Medium
**Impact:** 41+ channels exist but only ~13 are fully documented in the channel map
**Current State:** Known channels documented; remaining channels unaudited
**Follow-Up:**
- [ ] Run full Slack workspace channel audit via API
- [ ] Document agent presence in each channel
- [ ] Map routing rules for undocumented channels

### GAP-6: No Unified Webhook Schema

**Severity:** Medium
**Impact:** Each trigger source (Slack, GitHub, OpenClaw) has its own payload format
**Current State:** Source-specific handlers in n8n
**Follow-Up:**
- [ ] Design canonical webhook payload schema
- [ ] Build adapter nodes for each source type
- [ ] Migrate existing webhooks to normalized format
**Blocks:** Universal workflow integration (3B-2)

### GAP-7: Vectorization Pipeline Missing

**Severity:** Medium
**Impact:** Obsidian/Notion content is searchable by text but not semantically queryable
**Current State:** Bidirectional sync works; no embedding/vectorization layer
**Follow-Up:**
- [ ] Select vectorization service (OpenAI embeddings, Cohere, local model)
- [ ] Build ingestion pipeline (file change → extract → embed → index)
- [ ] Expose semantic search to agents via API or MCP
**Blocks:** Deep knowledge retrieval for agents

### GAP-8: Custom Agents Lack Documentation

**Severity:** Medium
**Impact:** Hoags, Kat, Hailey, Danielle, Sloane, EKT Agent have no public documentation of their prompts, configs, or capability boundaries
**Current State:** Described by role but implementation details unknown
**Follow-Up:**
- [ ] Document each custom agent's system prompt or instruction set
- [ ] Define capability boundaries and escalation paths
- [ ] Add to `#skills-tools-prompts` channel database

---

## Low-Severity Gaps

### GAP-9: No Approval Gate Mechanism

**Severity:** Low (until Phase 3)
**Impact:** Autonomous chains need human checkpoints for critical actions
**Follow-Up:**
- [ ] Design approval mechanism (Slack reaction, Linear approval status, or dedicated flow)
- [ ] Implement timeout behavior (auto-reject after N hours if no approval)

### GAP-10: No Rollback Automation

**Severity:** Low (until Phase 3)
**Impact:** If an autonomous deployment causes issues, rollback is manual
**Follow-Up:**
- [ ] Integrate Vercel rollback API into n8n
- [ ] Define rollback triggers (error rate spike, latency increase)
- [ ] Build automated rollback workflow

---

## Risks

### RISK-1: Token Cost Escalation

**Risk Level:** Medium
**Description:** As more agents become proactive (Phase 2), token consumption could increase significantly.
**Mitigation:**
- Maintain zero-waste routing pattern (tokens only on reaction)
- Implement token budgets per agent per day
- l8p protocol should monitor and flag cost anomalies

### RISK-2: Context Window Overflow

**Risk Level:** Medium
**Description:** Complex multi-agent chains may exceed individual agent context windows.
**Mitigation:**
- Structured A2A handoffs include summarized context, not full history
- Context decay with TTL prevents stale data accumulation
- Agents request additional context on-demand rather than receiving everything

### RISK-3: Single Point of Failure (n8n)

**Risk Level:** Medium-High
**Description:** n8n is the central hub for all workflow orchestration. Downtime = all automations halt.
**Mitigation:**
- Monitor n8n health proactively (Agent Health Monitor, #4)
- Consider n8n redundancy or failover
- Critical alerts should have a Slack-direct fallback path

### RISK-4: Agent Conflict / Contradictory Actions

**Risk Level:** Low-Medium
**Description:** Multiple agents acting on the same task could produce conflicting outputs.
**Mitigation:**
- Manus as single orchestrator prevents parallel conflicting actions
- BDI alignment ensures agents work toward same goals
- A2A protocol includes task locking (one agent per task at a time)

### RISK-5: Data Consistency Across Obsidian + Notion

**Risk Level:** Medium
**Description:** Bidirectional sync can introduce conflicts or data loss if both sides edit simultaneously.
**Mitigation:**
- Last-writer-wins with version history
- Designate primary source per content type (Obsidian for notes, Notion for databases)
- Weekly consistency audit

---

## Follow-Up Action List

| # | Action | Priority | Owner | Status |
|---|--------|----------|-------|--------|
| 1 | Decide metrics storage destination | High | Tom / Hoags | **UNKNOWN** |
| 2 | Design A2A handoff schema | High | Claude / Manus | **IN DEV** |
| 3 | Structure BDI data in Notion DB | High | Claude / Hoags | **UNKNOWN** |
| 4 | Build agent health monitoring | High | Computer / Manus | **UNKNOWN** |
| 5 | Run full workspace channel audit | Medium | Manus | **UNKNOWN** |
| 6 | Design unified webhook schema | Medium | Manus / n8n | **UNKNOWN** |
| 7 | Select vectorization service | Medium | Tom | **UNKNOWN** |
| 8 | Document custom agent configs | Medium | EKT Agent / Hoags | **UNKNOWN** |
| 9 | Design approval gate mechanism | Low | Tom / Hoags | **UNKNOWN** |
| 10 | Build rollback automation | Low | Cursor / Vercel | **UNKNOWN** |
| 11 | Provision market data API access | High | Tom | **UNKNOWN** |
| 12 | Configure LangSmith API access | Medium | LangSmith Fleet | **UNKNOWN** |
| 13 | Select sentiment analysis model | Medium | Claude | **UNKNOWN** |
| 14 | Finalize canonical folder template | Medium | Hoags / EKT Agent | **UNKNOWN** |
| 15 | Get n8n API access for programmatic modifications | Low | n8n admin | **UNKNOWN** |
