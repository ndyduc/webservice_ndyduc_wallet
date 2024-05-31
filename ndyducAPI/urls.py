"""
URL configuration for ndyducAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include



from ndyduc_wallet import views
from ndyduc_wallet import getdata
# from ndyduc_wallet import RESTAPIv3


urlpatterns = [
    path('', views.home, name='home'),
    path('check_user', views.check_user, name='check_user'),
    path('get_all_users/', views.get_all_users, name='get_all_users'),
    path('get_infor_home', views.get_infor_home, name='get_infor_home'),
    path('register', views.register, name='register'),
    path('confirm', views.confirm, name='confirm'),
    path('resend_email', views.resend_email, name='resend_email'),
    path('get_email_by_phone', views.get_email_by_phone, name='get_email_by_phone'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('get_daily_prices', views.get_daily_prices, name='get_daily_prices'),
    path('get_logo_tokens', views.get_logo_tokens, name='get_token_logo'),
    path('get_full_symbol', views.get_full_symbol, name='get_full_symbol'),
    path('add_kraken', views.add_kraken, name='add_kraken'),
    path('get_own_tokens', views.get_own_tokens, name='get_own_tokens'),
    path('check_getter', views.check_getter, name='check_getter'),
    path('complete_transfer', views.complete_transfer, name='complete_transfer'),
    path('get_bill', views.get_bill, name='get_bill'),
    path('save_template', views.save_template, name='save_template'),
    path('check_exchange', views.check_exchange, name='check_exchange'),
    path('complete_exchange', views.complete_exchange, name='complete_exchange'),
    path('get_coins', views.get_coins, name='get_coins'),
    path('get_wallets', views.get_wallets, name='get_wallets'),
    path('get_infor', views.get_infor, name='get_infor'),
    path('complete_change_email', views.complete_change_email, name='complete_change_email'),
    path('get_history', views.get_history, name='get_history'),
    path('get_network', views.get_network, name='get_network'),
    path('remove_wallet', views.remove_wallet, name='remove_wallet'),
    path('get_template', views.get_template, name='get_template'),
    path('remove_template', views.remove_template, name='remove_template'),
]