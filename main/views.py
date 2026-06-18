import os
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_decode
from .models import Good, GoodVariant,Color, Size , CartItem, OrderItem, Order, Subscriber
from django.views.generic import DetailView
from django.views import View
from .forms import UserCreationForm, AuthenticationForm
from .utils import verify
from django.contrib.auth import get_user_model
import json
import ollama
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

UserModel = get_user_model()

def additions(request):
    selected_colors = request.GET.getlist('color')
    search = request.GET.get('q')
    filters = Q()

    if selected_colors:
        filters &= Q(color__id__in=selected_colors)
    if search:
        search_words=search.split()
        search_query=Q()
        for word in search_words:
            search_query |= Q(product__title__icontains=word) | Q(product__short_descr__icontains=word) | Q(color__name__icontains=word)
        filters &= search_query

    variants = GoodVariant.objects.filter(filters, product__type__in=['Упаковка','Додатки'] ).distinct()
    sort_by = request.GET.get('sort')

    if sort_by:
        variants = variants.order_by(sort_by)
    else:
        variants = variants.order_by('-id')
        
    return render(request,'main/catalog.html',{'variants':variants,'length':len(variants),'colors': Color.objects.all(),
        'selected_colors': selected_colors,})

def home(request):
    goods=GoodVariant.objects.order_by('-orders')[:3]
    return render(request, 'main/index.html',{'goods':goods})

@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message', '')

        if not user_input:
            return JsonResponse({'reply': 'Ви нічого не написали.'})

        if 'chat_history' not in request.session:
            variants = GoodVariant.objects.select_related('product', 'color', 'size').all()
            catalog_text = "--- АКТУАЛЬНА БАЗА ТОВАРІВ ---\n"
            for v in variants:
                short_desc = (v.descr[:80] + '...') if len(v.descr) > 80 else v.descr
                size_str = v.size.name if v.size else "Стандартний"
                full_url = f"http://127.0.0.1:8000/good/{v.slug}"

                catalog_text += (
                    f"Назва: {v.product.title} | Колір: {v.color.name} | Розмір: {size_str} | Ціна: {v.price} грн | Опис: {short_desc} | Посилання:{full_url} "
                )

            system_prompt = (
                "ТИ — СПРАВЖНЯ ЛЮДИНА, УКРАЇНОМОВНИЙ ФЛОРИСТ-КОНСУЛЬТАНТ МАГАЗИНУ 'PETAL & BLOOM'.\n"
                "НАЙСУВОРІШІ ПРАВИЛА (ПОРУШЕННЯ ПРИЗВЕДЕ ДО ЗВІЛЬНЕННЯ):\n\n"

                "1. МОВА: Спілкуйся ВИКЛЮЧНО українською мовою. Ніколи не переходь на англійську.\n\n"

                "2. ЗАБОРОНА НА 'ШІ-ВІДМАЗКИ': НІКОЛИ не кажи, що ти штучний інтелект. НІКОЛИ не кажи, що посилання 'демонстраційні', 'не працюють' або 'тестові'. Всі посилання з бази — АБСОЛЮТНО РЕАЛЬНІ ТА РОБОЧІ.\n\n"

                "3. ФОРМАТ ПОСИЛАНЬ: Ти ПОВИНЕН копіювати рядок 'КОД_ДЛЯ_ВІДОБРАЖЕННЯ' повністю і без змін. Не використовуй формат [text](url).\n\n"

                "4. ТОВАРИ: Пропонуй тільки те, що є в базі. Якщо товару немає, скажи про це українською.\n\n"

                "ПРИКЛАД ІДЕАЛЬНОЇ ВІДПОВІДІ:\n"
                "Вітаю! Ось чудовий варіант для вас:\n"
                "[WIDGET: /media/goods/rose.jpg | http://127.0.0.1:8000/good/slug-123 | Троянда (Червоний)]\n"
                "Ціна 1500 грн. Бажаєте оформити замовлення?\n\n"

                "--- АКТУАЛЬНА БАЗА ТОВАРІВ ---\n"
                f"{catalog_text}"
            )
            request.session['chat_history'] = [{'role': 'system', 'content': system_prompt}]

        messages = request.session['chat_history']

        messages.append({'role': 'user', 'content': user_input})

        if len(messages) > 5:
            messages = [messages[0]] + messages[-4:]

        try:
            response = ollama.chat(model='petal_bloom_ai',
                messages=messages,
                options={
                    'temperature': 0.0,
                    'top_p': 0.1
                })
            ai_answer = response['message']['content']

            messages.append({'role': 'assistant', 'content': ai_answer})
            request.session['chat_history'] = messages
            request.session.modified = True

            return JsonResponse({'reply': ai_answer})

        except Exception as e:
            messages.pop()
            return JsonResponse({'reply': f"Технічна заминка флориста: {e}"})

    return JsonResponse({'error': 'Тільки POST запити'}, status=400)

