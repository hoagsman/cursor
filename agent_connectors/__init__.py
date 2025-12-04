"""
Agent Connectors - Enable agents to connect to Slack and Microsoft Teams.

This module provides connectors for agents to communicate through
popular messaging platforms like Slack and Microsoft Teams.
"""

from .base import BaseConnector, Message, MessageType
from .slack_connector import SlackConnector
from .teams_connector import TeamsConnector

__all__ = [
    "BaseConnector",
    "Message",
    "MessageType",
    "SlackConnector",
    "TeamsConnector",
]

__version__ = "0.1.0"
