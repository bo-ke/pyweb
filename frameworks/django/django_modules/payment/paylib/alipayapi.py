# _*_ coding:utf-8 _*_
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file urls.py
@time  1:08
这一行开始写文本解释与说明

# doc https://doc.open.alipay.com/doc2/detail.htm?spm=a219a.7629140.0.0.qXxvNP&treeId=59&articleId=103663&docType=1
# sign https://doc.open.alipay.com/doc2/detail?treeId=58&articleId=103242&docType=1

# doc precreate
# https://doc.open.alipay.com/docs/api.htm?spm=a219a.7395905.0.0.zt7lcf&docType=4&apiId=862

# 电脑网站支付
# https://docs.open.alipay.com/270/105900
# https://openhome.alipay.com/platform/demoManage.htm#/alipay.trade.page.pay

# App支付
# https://docs.open.alipay.com/204
# https://docs.open.alipay.com/204/105465/

"""
import os
import base64
from datetime import datetime
import urllib
import requests

ALI_PRIVATE_FILE_PATH = ""


class AliPayConfig(object):
    """
    支付宝 公共配置
    """
    APP_ID = ""
    precreate_GATEWAY = ""
    SIGN_TYPE = ""
    INPUT_CHARSTE = ""
    SELLER_ID = ""
    PARTNER = ""
    ALI_SERVICE_PATH = ""
    NOTIFY_URL = ""


class AliPayBase(object):
    """
    支付宝api 基类
    """

    def make_sign(self, para_str):
        """
        生成签名
        :param para_str:
        :return:
        """
        import OpenSSL
        ali_private_path = ALI_PRIVATE_FILE_PATH
        # print ali_private_path

        # 把私钥存到一个文件里，加载出来【尝试过用rsa模块的方法加载私钥字符串，会报格式错误。查看源码得知，需要从文件流加载】
        private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(ali_private_path).read())
        sign = base64.encodestring(OpenSSL.crypto.sign(private_key, para_str, 'sha256'))
        return sign

    def create_request_data(self):
        raise NotImplementedError

    def params_to_query(self, params):
        """
        生成需要签名的字符串
        :param params:
        :return:
        """
        """
        :param params:
        :return:
        """
        dict_items = {}
        for key, value in params.items():
            if isinstance(value, dict):
                dict_items[key] = value
                params[key] = "%s"
        all_str = ''
        for key in sorted(params.keys()):  # 把参数按key值排序：这是支付宝下单请求的参数格式规定
            all_str = all_str + '%s=%s&' % (key, params[key])
        all_str = all_str.rstrip('&')
        biz_content_dict = dict_items['biz_content']
        content_str = ''
        for key in sorted(biz_content_dict.keys()):
            if isinstance(biz_content_dict[key], str):
                content_str = content_str + '"%s":"%s",' % (key, biz_content_dict[key])
            else:
                content_str = content_str + '"%s":%s,' % (key, biz_content_dict[key])
        content_str = content_str.rstrip(',')
        content_str = '{' + content_str + '}'
        query = all_str % content_str
        return query


class AliPayDoWebPay(AliPayBase):
    """
    支付宝 下单接口封装
    doc https://docs.open.alipay.com/270/105900/
    """

    def __init__(self, orderid, goodsName, goodsPrice):
        self.notify_url = AliPayConfig.NOTIFY_URL
        self.precreate_GATEWAY = "https://openapi.alipay.com/gateway.do?"
        self.orderid = orderid
        self.goodsName = goodsName
        self.goodsPrice = goodsPrice

    # 获取二维码url
    def getAlipayUrl(self):
        # 构建公共参数
        params = {'method': 'alipay.trade.page.pay', 'version': '1.0', 'app_id': AliPayConfig.APP_ID,
                  'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'charset': 'utf-8',
                  'notify_url': self.notify_url, 'sign_type': 'RSA2'}

        # 构建订单参数
        biz_content = {'out_trade_no': self.orderid, 'qr_pay_mode': "2", 'subject': self.goodsName,
                       'product_code': 'FAST_INSTANT_TRADE_PAY', 'total_amount': self.goodsPrice}
        params['biz_content'] = biz_content

        # 由参数，生成签名，并且拼接得到下单参数字符串
        encode_params = self.make_payment_request(params)

        # 下单
        url = self.precreate_GATEWAY + encode_params
        # print(url)
        response = requests.get(url)
        # 提取下单响应
        body = response.text
        # 解析下单响应json字符串
        return body

    # 1：生成下单请求参数字符串
    def make_payment_request(self, params_dict):
        """
        构造支付请求参数
        :param params_dict:
        :return:
        """
        query_str = self.params_to_query(params_dict, )  # 拼接参数字符串
        sign = self.make_sign(query_str)  # 生成签名
        sign = urllib.parse.quote(sign, safe='')  # 解决中文参数编码问题
        res = "%s&sign=%s" % (query_str, sign)
        return res


def verify_notice_sign(params):
    trade_status = params.get("trade_status")  # 交易状态
    notify_id = params.get("notify_id")  # 获取notify_id
    seller_id = params.get("seller_id")  # 获取seller_id
    if trade_status == "TRADE_SUCCESS":
        gateway = "http://notify.alipay.com/trade/notify_query.do?"
        veryfy_url = "partner=%s&notify_id=%s" % (seller_id, notify_id)
        url = gateway + veryfy_url
        res = requests.get(url=url)
        result = res.text
    else:
        result = "false"
    return result == "true"