class GoodDetail(DetailView):
    model = GoodVariant
    template_name = 'main/detail.html'
    context_object_name = 'good'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_variant = self.object
        current_product = current_variant.product
        context['goods'] = GoodVariant.objects.exclude(id=self.object.id).filter(product__type=current_product.type).select_related('product', 'color','size')[:4]
        if current_variant.size:
            context['available_colors'] = current_product.variants.filter(size=current_variant.size)
        else:
            context['available_colors'] = current_product.variants.all()
        if current_product.type == 'Букет':
            context['available_sizes'] = current_product.variants.filter(color=current_variant.color).order_by('price')

        return context

def custom(request):
    selected_colors = request.GET.getlist('color')
    selected_flowers=request.GET.getlist('flower')
    search = request.GET.get('q')
    filters = Q()

    if selected_colors:
        filters &= Q(color__id__in=selected_colors)

    if selected_flowers:
        filters &= Q(product__id__in=selected_flowers)
    if search:
        search_words=search.split()
        search_query=Q()
        for word in search_words:
            search_query |= Q(product__title__icontains=word) | Q(product__short_descr__icontains=word) | Q(color__name__icontains=word)
        filters &= search_query

    variants = GoodVariant.objects.filter(filters, product__type='Квітка').distinct()
    sort_by = request.GET.get('sort')
    if sort_by:
        variants = variants.order_by(sort_by)
    else:
        variants = variants.order_by('-id')

    return render(request, 'main/catalog.html', {
        'variants': variants,
        'colors': Color.objects.all(),
        'selected_colors': selected_colors,
        'flowers': Good.objects.filter(type='Квітка').all(),
        'selected_flowers':selected_flowers,
        'length': len(variants)
    })

def ready(request):
    selected_colors = request.GET.getlist('color')
    filters = Q()
    price_range= request.GET.get('price_range')
    size= request.GET.get('size')
    event= request.GET.get('event')
    search = request.GET.get('q')
    if price_range:
        try:
            min_p, max_p = price_range.split('-')
            filters &= Q(price__gte=min_p)
            filters &= Q(price__lte=max_p)
        except ValueError:
            pass
    if size:
        filters &= Q(size__name=size)
    if event:
        filters &= Q(event=event)
    if selected_colors:
        filters &= Q(color__id__in=selected_colors)
    if search:
        search_words=search.split()
        search_query=Q()
        for word in search_words:
            search_query |= Q(product__title__icontains=word) | Q(product__short_descr__icontains=word) | Q(color__name__icontains=word)
        filters &= search_query

    variants = GoodVariant.objects.filter(filters, product__type='Букет').distinct()
    sort_by = request.GET.get('sort')

    if sort_by:
        variants = variants.order_by(sort_by)
    else:
        variants = variants.order_by('-id')

    return render(request,'main/catalog.html',{'variants':variants,'length':len(variants),
                                               'colors': Color.objects.all(),
                                               'selected_colors': selected_colors,
                                               'sizes':Size.objects.all()})



def order(request):
    variants = GoodVariant.objects.all()
    sort_by = request.GET.get('sort')
    if sort_by:
        variants = variants.order_by(sort_by)
    else:
        variants = variants.order_by('-id')

    return redirect('ready')


