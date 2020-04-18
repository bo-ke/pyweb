# _*_ coding:utf-8 _*_
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file views.py
@time  23:47
这一行开始写文本解释与说明

"""
from django.http import HttpResponse
from .models import MemberPurchaseInfo
from frameworks.django.django_modules.payment.paylib.alipayapi import AliPayDoWebPay, verify_notice_sign
from frameworks.django.django_modules.payment.paylib.wepayapi import WePayDoPay
from xml.etree.ElementTree import XML


def alipay(request):
    """
    阿里支付
    :param request:
    :return:
    """
    params = request.GET.dict()
    ali_pay_web_pay = AliPayDoWebPay(orderid=params["order_id"], goodsName=params["goods_name"],
                                     goodsPrice=params["goods_price"])
    pay_html = ali_pay_web_pay.getAlipayUrl()
    # print(pay_html)
    # 创建订单
    member_purchase_info = MemberPurchaseInfo(UUID=params.get("uuid", ""),
                                              OrderId=params["order_id"],
                                              UserName=params["user_name"],
                                              PaymentAmount=params["goods_price"],
                                              WhetherPaySuccess=0)
    member_purchase_info.save()
    res = HttpResponse(pay_html)
    return res


def alipay_callback(request):
    """
    支付宝支付回调
    :param request:
    :return:
        {'gmt_create': '2019-11-02 12:03:16',
        'charset': 'utf-8',
        'gmt_payment': '2019-11-02 12:03:20',
        'notify_time': '2019-11-02 12:03:21',
        'subject': '',
        'sign': 'aRIAfYvPVWSiBu4YLp6C//E1UTpZud/9z4AG5ST39cd7Rtc07KLS7aQKGqw==',
        'buyer_id': '2088022115891502',
        'invoice_amount': '0.01',
        'version': '1.0',
        'notify_id': '2019110200222120320091501415690032',
        'fund_bill_list': '[{"amount":"0.01","fundChannel":"PCREDIT"}]',
        'notify_type': 'trade_status_sync',
        'out_trade_no': '12027009513095153',
        'total_amount': '0.01', 'trade_status':
        'TRADE_SUCCESS', 'trade_no': '2019110222001491501409062615',
        'auth_app_id': '2019102368566289',
        'receipt_amount': '0.01', 'point_amount': '0.00', 'buyer_pay_amount': '0.01',
        'app_id': '', 'sign_type': 'RSA2', 'seller_id': ''}
        """
    if request.method == 'POST':
        params = request.POST.dict()  # 获取参数字典
        if verify_notice_sign(params):  # 调用检查支付结果的函数
            '''
                支付成功后逻辑
            '''
            # print('支付成功！')
            return HttpResponse('success')  # 返回成功信息到支付宝服务器
        else:
            '''
                支付失败后逻辑
            '''
            return HttpResponse('FAILED')
    else:
        return HttpResponse('FAILED')


def wepay(request):
    """
    微信支付
    :param request:
    :return:
    """
    try:
        if request.method == "POST":
            params = request.POST.dict()
            wepay = WePayDoPay(out_trade_no=params["order_id"], total_fee=params["goods_price"],
                               body=params["goods_name"])
            qr_base64_code = wepay.get_qr_base64_code()
            # 创建订单
            member_purchase_info = MemberPurchaseInfo(UUID=params.get("uuid", ""),
                                                      OrderId=params["order_id"],
                                                      UserName=params["user_name"],
                                                      PaymentAmount=params["goods_price"],
                                                      WhetherPaySuccess=0)
            member_purchase_info.save()
            return HttpResponse({"qr_base64_code": str(qr_base64_code)})
        else:
            return HttpResponse("method error, you should use POST method")
    except Exception as e:
        return HttpResponse(repr(e))


def wepay_callback(request):
    """
    微信支付回调
    :param request:
    :return:

    b'<xml><appid><![CDATA[wxed799b3eb9f64be6]]></appid>\n<bank_type><![CDATA[CFT]]>
    </bank_type>\n<cash_fee><![CDATA[1]]></cash_fee>\n<fee_type><![CDATA[CNY]]></fee_type>\n
    <is_subscribe><![CDATA[N]]></is_subscribe>\n<mch_id><![CDATA[1559936921]]>
    </mch_id>\n<nonce_str><![CDATA[ycrx0zv56bwk3tsf]]></nonce_str>\n<openid><![CDATA[o4g7TwMCAPuanofbARkfObaxDZLE]]>
    </openid>\n<out_trade_no><![CDATA[123456789sdf]]></out_trade_no>\n<result_code><![CDATA[SUCCESS]]>
    </result_code>\n<return_code><![CDATA[SUCCESS]]></return_code>\n<sign><![CDATA[CBE639933B4F4A3F99358D2F4EA4F6E0]]>
    </sign>\n<time_end><![CDATA[20191121023054]]></time_end>\n<total_fee>1</total_fee>\n<trade_type><![CDATA[NATIVE]]>
    </trade_type>\n<transaction_id><![CDATA[4200000460201911210380450477]]>
    </transaction_id>\n</xml>'
    """
    body = request.body
    if not body:
        return HttpResponse(('''
                <xml>
                  <return_code><![CDATA[FAIL]]></return_code>
                  <return_msg><![CDATA[FAIL]]></return_msg>
                </xml>
                '''))
    xml = XML(body)
    wp = WePayDoPay(out_trade_no='',
                    total_fee=0,
                    body='')
    success = wp.verify_notice_sign(xml)
    if not success:
        return HttpResponse('''
                <xml>
                  <return_code><![CDATA[FAIL]]></return_code>
                  <return_msg><![CDATA[Sign error]]></return_msg>
                </xml>
                ''')
    out_trade_no = xml.find('out_trade_no').text
    '''
    支付成功逻辑
    '''
    # print('支付成功！')
    return HttpResponse(('''
             <xml>
               <return_code><![CDATA[SUCCESS]]></return_code>
               <return_msg><![CDATA[OK]]></return_msg>
             </xml>
             '''))


def rotating_inquiry(request):
    """
    支付结果轮询
    :param request:
    :return:
    """
    try:
        if request.method == "POST":
            params = request.POST.dict()
            if "order_id" in params:
                purchase_info = MemberPurchaseInfo.objects.get(ORDERID=params["order_id"])
                result = purchase_info.WHETHERPAYSUCESS
                return HttpResponse(result)
            else:
                return HttpResponse("")
        else:
            return HttpResponse("method error, you should use POST method")
    except Exception as e:
        return HttpResponse(repr(e))
