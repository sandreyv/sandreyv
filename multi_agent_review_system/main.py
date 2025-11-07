"""
Главный файл для запуска многоагентной системы анализа и редактирования текстов.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from .core.coordinator import AgentCoordinator
from .agents import (
    MetaAgent,
    TextureAnalyzer1,
    TextureAnalyzer2,
    TextureAnalyzer3,
    ChiefEditorAgent,
    FactCheckerAgent,
    GeneralResearcherAgent,
    PostGeneralResearcherAgent,
    StyleAgent,
    ChiefReviewerAgent,
    CorrectorAgent,
)


class MultiAgentReviewSystem:
    """Главный класс многоагентной системы"""

    def __init__(self, api_key: str = None):
        """
        Инициализация системы

        Args:
            api_key: API ключ Anthropic (если не указан, берётся из переменной окружения)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "API ключ Anthropic не найден. "
                "Установите переменную окружения ANTHROPIC_API_KEY или передайте api_key."
            )

        self.meta_agent = MetaAgent(api_key=self.api_key)
        self.coordinator = AgentCoordinator()

        # Регистрируем всех агентов в порядке выполнения
        self._register_agents()

    def _register_agents(self):
        """Регистрация всех агентов в координаторе"""
        print("=" * 80)
        print("ИНИЦИАЛИЗАЦИЯ МНОГОАГЕНТНОЙ СИСТЕМЫ")
        print("=" * 80)

        # Порядок агентов согласно требованиям
        agents = [
            TextureAnalyzer1(api_key=self.api_key),
            TextureAnalyzer2(api_key=self.api_key),
            TextureAnalyzer3(api_key=self.api_key),
            ChiefEditorAgent(api_key=self.api_key),
            FactCheckerAgent(api_key=self.api_key),
            GeneralResearcherAgent(api_key=self.api_key),
            PostGeneralResearcherAgent(api_key=self.api_key),
            StyleAgent(api_key=self.api_key),
            ChiefReviewerAgent(api_key=self.api_key),
            CorrectorAgent(api_key=self.api_key),
            self.meta_agent,  # Мета-агент в конце для финального отчёта
        ]

        for agent in agents:
            self.coordinator.register_agent(agent)

        print("=" * 80)
        print(f"Всего агентов зарегистрировано: {len(agents)}")
        print("=" * 80)
        print()

    def process_text(self, text: str, save_results: bool = True) -> dict:
        """
        Обработать текст через всю цепочку агентов

        Args:
            text: Исходный текст для обработки
            save_results: Сохранять ли результаты в файлы

        Returns:
            dict с результатами обработки
        """
        print("\n" + "=" * 80)
        print("НАЧАЛО ОБРАБОТКИ ТЕКСТА")
        print("=" * 80)
        print(f"Длина исходного текста: {len(text)} символов")
        print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # Шаг 1: Анализ задачи мета-агентом
        print("\n[ШАГ 1] Мета-агент анализирует задачу...")
        document = self.meta_agent.analyze_task(text)

        # Шаг 2: Обработка через всех агентов
        print("\n[ШАГ 2] Запуск обработки через цепочку агентов...")
        result = self.coordinator.process_document(document)

        # Шаг 3: Сохранение результатов
        if save_results:
            self._save_results(result)

        print("\n" + "=" * 80)
        print("ОБРАБОТКА ЗАВЕРШЕНА")
        print("=" * 80)
        print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return result

    def _save_results(self, result: dict):
        """Сохранение результатов в файлы"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('output') / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        document = result['document']

        # Сохраняем финальный текст
        final_text_path = output_dir / 'final_text.txt'
        with open(final_text_path, 'w', encoding='utf-8') as f:
            f.write(document.current_text)

        # Сохраняем отчёт
        report_path = output_dir / 'report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(result['report'])

        # Сохраняем лог выполнения
        log_path = output_dir / 'execution_log.txt'
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result['execution_log']))

        # Сохраняем исходный текст для сравнения
        original_path = output_dir / 'original_text.txt'
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(document.original_text)

        print(f"\n✓ Результаты сохранены в: {output_dir}")
        print(f"  - Финальный текст: {final_text_path}")
        print(f"  - Отчёт: {report_path}")
        print(f"  - Лог выполнения: {log_path}")
        print(f"  - Исходный текст: {original_path}")


def main():
    """Главная функция для запуска из командной строки"""
    if len(sys.argv) < 2:
        print("Использование: python main.py <путь_к_файлу_с_текстом>")
        print("Или: python main.py --example  # для запуска с примером текста")
        sys.exit(1)

    if sys.argv[1] == '--example':
        # Пример текста для демонстрации
        text = """
        Искусственный интеллект и машинное обучение

        Машинное обучение — это революционная технология, которая меняет мир.
        Она позволяет компьютерам учиться на данных и делать предсказания.
        Это очень мощная технология, которая имеет много применений.

        Искусственный интеллект используется в медицине для диагностики заболеваний.
        Также ИИ применяется в автомобилях для автономного вождения.
        Нейронные сети могут распознавать образы и речь.

        В будущем AI будет еще более распространен и станет частью нашей повседневной жизни.
        """
    else:
        # Чтение текста из файла
        text_file = Path(sys.argv[1])
        if not text_file.exists():
            print(f"Ошибка: Файл {text_file} не найден")
            sys.exit(1)

        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()

    # Создаём и запускаем систему
    system = MultiAgentReviewSystem()
    result = system.process_text(text)

    # Выводим финальный текст
    print("\n" + "=" * 80)
    print("ФИНАЛЬНЫЙ ТЕКСТ (готов к копированию):")
    print("=" * 80)
    print(result['document'].current_text)
    print("=" * 80)


if __name__ == '__main__':
    main()