@login_required(login_url='login')
def buy(request, slug):
    good = get_object_or_404(GoodVariant, slug=slug)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            messages.error(request, 'Помилка: Кількість має бути більшою за нуль!')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        if good.quantity >= quantity:
            fname = request.POST.get('name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone')
            address = request.POST.get('address')
            comment = request.POST.get('comment')
            if fname and last_name and phone_number and address:
                order = Order.objects.create(
                    user=request.user,
                    fname=fname,
                    sname=last_name,
                    phone=phone_number,
                    address=address,
                    comment=comment,
                )
                OrderItem.objects.create(
                    order=order,
                    good=good,
                    quantity=quantity,
                    price=good.price
                )
                good.quantity -= quantity
                good.save()
                return redirect('payment',order.id)
            else:
                messages.error(request, 'Будь ласка, заповніть всі обов\'язкові поля')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.warning(request, 'На жаль, такої кількості товару немає на складі')
            return redirect(request.META.get('HTTP_REFERER', '/'))

    else:
        if good.quantity > 0:
            quantity = int(request.GET.get('quantity', 1))
            total_price = quantity * good.price
            if quantity <= 0:
                quantity = 1
            elif quantity > good.quantity:
                quantity = good.quantity

            return render(request, 'main/order.html', {
                'good': good,
                'quantity': quantity,
                'total_price': total_price
            })
        else:
            messages.warning(request, 'Цей товар закінчився')
            return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='login')
def checkout_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items:
        return redirect('ready')
    if request.method == 'POST':
        fname = request.POST.get('name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone')
        address = request.POST.get('address')
        comment = request.POST.get('comment')
        if fname and last_name and 9<len(phone_number)<12 and address:
            order = Order.objects.create(
                user=request.user,
                fname=fname,
                sname=last_name,
                phone=phone_number,
                address=address,
                comment=comment,
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    good=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                item.product.quantity -= item.quantity
                item.product.save()

            cart_items.delete()
            return redirect('payment',order.id)
        else:
            messages.error(request,'Будь ласка, заповніть всі обов\'язкові поля')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'main/order.html', {'cart': cart_items, 'cart_total': cart_total})

class Register(View):
    template_name = 'main/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            verify(request, user)
            return redirect('confirm')

        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            if hasattr(user, 'email_verify'):
                user.email_verify = True
            user.save()
            login(request, user)
            return redirect('main_home')

        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user


class MyloginView(LoginView):
    form_class = AuthenticationForm


@login_required(login_url='login')
def bin(request, slug):
    if request.method == 'POST':
        product = get_object_or_404(GoodVariant, slug=slug)
        quantity = int(request.POST.get('quantity',1))
        if product.quantity > 0 and quantity <= product.quantity:

            user = request.user
            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product
            )
            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity

            cart_item.save()

            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request,'На даний момент товару немає в наявності')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('main_home')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        item.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def succesful_order(request):
    return render(request,'main/success_order.html')

@login_required(login_url='login')
def my_orders(request):
    orders= Order.objects.filter(user=request.user).select_related('user')
    return render(request,'main/my_orders.html',{'orders':orders})

@login_required(login_url='login')
def add_sub(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if '@' and '.com' or '.net' in email:
            Subscriber.objects.create(email=email)
            return redirect('sub_success')
        else:
            messages.error(request, 'Введіть коректний email!')
            return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def succesful_sub(request):
    return render(request,'main/succ_sub.html')

@login_required(login_url='login')
def create_checkout_session(request,order_id):
    domain_url = 'http://localhost'
    order = get_object_or_404(Order,id=order_id)
    stripe_line_items = []

    for order_item in order.items.all():

        item_dict = {
            'price_data': {
                'currency': 'uah',
                'unit_amount': int(order_item.price * 100),
                'product_data': {
                    'name': order_item.good.product.title,
                },
            },
            'quantity': order_item.quantity,
        }
        stripe_line_items.append(item_dict)
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=str(order.id),
            payment_intent_data={
                'description': f'Оплата замовлення №{order.id} у квітковому магазині',
            },
            custom_text={
                'submit': {
                    'message': f'Ви оплачуєте замовлення №{order.id}. Дякуємо, що обрали нас!'
                }
            },
            payment_method_types=['card'],
            line_items=stripe_line_items,
            mode='payment',
            success_url=domain_url + '/successful_order/',
            cancel_url=domain_url + '/payment-cancel/',
        )

        return redirect(checkout_session.url, code=303)

    except stripe.error.StripeError as e:
        return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def payment_cancel(request):
    return render(request,'main/payment_cancel.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('client_reference_id')
        order = Order.objects.get(id=order_id)
        order.is_paid = True
        order.status= 'В обробці'
        order.save()

    return HttpResponse(status=200)

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'Скасовано':
        order.status = 'Скасовано'
        for item in order.items.all():
            item.restore_stock()
        order.save()

    return redirect('my_orders')