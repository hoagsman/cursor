# Sync Protocol: Notion AI ↔ Obsidian Vault

## Purpose

This document defines the bidirectional sync protocol between the Notion AI teamspace and the Obsidian Vault, both serving as the "Second Brain" for Alpha Loop Capital. The protocol ensures data consistency, conflict resolution, and audit traceability across both systems.

---

## Sync Workflow

### 1. Write Operations

Every write to the Second Brain follows this flow:

```
Agent/User initiates change
        │
        ▼
┌───────────────────┐
│  Pre-Write Check  │
│  (Consistency)    │
│                   │
│  1. Read current  │
│     state from    │
│     both systems  │
│  2. Verify no     │
│     pending sync  │
│  3. Lock resource │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Apply Change     │
│                   │
│  Primary target:  │
│  determined by    │
│  originating      │
│  channel          │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Propagate to     │
│  Secondary Target │
│                   │
│  Mirror change to │
│  the other system │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Post-Write       │
│  Verification     │
│                   │
│  1. Confirm both  │
│     systems match │
│  2. Update GitHub │
│  3. Log to        │
│     #second-brain │
│  4. Release lock  │
└───────────────────┘
```

### 2. Origin-Based Routing

| Origin Channel | Primary Target | Secondary Target | GitHub Update |
|----------------|----------------|------------------|---------------|
| `#notion-ai` | Notion teamspace | Obsidian vault | Required |
| `#obsidian-vault` | Obsidian vault | Notion teamspace | Required |
| `#second-brain` | Both simultaneously | N/A | Required |

---

## Conflict Resolution

### Detection

Conflicts are detected when:
- Both systems have been modified since the last sync checkpoint
- Content hashes differ between Notion and Obsidian for the same logical resource
- Timestamps indicate concurrent edits (within a configurable window, default: 60 seconds)

### Resolution Strategy

```
Conflict Detected
        │
        ▼
┌───────────────────┐
│  Compare          │
│  Timestamps       │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 Different   Same
 Timestamps  Timestamp
    │         │
    ▼         ▼
Last-Write  Obsidian
  Wins      Vault
            Priority
    │         │
    └────┬────┘
         │
         ▼
┌───────────────────┐
│  Log Resolution   │
│  to #second-brain │
│                   │
│  Include:         │
│  - Conflict type  │
│  - Winning source │
│  - Diff summary   │
│  - Timestamp      │
└───────────────────┘
```

### Priority Rules

1. **Last-write wins** — The most recent modification takes precedence.
2. **Vault priority on ties** — When timestamps are equal, Obsidian vault is canonical.
3. **Manual override** — Tom (or designated owner) can force-resolve via `#second-brain`.

---

## Sync Operations

### Full Sync

A complete bidirectional sync of all Second Brain content:

1. Export Notion Second Brain teamspace to structured markdown
2. Compare with Obsidian vault content via content hashing
3. Identify deltas (additions, modifications, deletions)
4. Apply changes per conflict resolution strategy
5. Commit sync state to GitHub
6. Report results to `#second-brain`

### Incremental Sync

Triggered on individual changes:

1. Detect change event (Notion webhook or Obsidian file watcher)
2. Identify affected resource
3. Apply pre-write consistency check
4. Propagate change to secondary target
5. Verify post-write consistency
6. Update GitHub if applicable

### Scheduled Sync Check

A periodic validation (recommended: every 6 hours) that:

1. Compares content hashes between Notion and Obsidian
2. Identifies any drift
3. Reports status to `#second-brain`
4. Auto-resolves minor discrepancies
5. Flags major conflicts for manual review

---

## Sync State Tracking

### Sync Checkpoint Format

```json
{
  "checkpoint_id": "uuid",
  "timestamp": "ISO-8601",
  "notion_state": {
    "pages_count": 0,
    "last_modified": "ISO-8601",
    "content_hash": "sha256"
  },
  "obsidian_state": {
    "files_count": 0,
    "last_modified": "ISO-8601",
    "content_hash": "sha256"
  },
  "status": "consistent|drift_detected|conflict_resolved",
  "conflicts_resolved": [],
  "github_commit": "sha"
}
```

### Status Codes

| Status | Description |
|--------|-------------|
| `consistent` | Both systems are in sync |
| `drift_detected` | Minor differences found, auto-resolved |
| `conflict_detected` | Conflicting changes require resolution |
| `conflict_resolved` | Conflict was resolved (includes resolution details) |
| `sync_in_progress` | Sync operation currently running |
| `sync_failed` | Sync failed (includes error details) |

---

## Error Handling

### Retry Strategy

- **Exponential backoff**: 4s, 8s, 16s, 32s
- **Max retries**: 4
- **Circuit breaker**: After 3 consecutive failures, pause sync and alert `#second-brain`

### Failure Escalation

1. **Automated retry** — Transient errors (network, rate limits)
2. **Agent notification** — Persistent errors alert `@Claude` and `@Computer` in `#second-brain`
3. **Manual intervention** — Structural conflicts escalate to Tom via `#second-brain`

---

## Audit Trail

All sync operations are logged with:

- Operation type (full sync, incremental, conflict resolution)
- Originating agent and channel
- Affected resources
- Before/after state hashes
- Resolution details (if conflict)
- GitHub commit reference

Logs are posted to `#second-brain` and stored in the GitHub repository under `docs/sync-logs/`.

---

## Related Documentation

- [Second Brain Architecture](./SECOND_BRAIN_ARCHITECTURE.md) — System overview
- [Agent Roles](./AGENT_ROLES.md) — Agent responsibilities per channel
