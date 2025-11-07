"""
Базовый класс для всех агентов в системе.
Определяет общий интерфейс и функциональность.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import anthropic
import os


@dataclass
class Comment:
    """Комментарий агента к тексту"""
    agent_name: str
    position: str  # Позиция в тексте (номер абзаца, строки, фразы)
    comment_text: str
    comment_type: str  # 'factual', 'style', 'logic', 'research', 'correction'
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source_url: Optional[str] = None  # Для фактчекинга
    status: str = 'active'  # 'active', 'resolved', 'removed'

    def __str__(self):
        result = f"[{self.agent_name}] {self.position}: {self.comment_text}"
        if self.source_url:
            result += f" ({self.source_url})"
        return result


@dataclass
class TextDocument:
    """Документ с текстом и комментариями"""
    original_text: str
    current_text: str
    comments: List[Comment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_history: List[str] = field(default_factory=list)

    def add_comment(self, comment: Comment):
        """Добавить комментарий к документу"""
        self.comments.append(comment)

    def get_comments_by_agent(self, agent_name: str) -> List[Comment]:
        """Получить все комментарии от конкретного агента"""
        return [c for c in self.comments if c.agent_name == agent_name]

    def get_active_comments(self) -> List[Comment]:
        """Получить все активные комментарии"""
        return [c for c in self.comments if c.status == 'active']

    def remove_all_comments(self):
        """Удалить все комментарии"""
        for comment in self.comments:
            comment.status = 'removed'


class BaseAgent(ABC):
    """Базовый класс для всех агентов"""

    def __init__(self, name: str, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        self.name = name
        self.model = model
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "API ключ Anthropic не найден. "
                "Установите переменную окружения ANTHROPIC_API_KEY или передайте api_key явно."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.processing_log: List[str] = []

    def log(self, message: str):
        """Логирование действий агента"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{self.name}] {message}"
        self.processing_log.append(log_entry)
        print(log_entry)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Получить системный промпт для агента"""
        pass

    @abstractmethod
    def process(self, document: TextDocument) -> TextDocument:
        """
        Обработать документ.
        Каждый агент реализует свою логику обработки.
        """
        pass

    def call_claude(self, messages: List[Dict[str, str]], max_tokens: int = 8000) -> str:
        """Вызов Claude API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.get_system_prompt(),
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            self.log(f"Ошибка при вызове Claude API: {str(e)}")
            raise

    def prepare_document_for_prompt(self, document: TextDocument) -> str:
        """Подготовить документ для отправки в промпт"""
        result = f"=== ТЕКСТ ===\n{document.current_text}\n\n"

        active_comments = document.get_active_comments()
        if active_comments:
            result += "=== КОММЕНТАРИИ ПРЕДЫДУЩИХ АГЕНТОВ ===\n"
            for comment in active_comments:
                result += f"{comment}\n"
            result += "\n"

        if document.processing_history:
            result += "=== ИСТОРИЯ ОБРАБОТКИ ===\n"
            result += "\n".join(document.processing_history[-5:])  # Последние 5 записей
            result += "\n\n"

        return result
