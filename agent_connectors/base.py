"""
Base connector class and common types for agent messaging.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional


class MessageType(Enum):
    """Type of message being sent or received."""
    TEXT = "text"
    FILE = "file"
    REACTION = "reaction"
    THREAD_REPLY = "thread_reply"


@dataclass
class Message:
    """Represents a message sent or received by an agent."""
    content: str
    channel: str
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    message_type: MessageType = MessageType.TEXT
    thread_id: Optional[str] = None
    attachments: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "content": self.content,
            "channel": self.channel,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "message_type": self.message_type.value,
            "thread_id": self.thread_id,
            "attachments": self.attachments,
            "metadata": self.metadata,
        }


class BaseConnector(ABC):
    """
    Abstract base class for messaging platform connectors.
    
    All platform-specific connectors should inherit from this class
    and implement the required abstract methods.
    """
    
    def __init__(self, name: str):
        """
        Initialize the connector.
        
        Args:
            name: A friendly name for this connector instance.
        """
        self.name = name
        self._connected = False
        self._message_handlers: list[Callable[[Message], None]] = []
    
    @property
    def is_connected(self) -> bool:
        """Check if the connector is currently connected."""
        return self._connected
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the messaging platform.
        
        Returns:
            True if connection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the messaging platform.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to the platform.
        
        Args:
            message: The message to send.
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    async def send_text(self, channel: str, text: str, thread_id: Optional[str] = None) -> bool:
        """
        Send a simple text message.
        
        Args:
            channel: The channel/conversation to send to.
            text: The text content of the message.
            thread_id: Optional thread ID for replies.
            
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    async def get_channels(self) -> list[dict[str, Any]]:
        """
        Get a list of available channels/conversations.
        
        Returns:
            List of channel information dictionaries.
        """
        pass
    
    def register_message_handler(self, handler: Callable[[Message], None]) -> None:
        """
        Register a callback function to handle incoming messages.
        
        Args:
            handler: A function that takes a Message and processes it.
        """
        self._message_handlers.append(handler)
    
    def unregister_message_handler(self, handler: Callable[[Message], None]) -> None:
        """
        Unregister a previously registered message handler.
        
        Args:
            handler: The handler function to remove.
        """
        if handler in self._message_handlers:
            self._message_handlers.remove(handler)
    
    def _notify_handlers(self, message: Message) -> None:
        """
        Notify all registered handlers about a new message.
        
        Args:
            message: The received message.
        """
        for handler in self._message_handlers:
            try:
                handler(message)
            except Exception as e:
                # Log error but don't stop processing
                print(f"Error in message handler: {e}")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, connected={self._connected})"
