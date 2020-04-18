# _*_ coding:utf-8 _*_
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file urls.py
@time  1:08
这一行开始写文本解释与说明

"""
from django.urls import path
from .views import alipay_callback, ali_pay, rotating_inquiry, wepay, wepay_callback

urlpatterns = [
    path('pay-callback', alipay_callback, name="阿里支付回调"),
    path('ali-pay', ali_pay, name="阿里支付"),
    path('wepay', wepay, name="微信支付"),
    path('wepay-callback', wepay_callback, name="微信支付回调"),
    path('rotating-inquiry', rotating_inquiry, name="支付结果轮询")
]
