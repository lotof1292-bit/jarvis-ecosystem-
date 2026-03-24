"""
JARVIS FASE 5 - Remote Module
Módulo de control remoto de dispositivos Android
"""

from .tailscale_deeplink import TailscaleDeepLink
from .termux_agent import TermuxAgent
from .remote_control import RemoteControl

__all__ = [
    'TailscaleDeepLink',
    'TermuxAgent',
    'RemoteControl'
]
