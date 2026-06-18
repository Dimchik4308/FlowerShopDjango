from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('logins',views.MyloginView.as_view(),name='login'),
    path('',views.home,name='main_home'),
    path('custom/',views.custom,name='custom'),
    path('ready/',views.ready,name='ready'),
    path('register/',views.Register.as_view(),name='register'),
    path('confirm_email/', TemplateView.as_view(template_name='main/confirm_email.html'),name='confirm'),
    path('additions/',views.additions,name='additions'),
    path('bin/<slug:slug>/', views.bin, name='bin'),
    path('verify/<uidb64>/<token>/',views.EmailVerify.as_view(),name='verify_email'),
    path('invalid_verify/',TemplateView.as_view(template_name='main/invalid_verify.html'), name='invalid_verify'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),
    path('api/chat/', views.api_chat, name='api-chat'),
    path('checkout/', views.checkout_cart, name='checkout_cart'),
    path('successful_order/', views.succesful_order, name='success_order'),
    path('my_orders/',views.my_orders, name='my_orders'),
    path('sub/', views.add_sub, name='add_sub'),
    path('succes_sub/',views.succesful_sub,name='sub_success'),
    path('orders/', views.order, name='order'),
path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('payment-cancel/', views.payment_cancel, name='payment-cancel'),
    path('good/<str:slug>/buy',views.buy, name='buy'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='main/password_reset_form.html',email_template_name='main/password_reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),
    path('good/<str:slug>/',views.GoodDetail.as_view(),name='good-detail'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
path('payment/<int:order_id>', views.create_checkout_session, name='payment'),
]