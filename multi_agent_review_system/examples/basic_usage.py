"""
Примеры использования многоагентной системы
"""

import os
import sys

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import MultiAgentReviewSystem


def example_1_basic_usage():
    """Пример 1: Базовое использование"""
    print("=" * 80)
    print("ПРИМЕР 1: Базовое использование системы")
    print("=" * 80)

    # Пример текста
    text = """
    Облачные технологии и искусственный интеллект

    Облачные вычисления революционизировали IT-индустрию. Благодаря облаку компании
    могут масштабировать свою инфраструктуру очень быстро. Облако позволяет снизить
    затраты на IT.

    Машинное обучение это подмножество искусственного интеллекта. ML алгоритмы
    обучаются на данных и делают предсказания. Нейронные сети это один из видов ML.

    В 2023 году рынок облачных услуг вырос на 25 процентов. AWS занимает 32% рынка,
    за ней следует Azure с 23%. Google Cloud на третьем месте.

    В будущем облако и ИИ будут ещё более тесно интегрированы, что позволит
    создавать более интеллектуальные приложения.
    """

    # Инициализация системы
    system = MultiAgentReviewSystem()

    # Обработка текста
    result = system.process_text(text, save_results=True)

    # Вывод результатов
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТ ОБРАБОТКИ:")
    print("=" * 80)
    print(result['document'].current_text)
    print("\n" + "=" * 80)


def example_2_file_processing():
    """Пример 2: Обработка текста из файла"""
    print("=" * 80)
    print("ПРИМЕР 2: Обработка текста из файла")
    print("=" * 80)

    # Создаём тестовый файл
    test_file = 'test_article.txt'

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
        Квантовые компьютеры: будущее уже здесь

        Квантовые компьютеры представляют собой новую парадигму вычислений.
        В отличие от классических компьютеров, они используют принципы квантовой механики.

        Кубиты могут находиться в состоянии суперпозиции, что позволяет проводить
        параллельные вычисления. IBM и Google активно развивают квантовые технологии.

        Ожидается, что к 2030 году квантовые компьютеры смогут решать задачи,
        недоступные классическим суперкомпьютерам.
        """)

    # Читаем и обрабатываем
    with open(test_file, 'r', encoding='utf-8') as f:
        text = f.read()

    system = MultiAgentReviewSystem()
    result = system.process_text(text, save_results=True)

    print(f"\nТекст из файла '{test_file}' успешно обработан!")
    print(f"Результаты сохранены в директории 'output/'")

    # Удаляем тестовый файл
    os.remove(test_file)


def example_3_programmatic_access():
    """Пример 3: Программный доступ к результатам"""
    print("=" * 80)
    print("ПРИМЕР 3: Программный доступ к результатам")
    print("=" * 80)

    text = """
    Блокчейн и криптовалюты

    Блокчейн - это распределенная база данных. Биткойн был создан в 2009 году.
    Ethereum добавил смарт-контракты, которые позволяют создавать децентрализованные приложения.
    """

    system = MultiAgentReviewSystem()
    result = system.process_text(text, save_results=False)

    # Доступ к различным частям результата
    document = result['document']
    report = result['report']
    log = result['execution_log']

    print(f"\nДлина исходного текста: {len(document.original_text)} символов")
    print(f"Длина финального текста: {len(document.current_text)} символов")
    print(f"Всего комментариев было: {len(document.comments)}")
    print(f"Активных комментариев: {len(document.get_active_comments())}")
    print(f"Записей в логе: {len(log)}")

    print("\nФинальный текст:")
    print("-" * 80)
    print(document.current_text)


def example_4_batch_processing():
    """Пример 4: Пакетная обработка нескольких текстов"""
    print("=" * 80)
    print("ПРИМЕР 4: Пакетная обработка")
    print("=" * 80)

    texts = [
        ("Статья 1", "Искусственный интеллект меняет медицину. ИИ помогает диагностировать заболевания."),
        ("Статья 2", "Робототехника развивается быстро. Роботы уже используются в производстве."),
        ("Статья 3", "Автономные автомобили станут реальностью в ближайшие годы."),
    ]

    system = MultiAgentReviewSystem()

    results = []
    for title, text in texts:
        print(f"\nОбработка: {title}")
        result = system.process_text(text, save_results=False)
        results.append((title, result))
        print(f"✓ {title} обработана")

    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ ПАКЕТНОЙ ОБРАБОТКИ:")
    print("=" * 80)

    for title, result in results:
        print(f"\n{title}:")
        print("-" * 40)
        print(result['document'].current_text[:200] + "...")


def example_5_custom_configuration():
    """Пример 5: Использование с явной передачей API ключа"""
    print("=" * 80)
    print("ПРИМЕР 5: Кастомная конфигурация")
    print("=" * 80)

    # Получаем API ключ из переменной окружения
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("Внимание: API ключ не найден в переменных окружения")
        print("Установите ANTHROPIC_API_KEY для работы системы")
        return

    # Инициализация с явной передачей ключа
    system = MultiAgentReviewSystem(api_key=api_key)

    text = "Краткий текст для демонстрации кастомной конфигурации."

    result = system.process_text(text, save_results=False)

    print("\nСистема успешно инициализирована с кастомной конфигурацией")
    print(f"Обработано агентов: {len(system.coordinator.agents)}")


def main():
    """Запуск всех примеров"""
    examples = [
        ("Базовое использование", example_1_basic_usage),
        ("Обработка файла", example_2_file_processing),
        ("Программный доступ", example_3_programmatic_access),
        ("Пакетная обработка", example_4_batch_processing),
        ("Кастомная конфигурация", example_5_custom_configuration),
    ]

    print("\n")
    print("=" * 80)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ МНОГОАГЕНТНОЙ СИСТЕМЫ")
    print("=" * 80)
    print("\nДоступные примеры:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\nВыберите пример (1-5) или 0 для запуска всех: ", end="")

    try:
        choice = int(input())

        if choice == 0:
            for name, func in examples:
                print(f"\n\n{'=' * 80}")
                print(f"Запуск примера: {name}")
                print('=' * 80)
                try:
                    func()
                except Exception as e:
                    print(f"Ошибка в примере '{name}': {e}")
        elif 1 <= choice <= len(examples):
            examples[choice - 1][1]()
        else:
            print("Неверный выбор")

    except ValueError:
        print("Ошибка: введите число")
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")


if __name__ == '__main__':
    # Проверяем наличие API ключа
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("=" * 80)
        print("ВНИМАНИЕ: API ключ Anthropic не найден!")
        print("=" * 80)
        print("\nДля работы системы необходим API ключ Anthropic.")
        print("\nУстановите переменную окружения:")
        print("  export ANTHROPIC_API_KEY='your_api_key_here'")
        print("\nИли создайте файл .env с содержимым:")
        print("  ANTHROPIC_API_KEY=your_api_key_here")
        print("\n" + "=" * 80)
        sys.exit(1)

    main()
