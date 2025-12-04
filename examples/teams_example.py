"""
Example: Using the Microsoft Teams Connector

This example demonstrates how to connect an agent to Microsoft Teams,
send messages via webhooks or Graph API, and use Adaptive Cards.

Prerequisites for Webhook Mode (simple):
1. In Teams, go to a channel -> Connectors -> Incoming Webhook
2. Create a webhook and copy the URL
3. Set environment variable: TEAMS_WEBHOOK_URL

Prerequisites for Graph API Mode (full features):
1. Register an app in Azure AD (https://portal.azure.com)
2. Add API permissions: ChannelMessage.Send, Channel.ReadBasic.All
3. Create a client secret
4. Set environment variables:
   - TEAMS_TENANT_ID: Your Azure AD tenant ID
   - TEAMS_CLIENT_ID: Application (client) ID
   - TEAMS_CLIENT_SECRET: Client secret value
"""

import asyncio
import os
from agent_connectors import TeamsConnector


async def webhook_example():
    """Simple example: Send messages via incoming webhook."""
    
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("Please set TEAMS_WEBHOOK_URL environment variable")
        return
    
    # Create connector with webhook URL
    connector = TeamsConnector(webhook_url=webhook_url)
    
    if await connector.connect():
        print("Connected to Teams via webhook!")
        
        # Send a simple text message
        success = await connector.send_text(
            channel="",  # Not needed for webhooks
            text="Hello from the agent! 🤖"
        )
        
        if success:
            print("Message sent successfully!")
        else:
            print("Failed to send message")
        
        await connector.disconnect()
    else:
        print("Failed to connect to Teams")


async def adaptive_card_example():
    """Example: Send an Adaptive Card via webhook."""
    
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("Please set TEAMS_WEBHOOK_URL environment variable")
        return
    
    connector = TeamsConnector(webhook_url=webhook_url)
    
    if await connector.connect():
        # Use the helper to create a simple card
        simple_card = TeamsConnector.create_adaptive_card(
            title="Agent Report",
            body_text="The daily processing job completed successfully.",
            actions=[
                {
                    "type": "Action.OpenUrl",
                    "title": "View Report",
                    "url": "https://example.com/reports/daily"
                }
            ]
        )
        
        success = await connector.send_adaptive_card(
            channel="",
            card=simple_card
        )
        
        if success:
            print("Adaptive Card sent!")
        
        # Send a more complex custom card
        custom_card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "Image",
                                    "url": "https://via.placeholder.com/48",
                                    "size": "Small",
                                    "style": "Person"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Agent System",
                                    "weight": "Bolder",
                                    "size": "Medium"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "Status Update",
                                    "spacing": "None",
                                    "isSubtle": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Status", "value": "✅ Online"},
                        {"title": "Tasks Completed", "value": "47"},
                        {"title": "Success Rate", "value": "98.5%"},
                        {"title": "Last Updated", "value": "Just now"}
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Dashboard",
                    "url": "https://example.com/dashboard"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "Logs",
                    "url": "https://example.com/logs"
                }
            ]
        }
        
        await connector.send_adaptive_card(channel="", card=custom_card)
        print("Custom Adaptive Card sent!")
        
        await connector.disconnect()


async def graph_api_example():
    """Example: Use Graph API for full Teams integration."""
    
    tenant_id = os.environ.get("TEAMS_TENANT_ID")
    client_id = os.environ.get("TEAMS_CLIENT_ID")
    client_secret = os.environ.get("TEAMS_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        print("Please set TEAMS_TENANT_ID, TEAMS_CLIENT_ID, and TEAMS_CLIENT_SECRET")
        return
    
    connector = TeamsConnector(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    if await connector.connect():
        print("Connected to Teams via Graph API!")
        
        # List available channels
        channels = await connector.get_channels()
        print(f"\nAvailable channels ({len(channels)}):")
        for ch in channels[:5]:  # Show first 5
            print(f"  - {ch['name']} ({ch['id']})")
        
        if channels:
            # Send a message to the first channel
            channel_id = channels[0]["id"]
            
            success = await connector.send_text(
                channel=channel_id,
                text="Hello from the agent via Graph API! 🤖"
            )
            
            if success:
                print(f"\nMessage sent to {channels[0]['name']}!")
        
        await connector.disconnect()
    else:
        print("Failed to connect to Teams")


if __name__ == "__main__":
    # Run the webhook example by default
    asyncio.run(webhook_example())
    
    # Uncomment to run other examples:
    # asyncio.run(adaptive_card_example())
    # asyncio.run(graph_api_example())
