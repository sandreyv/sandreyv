"""
Координатор для управления потоком работы между агентами.
Определяет порядок выполнения и передачу данных между агентами.
"""

from typing import List, Dict, Any
from .base_agent import BaseAgent, TextDocument
from datetime import datetime


class AgentCoordinator:
    """Координатор агентов"""

    def __init__(self):
        self.agents: List[BaseAgent] = []
        self.execution_log: List[str] = []

    def register_agent(self, agent: BaseAgent):
        """Зарегистрировать агента в системе"""
        self.agents.append(agent)
        self.log(f"Зарегистрирован агент: {agent.name}")

    def log(self, message: str):
        """Логирование"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [COORDINATOR] {message}"
        self.execution_log.append(log_entry)
        print(log_entry)

    def process_document(self, document: TextDocument) -> Dict[str, Any]:
        """
        Обработать документ через всех зарегистрированных агентов

        Returns:
            Dict с финальным документом и отчётом
        """
        self.log(f"Начинаем обработку документа через {len(self.agents)} агентов")

        for i, agent in enumerate(self.agents, 1):
            self.log(f"Передаём документ агенту {i}/{len(self.agents)}: {agent.name}")

            try:
                # Обработка документа агентом
                document = agent.process(document)

                # Добавляем запись в историю обработки
                document.processing_history.append(
                    f"Обработан агентом: {agent.name} ({datetime.now().isoformat()})"
                )

                self.log(f"Агент {agent.name} завершил обработку")
                self.log(f"Текущее количество комментариев: {len(document.get_active_comments())}")

            except Exception as e:
                self.log(f"ОШИБКА при обработке агентом {agent.name}: {str(e)}")
                raise

        self.log("Обработка завершена")

        # Формируем финальный отчёт
        report = self.generate_report(document)

        return {
            'document': document,
            'report': report,
            'execution_log': self.execution_log
        }

    def generate_report(self, document: TextDocument) -> str:
        """Сгенерировать отчёт о проделанной работе"""
        report_lines = [
            "=" * 80,
            "ОТЧЁТ О ПРОДЕЛАННОЙ РАБОТЕ",
            "=" * 80,
            "",
            f"Исходная длина текста: {len(document.original_text)} символов",
            f"Финальная длина текста: {len(document.current_text)} символов",
            f"Всего комментариев: {len(document.comments)}",
            f"Активных комментариев: {len(document.get_active_comments())}",
            "",
            "=" * 80,
            "АГЕНТЫ, УЧАСТВОВАВШИЕ В ОБРАБОТКЕ:",
            "=" * 80,
            ""
        ]

        for agent in self.agents:
            agent_comments = document.get_comments_by_agent(agent.name)
            report_lines.append(f"- {agent.name}: {len(agent_comments)} комментариев")

        report_lines.extend([
            "",
            "=" * 80,
            "ИСТОРИЯ ОБРАБОТКИ:",
            "=" * 80,
            ""
        ])

        report_lines.extend(document.processing_history)

        report_lines.extend([
            "",
            "=" * 80,
            "АКТИВНЫЕ КОММЕНТАРИИ (если остались):",
            "=" * 80,
            ""
        ])

        active_comments = document.get_active_comments()
        if active_comments:
            for comment in active_comments:
                report_lines.append(str(comment))
        else:
            report_lines.append("Все комментарии были обработаны и удалены.")

        return "\n".join(report_lines)
