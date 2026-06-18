import ollama
from django.core.management.base import BaseCommand
from main.models import GoodVariant


class Command(BaseCommand):
    help = 'Броньований чат з локальною ШІ, який видає точні посилання'

    def handle(self, *args, **kwargs):
        self.stdout.write('Підтягуємо товари з бази та формуємо посилання...')

        try:
            # 1. Витягуємо товари
            variants = GoodVariant.objects.select_related('product', 'color', 'size').all()

            catalog_text = "--- АКТУАЛЬНА БАЗА ТОВАРІВ ---\n"
            for v in variants:
                size_str = v.size.name if v.size else "Стандартний"
                short_desc = (v.descr[:80] + '...') if len(v.descr) > 80 else v.descr
                full_url = f"http://127.0.0.1:8000/good/{v.slug}"

                catalog_text += (
                    f"Товар: {v.product.title} | Колір: {v.color.name} | Розмір: {size_str} | "
                    f"Ціна: {v.price} грн | "
                    f"ГОТОВЕ_ПОСИЛАННЯ: {full_url}\n"
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Помилка бази даних: {e}'))
            return

        if "Товар:" not in catalog_text:
            self.stdout.write(self.style.ERROR('База пуста!'))
            return

        # 2. МАКСИМАЛЬНО ЖОРСТКИЙ СИСТЕМНИЙ ПРОМПТ
        system_prompt = (
            "Ти — флорист-консультант квіткового магазину Petal & Bloom. Твоя мета — продавати квіти.\n"
            "НАЙСУВОРІШІ ПРАВИЛА (ЯКЩО ТИ ЇХ ПОРУШИШ, СИСТЕМА ЗЛАМАЄТЬСЯ):\n"
            "1. МОВА: Спілкуйся ВИКЛЮЧНО українською мовою. Ніколи не використовуй російську чи англійську.\n"
            "2. ТОВАРИ: Ти маєш право пропонувати ТІЛЬКИ ті товари, які є у списку бази нижче. Не вигадуй квіти, яких там немає.\n"
            "3. ПОСИЛАННЯ: Коли пропонуєш товар, ти ЗОБОВ'ЯЗАНИЙ надати клієнту посилання на нього. БЕРИ ПОСИЛАННЯ СТРОГО З ПОЛЯ 'ГОТОВЕ_ПОСИЛАННЯ'. Нічого не змінюй, не скорочуй цифри в кінці. Виводь посилання повністю, починаючи з http://.\n\n"
            "Приклад правильної відповіді: 'Ось чудовий варіант: Троянда Еквадор (Червоний, 15 шт) за 1650 грн. Замовити: http://127.0.0.1:8000/good/troyanda-ekvador-chervonij-15-sht-1234567890'\n\n"
            "Якщо ти видаєш користувачу посилання на квіти поштучно то уважно перевіряй посилання з базою даних чи правильно воно написано"
            f"{catalog_text}"
        )

        # Якщо ти створив кастомну модель з Modelfile — пиши тут 'petal_bloom_ai'
        # Якщо ні — залишай 'llama3'
        MODEL_NAME = 'llama3'

        messages = [{'role': 'system', 'content': system_prompt}]

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ ШІ ({MODEL_NAME}) готовий! Усі лінки згенеровані. (напиши "q" для виходу)'))
        self.stdout.write('-' * 50)

        # 3. Цикл чату
        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['вихід', 'exit', 'quit', 'q']:
                    self.stdout.write(self.style.SUCCESS('Чат завершено.'))
                    break

                messages.append({'role': 'user', 'content': user_input})

                # Зберігаємо пам'ять короткою (системний промпт + 4 останні фрази)
                if len(messages) > 5:
                    messages = [messages[0]] + messages[-4:]

                self.stdout.write(self.style.WARNING("Флорист друкує..."))

                response = ollama.chat(model=MODEL_NAME, messages=messages)

                if 'message' in response and 'content' in response['message']:
                    ai_answer = response['message']['content']
                    self.stdout.write(self.style.SUCCESS(f"\nФлорист: {ai_answer}"))
                    messages.append({'role': 'assistant', 'content': ai_answer})
                else:
                    self.stdout.write(self.style.ERROR("\nПомилка: Модель повернула пусту відповідь."))
                    messages.pop()

            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('\nВихід.'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\nСталася помилка: {e}"))
                if messages and messages[-1]['role'] == 'user':
                    messages.pop()