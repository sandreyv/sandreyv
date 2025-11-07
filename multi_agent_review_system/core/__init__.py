"""Core модуль многоагентной системы"""

from .base_agent import BaseAgent, TextDocument, Comment
from .coordinator import AgentCoordinator

__all__ = ['BaseAgent', 'TextDocument', 'Comment', 'AgentCoordinator']
