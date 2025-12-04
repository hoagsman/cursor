# Agent Connectors

Enable your agents to communicate through Slack and Microsoft Teams.

## Overview

The `agent_connectors` module provides a unified interface for agents to send and receive messages through popular messaging platforms. It includes:

- **SlackConnector**: Full Slack integration via Web API and Socket Mode
- **TeamsConnector**: Microsoft Teams integration via webhooks or Graph API
- **BaseConnector**: Abstract base class for building custom connectors

## Installation

```bash
pip install -r requirements.txt
```

### Dependencies

- `aiohttp>=3.8.0` - Async HTTP client (required)
- `slack_sdk>=3.21.0` - Slack SDK (required for Slack)

## Quick Start

### Slack

```python
import asyncio
from agent_connectors import SlackConnector

async def main():
    connector = SlackConnector(bot_token="xoxb-your-token")
    await connector.connect()
    await connector.send_text("#general", "Hello from agent!")
    await connector.disconnect()

asyncio.run(main())
```

### Microsoft Teams (Webhook)

```python
import asyncio
from agent_connectors import TeamsConnector

async def main():
    connector = TeamsConnector(webhook_url="https://your-webhook-url")
    await connector.connect()
    await connector.send_text("", "Hello from agent!")
    await connector.disconnect()

asyncio.run(main())
```

## Slack Connector

### Setup

1. Create a Slack App at https://api.slack.com/apps
2. Add Bot Token Scopes:
   - `chat:write` - Send messages
   - `channels:read` - List channels
   - `reactions:write` - Add reactions
   - `files:write` - Upload files
3. For real-time messages, enable Socket Mode and add Event Subscriptions
4. Install the app to your workspace
5. Copy the Bot User OAuth Token (`xoxb-...`)

### Features

| Feature | Method | Description |
|---------|--------|-------------|
| Send text | `send_text()` | Send a simple text message |
| Send blocks | `send_blocks()` | Send Block Kit formatted messages |
| Upload file | `upload_file()` | Upload a file to a channel |
| Add reaction | `add_reaction()` | Add emoji reaction to a message |
| List channels | `get_channels()` | Get available channels |
| Receive messages | `register_message_handler()` | Handle incoming messages |

### Example: Rich Messages

```python
blocks = [
    {
        "type": "header",
        "text": {"type": "plain_text", "text": "Status Update"}
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "Task completed *successfully*!"}
    }
]

await connector.send_blocks("#updates", blocks)
```

### Example: Listening for Messages

```python
from agent_connectors import SlackConnector, Message

def handle_message(message: Message):
    print(f"Received: {message.content}")

connector = SlackConnector(
    bot_token="xoxb-...",
    app_token="xapp-..."  # Required for Socket Mode
)

connector.register_message_handler(handle_message)
await connector.connect()
await connector.start_listening()
```

## Teams Connector

### Setup Options

#### Option 1: Incoming Webhook (Simple)

Best for: One-way notifications, alerts, status updates

1. In Teams, go to a channel → ⋯ → Connectors
2. Add "Incoming Webhook"
3. Configure and copy the webhook URL

#### Option 2: Graph API (Full Features)

Best for: Two-way communication, listing channels, replying to messages

1. Register an app in Azure Portal
2. Add API permissions:
   - `ChannelMessage.Send`
   - `Channel.ReadBasic.All`
   - `Team.ReadBasic.All`
3. Create a client secret
4. Note your Tenant ID, Client ID, and Client Secret

### Features

| Feature | Mode | Method |
|---------|------|--------|
| Send text | Both | `send_text()` |
| Send Adaptive Card | Both | `send_adaptive_card()` |
| List channels | Graph only | `get_channels()` |
| Reply to message | Graph only | `reply_to_message()` |

### Example: Adaptive Cards

```python
from agent_connectors import TeamsConnector

# Use the helper method
card = TeamsConnector.create_adaptive_card(
    title="Alert",
    body_text="System health check completed.",
    actions=[
        {"type": "Action.OpenUrl", "title": "View", "url": "https://..."}
    ]
)

await connector.send_adaptive_card("", card)
```

### Example: Graph API

```python
connector = TeamsConnector(
    tenant_id="...",
    client_id="...",
    client_secret="..."
)

await connector.connect()

# List channels
channels = await connector.get_channels()
for ch in channels:
    print(f"{ch['team_name']} - {ch['channel_name']}")

# Send to a specific channel
await connector.send_text(
    channel="team-id/channel-id",
    text="Hello!"
)
```

## Building Custom Connectors

Extend `BaseConnector` to add support for other platforms:

```python
from agent_connectors import BaseConnector, Message

class MyConnector(BaseConnector):
    async def connect(self) -> bool:
        # Implement connection logic
        self._connected = True
        return True
    
    async def disconnect(self) -> bool:
        self._connected = False
        return True
    
    async def send_message(self, message: Message) -> bool:
        # Implement sending logic
        return True
    
    async def send_text(self, channel, text, thread_id=None) -> bool:
        return await self.send_message(Message(content=text, channel=channel))
    
    async def get_channels(self):
        return []
```

## Message Object

All connectors use a common `Message` class:

```python
from agent_connectors import Message, MessageType

message = Message(
    content="Hello!",
    channel="#general",
    author="U12345",
    message_type=MessageType.TEXT,
    thread_id=None,
    attachments=[],
    metadata={}
)
```

## Environment Variables

| Variable | Platform | Description |
|----------|----------|-------------|
| `SLACK_BOT_TOKEN` | Slack | Bot User OAuth Token |
| `SLACK_APP_TOKEN` | Slack | App-Level Token (Socket Mode) |
| `TEAMS_WEBHOOK_URL` | Teams | Incoming Webhook URL |
| `TEAMS_TENANT_ID` | Teams | Azure AD Tenant ID |
| `TEAMS_CLIENT_ID` | Teams | Azure AD Client ID |
| `TEAMS_CLIENT_SECRET` | Teams | Azure AD Client Secret |

## Error Handling

All connector methods return boolean success values. For more details, check the console output or wrap calls in try/except:

```python
try:
    success = await connector.send_text("#channel", "message")
    if not success:
        print("Message failed to send")
except Exception as e:
    print(f"Error: {e}")
```

## See Also

- [Slack API Documentation](https://api.slack.com/docs)
- [Microsoft Teams Developer Documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
