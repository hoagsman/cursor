# API Keys & Environments Reference

> Master inventory of all 75+ API keys, service credentials, and environment variables across the full stack.
> Last audited: 2026-03-21

---

## Table of Contents

- [Overview](#overview)
- [1. AI & Language Models](#1-ai--language-models)
- [2. Cloud & Hosting](#2-cloud--hosting)
- [3. Databases & Storage](#3-databases--storage)
- [4. Vector Databases & Search](#4-vector-databases--search)
- [5. Authentication & Identity](#5-authentication--identity)
- [6. Payments & Billing](#6-payments--billing)
- [7. Communication & Messaging](#7-communication--messaging)
- [8. Version Control & CI/CD](#8-version-control--cicd)
- [9. Productivity & Knowledge Management](#9-productivity--knowledge-management)
- [10. Trading & Finance](#10-trading--finance)
- [11. Media & Content](#11-media--content)
- [12. Monitoring & Observability](#12-monitoring--observability)
- [13. Agent & Orchestration Platforms](#13-agent--orchestration-platforms)
- [14. Development Tools & IDEs](#14-development-tools--ides)
- [15. Domain & DNS](#15-domain--dns)
- [Environment File Templates](#environment-file-templates)
- [Service-to-Channel Mapping](#service-to-channel-mapping)
- [Security Notes](#security-notes)

---

## Overview

This document catalogs every API key, secret, token, and environment variable required across the ecosystem. Services are grouped by category. Each entry includes:

| Column | Meaning |
|--------|---------|
| **Variable** | The environment variable name |
| **Service** | Provider or product |
| **Where Used** | Project, channel, or config that consumes it |
| **Required** | Whether the integration fails without it |
| **Docs** | Link to the provider's credential setup page |

---

## 1. AI & Language Models

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 1 | `OPENAI_API_KEY` | OpenAI (GPT-4, GPT-4o, DALL-E, Whisper) | Second Brain, apps, agents | Yes | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| 2 | `OPENAI_ORG_ID` | OpenAI Organization | Multi-org billing | No | [platform.openai.com/account/organization](https://platform.openai.com/account/organization) |
| 3 | `ANTHROPIC_API_KEY` | Anthropic (Claude 4.x) | Cursor, agents, Second Brain | Yes | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |
| 4 | `REPLICATE_API_TOKEN` | Replicate (model hosting) | Image/audio generation, ML pipelines | Yes | [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) |
| 5 | `HUGGINGFACE_API_KEY` | Hugging Face | Model inference, embeddings | No | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| 6 | `GOOGLE_AI_API_KEY` | Google AI (Gemini) | Multi-model fallback | No | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| 7 | `MISTRAL_API_KEY` | Mistral AI | Alternative LLM | No | [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys) |
| 8 | `PERPLEXITY_API_KEY` | Perplexity AI | Search-augmented generation | No | [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) |
| 9 | `GROQ_API_KEY` | Groq | Fast inference | No | [console.groq.com/keys](https://console.groq.com/keys) |
| 10 | `TOGETHER_API_KEY` | Together AI | Open-source model hosting | No | [api.together.xyz/settings/api-keys](https://api.together.xyz/settings/api-keys) |
| 11 | `COHERE_API_KEY` | Cohere | Embeddings, reranking | No | [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys) |

---

## 2. Cloud & Hosting

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 12 | `VERCEL_TOKEN` | Vercel (deploy) | CI/CD, preview deploys | Yes | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| 13 | `VERCEL_ORG_ID` | Vercel Organization | Team deploys | Yes | Vercel dashboard → Settings |
| 14 | `VERCEL_PROJECT_ID` | Vercel Project | Per-app deploys | Yes | Vercel dashboard → Project Settings |
| 15 | `NEXT_PUBLIC_VERCEL_URL` | Vercel (auto) | Frontend base URL | Auto | Set by Vercel automatically |
| 16 | `AWS_ACCESS_KEY_ID` | AWS IAM | Lambda, S3, SES | No | [console.aws.amazon.com/iam](https://console.aws.amazon.com/iam) |
| 17 | `AWS_SECRET_ACCESS_KEY` | AWS IAM | Lambda, S3, SES | No | [console.aws.amazon.com/iam](https://console.aws.amazon.com/iam) |
| 18 | `AWS_REGION` | AWS | Region routing | No | — |
| 19 | `CLOUDFLARE_API_TOKEN` | Cloudflare | DNS, Workers, R2 | No | [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens) |
| 20 | `CLOUDFLARE_ACCOUNT_ID` | Cloudflare | Workers, R2 | No | Cloudflare dashboard |
| 21 | `RAILWAY_TOKEN` | Railway | Alternative hosting | No | [railway.app/account/tokens](https://railway.app/account/tokens) |

---

## 3. Databases & Storage

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 22 | `SUPABASE_URL` | Supabase (project URL) | Auth, DB, storage | Yes | [supabase.com/dashboard](https://supabase.com/dashboard) |
| 23 | `SUPABASE_ANON_KEY` | Supabase (public anon) | Client-side queries | Yes | Supabase → Settings → API |
| 24 | `SUPABASE_SERVICE_ROLE_KEY` | Supabase (admin) | Server-side, Edge Functions | Yes | Supabase → Settings → API |
| 25 | `SUPABASE_JWT_SECRET` | Supabase JWT | Custom auth flows | No | Supabase → Settings → API |
| 26 | `SUPABASE_DB_URL` | Supabase (direct Postgres) | Migrations, Prisma | No | Supabase → Settings → Database |
| 27 | `DATABASE_URL` | Neon (serverless Postgres) | Prisma, Drizzle, direct SQL | Yes | [console.neon.tech](https://console.neon.tech) |
| 28 | `NEON_API_KEY` | Neon Management API | Branch management | No | [console.neon.tech/app/settings/api-keys](https://console.neon.tech/app/settings/api-keys) |
| 29 | `NEON_DATABASE_URL` | Neon (pooled connection) | Serverless functions | No | Neon dashboard → Connection |
| 30 | `REDIS_URL` | Redis (Upstash / self-hosted) | Caching, rate limiting, queues | Yes | [console.upstash.com](https://console.upstash.com) |
| 31 | `UPSTASH_REDIS_REST_URL` | Upstash Redis REST | Serverless Redis | No | [console.upstash.com](https://console.upstash.com) |
| 32 | `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis REST | Serverless Redis auth | No | [console.upstash.com](https://console.upstash.com) |
| 33 | `MONGODB_URI` | MongoDB Atlas | Document storage | No | [cloud.mongodb.com](https://cloud.mongodb.com) |
| 34 | `FIREBASE_API_KEY` | Firebase | Auth, Firestore | No | [console.firebase.google.com](https://console.firebase.google.com) |
| 35 | `FIREBASE_PROJECT_ID` | Firebase | Project identification | No | Firebase console |
| 36 | `FIREBASE_AUTH_DOMAIN` | Firebase | Auth redirect | No | Firebase console |
| 37 | `S3_BUCKET_NAME` | AWS S3 | File storage | No | AWS console |
| 38 | `S3_ENDPOINT` | S3-compatible (R2, MinIO) | Object storage | No | — |

---

## 4. Vector Databases & Search

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 39 | `PINECONE_API_KEY` | Pinecone | Vector search, RAG | Yes | [app.pinecone.io](https://app.pinecone.io) |
| 40 | `PINECONE_ENVIRONMENT` | Pinecone | Region/pod config | Yes | Pinecone dashboard |
| 41 | `PINECONE_INDEX_NAME` | Pinecone | Index targeting | Yes | Pinecone dashboard |
| 42 | `WEAVIATE_URL` | Weaviate | Alternative vector DB | No | [console.weaviate.cloud](https://console.weaviate.cloud) |
| 43 | `WEAVIATE_API_KEY` | Weaviate | Auth | No | Weaviate dashboard |
| 44 | `QDRANT_URL` | Qdrant | Alternative vector DB | No | [cloud.qdrant.io](https://cloud.qdrant.io) |
| 45 | `QDRANT_API_KEY` | Qdrant | Auth | No | Qdrant dashboard |
| 46 | `ALGOLIA_APP_ID` | Algolia | Full-text search | No | [dashboard.algolia.com](https://dashboard.algolia.com) |
| 47 | `ALGOLIA_API_KEY` | Algolia | Search queries | No | Algolia dashboard |

---

## 5. Authentication & Identity

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 48 | `NEXTAUTH_SECRET` | NextAuth.js | Session signing | Yes | Generate with `openssl rand -base64 32` |
| 49 | `NEXTAUTH_URL` | NextAuth.js | Callback URL | Yes | — |
| 50 | `CLERK_SECRET_KEY` | Clerk | Server auth | No | [dashboard.clerk.com](https://dashboard.clerk.com) |
| 51 | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk | Client auth | No | Clerk dashboard |
| 52 | `AUTH0_CLIENT_ID` | Auth0 | OAuth | No | [manage.auth0.com](https://manage.auth0.com) |
| 53 | `AUTH0_CLIENT_SECRET` | Auth0 | OAuth server | No | Auth0 dashboard |
| 54 | `AUTH0_DOMAIN` | Auth0 | Tenant domain | No | Auth0 dashboard |
| 55 | `GOOGLE_CLIENT_ID` | Google OAuth | Social login | No | [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) |
| 56 | `GOOGLE_CLIENT_SECRET` | Google OAuth | Social login | No | Google Cloud console |
| 57 | `GITHUB_CLIENT_ID` | GitHub OAuth | Social login | No | [github.com/settings/developers](https://github.com/settings/developers) |
| 58 | `GITHUB_CLIENT_SECRET` | GitHub OAuth | Social login | No | GitHub Developer Settings |

---

## 6. Payments & Billing

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 59 | `STRIPE_SECRET_KEY` | Stripe | Payment processing | Yes | [dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys) |
| 60 | `STRIPE_PUBLISHABLE_KEY` | Stripe | Client checkout | Yes | Stripe dashboard |
| 61 | `STRIPE_WEBHOOK_SECRET` | Stripe | Webhook verification | Yes | Stripe dashboard → Webhooks |
| 62 | `LEMON_SQUEEZY_API_KEY` | Lemon Squeezy | Alt payments | No | [app.lemonsqueezy.com/settings/api](https://app.lemonsqueezy.com/settings/api) |

---

## 7. Communication & Messaging

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 63 | `SLACK_BOT_TOKEN` | Slack (Bot) | Agent messaging | Yes | [api.slack.com/apps](https://api.slack.com/apps) |
| 64 | `SLACK_APP_TOKEN` | Slack (Socket Mode) | Real-time events | Yes | Slack app dashboard |
| 65 | `SLACK_SIGNING_SECRET` | Slack | Webhook verification | Yes | Slack app dashboard |
| 66 | `SLACK_WEBHOOK_URL` | Slack (Incoming Webhook) | Notifications, alerts | No | Slack app → Webhooks |
| 67 | `DISCORD_BOT_TOKEN` | Discord | Bot messaging | No | [discord.com/developers/applications](https://discord.com/developers/applications) |
| 68 | `DISCORD_WEBHOOK_URL` | Discord (Webhook) | Notifications | No | Discord channel settings |
| 69 | `TEAMS_WEBHOOK_URL` | Microsoft Teams | Incoming messages | No | Teams channel → Connectors |
| 70 | `TEAMS_TENANT_ID` | Azure AD / Teams | Graph API auth | No | [portal.azure.com](https://portal.azure.com) |
| 71 | `TEAMS_CLIENT_ID` | Azure AD / Teams | Graph API auth | No | Azure AD → App registrations |
| 72 | `TEAMS_CLIENT_SECRET` | Azure AD / Teams | Graph API auth | No | Azure AD → Certificates & secrets |
| 73 | `TWILIO_ACCOUNT_SID` | Twilio | SMS, voice | No | [console.twilio.com](https://console.twilio.com) |
| 74 | `TWILIO_AUTH_TOKEN` | Twilio | API auth | No | Twilio console |
| 75 | `TWILIO_PHONE_NUMBER` | Twilio | Sender ID | No | Twilio console |
| 76 | `SENDGRID_API_KEY` | SendGrid | Transactional email | No | [app.sendgrid.com/settings/api_keys](https://app.sendgrid.com/settings/api_keys) |
| 77 | `RESEND_API_KEY` | Resend | Email delivery | No | [resend.com/api-keys](https://resend.com/api-keys) |
| 78 | `EMAIL_ALERTS_TO` | SMTP / custom | Alert recipient | No | — |

---

## 8. Version Control & CI/CD

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 79 | `GITHUB_TOKEN` | GitHub | API, Actions, PRs | Yes | [github.com/settings/tokens](https://github.com/settings/tokens) |
| 80 | `GITHUB_APP_ID` | GitHub App | Bot integrations | No | GitHub Developer Settings |
| 81 | `GITHUB_APP_PRIVATE_KEY` | GitHub App | JWT signing | No | GitHub App settings |
| 82 | `LINEAR_API_KEY` | Linear | Issue tracking | No | [linear.app/settings/api](https://linear.app/settings/api) |
| 83 | `JIRA_API_TOKEN` | Jira | Issue tracking | No | [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |
| 84 | `JIRA_DOMAIN` | Jira | Instance URL | No | — |

---

## 9. Productivity & Knowledge Management

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 85 | `NOTION_API_KEY` | Notion | Second Brain, docs | Yes | [www.notion.so/my-integrations](https://www.notion.so/my-integrations) |
| 86 | `NOTION_DATABASE_ID` | Notion | Target DB for sync | No | Notion share link |
| 87 | `NOTION_WORKSPACE_ID` | Notion | Workspace scoping | No | Notion settings |
| 88 | `AIRTABLE_API_KEY` | Airtable | Spreadsheet data | No | [airtable.com/account](https://airtable.com/account) |
| 89 | `AIRTABLE_BASE_ID` | Airtable | Base targeting | No | Airtable API docs |
| 90 | `GOOGLE_SHEETS_API_KEY` | Google Sheets | Spreadsheet data | No | Google Cloud console |
| 91 | `GOOGLE_SERVICE_ACCOUNT_JSON` | Google (service acct) | Drive, Sheets, Calendar | No | Google Cloud → Service Accounts |
| 92 | `PIPEDREAM_API_KEY` | Pipedream | Workflow automation | No | [pipedream.com/settings/api-keys](https://pipedream.com/settings/api-keys) |

---

## 10. Trading & Finance

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 93 | `COINBASE_API_KEY` | Coinbase Advanced Trade | Crypto trading algo | Yes* | [coinbase.com/settings/api](https://www.coinbase.com/settings/api) |
| 94 | `COINBASE_API_SECRET` | Coinbase | Trade execution | Yes* | Coinbase API settings |
| 95 | `TRADING_MODE` | Internal config | `paper` / `live` | Yes* | — |
| 96 | `INITIAL_CAPITAL` | Internal config | Starting balance | No | — |
| 97 | `MAX_DAILY_LOSS_PERCENT` | Internal config | Risk management | No | — |
| 98 | `STOP_LOSS_PERCENT` | Internal config | Per-trade risk | No | — |

> *Required only for the trading algorithm projects.

---

## 11. Media & Content

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 99 | `SPOTIFY_CLIENT_ID` | Spotify | Music integration | No | [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) |
| 100 | `SPOTIFY_CLIENT_SECRET` | Spotify | OAuth | No | Spotify dashboard |
| 101 | `TWITTER_API_KEY` | X (Twitter) | Social posting | No | [developer.twitter.com](https://developer.twitter.com) |
| 102 | `TWITTER_API_SECRET` | X (Twitter) | OAuth | No | Twitter developer portal |
| 103 | `TWITTER_BEARER_TOKEN` | X (Twitter) | Read-only API | No | Twitter developer portal |
| 104 | `BEEHIIV_API_KEY` | Beehiiv | Newsletter | No | [app.beehiiv.com](https://app.beehiiv.com) |
| 105 | `SUBSTACK_API_KEY` | Substack | Newsletter | No | — |
| 106 | `YOUTUBE_API_KEY` | YouTube Data API | Video data | No | [console.cloud.google.com](https://console.cloud.google.com) |

---

## 12. Monitoring & Observability

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 107 | `LANGSMITH_API_KEY` | LangSmith | LLM tracing | No | [smith.langchain.com](https://smith.langchain.com) |
| 108 | `LANGSMITH_PROJECT` | LangSmith | Project scoping | No | LangSmith dashboard |
| 109 | `LANGFUSE_PUBLIC_KEY` | Langfuse | LLM observability | No | [cloud.langfuse.com](https://cloud.langfuse.com) |
| 110 | `LANGFUSE_SECRET_KEY` | Langfuse | Server-side tracing | No | Langfuse dashboard |
| 111 | `SENTRY_DSN` | Sentry | Error tracking | No | [sentry.io](https://sentry.io) |
| 112 | `DATADOG_API_KEY` | Datadog | APM, logs | No | [app.datadoghq.com/organization-settings/api-keys](https://app.datadoghq.com/organization-settings/api-keys) |
| 113 | `POSTHOG_API_KEY` | PostHog | Product analytics | No | [posthog.com](https://posthog.com) |
| 114 | `AXIOM_TOKEN` | Axiom | Log aggregation | No | [app.axiom.co](https://app.axiom.co) |

---

## 13. Agent & Orchestration Platforms

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 115 | `CURSOR_API_KEY` | Cursor | Cloud agents | Yes | [cursor.com/settings](https://cursor.com/settings) |
| 116 | `REPLIT_TOKEN` | Replit | Replit agent | No | [replit.com/account](https://replit.com/account) |
| 117 | `MANUS_API_KEY` | Manus | Orchestration agent | No | Manus dashboard |
| 118 | `LANGCHAIN_API_KEY` | LangChain | Chain orchestration | No | [smith.langchain.com](https://smith.langchain.com) |
| 119 | `LANGCHAIN_TRACING_V2` | LangChain | Enable tracing (`true`) | No | — |
| 120 | `LANGCHAIN_PROJECT` | LangChain | Project name | No | — |

---

## 14. Development Tools & IDEs

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 121 | `BLACKBOX_API_KEY` | BLACKBOX AI | Code assistant | No | [blackbox.ai](https://www.blackbox.ai) |
| 122 | `SOURCERY_TOKEN` | Sourcery | Code review | No | [sourcery.ai](https://sourcery.ai) |
| 123 | `CODEX_API_KEY` | OpenAI Codex / custom | Code generation | No | — |
| 124 | `NPM_TOKEN` | npm | Package publishing | No | [npmjs.com/settings/tokens](https://www.npmjs.com/settings/tokens) |
| 125 | `PYPI_TOKEN` | PyPI | Python package publishing | No | [pypi.org/manage/account](https://pypi.org/manage/account) |

---

## 15. Domain & DNS

| # | Variable | Service | Where Used | Required | Docs |
|---|----------|---------|------------|----------|------|
| 126 | `NAMECHEAP_API_KEY` | Namecheap | Domain management | No | [namecheap.com](https://www.namecheap.com) |
| 127 | `GODADDY_API_KEY` | GoDaddy | Domain management | No | [developer.godaddy.com](https://developer.godaddy.com) |

---

## Environment File Templates

### `.env.local` (Next.js / Vercel apps)

```bash
# === AI ===
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
REPLICATE_API_TOKEN=

# === Database ===
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=                    # Neon
REDIS_URL=                       # Upstash

# === Vector DB ===
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
PINECONE_INDEX_NAME=

# === Auth ===
NEXTAUTH_SECRET=
NEXTAUTH_URL=http://localhost:3000

# === Payments ===
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# === Communication ===
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
SLACK_SIGNING_SECRET=

# === Services ===
GITHUB_TOKEN=
NOTION_API_KEY=
LINEAR_API_KEY=
VERCEL_TOKEN=

# === Monitoring ===
LANGSMITH_API_KEY=
SENTRY_DSN=
```

### `.env.trading` (Crypto trading algo)

```bash
# === Coinbase ===
COINBASE_API_KEY=
COINBASE_API_SECRET=
TRADING_MODE=paper               # paper | live
INITIAL_CAPITAL=1000
MAX_DAILY_LOSS_PERCENT=5
STOP_LOSS_PERCENT=2

# === Notifications ===
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
EMAIL_ALERTS_TO=
```

### `.env.agents` (Agent integrations)

```bash
# === Agents ===
CURSOR_API_KEY=
REPLIT_TOKEN=
MANUS_API_KEY=

# === Slack (Socket Mode) ===
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# === Teams (Graph API) ===
TEAMS_TENANT_ID=
TEAMS_CLIENT_ID=
TEAMS_CLIENT_SECRET=
TEAMS_WEBHOOK_URL=

# === LLM Tracing ===
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
LANGCHAIN_TRACING_V2=true
```

---

## Service-to-Channel Mapping

Key Slack channels and their primary service integrations:

| Channel | Primary Services |
|---------|-----------------|
| `#daily-log` | Notion, Google Drive, Outlook, Gmail, Cursor, Claude, ChatGPT |
| `#investment-ops` | Coinbase, Neon, Supabase, Trading algo |
| `#ideas-research` | OpenAI, Anthropic, Replicate, Perplexity |
| `#launch-prep` | Vercel, Stripe, Supabase, GitHub Actions |
| `#announcements` | Slack, Discord, Teams, Beehiiv |
| `#community-feedback` | Linear, GitHub Issues, Notion |
| `#readme` | All agents — Cursor, Claude, Manus, Vercel, Notion AI, Replit |

---

## Security Notes

1. **Never commit secrets.** All `.env` files must be in `.gitignore`.
2. **Use Cursor Cloud Agent Secrets** for CI: [cursor.com/onboard](https://cursor.com/onboard) → Cloud Agents → Secrets.
3. **Rotate keys regularly.** Set calendar reminders for 90-day rotation.
4. **Principle of least privilege.** Use scoped tokens (read-only where possible).
5. **Audit access.** Review active tokens monthly on each provider dashboard.
6. **Vault for production.** Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, Doppler, or Infisical) for production workloads.
7. **Environment separation.** Maintain separate keys for `development`, `staging`, and `production`.

### Quick Checklist

- [ ] All 127 variables documented above reviewed
- [ ] Required keys (`Yes`) provisioned and tested
- [ ] `.env.local` populated for local development
- [ ] Cursor Cloud Agent secrets configured
- [ ] Vercel environment variables set per project
- [ ] Supabase Edge Function secrets configured
- [ ] Neon connection strings verified
- [ ] Redis/Upstash connectivity tested
- [ ] Pinecone index created and API key verified
- [ ] Slack bot installed to workspace with correct scopes
- [ ] GitHub tokens have required repo/org permissions
- [ ] Stripe webhooks pointing to correct endpoints
- [ ] Trading algo in `paper` mode before going live
- [ ] Monitoring (LangSmith/Sentry) receiving events
