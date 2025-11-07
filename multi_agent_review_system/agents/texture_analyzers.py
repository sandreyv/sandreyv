"""
Агенты Анализаторы фактуры (1, 2, 3).
Последовательно анализируют текст на экспертность и оставляют комментарии.
"""

from ..core.base_agent import BaseAgent, TextDocument, Comment
import re


class TextureAnalyzerBase(BaseAgent):
    """Базовый класс для анализаторов фактуры"""

    def __init__(self, name: str, order: int, api_key=None):
        super().__init__(name=name, api_key=api_key)
        self.order = order

    def get_system_prompt(self) -> str:
        return f"""Ты — {self.name}, эксперт по анализу текстов.

Твоя задача:
1. Внимательно прочитать текст
2. Определить контекст и тематику
3. Вжиться в роль эксперта по данному направлению
4. Проверить текст на экспертность, глубину раскрытия темы, точность формулировок
5. Оставить комментарии там, где текст нуждается в доработке

ВАЖНО:
- НЕ правь текст сам
- Оставляй комментарии в формате: [КОММЕНТАРИЙ #N] <позиция в тексте>: <твой комментарий>
- Указывай, ГДЕ (номер абзаца/предложения), ПОЧЕМУ и ЗАЧЕМ нужно подправить
- Будь конструктивным и конкретным

{"Это уже " + str(self.order) + "-й анализ, учитывай комментарии предыдущих агентов." if self.order > 1 else "Ты первый анализируешь текст."}

Формат комментария:
[КОММЕНТАРИЙ #N] Абзац X, предложение Y: <подробное объяснение, что не так и как улучшить>
"""

    def process(self, document: TextDocument) -> TextDocument:
        self.log(f"Начинаем анализ фактуры (уровень {self.order})")

        prompt = f"""Проанализируй текст на экспертность и оставь комментарии:

{self.prepare_document_for_prompt(document)}

Проанализируй текст и оставь свои комментарии в указанном формате.
Если предыдущие агенты уже оставили комментарии, изучи их и добавь свои, если есть что добавить.
Если всё в порядке и добавить нечего, напиши: "КОММЕНТАРИЕВ НЕТ"
"""

        messages = [{"role": "user", "content": prompt}]
        response = self.call_claude(messages, max_tokens=4000)

        # Парсим комментарии из ответа
        if "КОММЕНТАРИЕВ НЕТ" not in response.upper():
            comments = self._parse_comments(response)
            for comment_text, position in comments:
                comment = Comment(
                    agent_name=self.name,
                    position=position,
                    comment_text=comment_text,
                    comment_type='factual'
                )
                document.add_comment(comment)
                self.log(f"Добавлен комментарий: {position}")

        self.log(f"Анализ завершён. Добавлено комментариев: {len(document.get_comments_by_agent(self.name))}")

        return document

    def _parse_comments(self, response: str) -> list:
        """Парсинг комментариев из ответа агента"""
        comments = []

        # Ищем паттерн: [КОММЕНТАРИЙ #N] позиция: текст
        pattern = r'\[КОММЕНТАРИЙ #\d+\]\s*([^:]+):\s*(.+?)(?=\[КОММЕНТАРИЙ #|\Z)'

        matches = re.finditer(pattern, response, re.DOTALL)

        for match in matches:
            position = match.group(1).strip()
            comment_text = match.group(2).strip()
            comments.append((comment_text, position))

        return comments


class TextureAnalyzer1(TextureAnalyzerBase):
    """Первый анализатор фактуры"""

    def __init__(self, api_key=None):
        super().__init__(name="Агент Анализатор фактуры Первый", order=1, api_key=api_key)


class TextureAnalyzer2(TextureAnalyzerBase):
    """Второй анализатор фактуры"""

    def __init__(self, api_key=None):
        super().__init__(name="Агент Анализатор фактуры Второй", order=2, api_key=api_key)


class TextureAnalyzer3(TextureAnalyzerBase):
    """Третий анализатор фактуры"""

    def __init__(self, api_key=None):
        super().__init__(name="Агент Анализатор фактуры Третий", order=3, api_key=api_key)
