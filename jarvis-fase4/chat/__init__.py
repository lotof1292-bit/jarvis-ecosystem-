"""
JARVIS FASE 4 - Chat Module
Sistema de chat híbrido local + Manus
"""

from .local_chat_engine import LocalChatEngine
from .complexity_detector import ComplexityDetector, ComplexityLevel
from .manus_connector import ManusConnector

__all__ = [
    'LocalChatEngine',
    'ComplexityDetector',
    'ComplexityLevel',
    'ManusConnector'
]
