"""
Агент Шеф-редактор.
Анализирует смыслы, подачу, логику изложения, фактологию.
Принимает решения о комментариях предыдущих агентов.
"""

from ..core.base_agent import BaseAgent, TextDocument


class ChiefEditorAgent(BaseAgent):
    """Агент Шеф-редактор"""

    def __init__(self, api_key=None):
        super().__init__(name="Агент Шеф-редактор", api_key=api_key)

    def get_system_prompt(self) -> str:
        return """Ты — Шеф-редактор, главный по смыслам и логике текста.

Твоя задача:
1. Оценить текст с точки зрения:
   - Смыслов и главной идеи
   - Подачи материала
   - Логики изложения
   - Фактологических пробелов (недостаток информации)
   - Фактологических перегрузок (избыток деталей)

2. Изучить все комментарии от Агентов Анализаторов фактуры

3. Принять решение по каждому комментарию:
   - Оставить, если комментарий ценный и конструктивный
   - Удалить, если комментарий избыточный, спорный или не соответствует общей концепции

4. Оставить свои комментарии в формате:
   [ШЕФРЕД-КОММЕНТАРИЙ] <позиция>: <комментарий>

ВАЖНО:
- Ты принимаешь стратегические решения о направлении доработки текста
- Фокусируйся на общей картине, а не на мелких деталях
- Будь объективным и взвешенным в оценках

Для удаления комментариев используй формат:
[УДАЛИТЬ КОММЕНТАРИЙ] <имя агента>, <позиция>: <причина удаления>
"""

    def process(self, document: TextDocument) -> TextDocument:
        self.log("Начинаем работу Шеф-редактора")

        prompt = f"""Проанализируй текст и комментарии как Шеф-редактор:

{self.prepare_document_for_prompt(document)}

Задачи:
1. Оцени текст по смыслам, подаче, логике, фактологии
2. Изучи все комментарии Агентов Анализаторов
3. Реши, какие комментарии оставить, а какие удалить (укажи причину)
4. Добавь свои комментарии, если нужно

Используй указанные форматы для комментариев и удалений."""

        messages = [{"role": "user", "content": prompt}]
        response = self.call_claude(messages, max_tokens=5000)

        # Обработка ответа
        self._process_response(response, document)

        self.log(f"Работа завершена. Всего комментариев: {len(document.get_active_comments())}")

        return document

    def _process_response(self, response: str, document: TextDocument):
        """Обработка ответа шеф-редактора"""
        import re

        # Парсим команды на удаление комментариев
        delete_pattern = r'\[УДАЛИТЬ КОММЕНТАРИЙ\]\s*([^,]+),\s*([^:]+):\s*(.+?)(?=\[|$)'
        delete_matches = re.finditer(delete_pattern, response, re.DOTALL)

        for match in delete_matches:
            agent_name = match.group(1).strip()
            position = match.group(2).strip()
            reason = match.group(3).strip()

            # Находим и удаляем комментарий
            for comment in document.comments:
                if (comment.agent_name == agent_name and
                    comment.position == position and
                    comment.status == 'active'):
                    comment.status = 'removed'
                    self.log(f"Удалён комментарий от {agent_name} ({position}): {reason}")
                    break

        # Парсим новые комментарии шеф-редактора
        comment_pattern = r'\[ШЕФРЕД-КОММЕНТАРИЙ\]\s*([^:]+):\s*(.+?)(?=\[|$)'
        comment_matches = re.finditer(comment_pattern, response, re.DOTALL)

        for match in comment_matches:
            position = match.group(1).strip()
            comment_text = match.group(2).strip()

            from ..core.base_agent import Comment
            comment = Comment(
                agent_name=self.name,
                position=position,
                comment_text=comment_text,
                comment_type='logic'
            )
            document.add_comment(comment)
            self.log(f"Добавлен комментарий: {position}")
