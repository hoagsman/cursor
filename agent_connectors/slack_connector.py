"""
Slack connector for agent messaging.

This module provides a connector for agents to send and receive
messages through Slack using the Slack SDK.
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from .base import BaseConnector, Message, MessageType

try:
    from slack_sdk.web.async_client import AsyncWebClient
    from slack_sdk.socket_mode.aiohttp import SocketModeClient
    from slack_sdk.socket_mode.request import SocketModeRequest
    from slack_sdk.socket_mode.response import SocketModeResponse
    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False


class SlackConnector(BaseConnector):
    """
    Connector for Slack messaging platform.
    
    Supports both sending messages via the Web API and receiving
    messages in real-time via Socket Mode.
    
    Example:
        ```python
        connector = SlackConnector(
            bot_token="xoxb-your-bot-token",
            app_token="xapp-your-app-token"  # For Socket Mode
        )
        await connector.connect()
        await connector.send_text("#general", "Hello from agent!")
        ```
    """
    
    def __init__(
        self,
        bot_token: str,
        app_token: Optional[str] = None,
        name: str = "slack"
    ):
        """
        Initialize the Slack connector.
        
        Args:
            bot_token: Slack bot token (xoxb-...).
            app_token: Slack app-level token for Socket Mode (xapp-...).
                      Required for receiving real-time messages.
            name: A friendly name for this connector instance.
        """
        super().__init__(name)
        
        if not SLACK_SDK_AVAILABLE:
            raise ImportError(
                "slack_sdk is required for SlackConnector. "
                "Install it with: pip install slack_sdk aiohttp"
            )
        
        self._bot_token = bot_token
        self._app_token = app_token
        self._web_client: Optional[AsyncWebClient] = None
        self._socket_client: Optional[SocketModeClient] = None
        self._bot_user_id: Optional[str] = None
    
    async def connect(self) -> bool:
        """
        Connect to Slack.
        
        Establishes connection to the Slack Web API and optionally
        starts Socket Mode for real-time message receiving.
        
        Returns:
            True if connection was successful, False otherwise.
        """
        try:
            # Initialize the web client
            self._web_client = AsyncWebClient(token=self._bot_token)
            
            # Test the connection and get bot info
            auth_response = await self._web_client.auth_test()
            if not auth_response["ok"]:
                return False
            
            self._bot_user_id = auth_response["user_id"]
            
            # Set up Socket Mode if app token is provided
            if self._app_token:
                self._socket_client = SocketModeClient(
                    app_token=self._app_token,
                    web_client=self._web_client
                )
                self._socket_client.socket_mode_request_listeners.append(
                    self._handle_socket_event
                )
                await self._socket_client.connect()
            
            self._connected = True
            return True
            
        except Exception as e:
            print(f"Failed to connect to Slack: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Slack.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        try:
            if self._socket_client:
                await self._socket_client.disconnect()
                self._socket_client = None
            
            self._web_client = None
            self._connected = False
            return True
            
        except Exception as e:
            print(f"Failed to disconnect from Slack: {e}")
            return False
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to Slack.
        
        Args:
            message: The message to send.
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not self._web_client:
            return False
        
        try:
            kwargs: dict[str, Any] = {
                "channel": message.channel,
                "text": message.content,
            }
            
            if message.thread_id:
                kwargs["thread_ts"] = message.thread_id
            
            if message.attachments:
                kwargs["attachments"] = message.attachments
            
            # Handle blocks from metadata if provided
            if "blocks" in message.metadata:
                kwargs["blocks"] = message.metadata["blocks"]
            
            response = await self._web_client.chat_postMessage(**kwargs)
            return response["ok"]
            
        except Exception as e:
            print(f"Failed to send Slack message: {e}")
            return False
    
    async def send_text(
        self,
        channel: str,
        text: str,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Send a simple text message to a Slack channel.
        
        Args:
            channel: The channel ID or name (e.g., "#general" or "C1234567890").
            text: The text content of the message.
            thread_id: Optional thread timestamp for replies.
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        message = Message(
            content=text,
            channel=channel,
            thread_id=thread_id
        )
        return await self.send_message(message)
    
    async def send_blocks(
        self,
        channel: str,
        blocks: list[dict[str, Any]],
        text: str = "",
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Send a message with Block Kit blocks.
        
        Args:
            channel: The channel ID or name.
            blocks: List of Block Kit block elements.
            text: Fallback text for notifications.
            thread_id: Optional thread timestamp for replies.
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        message = Message(
            content=text,
            channel=channel,
            thread_id=thread_id,
            metadata={"blocks": blocks}
        )
        return await self.send_message(message)
    
    async def get_channels(self) -> list[dict[str, Any]]:
        """
        Get a list of available Slack channels.
        
        Returns:
            List of channel information dictionaries.
        """
        if not self._web_client:
            return []
        
        try:
            channels = []
            cursor = None
            
            while True:
                response = await self._web_client.conversations_list(
                    cursor=cursor,
                    types="public_channel,private_channel"
                )
                
                if not response["ok"]:
                    break
                
                for channel in response.get("channels", []):
                    channels.append({
                        "id": channel["id"],
                        "name": channel["name"],
                        "is_private": channel.get("is_private", False),
                        "is_member": channel.get("is_member", False),
                    })
                
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            
            return channels
            
        except Exception as e:
            print(f"Failed to get Slack channels: {e}")
            return []
    
    async def upload_file(
        self,
        channel: str,
        file_path: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Upload a file to a Slack channel.
        
        Args:
            channel: The channel ID to upload to.
            file_path: Path to the file to upload.
            title: Optional title for the file.
            initial_comment: Optional comment to include with the file.
            thread_id: Optional thread timestamp for replies.
            
        Returns:
            True if the file was uploaded successfully, False otherwise.
        """
        if not self._web_client:
            return False
        
        try:
            kwargs: dict[str, Any] = {
                "channels": channel,
                "file": file_path,
            }
            
            if title:
                kwargs["title"] = title
            if initial_comment:
                kwargs["initial_comment"] = initial_comment
            if thread_id:
                kwargs["thread_ts"] = thread_id
            
            response = await self._web_client.files_upload_v2(**kwargs)
            return response["ok"]
            
        except Exception as e:
            print(f"Failed to upload file to Slack: {e}")
            return False
    
    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> bool:
        """
        Add a reaction to a message.
        
        Args:
            channel: The channel ID containing the message.
            timestamp: The timestamp of the message to react to.
            emoji: The emoji name (without colons).
            
        Returns:
            True if the reaction was added successfully, False otherwise.
        """
        if not self._web_client:
            return False
        
        try:
            response = await self._web_client.reactions_add(
                channel=channel,
                timestamp=timestamp,
                name=emoji
            )
            return response["ok"]
            
        except Exception as e:
            print(f"Failed to add Slack reaction: {e}")
            return False
    
    async def _handle_socket_event(
        self,
        client: SocketModeClient,
        request: SocketModeRequest
    ) -> None:
        """Handle incoming Socket Mode events."""
        # Acknowledge the event
        response = SocketModeResponse(envelope_id=request.envelope_id)
        await client.send_socket_mode_response(response)
        
        # Process message events
        if request.type == "events_api":
            event = request.payload.get("event", {})
            
            if event.get("type") == "message" and "subtype" not in event:
                # Skip bot's own messages
                if event.get("user") == self._bot_user_id:
                    return
                
                message = Message(
                    content=event.get("text", ""),
                    channel=event.get("channel", ""),
                    author=event.get("user"),
                    timestamp=datetime.fromtimestamp(float(event.get("ts", 0))),
                    message_type=MessageType.THREAD_REPLY if event.get("thread_ts") else MessageType.TEXT,
                    thread_id=event.get("thread_ts"),
                    metadata={"raw_event": event}
                )
                
                self._notify_handlers(message)
    
    async def start_listening(self) -> None:
        """
        Start listening for incoming messages.
        
        This method blocks until disconnect() is called.
        Requires an app_token to be provided during initialization.
        """
        if not self._socket_client:
            raise RuntimeError(
                "Socket Mode client not initialized. "
                "Provide an app_token when creating the connector."
            )
        
        # Keep the connection alive
        while self._connected:
            await asyncio.sleep(1)
