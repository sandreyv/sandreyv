"""
Агент по стилистике.
Удаляет комментарии и вычитывает текст по стилистическим правилам.
"""

from ..core.base_agent import BaseAgent, TextDocument


class StyleAgent(BaseAgent):
    """Агент по стилистике"""

    def __init__(self, api_key=None):
        super().__init__(name="Агент по стилистике", api_key=api_key)

    def get_system_prompt(self) -> str:
        return """Ты — Агент по стилистике, эксперт по языку и стилю.

Твоя задача:
1. УДАЛИТЬ ВСЕ КОММЕНТАРИИ, оставленные предыдущими агентами
2. Вычитать текст по следующим правилам:

СТИЛИСТИЧЕСКИЕ ПРАВИЛА:
- Избегать канцеляризмов и бюрократического языка
- Использовать простые и понятные формулировки
- Избегать тавтологий и повторов близко стоящих слов
- Заменять длинные конструкции на короткие
- Избегать пассивного залога где возможно
- Использовать активные глаголы
- Короткие предложения лучше длинных
- Избегать вводных слов без необходимости
- Числительные до 10 писать словами (кроме точных данных)
- Единообразие терминологии

3. Внести необходимые стилистические правки

Формат правок:
[СТИЛЬ] <позиция>: БЫЛО: "<старый вариант>" → СТАЛО: "<новый вариант>"

ВАЖНО:
- Все комментарии должны быть удалены
- Вноси только стилистические правки, не меняй смысл
- Сохраняй все ссылки и источники, добавленные рессёрчерами
- Будь точным и аккуратным
"""

    def process(self, document: TextDocument) -> TextDocument:
        self.log("Начинаем стилистическую вычитку")
        self.log(f"Комментариев перед удалением: {len(document.get_active_comments())}")

        # Удаляем все комментарии
        document.remove_all_comments()
        self.log("Все комментарии удалены")

        # Вычитываем текст
        prompt = f"""Вычитай текст по стилистическим правилам:

{document.current_text}

Примени стилистические правки и верни результат в формате:
[СТИЛЬ] <позиция>: БЫЛО: "<текст>" → СТАЛО: "<текст>"

После всех правок верни ФИНАЛЬНЫЙ ТЕКСТ целиком в блоке:
```ФИНАЛЬНЫЙ_ТЕКСТ
<весь отредактированный текст>
```

Если стилистических правок не требуется, верни текст как есть в блоке ФИНАЛЬНЫЙ_ТЕКСТ.
"""

        messages = [{"role": "user", "content": prompt}]
        response = self.call_claude(messages, max_tokens=10000)

        # Парсим правки и извлекаем финальный текст
        self._apply_style_edits(response, document)

        self.log(f"Стилистическая вычитка завершена")

        return document

    def _apply_style_edits(self, response: str, document: TextDocument):
        """Применение стилистических правок"""
        import re

        # Ищем блок с финальным текстом
        final_text_match = re.search(r'```ФИНАЛЬНЫЙ_ТЕКСТ\s*\n(.*?)\n```', response, re.DOTALL)

        if final_text_match:
            document.current_text = final_text_match.group(1).strip()
            self.log("Применён финальный текст из ответа")
        else:
            # Если нет блока с финальным текстом, применяем правки последовательно
            pattern = r'\[СТИЛЬ\]\s*([^:]+):\s*БЫЛО:\s*"([^"]+)"\s*→\s*СТАЛО:\s*"([^"]+)"'
            matches = re.finditer(pattern, response, re.DOTALL)

            edits_count = 0
            for match in matches:
                position = match.group(1).strip()
                old_text = match.group(2).strip()
                new_text = match.group(3).strip()

                if old_text in document.current_text:
                    document.current_text = document.current_text.replace(old_text, new_text, 1)
                    edits_count += 1
                    self.log(f"Применена правка: {position}")

            self.log(f"Применено стилистических правок: {edits_count}")
