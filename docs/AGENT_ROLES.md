# Agent Roles & Responsibilities

## Overview

The Second Brain system is operated by a fleet of AI agents coordinated across three Slack channels. Each agent has defined roles, responsibilities, and escalation paths. This document serves as the canonical reference for agent assignments.

---

## Channel: `#notion-ai` (C0ANCJSFGV7)

Scope: Notion page/database CRUD, Notion AI automations, Second Brain sync validation, issue triage.

### Primary Agents

| Agent | Slack Handle | Responsibilities |
|-------|-------------|-----------------|
| **Notion** | `@Notion` | Page edits, database queries, teamspace changes |
| **Notion AI** | `@Notion AI` | AI content generation within Notion, automated page updates |

### Secondary Agents

| Agent | Slack Handle | Responsibilities |
|-------|-------------|-----------------|
| **Manus** | `@Manus` | Cross-system orchestration (Notion ↔ Obsidian ↔ GitHub), scheduled sync checks, bulk operations |
| **Claude** | `@Claude` | Deep analysis of vault structure, conflict resolution logic, architecture decisions |
| **Computer** | `@Computer` | Real-time data pulls, cross-repo verification, GitHub Actions monitoring |

### When to Tag

- `@Notion` / `@Notion AI` — Page edits, database queries, teamspace changes, AI content generation within Notion
- `@Manus` — Cross-system orchestration, scheduled sync checks, bulk operations
- `@Claude` — Deep analysis, conflict resolution, architecture decisions
- `@Computer` — Real-time data pulls, cross-repo verification, GitHub monitoring

---

## Channel: `#obsidian-vault` (C0ADHSBR7GB)

Scope: Obsidian-side sync, vault workflows, canonical context memory, integrated workflows.

### Primary Agents

| Agent | Slack Handle | Responsibilities |
|-------|-------------|-----------------|
| **Cursor** | `@Cursor` | Code-level vault operations, file management, markdown processing |
| **Computer** | `@Computer` | Real-time vault status, file system operations, sync monitoring |

### Secondary Agents

| Agent | Slack Handle | Responsibilities |
|-------|-------------|-----------------|
| **Claude** | `@Claude` | Content analysis, structural decisions, conflict assessment |
| **Manus** | `@Manus` | Cross-system sync, bulk vault operations, scheduled tasks |
| **OneDrive and SharePoint** | `@OneDrive and SharePoint` | Cloud storage sync, file backup |
| **Google Drive** | `@Google Drive` | Secondary backup, file sharing |

### When to Tag

- `@Cursor` — File edits within the vault, markdown processing, code changes
- `@Computer` — Real-time vault monitoring, file system checks
- `@Claude` — Content analysis, structural decisions
- `@Manus` — Cross-system sync operations

---

## Channel: `#second-brain` (C0AEU1NFAE7)

Scope: Parent singularity — bidirectional sync status, conflict resolution, cross-system consistency.

### Primary Agents

| Agent | Slack Handle | Responsibilities |
|-------|-------------|-----------------|
| **Computer** | `@Computer` | Portfolio tracking, position alerts, risk monitoring, real-time data |
| **Manus** | `@Manus` | Cross-system orchestration, sync status aggregation, conflict coordination |

### Secondary Agents

| Agent | Slack Handle | Responsibilities |
|-------|-------------|-----------------|
| **Claude** | `@Claude` | Risk model analysis, conflict resolution, architecture oversight |
| **Notion** | `@Notion` | Notion-side status reporting |
| **Notion AI** | `@Notion AI` | AI-generated sync summaries |
| **Cursor** | `@Cursor` | GitHub-side status, PR verification |

### When to Tag

- `@Computer` — Real-time portfolio data, cross-repo verification, system health
- `@Manus` — Sync status, conflict coordination, bulk operations
- `@Claude` — Risk analysis, conflict resolution, architectural decisions

---

## Full Agent Fleet

All agents present across the tri-channel system:

| Agent | Primary Channel(s) | Role Category |
|-------|-------------------|---------------|
| Notion | `#notion-ai` | Data Management |
| Notion AI | `#notion-ai` | AI Automation |
| Cursor | `#obsidian-vault` | Code & Files |
| Computer | All channels | Real-time Operations |
| Manus | All channels | Orchestration |
| Claude | All channels | Analysis & Architecture |
| Linear | `#second-brain` | Issue Tracking |
| LangSmith Fleet | `#second-brain` | Agent Monitoring |
| Ellie | All channels | Executive Assistant |
| Kilo | `#second-brain` | Analytics |
| Vercel | `#notion-ai` | Deployment |
| Sourcery | All channels | Code Quality |
| Codex | `#obsidian-vault` | Code Generation |
| OneDrive and SharePoint | `#obsidian-vault` | Cloud Storage |
| ChatGPT | All channels | General AI |
| BLACKBOX Agent | `#second-brain` | Security |
| Replit | `#obsidian-vault` | Development |
| Google Sheets Workflow Steps | `#notion-ai` | Workflow Automation |
| Google Drive | `#obsidian-vault` | File Storage |
| Outlook Calendar | `#second-brain` | Scheduling |

---

## Escalation Matrix

### Level 1: Automated Resolution
- **Trigger**: Transient sync failures, minor drift
- **Agents**: `@Computer`, `@Manus`
- **Action**: Auto-retry with exponential backoff, log to `#second-brain`

### Level 2: Agent Intervention
- **Trigger**: Persistent failures, structural conflicts
- **Agents**: `@Claude`, `@Computer`
- **Action**: Analyze root cause, propose resolution, report to `#second-brain`

### Level 3: Manual Override
- **Trigger**: Critical data conflicts, system-wide inconsistency
- **Agents**: All primary agents
- **Action**: Escalate to Tom via `#second-brain`, await manual resolution

---

## Operating Principles

1. **Consistency First**: No agent writes to a single system without verifying cross-system consistency.
2. **Audit Everything**: All operations are logged to `#second-brain` and GitHub.
3. **Vault Priority**: On tie-breaking conflicts, Obsidian vault is canonical.
4. **Agent Identity**: All output is attributed to Tom Hogan / Alpha Loop Capital, never to the AI agents themselves.
5. **Air Gap**: Private workspace (Philly) content never propagates to shared systems without explicit command.

---

## Related Documentation

- [Second Brain Architecture](./SECOND_BRAIN_ARCHITECTURE.md) — System overview
- [Sync Protocol](./SYNC_PROTOCOL.md) — Bidirectional sync workflow
