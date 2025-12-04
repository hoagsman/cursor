"""
Microsoft Teams connector for agent messaging.

This module provides a connector for agents to send and receive
messages through Microsoft Teams using the Bot Framework SDK
and Microsoft Graph API.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional

from .base import BaseConnector, Message, MessageType

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class TeamsConnector(BaseConnector):
    """
    Connector for Microsoft Teams messaging platform.
    
    Supports sending messages via incoming webhooks for simple use cases,
    or via the Microsoft Graph API for full functionality including
    reading messages and managing channels.
    
    Example using webhook (simple):
        ```python
        connector = TeamsConnector(
            webhook_url="https://your-org.webhook.office.com/..."
        )
        await connector.connect()
        await connector.send_text("", "Hello from agent!")  # Channel not needed for webhook
        ```
    
    Example using Graph API (full features):
        ```python
        connector = TeamsConnector(
            tenant_id="your-tenant-id",
            client_id="your-client-id",
            client_secret="your-client-secret"
        )
        await connector.connect()
        await connector.send_text("channel-id", "Hello from agent!")
        ```
    """
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        name: str = "teams"
    ):
        """
        Initialize the Teams connector.
        
        For simple webhook-based messaging, provide only webhook_url.
        For full Graph API access, provide tenant_id, client_id, and client_secret.
        
        Args:
            webhook_url: Incoming webhook URL for simple message sending.
            tenant_id: Azure AD tenant ID for Graph API authentication.
            client_id: Azure AD application (client) ID.
            client_secret: Azure AD client secret.
            name: A friendly name for this connector instance.
        """
        super().__init__(name)
        
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for TeamsConnector. "
                "Install it with: pip install aiohttp"
            )
        
        self._webhook_url = webhook_url
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Determine mode based on provided credentials
        self._use_webhook = webhook_url is not None
        self._use_graph = all([tenant_id, client_id, client_secret])
        
        if not self._use_webhook and not self._use_graph:
            raise ValueError(
                "Either webhook_url or (tenant_id, client_id, client_secret) "
                "must be provided."
            )
    
    async def connect(self) -> bool:
        """
        Connect to Microsoft Teams.
        
        For webhook mode, this just initializes the HTTP session.
        For Graph API mode, this authenticates and obtains an access token.
        
        Returns:
            True if connection was successful, False otherwise.
        """
        try:
            self._session = aiohttp.ClientSession()
            
            if self._use_graph:
                # Authenticate with Azure AD
                if not await self._authenticate():
                    await self._session.close()
                    return False
            
            self._connected = True
            return True
            
        except Exception as e:
            print(f"Failed to connect to Teams: {e}")
            if self._session:
                await self._session.close()
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Microsoft Teams.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self._access_token = None
            self._token_expiry = None
            self._connected = False
            return True
            
        except Exception as e:
            print(f"Failed to disconnect from Teams: {e}")
            return False
    
    async def _authenticate(self) -> bool:
        """Authenticate with Azure AD and obtain an access token."""
        if not self._session:
            return False
        
        try:
            token_url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
            
            data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": "https://graph.microsoft.com/.default"
            }
            
            async with self._session.post(token_url, data=data) as response:
                if response.status != 200:
                    return False
                
                result = await response.json()
                self._access_token = result["access_token"]
                # Token typically expires in 1 hour
                expires_in = result.get("expires_in", 3600)
                self._token_expiry = datetime.now()
                
                return True
                
        except Exception as e:
            print(f"Failed to authenticate with Azure AD: {e}")
            return False
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token, refreshing if necessary."""
        if not self._use_graph:
            return True
        
        # Re-authenticate if token is expired or about to expire
        if self._token_expiry is None or self._access_token is None:
            return await self._authenticate()
        
        return True
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to Microsoft Teams.
        
        Args:
            message: The message to send.
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if self._use_webhook:
            return await self._send_webhook_message(message)
        else:
            return await self._send_graph_message(message)
    
    async def _send_webhook_message(self, message: Message) -> bool:
        """Send a message via incoming webhook."""
        if not self._session or not self._webhook_url:
            return False
        
        try:
            # Build adaptive card or simple message
            if message.metadata.get("adaptive_card"):
                payload = {
                    "type": "message",
                    "attachments": [
                        {
                            "contentType": "application/vnd.microsoft.card.adaptive",
                            "content": message.metadata["adaptive_card"]
                        }
                    ]
                }
            else:
                payload = {
                    "text": message.content
                }
            
            async with self._session.post(
                self._webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"Failed to send Teams webhook message: {e}")
            return False
    
    async def _send_graph_message(self, message: Message) -> bool:
        """Send a message via Microsoft Graph API."""
        if not self._session or not await self._ensure_authenticated():
            return False
        
        try:
            # Channel format: team_id/channel_id
            if "/" in message.channel:
                team_id, channel_id = message.channel.split("/", 1)
            else:
                print("Channel must be in format: team_id/channel_id")
                return False
            
            url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
            
            body: dict[str, Any] = {
                "body": {
                    "content": message.content,
                    "contentType": "text"
                }
            }
            
            # Support HTML content
            if message.metadata.get("content_type") == "html":
                body["body"]["contentType"] = "html"
            
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }
            
            async with self._session.post(url, json=body, headers=headers) as response:
                return response.status in (200, 201)
                
        except Exception as e:
            print(f"Failed to send Teams Graph message: {e}")
            return False
    
    async def send_text(
        self,
        channel: str,
        text: str,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Send a simple text message to a Teams channel.
        
        For webhook mode, the channel parameter is ignored.
        For Graph API mode, use format: "team_id/channel_id".
        
        Args:
            channel: The channel identifier (ignored for webhook mode).
            text: The text content of the message.
            thread_id: Optional thread ID for replies (Graph API only).
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        message = Message(
            content=text,
            channel=channel,
            thread_id=thread_id
        )
        return await self.send_message(message)
    
    async def send_adaptive_card(
        self,
        channel: str,
        card: dict[str, Any],
        fallback_text: str = ""
    ) -> bool:
        """
        Send an Adaptive Card to a Teams channel.
        
        Args:
            channel: The channel identifier.
            card: The Adaptive Card JSON structure.
            fallback_text: Fallback text for clients that don't support cards.
            
        Returns:
            True if the card was sent successfully, False otherwise.
        """
        message = Message(
            content=fallback_text,
            channel=channel,
            metadata={"adaptive_card": card}
        )
        return await self.send_message(message)
    
    async def get_channels(self) -> list[dict[str, Any]]:
        """
        Get a list of available Teams channels.
        
        This method requires Graph API credentials.
        
        Returns:
            List of channel information dictionaries.
        """
        if not self._use_graph:
            print("get_channels requires Graph API credentials")
            return []
        
        if not self._session or not await self._ensure_authenticated():
            return []
        
        try:
            channels = []
            
            # First, get all teams the app has access to
            teams_url = "https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')"
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }
            
            async with self._session.get(teams_url, headers=headers) as response:
                if response.status != 200:
                    return []
                
                teams_data = await response.json()
                
                for team in teams_data.get("value", []):
                    team_id = team["id"]
                    team_name = team.get("displayName", "Unknown")
                    
                    # Get channels for each team
                    channels_url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
                    
                    async with self._session.get(channels_url, headers=headers) as ch_response:
                        if ch_response.status == 200:
                            channels_data = await ch_response.json()
                            
                            for channel in channels_data.get("value", []):
                                channels.append({
                                    "id": f"{team_id}/{channel['id']}",
                                    "name": f"{team_name} - {channel.get('displayName', 'Unknown')}",
                                    "team_id": team_id,
                                    "team_name": team_name,
                                    "channel_id": channel["id"],
                                    "channel_name": channel.get("displayName", "Unknown"),
                                })
            
            return channels
            
        except Exception as e:
            print(f"Failed to get Teams channels: {e}")
            return []
    
    async def reply_to_message(
        self,
        channel: str,
        message_id: str,
        text: str
    ) -> bool:
        """
        Reply to a specific message in a Teams channel.
        
        This method requires Graph API credentials.
        
        Args:
            channel: The channel identifier (format: team_id/channel_id).
            message_id: The ID of the message to reply to.
            text: The reply text.
            
        Returns:
            True if the reply was sent successfully, False otherwise.
        """
        if not self._use_graph:
            print("reply_to_message requires Graph API credentials")
            return False
        
        if not self._session or not await self._ensure_authenticated():
            return False
        
        try:
            if "/" not in channel:
                print("Channel must be in format: team_id/channel_id")
                return False
            
            team_id, channel_id = channel.split("/", 1)
            url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
            
            body = {
                "body": {
                    "content": text,
                    "contentType": "text"
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }
            
            async with self._session.post(url, json=body, headers=headers) as response:
                return response.status in (200, 201)
                
        except Exception as e:
            print(f"Failed to send Teams reply: {e}")
            return False
    
    @staticmethod
    def create_adaptive_card(
        title: str,
        body_text: str,
        actions: Optional[list[dict[str, Any]]] = None
    ) -> dict[str, Any]:
        """
        Helper method to create a simple Adaptive Card.
        
        Args:
            title: The card title.
            body_text: The main body text.
            actions: Optional list of action buttons.
            
        Returns:
            An Adaptive Card JSON structure.
        """
        card: dict[str, Any] = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": title,
                    "weight": "Bolder",
                    "size": "Large"
                },
                {
                    "type": "TextBlock",
                    "text": body_text,
                    "wrap": True
                }
            ]
        }
        
        if actions:
            card["actions"] = actions
        
        return card
