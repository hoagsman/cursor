# Second Brain Architecture

## Overview

The Second Brain is the canonical context memory system for Alpha Loop Capital (ALC). It operates as a **bidirectional sync** between two primary data stores — **Notion AI** and **Obsidian Vault** — coordinated via **Slack** and version-controlled through **GitHub**.

The system follows a tri-channel Slack architecture where each channel governs a specific domain, with the `#second-brain` channel acting as the parent singularity that ensures cross-system consistency.

---

## Tri-Channel Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    #second-brain                         │
│         Parent Singularity / Conflict Resolution         │
│   Bidirectional sync status, cross-system consistency    │
│                                                          │
│   Sources: Notion + Obsidian (last-write wins,           │
│            vault priority on ties)                        │
└──────────────────────┬──────────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
┌──────────────────────┐ ┌──────────────────────┐
│     #notion-ai       │ │   #obsidian-vault    │
│  Singularity One     │ │  Singularity Two     │
│                      │ │                      │
│  Source of Truth:    │ │  Source of Truth:     │
│  Notion teamspace    │ │  Obsidian vault      │
│  "Second Brain"      │ │  "Second Brain"      │
│                      │ │                      │
│  Scope:              │ │  Scope:              │
│  - Page/DB CRUD      │ │  - Vault sync        │
│  - AI automations    │ │  - Markdown files    │
│  - Teamspace changes │ │  - Context memory    │
│  - AI content gen    │ │  - Integrated wkflws │
└──────────────────────┘ └──────────────────────┘
```

### Channel Details

| Channel | Slack ID | Purpose | Source of Truth |
|---------|----------|---------|-----------------|
| `#notion-ai` | `C0ANCJSFGV7` | Notion-side edits, AI integrations, database/page automations | Notion teamspace "Second Brain" |
| `#obsidian-vault` | `C0ADHSBR7GB` | Obsidian-side sync, vault workflows, canonical context memory | Obsidian vault |
| `#second-brain` | `C0AEU1NFAE7` | Parent singularity — bidirectional sync status, conflict resolution, cross-system consistency | Both (last-write wins, vault priority on ties) |

---

## Consistency Model

### Conflict Resolution

The system uses a **last-write-wins** strategy with **vault priority on ties**:

1. When a change occurs in either Notion or Obsidian, the most recent write takes precedence.
2. In the event of a simultaneous conflict (same timestamp), the Obsidian vault is the canonical source.
3. All conflict resolutions are logged in `#second-brain` for audit.

### Consistency Checklist

Every operation that modifies the Second Brain must satisfy all three conditions:

- [ ] **Notion**: Second Brain teamspace reflects the change
- [ ] **Obsidian**: Vault is consistent with the change
- [ ] **GitHub**: Relevant repositories are updated (commits, PRs, docs)

### Standing Rule

> Before any write to Notion or Obsidian, verify consistency across both singularities and confirm GitHub repos are updated.

---

## Data Flow

```
                    ┌─────────────┐
                    │   GitHub    │
                    │  (Version   │
                    │  Control)   │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼─────┐ ┌────▼──────┐
              │  Notion   │ │  Obsidian │
              │  Second   │◄►│  Second   │
              │  Brain    │ │  Brain    │
              │ Teamspace │ │  Vault    │
              └─────┬─────┘ └─────┬─────┘
                    │             │
              ┌─────▼─────┐ ┌────▼──────┐
              │ #notion-ai│ │#obsidian- │
              │           │ │  vault    │
              └─────┬─────┘ └─────┬─────┘
                    │             │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │#second-brain│
                    │  (Parent)   │
                    └─────────────┘
```

---

## Integration Points

### Notion AI
- Page and database CRUD operations
- AI-powered content generation
- Teamspace automation
- Database schema management

### Obsidian Vault
- Markdown file sync
- Context memory persistence
- Plugin-based workflows
- Local-first editing with sync

### GitHub
- Version control for all code artifacts
- CI/CD workflows for consistency checks
- PR-based review for structural changes
- Issue tracking for sync failures

### Slack
- Real-time coordination between agents
- Consistency status reporting
- Conflict resolution logging
- Agent-to-agent communication

---

## Related Documentation

- [Sync Protocol](./SYNC_PROTOCOL.md) — Detailed bidirectional sync workflow
- [Agent Roles](./AGENT_ROLES.md) — Agent responsibilities per channel
