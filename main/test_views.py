import pytest
from .models import User,GoodVariant,Order,OrderItem,Good, Color, CartItem, Subscriber
from django.urls import reverse
from django.core import mail
from .admin import send_newsletter
from unittest.mock import Mock

@pytest.mark.django_db
def test_main_page_status_code(client):
    url = '/'
    response= client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_buy_alg_logic(client):
    user= User.objects.create_user(username='Vasyatest',email='test@gmail.com', password='Test13test',email_verify=True)
    client.force_login(user)
    product = Good.objects.create(title='Гіпсофіла',short_descr='Гарна квітка',type='Квітка')
    color = Color.objects.create(name='Red')
    good=GoodVariant.objects.create(product=product,
                                    color=color,
                                    descr='Lyalyalyalya',
                                    price=120,
                                    quantity=100,
                                    event='Побачення',
                                    style='Святковий',
                                    )
    form_data={
        'quantity': 2,
        'name': 'Dima',
        'last_name': 'Laz',
        'phone': '0000000000',
        'address':'Sosnivka',
        'comment': 'Бігом'
    }
    url=reverse('buy',args=[good.slug])
    response= client.post(url,data=form_data)
    good.refresh_from_db()
    assert good.quantity == 98
    assert Order.objects.count() == 1

@pytest.mark.django_db
def test_buy_alg_not_logined(client):
    product = Good.objects.create(title='Гіпсофіла',short_descr='Гарна квітка',type='Квітка')
    color = Color.objects.create(name='Red')
    good=GoodVariant.objects.create(product=product,
                                    color=color,
                                    descr='Lyalyalyalya',
                                    price=120,
                                    quantity=100,
                                    event='Побачення',
                                    style='Святковий',
                                    )
    form_data={
        'quantity': 2,
        'name': 'Dima',
        'last_name': 'Laz',
        'phone': '0000000000',
        'address':'Sosnivka',
        'comment': 'Бігом'
    }
    url=reverse('buy',args=[good.slug])
    response= client.post(url,data=form_data)
    response = client.get(url)
    good.refresh_from_db()
    assert response.status_code == 302
    login_url= reverse('login')
    assert response.url.startswith(login_url)

@pytest.mark.django_db
def test_buy_alg_bin(client):
    user= User.objects.create_user(username='Vasyatest',email='test@gmail.com', password='Test13test',email_verify=True)
    client.force_login(user)
    product = Good.objects.create(title='Гіпсофіла',short_descr='Гарна квітка',type='Квітка')
    color = Color.objects.create(name='Red')
    colorsec = Color.objects.create(name='Green')
    good=GoodVariant.objects.create(product=product,
                                    color=color,
                                    descr='Lyalyalyalya',
                                    price=120,
                                    quantity=100,
                                    event='Побачення',
                                    style='Святковий',
                                    )
    goodsec = GoodVariant.objects.create(product=product,
                                      color=colorsec,
                                      descr='Lyalyalyalya',
                                      price=110,
                                      quantity=10,
                                      event='Побачення',
                                      style='Святковий',
                                      )
    cartitem= CartItem.objects.create(
        user=user,
        product=good,
        quantity=1
    )
    cartitem2 = CartItem.objects.create(
        user=user,
        product=goodsec,
        quantity=2
    )
    form_data={
        'name': 'Dima',
        'last_name': 'Laz',
        'phone': '0000000000',
        'address':'Sosnivka',
        'comment': 'Бігом'
    }
    assert CartItem.objects.filter(user=user).count() == 2
    url=reverse('checkout_cart')
    response= client.post(url,data=form_data)
    good.refresh_from_db()
    goodsec.refresh_from_db()
    assert good.quantity == 99
    assert goodsec.quantity == 8
    assert Order.objects.count() == 1
    assert CartItem.objects.filter(user=user).count() == 0

@pytest.mark.django_db
def test_buy_alg_edge(client):
    user= User.objects.create_user(username='Vasyatest',email='test@gmail.com', password='Test13test',email_verify=True)
    client.force_login(user)
    product = Good.objects.create(title='Гіпсофіла',short_descr='Гарна квітка',type='Квітка')
    color = Color.objects.create(name='Red')
    good=GoodVariant.objects.create(product=product,
                                    color=color,
                                    descr='Lyalyalyalya',
                                    price=120,
                                    quantity=15,
                                    event='Побачення',
                                    style='Святковий',
                                    )

    form_data={
        'quantity': 100,
        'name': 'Dima',
        'last_name': 'Laz',
        'phone': '0000000000',
        'address':'Sosnivka',
        'comment': 'Бігом'
    }
    url=reverse('buy', args=[good.slug])
    response= client.post(url,data=form_data)
    good.refresh_from_db()
    assert good.quantity == 15
    assert Order.objects.count() == 0

@pytest.mark.django_db
def test_buy_alg_model(client):
    user= User.objects.create_user(username='Vasyatest',email='test@gmail.com', password='Test13test',email_verify=True)
    client.force_login(user)
    product = Good.objects.create(title='Гіпсофіла',short_descr='Гарна квітка',type='Квітка')
    color = Color.objects.create(name='Red')
    good=GoodVariant.objects.create(product=product,
                                    color=color,
                                    descr='Lyalyalyalya',
                                    price=120,
                                    slug='fsdfsfsdf',
                                    quantity=15,
                                    event='Побачення',
                                    style='Святковий',
                                    )
    goodsec = GoodVariant.objects.create(product=product,
                                      color=color,
                                      descr='Lyalyalyalya',
                                      price=180,
                                      slug='fasdasdfsfsdf',
                                      quantity=15,
                                      event='Побачення',
                                      style='Святковий',
                                      )

    order=Order.objects.create(
        user=user,
        fname='Vasya',
        sname='Pupkin',
        address='Kyiv',
        phone='1'
    )
    order_item_first=OrderItem.objects.create(
        order=order,
        good=good,
        quantity=1,
        price=good.price
    )
    order_item_second = OrderItem.objects.create(
        order=order,
        good=goodsec,
        quantity=2,
        price=goodsec.price
    )

    result = order.total_price
    assert result == 480

@pytest.mark.django_db
def test_buy_alg_send(client):
    sub= Subscriber.objects.create(
        email='napriklad@gmail.com'
    )
    product = Good.objects.create(title='Гіпсофіла', short_descr='Гарна квітка', type='Квітка')
    color = Color.objects.create(name='Red')
    good = GoodVariant.objects.create(product=product,
                                      color=color,
                                      descr='Lyalyalyalya',
                                      price=120,
                                      slug='fsdfsfsdf',
                                      quantity=15,
                                      event='Побачення',
                                      style='Святковий',
                                      )
    mock_request = Mock()
    mock_modeladmin = Mock()
    queryset=[good]
    send_newsletter(mock_modeladmin, mock_request, queryset)
    assert len(mail.outbox) == 1
    sent_mail=mail.outbox[0]
    assert 'napriklad@gmail.com' in sent_mail.bcc
    assert 'Новинки' in sent_mail.subject
