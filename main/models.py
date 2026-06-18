from time import time
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from unidecode import unidecode
from django.utils.translation import gettext_lazy as _
from django.db import models

class Size(models.Model):
    name = models.CharField('Кількість / Розмір', max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Розмір'
        verbose_name_plural = 'Розміри'

class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name='Назва кольору')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Колір'
        verbose_name_plural = 'Кольори'
    
class Good(models.Model):
    title=models.CharField('Назва',max_length=50)
    short_descr=models.CharField('Короткий опис',max_length=30)

    class GoodType(models.TextChoices):
        FLOWER = 'Квітка', 'Квітка'
        BOUQUET = 'Букет', 'Букет'
        PACKAGING = 'Упаковка', 'Упаковка'
        ADDITIONS = 'Додатки', 'Додатки'

    type = models.CharField('Тип',max_length=20,choices=GoodType.choices,default=GoodType.FLOWER)

    def __str__(self):
        return f'Товар: {self.title}'

    class Meta:
        verbose_name='Товар'
        verbose_name_plural='Товари'

class GoodVariant(models.Model):
    product = models.ForeignKey(Good, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    descr = models.TextField('Повний Опис')
    price = models.PositiveIntegerField('Ціна')
    quantity = models.PositiveIntegerField('Кількість')
    event = models.CharField('Подія', max_length=30)
    style = models.CharField('Стиль', max_length=30)
    img = models.ImageField('Фото',upload_to='',null=True,blank=True)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    orders = models.PositiveIntegerField(default=0)
    old_price = models.PositiveIntegerField('Стара ціна', blank=True, null=True)
    discount=models.PositiveIntegerField('Відсоток знижки',blank=True,null=True)
    size = models.ForeignKey(Size, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Розмір (кількість)')
    date = models.DateTimeField('Дата викладення товару на сайт', auto_now_add=True)

    @property
    def is_new(self):
        difference=timezone.now() - self.date

        return difference.days<=3

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            if self.size:
                self.slug = f'{slugify(unidecode(self.product.title))}-{slugify(unidecode(self.color.name))}-{slugify(unidecode(self.size.name))}-{int(time())}'
            else:
                self.slug = f'{slugify(unidecode(self.product.title))}-{slugify(unidecode(self.color.name))}-{int(time())}'
        if self.pk:
            original_obj = GoodVariant.objects.get(pk=self.pk)
            if original_obj.price != self.price:
                self.old_price = original_obj.price
                if self.price < self.old_price:
                    self.discount =((self.old_price - self.price) / self.old_price) * 100
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Варіація товару'
        verbose_name_plural = 'Варіації товарів'

    def __str__(self):
        return f"{self.product.title} - {self.color.name}"


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    email_verify = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('GoodVariant', on_delete=models.CASCADE, related_name='in_carts')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Кошик {self.user.username} - {self.product} ({self.quantity} шт.)"

    def get_total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orderer')
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default='Нове', choices=[
        ('Очікує на оплату', 'Очікує на оплату'),
        ('В обробці', 'В обробці'),
        ('Доставлено', 'Доставлено'),
        ('Скасовано', 'Скасовано')
    ])

    fname = models.CharField("Ім'я покупця", max_length=100 ,null=False)
    sname = models.CharField("Прізвище покупця", max_length=100 , null=False)
    phone = models.CharField('Номер телефону покупця', max_length=100 ,null=False)
    address = models.TextField('Адреса доставки', null=False)
    comment = models.TextField('Побажання до замовлення',null=True,blank=True)
    is_paid= models.BooleanField('Чи оплачене замовлення',default=False)


    @property
    def total_price(self):
        items = self.items.all()
        return sum(item.price * item.quantity for item in items)

    def to_delete(self):
        period = timezone.now() - self.created_at
        if period.days > 3 and not self.is_paid:
            for item in self.items.all():
                item.restore()
            self.delete()
            


    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    def __str__(self):
        return f"Замовлення #{self.id} від {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    good = models.ForeignKey(GoodVariant, on_delete=models.SET_NULL, null=True, related_name='goods')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Замовлений товар'
        verbose_name_plural = 'Замовлені товари'

    def restore(self):
        if self.good:
            self.good.quantity+=self.quantity
            self.good.save()


    def __str__(self):
        good_name = self.good.product.title if self.good else "Видалений товар"
        return f"{good_name} (x{self.quantity}) у Замовленні #{self.order.id}"

class Subscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email підписника")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Підписник"
        verbose_name_plural = "Підписники"