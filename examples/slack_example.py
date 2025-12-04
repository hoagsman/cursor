"""
Example: Using the Slack Connector

This example demonstrates how to connect an agent to Slack,
send messages, and listen for incoming messages.

Prerequisites:
1. Create a Slack App at https://api.slack.com/apps
2. Add Bot Token Scopes: chat:write, channels:read, reactions:write
3. For receiving messages, enable Socket Mode and add:
   - Event Subscriptions: message.channels, message.groups, message.im
4. Install the app to your workspace
5. Set environment variables:
   - SLACK_BOT_TOKEN: Bot User OAuth Token (xoxb-...)
   - SLACK_APP_TOKEN: App-Level Token (xapp-...) for Socket Mode
"""

import asyncio
import os
from agent_connectors import SlackConnector, Message


async def simple_send_example():
    """Simple example: Send a message to a Slack channel."""
    
    # Get token from environment
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if not bot_token:
        print("Please set SLACK_BOT_TOKEN environment variable")
        return
    
    # Create and connect
    connector = SlackConnector(bot_token=bot_token)
    
    if await connector.connect():
        print("Connected to Slack!")
        
        # Send a simple text message
        success = await connector.send_text(
            channel="#general",  # or use channel ID like "C1234567890"
            text="Hello from the agent! 🤖"
        )
        
        if success:
            print("Message sent successfully!")
        else:
            print("Failed to send message")
        
        # List available channels
        channels = await connector.get_channels()
        print(f"\nAvailable channels ({len(channels)}):")
        for ch in channels[:5]:  # Show first 5
            print(f"  - #{ch['name']} ({ch['id']})")
        
        await connector.disconnect()
    else:
        print("Failed to connect to Slack")


async def receive_messages_example():
    """Example: Listen for and respond to incoming messages."""
    
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    app_token = os.environ.get("SLACK_APP_TOKEN")
    
    if not bot_token or not app_token:
        print("Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN environment variables")
        return
    
    connector = SlackConnector(
        bot_token=bot_token,
        app_token=app_token
    )
    
    # Define a message handler
    def handle_message(message: Message):
        print(f"Received message from {message.author}: {message.content}")
        
        # You could respond to messages here
        # asyncio.create_task(connector.send_text(
        #     channel=message.channel,
        #     text=f"I received your message: {message.content}",
        #     thread_id=message.metadata.get("raw_event", {}).get("ts")
        # ))
    
    # Register the handler
    connector.register_message_handler(handle_message)
    
    if await connector.connect():
        print("Connected to Slack and listening for messages...")
        print("Press Ctrl+C to stop")
        
        try:
            await connector.start_listening()
        except KeyboardInterrupt:
            print("\nStopping...")
        
        await connector.disconnect()


async def send_rich_message_example():
    """Example: Send a message with Block Kit formatting."""
    
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if not bot_token:
        print("Please set SLACK_BOT_TOKEN environment variable")
        return
    
    connector = SlackConnector(bot_token=bot_token)
    
    if await connector.connect():
        # Create a rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Agent Status Update 🤖"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Status:*\n✅ Online"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Task:*\nProcessing data"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "The agent has completed *47 tasks* today with a success rate of *98.5%*."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "url": "https://example.com/agent/status"
                    }
                ]
            }
        ]
        
        success = await connector.send_blocks(
            channel="#general",
            blocks=blocks,
            text="Agent Status Update"  # Fallback for notifications
        )
        
        if success:
            print("Rich message sent!")
        
        await connector.disconnect()


if __name__ == "__main__":
    # Run the simple example by default
    asyncio.run(simple_send_example())
    
    # Uncomment to run other examples:
    # asyncio.run(receive_messages_example())
    # asyncio.run(send_rich_message_example())
