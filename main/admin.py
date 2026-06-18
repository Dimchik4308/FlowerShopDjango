from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Good, GoodVariant, Size, Color, Order, OrderItem, Subscriber
from django.core.mail import EmailMessage
from django.conf import settings

User=get_user_model()


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')


@admin.action(description="Відправити розсилку про вибрані товари")
def send_newsletter(modeladmin, request, queryset):
    subscribers = list(Subscriber.objects.values_list('email', flat=True))

    if not subscribers:
        modeladmin.message_user(request, "Немає жодного підписника для розсилки!", level='ERROR')
        return

    text = "Вітаємо! У Petal & Bloom з'явилися неймовірні новинки:\n\n"
    for good in queryset:
        text += f"{good.product.type} {good.product.title} — {good.price} грн\n"

    text += "\nЗаходьте на сайт, щоб замовити першими!"

    msg = EmailMessage(
        subject="Новинки вже на сайті!",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.DEFAULT_FROM_EMAIL],
        bcc=subscribers
    )
    msg.send(fail_silently=False)
    modeladmin.message_user(request, f"Розсилку успішно відправлено на {len(subscribers)} адрес!")

class GoodVariantInline(admin.StackedInline):
    model = GoodVariant
    extra = 1
    show_change_link = True

@admin.register(User)
class UserAdmin(UserAdmin):
    pass

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    inlines = [GoodVariantInline]

@admin.register(GoodVariant)
class Variant(admin.ModelAdmin):
    readonly_fields = ('slug', 'orders', 'old_price','discount')
    actions = [send_newsletter]

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = [ 'name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
