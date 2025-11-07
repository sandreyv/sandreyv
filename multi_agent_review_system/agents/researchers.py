"""
Агенты-рессёрчеры для проверки фактов и поиска информации.
Включает: FactCheckerAgent, GeneralResearcherAgent, PostGeneralResearcherAgent
"""

from ..core.base_agent import BaseAgent, TextDocument, Comment
import re


class FactCheckerAgent(BaseAgent):
    """
    Агент-рессёрчер-фактчекер.
    Детально проверяет каждое слово, факт, утверждение, число.
    """

    def __init__(self, api_key=None):
        super().__init__(name="Агент-рессёрчер-фактчекер", api_key=api_key)

    def get_system_prompt(self) -> str:
        return """Ты — Агент-рессёрчер-фактчекер, эксперт по проверке фактов.

Твоя задача:
1. Раскладывать текст на составные части: блоки → абзацы → строки → предложения → фразы → слова
2. Проверять каждое утверждение, факт, число, техническое слово, аббревиатуру
3. Для каждого факта указывать:
   - ✓ ПОДТВЕРЖДЕНО: <краткая справка> (URL: <ссылка>)
   - × НЕ ПОДТВЕРЖДЕНО: <что именно не удалось проверить>
   - ? ТРЕБУЕТ ПРОВЕРКИ: <что нужно уточнить>

4. Добавлять комментарии в формате:
   [ФАКТЧЕК] <позиция в тексте>: <результат проверки>

ВАЖНО:
- Проверяй КАЖДОЕ утверждение, которое можно проверить
- Ищи только АВТОРИТЕТНЫЕ и ПЕРВОИСТОЧНИКИ (не перепечатки)
- Если факт не подтверждается — обязательно отметь это
- Будь дотошным и внимательным

Формат ответа:
[ФАКТЧЕК] <позиция>: <результат проверки> (URL: <ссылка> или × НЕ ПОДТВЕРЖДЕНО)
"""

    def process(self, document: TextDocument) -> TextDocument:
        self.log("Начинаем фактчекинг")

        # Разбиваем текст на предложения для анализа
        sentences = self._split_into_sentences(document.current_text)

        self.log(f"Текст разбит на {len(sentences)} предложений")

        # Обрабатываем группами по 5 предложений
        for i in range(0, len(sentences), 5):
            batch = sentences[i:i+5]
            batch_text = " ".join(batch)

            prompt = f"""Проверь факты в следующем фрагменте текста:

{batch_text}

Для каждого проверяемого факта укажи результат проверки в формате:
[ФАКТЧЕК] Предложение #<номер>: <результат>

Проверяй:
- Конкретные утверждения и факты
- Числа и статистику
- Технические термины и аббревиатуры
- Имена, даты, события

Если в фрагменте нет проверяемых фактов, напиши: "ФАКТОВ ДЛЯ ПРОВЕРКИ НЕ ОБНАРУЖЕНО"
"""

            messages = [{"role": "user", "content": prompt}]
            response = self.call_claude(messages, max_tokens=3000)

            if "ФАКТОВ ДЛЯ ПРОВЕРКИ НЕ ОБНАРУЖЕНО" not in response.upper():
                self._parse_factcheck_results(response, document, i)

            self.log(f"Обработано предложений: {min(i+5, len(sentences))}/{len(sentences)}")

        self.log(f"Фактчекинг завершён. Добавлено комментариев: {len(document.get_comments_by_agent(self.name))}")

        return document

    def _split_into_sentences(self, text: str) -> list:
        """Разбивает текст на предложения"""
        # Простое разбиение по точкам, восклицательным и вопросительным знакам
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _parse_factcheck_results(self, response: str, document: TextDocument, offset: int):
        """Парсинг результатов фактчекинга"""
        pattern = r'\[ФАКТЧЕК\]\s*([^:]+):\s*(.+?)(?=\[ФАКТЧЕК\]|$)'
        matches = re.finditer(pattern, response, re.DOTALL)

        for match in matches:
            position = match.group(1).strip()
            result = match.group(2).strip()

            # Извлекаем URL, если есть
            url_match = re.search(r'URL:\s*(https?://[^\s\)]+)', result)
            source_url = url_match.group(1) if url_match else None

            comment = Comment(
                agent_name=self.name,
                position=position,
                comment_text=result,
                comment_type='research',
                source_url=source_url
            )
            document.add_comment(comment)


