# _*_ coding:utf-8 _*_
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file models.py
@time  23:46
这一行开始写文本解释与说明

"""

from django.db import models


# Create your models here.


class MemberPurchaseInfo(models.Model):
    """
    用户购买信息
    """
    OrderId = models.CharField(u"定购ID", max_length=30, unique=True)
    UUID = models.CharField(u"用户唯一标识uuid", max_length=100, blank=True, null=True)
    UserName = models.CharField(u"用户名", max_length=255)
    PurchaseTime = models.DateTimeField(u"支付时间", auto_now_add=True)
    PurchaseMethod = models.CharField(u"支付方式", max_length=5, choices=(("1", "支付宝"), ("2", "微信")))
    PaymentAmount = models.CharField(u"支付金额", max_length=7)
    WhetherPaySuccess = models.CharField(u"支付是否成功", max_length=3, choices=(("0", "否"), ("1", "是")))

    def __str__(self):
        return self.UserName

    class Meta:
        verbose_name = "用户购买信息表"
        verbose_name_plural = verbose_name
