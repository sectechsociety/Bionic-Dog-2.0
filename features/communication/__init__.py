"""
Dog-to-Dog Communication Module
Enables Tom and Jerry to communicate and coordinate actions
"""

from .message_handler import MessageHandler
from .communication_protocol import CommunicationProtocol
from .sync_controller import SyncController

__all__ = ['MessageHandler', 'CommunicationProtocol', 'SyncController']