class GeneralResearcherAgent(BaseAgent):
    """
    Агент-рессёрчер-general.
    Перепроверяет факты после фактчекера.
    """

    def __init__(self, api_key=None):
        super().__init__(name="Агент-рессёрчер-general", api_key=api_key)

    def get_system_prompt(self) -> str:
        return """Ты — Агент-рессёрчер-general, перепроверяющий эксперт.

Твоя задача:
1. Изучить все комментарии Агента-рессёрчера-фактчекера
2. Перепроверить каждый факт самостоятельно
3. Для каждой проверки указать:
   - ✓ ПОДТВЕРЖДАЮ: <краткая справка> (URL: <ссылка>)
   - × НЕ НАШЁЛ ИНФОРМАЦИЮ: <что искал>

Формат:
[GENERAL-ПРОВЕРКА] <позиция>: <результат> (URL: <ссылка>)

ВАЖНО:
- Проверяй независимо от результатов фактчекера
- Ищи только АВТОРИТЕТНЫЕ ПЕРВОИСТОЧНИКИ
- Будь объективным в оценках
"""

    def process(self, document: TextDocument) -> TextDocument:
        self.log("Начинаем перепроверку фактов")

        # Получаем все комментарии фактчекера
        factcheck_comments = [c for c in document.comments
                             if c.agent_name == "Агент-рессёрчер-фактчекер" and c.status == 'active']

        self.log(f"Найдено {len(factcheck_comments)} фактов для перепроверки")

        # Обрабатываем группами по 3 факта
        for i in range(0, len(factcheck_comments), 3):
            batch = factcheck_comments[i:i+3]

            facts_text = "\n".join([
                f"{j+1}. {c.position}: {c.comment_text}"
                for j, c in enumerate(batch)
            ])

            prompt = f"""Перепроверь следующие факты:

{facts_text}

Для каждого факта проведи независимую проверку и укажи результат в формате:
[GENERAL-ПРОВЕРКА] <позиция>: <результат>

Обязательно укажи источники (URL) для подтверждённых фактов.
"""

            messages = [{"role": "user", "content": prompt}]
            response = self.call_claude(messages, max_tokens=3000)

            self._parse_verification_results(response, document)

            self.log(f"Перепроверено фактов: {min(i+3, len(factcheck_comments))}/{len(factcheck_comments)}")

        self.log(f"Перепроверка завершена. Добавлено комментариев: {len(document.get_comments_by_agent(self.name))}")

        return document

    def _parse_verification_results(self, response: str, document: TextDocument):
        """Парсинг результатов перепроверки"""
        pattern = r'\[GENERAL-ПРОВЕРКА\]\s*([^:]+):\s*(.+?)(?=\[GENERAL-ПРОВЕРКА\]|$)'
        matches = re.finditer(pattern, response, re.DOTALL)

        for match in matches:
            position = match.group(1).strip()
            result = match.group(2).strip()

            url_match = re.search(r'URL:\s*(https?://[^\s\)]+)', result)
            source_url = url_match.group(1) if url_match else None

            comment = Comment(
                agent_name=self.name,
                position=position,
                comment_text=result,
                comment_type='research',
                source_url=source_url
            )
            document.add_comment(comment)


class PostGeneralResearcherAgent(BaseAgent):
    """
    Агент-рессёрчер-post-general.
    Находит информацию для неподтверждённых фактов и комментариев.
    Вносит правки в текст.
    """

    def __init__(self, api_key=None):
        super().__init__(name="Агент-рессёрчер-post-general", api_key=api_key)

    def get_system_prompt(self) -> str:
        return """Ты — Агент-рессёрчер-post-general, эксперт по поиску решений.

Твоя задача:
1. Изучить комментарии Агентов Анализаторов и Шеф-редактора
2. Найти информацию, которую они запрашивают
3. Изучить неподтверждённые факты от рессёрчеров
4. Найти АВТОРИТЕТНУЮ замену для неподтверждённой информации
5. ВНЕСТИ ПРАВКИ В ТЕКСТ с указанием источников

Формат правок:
[ПРАВКА] <позиция>: БЫЛО: "<старый текст>" → СТАЛО: "<новый текст>" (URL: <источник>)

ВАЖНО:
- Ищи только по АВТОРИТЕТНЫМ ПЕРВОИСТОЧНИКАМ (не перепечатки!)
- Все изменения должны быть подтверждены источниками
- Указывай URL в скобках после изменений
- Будь точным и аккуратным с правками

Ты ЕДИНСТВЕННЫЙ агент, который ВНОСИТ ИЗМЕНЕНИЯ В ТЕКСТ.
"""

    def process(self, document: TextDocument) -> TextDocument:
        self.log("Начинаем финальный рессёрч и правки")

        # Собираем все активные комментарии
        active_comments = document.get_active_comments()

        self.log(f"Найдено {len(active_comments)} активных комментариев")

        prompt = f"""Изучи текст и все комментарии:

{self.prepare_document_for_prompt(document)}

Твои задачи:
1. Для каждого комментария от Анализаторов и Шеф-редактора — найди необходимую информацию
2. Для неподтверждённых фактов — найди проверенную альтернативу
3. Внеси правки в текст в указанном формате
4. Каждую правку подтверди источником (URL)

ВАЖНО: Используй формат [ПРАВКА] для всех изменений!
"""

        messages = [{"role": "user", "content": prompt}]
        response = self.call_claude(messages, max_tokens=8000)

        # Применяем правки
        self._apply_edits(response, document)

        self.log(f"Финальный рессёрч завершён. Применено правок: {len(document.get_comments_by_agent(self.name))}")

        return document

    def _apply_edits(self, response: str, document: TextDocument):
        """Применение правок к тексту"""
        pattern = r'\[ПРАВКА\]\s*([^:]+):\s*БЫЛО:\s*"([^"]+)"\s*→\s*СТАЛО:\s*"([^"]+)"\s*\(URL:\s*([^\)]+)\)'
        matches = re.finditer(pattern, response, re.DOTALL)

        edits_count = 0

        for match in matches:
            position = match.group(1).strip()
            old_text = match.group(2).strip()
            new_text = match.group(3).strip()
            source_url = match.group(4).strip()

            # Применяем правку к тексту
            if old_text in document.current_text:
                document.current_text = document.current_text.replace(old_text, new_text, 1)
                edits_count += 1

                # Добавляем комментарий о правке
                comment = Comment(
                    agent_name=self.name,
                    position=position,
                    comment_text=f"Заменено: '{old_text}' → '{new_text}'",
                    comment_type='research',
                    source_url=source_url
                )
                document.add_comment(comment)

                self.log(f"Применена правка: {position}")
            else:
                self.log(f"ВНИМАНИЕ: Не найден текст для замены: '{old_text}'")

        self.log(f"Всего применено правок: {edits_count}")
