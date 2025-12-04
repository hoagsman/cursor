"""
Example: Multi-Platform Agent

This example demonstrates how to create an agent that can communicate
across both Slack and Microsoft Teams simultaneously.

This is useful for:
- Broadcasting messages to multiple platforms
- Building agents that bridge conversations between platforms
- Centralized notification systems
"""

import asyncio
import os
from typing import Optional
from agent_connectors import SlackConnector, TeamsConnector, Message, BaseConnector


class MultiPlatformAgent:
    """
    An agent that can communicate across multiple messaging platforms.
    """
    
    def __init__(self):
        self.connectors: dict[str, BaseConnector] = {}
        self._running = False
    
    async def add_slack(
        self,
        bot_token: str,
        app_token: Optional[str] = None,
        name: str = "slack"
    ) -> bool:
        """Add a Slack connector to the agent."""
        connector = SlackConnector(
            bot_token=bot_token,
            app_token=app_token,
            name=name
        )
        
        if await connector.connect():
            self.connectors[name] = connector
            print(f"✅ Connected to Slack as '{name}'")
            return True
        
        print(f"❌ Failed to connect to Slack as '{name}'")
        return False
    
    async def add_teams_webhook(
        self,
        webhook_url: str,
        name: str = "teams"
    ) -> bool:
        """Add a Teams webhook connector to the agent."""
        connector = TeamsConnector(
            webhook_url=webhook_url,
            name=name
        )
        
        if await connector.connect():
            self.connectors[name] = connector
            print(f"✅ Connected to Teams (webhook) as '{name}'")
            return True
        
        print(f"❌ Failed to connect to Teams as '{name}'")
        return False
    
    async def add_teams_graph(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        name: str = "teams"
    ) -> bool:
        """Add a Teams Graph API connector to the agent."""
        connector = TeamsConnector(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            name=name
        )
        
        if await connector.connect():
            self.connectors[name] = connector
            print(f"✅ Connected to Teams (Graph API) as '{name}'")
            return True
        
        print(f"❌ Failed to connect to Teams as '{name}'")
        return False
    
    async def broadcast(self, message: str, channels: dict[str, str]) -> dict[str, bool]:
        """
        Broadcast a message to multiple platforms.
        
        Args:
            message: The message text to send.
            channels: A dict mapping connector names to channel identifiers.
                     Example: {"slack": "#general", "teams": ""}
        
        Returns:
            A dict mapping connector names to success status.
        """
        results = {}
        
        tasks = []
        for connector_name, channel in channels.items():
            if connector_name in self.connectors:
                connector = self.connectors[connector_name]
                tasks.append((
                    connector_name,
                    connector.send_text(channel, message)
                ))
        
        for connector_name, task in tasks:
            try:
                results[connector_name] = await task
            except Exception as e:
                print(f"Error sending to {connector_name}: {e}")
                results[connector_name] = False
        
        return results
    
    async def send_to(
        self,
        connector_name: str,
        channel: str,
        message: str
    ) -> bool:
        """Send a message to a specific platform."""
        if connector_name not in self.connectors:
            print(f"Unknown connector: {connector_name}")
            return False
        
        return await self.connectors[connector_name].send_text(channel, message)
    
    def on_message(self, handler):
        """
        Register a message handler for all platforms.
        
        The handler receives the message and the connector name.
        """
        def wrapped_handler(message: Message):
            # Find which connector received this
            for name, connector in self.connectors.items():
                if hasattr(connector, '_bot_user_id'):  # Slack
                    handler(message, name)
                    return
        
        for connector in self.connectors.values():
            connector.register_message_handler(wrapped_handler)
    
    async def disconnect_all(self):
        """Disconnect from all platforms."""
        for name, connector in self.connectors.items():
            await connector.disconnect()
            print(f"Disconnected from {name}")
        
        self.connectors.clear()


async def main():
    """Example usage of the MultiPlatformAgent."""
    
    agent = MultiPlatformAgent()
    
    # Connect to Slack if credentials are available
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if slack_token:
        await agent.add_slack(bot_token=slack_token)
    
    # Connect to Teams via webhook if URL is available
    teams_webhook = os.environ.get("TEAMS_WEBHOOK_URL")
    if teams_webhook:
        await agent.add_teams_webhook(webhook_url=teams_webhook)
    
    if not agent.connectors:
        print("No platforms configured. Please set environment variables:")
        print("  - SLACK_BOT_TOKEN for Slack")
        print("  - TEAMS_WEBHOOK_URL for Teams")
        return
    
    print(f"\nAgent connected to {len(agent.connectors)} platform(s)")
    
    # Broadcast a message to all connected platforms
    channels = {}
    if "slack" in agent.connectors:
        channels["slack"] = "#general"
    if "teams" in agent.connectors:
        channels["teams"] = ""  # Not needed for webhook
    
    print("\nBroadcasting message...")
    results = await agent.broadcast(
        message="🤖 Agent is now online and monitoring!",
        channels=channels
    )
    
    for platform, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {platform}")
    
    # Clean up
    await agent.disconnect_all()


if __name__ == "__main__":
    asyncio.run(main())
