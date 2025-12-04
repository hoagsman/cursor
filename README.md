# Cursor

[Cursor](https://cursor.com) is a code editor built for programming with AI.

Creating new posts on [the forum](https://forum.cursor.com/) for bugs or feature requests is much appreciated 🙂 Feel free to react to the ones you'd like us to prioritize.

## Getting Started

Head over to [our website](https://cursor.com/) to download and try out the editor.

## Features

[See here](https://cursor.com/features) for more info on Cursor's features.

## Agent Connectors

Enable your agents to communicate through Slack and Microsoft Teams.

### Installation

```bash
pip install -r requirements.txt
```

### Quick Start

**Slack:**
```python
from agent_connectors import SlackConnector

connector = SlackConnector(bot_token="xoxb-your-token")
await connector.connect()
await connector.send_text("#general", "Hello from agent!")
```

**Microsoft Teams:**
```python
from agent_connectors import TeamsConnector

connector = TeamsConnector(webhook_url="https://your-webhook-url")
await connector.connect()
await connector.send_text("", "Hello from agent!")
```

### Documentation

See the full documentation in [docs/AGENT_CONNECTORS.md](docs/AGENT_CONNECTORS.md).

### Examples

- [Slack Examples](examples/slack_example.py)
- [Teams Examples](examples/teams_example.py)
- [Multi-Platform Agent](examples/multi_platform_agent.py)
