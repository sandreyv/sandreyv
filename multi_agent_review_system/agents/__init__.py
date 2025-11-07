"""Модуль со всеми специализированными агентами"""

from .meta_agent import MetaAgent
from .texture_analyzers import TextureAnalyzer1, TextureAnalyzer2, TextureAnalyzer3
from .chief_editor import ChiefEditorAgent
from .researchers import FactCheckerAgent, GeneralResearcherAgent, PostGeneralResearcherAgent
from .style_agent import StyleAgent
from .chief_reviewer import ChiefReviewerAgent
from .corrector import CorrectorAgent

__all__ = [
    'MetaAgent',
    'TextureAnalyzer1',
    'TextureAnalyzer2',
    'TextureAnalyzer3',
    'ChiefEditorAgent',
    'FactCheckerAgent',
    'GeneralResearcherAgent',
    'PostGeneralResearcherAgent',
    'StyleAgent',
    'ChiefReviewerAgent',
    'CorrectorAgent',
]
