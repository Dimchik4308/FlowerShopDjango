import random
from django.core.management.base import BaseCommand
from main.models import Good, GoodVariant, Color, Size  # <--- Додали Size сюди


class Command(BaseCommand):
    help = 'Заповнює базу базовими товарами та букетами з розмірами (9, 15, 25, 51)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очищаємо старі дані...')
        GoodVariant.objects.all().delete()
        Good.objects.all().delete()
        Color.objects.all().delete()
        Size.objects.all().delete()  # <--- Очищаємо таблицю розмірів

        # 1. Базові кольори
        self.stdout.write('Створюємо базові кольори...')
        color_names = ['Червоний', 'Білий', 'Жовтий', 'Рожевий', 'Фіолетовий', 'Бежевий']
        colors_dict = {}
        for name in color_names:
            color, _ = Color.objects.get_or_create(name=name)
            colors_dict[name] = color

        # 2. Базові розміри
        self.stdout.write('Створюємо розміри для букетів...')
        size_numbers = [9, 15, 25, 51]
        sizes_dict = {}
        for num in size_numbers:
            size_name = f"{num} шт"
            size_obj, _ = Size.objects.get_or_create(name=size_name)
            sizes_dict[size_name] = size_obj

        # 3. Каталог товарів (Квіти без розміру, Букети з розмірами)
        catalog = [
            # --- ОКРЕМІ КВІТИ (БЕЗ РОЗМІРУ) ---
            {
                'title': 'Троянда Еквадор', 'short_descr': 'Висока, великий бутон', 'type': Good.GoodType.FLOWER,
                'variants': ['Червоний', 'Білий', 'Рожевий'], 'base_price': 120, 'has_sizes': False,
                'long_descr': "Еквадорська троянда — це справжня класика та еталон флористики. Завдяки ідеальному клімату Еквадору, ці квіти мають товсте, міцне стебло та неймовірно великий бутон, який розкривається поступово. Чудовий вибір для особливих зізнань."
            },
            {
                'title': 'Тюльпан', 'short_descr': 'Свіжий весняний', 'type': Good.GoodType.FLOWER,
                'variants': ['Червоний', 'Жовтий', 'Білий', 'Рожевий'], 'base_price': 45, 'has_sizes': False,
                'long_descr': "Тюльпан — це справжній вісник весни. Його хрусткі зелені листочки та ідеальної форми бутони створюють неперевершену атмосферу легкості та радості. Подаруйте частинку сонячного настрою своїм близьким!"
            },
            {
                'title': 'Півонія', 'short_descr': 'Пишна та ароматна', 'type': Good.GoodType.FLOWER,
                'variants': ['Рожевий', 'Білий'], 'base_price': 150, 'has_sizes': False,
                'long_descr': "Півонія — королева квітів з пишним, багатошаровим бутоном та солодким ароматом. Спостерігати за тим, як туга кулька розкривається у велику мереживну квітку — це справжня магія природи."
            },

            # --- БУКЕТИ (З РОЗМІРАМИ 9, 15, 25, 51) ---
            # Замість конкретних "51 троянда", робимо гнучкий монобукет
            {
                'title': 'Монобукет Троянд', 'short_descr': 'Класичний букет троянд', 'type': Good.GoodType.BOUQUET,
                'variants': ['Червоний', 'Білий'], 'stem_price': 100, 'has_sizes': True,
                'long_descr': "Розкішний монобукет зі свіжих еквадорських троянд. Символ щирості, пристрасті та найсвітліших почуттів. Професійно зібраний флористами по спіралі та перев'язаний широкою атласною стрічкою. Оберіть свій ідеальний розмір!"
            },
            {
                'title': 'Монобукет Тюльпанів', 'short_descr': 'Яскравий весняний мікс', 'type': Good.GoodType.BOUQUET,
                'variants': ['Жовтий', 'Рожевий'], 'stem_price': 40, 'has_sizes': True,
                'long_descr': "Велика та ніжна композиція з хрустких тюльпанів. Ідеально підходить для привітання з весняними святами або просто для того, щоб підняти настрій. Оформлений у сучасну матову флористичну кальку світлого відтінку."
            },
            {
                'title': 'Букет Півоній', 'short_descr': 'Пишний ароматний букет', 'type': Good.GoodType.BOUQUET,
                'variants': ['Рожевий', 'Білий'], 'stem_price': 140, 'has_sizes': True,
                'long_descr': "Сезонний хіт — розкішний букет з великих півоній. Пишний, неймовірно ароматний та дуже красивий. Упакований у мінімалістичний крафт або дизайнерську плівку, щоб не відволікати увагу від самих квітів."
            },

            # --- УПАКОВКА ТА ДОДАТКИ (БЕЗ РОЗМІРУ) ---
            {
                'title': 'Упаковка Крафт', 'short_descr': 'Етичний папір', 'type': Good.GoodType.PACKAGING,
                'variants': ['Бежевий'], 'base_price': 50, 'has_sizes': False,
                'long_descr': "Стильне пакування з щільного крафт-паперу класичного бежевого відтінку. Надійно захищає квіти і вигідно підкреслює їхню природну красу. Ідеально для мінімалістичних композицій."
            },
            {
                'title': 'Листівка', 'short_descr': 'З вашим текстом', 'type': Good.GoodType.ADDITIONS,
                'variants': ['Білий'], 'base_price': 30, 'has_sizes': False,
                'long_descr': "Ексклюзивна мінімалістична дизайнерська листівка. Ми вручну підпишемо цю листівку найтеплішими словами від вашого імені, щоб зробити сюрприз ще більш особистим та зворушливим."
            }
        ]

        events = ['День народження', 'Побачення', 'Без приводу']
        styles = ['Класика', 'Мінімалізм']

        total_variants = 0

        self.stdout.write('Генеруємо товари, варіації кольорів та розмірів...')
        for item in catalog:
            good = Good.objects.create(
                title=item['title'],
                short_descr=item['short_descr'],
                type=item['type']
            )

            for color_name in item['variants']:

                # ЯКЩО ЦЕ БУКЕТ З РОЗМІРАМИ
                if item.get('has_sizes'):
                    for num in size_numbers:
                        size_name = f"{num} шт"
                        # Рахуємо ціну: (ціна за 1 гілку * кількість) + 150 грн за роботу/упаковку
                        calc_price = (item['stem_price'] * num) + 150

                        GoodVariant.objects.create(
                            product=good,
                            color=colors_dict[color_name],
                            size=sizes_dict[size_name],  # <--- Підв'язуємо розмір
                            descr=item['long_descr'],
                            price=calc_price,  # <--- Динамічна ціна
                            quantity=random.randint(5, 20),
                            event=random.choice(events),
                            style=random.choice(styles),
                            orders=random.randint(0, 15)
                        )
                        total_variants += 1

                # ЯКЩО ЦЕ КВІТКА / УПАКОВКА (БЕЗ РОЗМІРУ)
                else:
                    price = item['base_price'] + random.randint(-5, 10)

                    GoodVariant.objects.create(
                        product=good,
                        color=colors_dict[color_name],
                        size=None,  # <--- Розміру немає
                        descr=item['long_descr'],
                        price=price,
                        quantity=random.randint(15, 50),
                        event=random.choice(events),
                        style=random.choice(styles),
                        orders=random.randint(0, 15)
                    )
                    total_variants += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Готово! Створено {total_variants} карток товарів.'))
        self.stdout.write(self.style.SUCCESS('Всі букети успішно розбиті на розміри 9, 15, 25 та 51 шт!'))