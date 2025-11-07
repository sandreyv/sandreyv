#!/usr/bin/env python3
"""
Скрипт для тестирования многоагентной системы на предоставленном тексте.

Использование:
1. Установите API ключ: export ANTHROPIC_API_KEY='your_key'
2. Запустите: python run_test.py
"""

import os
import sys

# Проверка API ключа
if not os.getenv('ANTHROPIC_API_KEY'):
    print("=" * 80)
    print("ОШИБКА: API ключ Anthropic не найден!")
    print("=" * 80)
    print("\nДля запуска установите переменную окружения:")
    print("  export ANTHROPIC_API_KEY='your_api_key_here'")
    print("\nПолучить API ключ можно на: https://console.anthropic.com/")
    print("=" * 80)
    sys.exit(1)

# Импорт системы
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'multi_agent_review_system'))
from main import MultiAgentReviewSystem

# Текст для обработки
text = """Данные источники представляют собой всесторонний сравнительный анализ коммуникационных стратегий и технологических предложений компаний Сбер и Яндекс, нацеленных на привлечение IT-специалистов. Значительная часть текстов фокусируется на Яндексе, подробно описывая его обширную экосистему из более чем 90 сервисов, акцент на Highload-инфраструктуре (YTsaurus, YDB) и уникальную инженерную культуру, поощряющую горизонтальную мобильность и открытый обмен знаниями (ШАД, опенсорс). В противовес этому, Сбер позиционируется как лидер в области глубоких R&D и AI-технологий (GigaChat, квантовые вычисления, AR/VR SDK), предлагающий структурированную адаптацию (IT Bootcamp) и быстрый найм (One Day Offer), но при этом эксперты отмечают необходимость большей публичной прозрачности его внутренних архитектурных решений. Общее содержание включает описания вакансий, ключевых продуктов и методов работы обеих компаний."""

print("\n" + "=" * 80)
print("ЗАПУСК МНОГОАГЕНТНОЙ СИСТЕМЫ")
print("=" * 80)
print("\nОбрабатываемый текст:")
print("-" * 80)
print(text)
print("-" * 80)
print()

# Инициализация и запуск
try:
    system = MultiAgentReviewSystem()
    result = system.process_text(text, save_results=True)

    print("\n" + "=" * 80)
    print("ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 80)

    print("\nФИНАЛЬНЫЙ ТЕКСТ:")
    print("=" * 80)
    print(result['document'].current_text)
    print("=" * 80)

    print("\nКРАТКИЙ ОТЧЁТ:")
    print("-" * 80)
    print(f"Исходная длина: {len(result['document'].original_text)} символов")
    print(f"Финальная длина: {len(result['document'].current_text)} символов")
    print(f"Обработано агентов: {len(result['execution_log'])}")
    print(f"Комментариев создано: {len(result['document'].comments)}")
    print()

    if result['document'].metadata.get('final_summary'):
        print("РЕЗЮМЕ МЕТА-АГЕНТА:")
        print("-" * 80)
        print(result['document'].metadata['final_summary'])
        print()

    print("Подробные результаты сохранены в директории 'output/'")
    print()

except Exception as e:
    print("\n" + "=" * 80)
    print("ОШИБКА ПРИ ОБРАБОТКЕ")
    print("=" * 80)
    print(f"\n{type(e).__name__}: {e}")
    print("\nПроверьте:")
    print("1. API ключ установлен корректно")
    print("2. Есть доступ к интернету")
    print("3. API ключ имеет достаточный баланс")
    sys.exit(1)
