# _*_ coding:utf-8 _*_
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file urls.py
@time  1:08
这一行开始写文本解释与说明

doc -- https://pay.weixin.qq.com/wiki/doc/api/tools/mch_pay.php?chapter=14_2
       https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_1
test api -- http://mp.weixin.qq.com/debug/cgi-bin/readtmpl?t=pay/index&pass_ticket=Vk3Mm8MK6EcgHMomyKlmt7Rj6ktvDqMJ4VAiUleuaveLdfnQtlJDTHolUEts8nIq
 -- http://www.cocoachina.com/bbs/read.php?tid=321546
 https://doc.open.alipay.com/doc2/detail.htm?spm=a219a.7629140.0.0.qXxvNP&treeId=59&articleId=103663&docType=1
"""
import hashlib
import random
import string
import time
import xml.etree.ElementTree as ET
from urllib import request
import ssl
import qrcode
import base64
from io import BytesIO

ssl._create_default_https_context = ssl._create_unverified_context


class WePayConfig(object):
    MCHID = ""  # 商户号
    APPID = ""  # APPID
    KEY = ""  # 微信API密钥


class WePayBase(object):
    """
    微信支付基类
    """

    def dict_to_xml(self, param_map):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in param_map.items():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    def xml_to_dict(self, xml):
        data = {}
        root = ET.fromstring(xml)
        for child in root:
            value = child.text
            data[child.tag] = value
        return data

    def get_sign(self, param_map):
        """生成签名"""

        # print(param_map)

        sort_param = sorted(
            [(key, value) for key, value in param_map.items()],
            key=lambda x: x[0]
        )
        content = '&'.join(['='.join(x) for x in sort_param])
        key = WePayConfig.KEY

        sign_content = "{0}&key={1}".format(content, key)
        smd5 = hashlib.md5()
        # print(sign_content)
        smd5.update(sign_content.encode("utf8"))
        return smd5.hexdigest().upper()

    def random_str(self):
        content = string.ascii_letters[:26] + string.digits
        return ''.join(random.sample(content, 16))


class WePayDoPay(WePayBase):
    """
    微信下单接口
    """

    def __init__(self, out_trade_no, total_fee, body, subject='buy', payment_type="NATIVE", ip="127.0.0.1"):

        self.url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        self.notify_url = "http://wx.mozlen.com/api/wxpay/callback/v1"

        self.out_trade_no = str(out_trade_no)
        self.subject = subject
        self.trade_type = payment_type
        self.total_fee = str(int(float(total_fee) * 100))
        self.body = body
        self.ip = ip
        self.prepay_id = ''
        self.xml = ''
        self.code_url = ''
        self.nonce_str = self.random_str()
        self.openid = ''

    def post_xml(self, second=30):
        data = self.create_xml()
        data = data.encode(encoding='UTF8')
        req = request.Request(self.url, data=data, method='POST')  # POST方法
        response = request.urlopen(req).read()
        return response

    def create_xml(self):
        """
        生成接口参数xml
        :return:
        """

        web_wx_appid = WePayConfig.APPID
        web_wx_mchid = WePayConfig.MCHID

        param_map = {
            'appid': web_wx_appid,
            'mch_id': web_wx_mchid,
            'spbill_create_ip': self.ip,
            'nonce_str': self.nonce_str,
            'out_trade_no': self.out_trade_no,
            'body': self.body,
            'total_fee': self.total_fee,
            'notify_url': self.notify_url,
            'trade_type': self.trade_type
        }

        if self.openid:
            param_map['openid'] = self.openid

        param_map['sign'] = self.get_sign(param_map)
        self.xml = self.dict_to_xml(param_map)

        return self.xml

    def qr_code_xml(self, prepay_id):
        web_wx_appid = WePayConfig.APPID
        web_wx_mchid = WePayConfig.MCHID

        param_map = {
            "return_code": "SUCCESS",
            'appid': web_wx_appid,
            'mch_id': web_wx_mchid,
            'nonce_str': self.nonce_str,
            "prepay_id": prepay_id,
            "result_code": "SUCCESS",
        }

        param_map['sign'] = self.get_sign(param_map)
        xml = self.dict_to_xml(param_map)
        return xml

    def _get_prepay_id(self):
        """获取prepay_id"""
        result = self.xml_to_dict(self.post_xml())
        result_code = result.get('result_code')
        if result_code != "SUCCESS":
            e = Exception()
            e.desc = result.get("err_code", "")
            e.message = result.get("return_msg", "")
            # logging.error(result)
            raise Exception("微信支付错误, err_code_des:" + result.get("err_code_des", ""))
        self.prepay_id = result.get('prepay_id')
        self.nonce_str = result.get("nonce_str")
        self.code_url = result.get("code_url")
        return self.prepay_id

    def get_pay_params(self):
        web_wx_appid = WePayConfig.APPID
        web_wx_mchid = WePayConfig.MCHID

        prepay_id = self._get_prepay_id()
        param_map = {
            'prepayid': prepay_id,
            'appid': web_wx_appid,
            'partnerid': web_wx_mchid,
            'package': 'Sign=WXPay',
            'noncestr': self.nonce_str,
            'timestamp': str(int(time.time()))
        }
        sign = self.get_sign(param_map)

        param_map['prepay_id'] = prepay_id
        param_map['sign'] = sign

        return param_map

    def do_pay_params(self):
        web_wx_appid = WePayConfig.APPID
        web_wx_mchid = WePayConfig.MCHID

        prepay_id = self._get_prepay_id()
        param_map = {
            'prepayid': prepay_id,
            'appid': web_wx_appid,
            'partnerid': web_wx_mchid,
            'package': 'Sign=WXPay',
            'noncestr': self.nonce_str,
            'timestamp': str(int(time.time()))
        }

        sort_param = sorted(
            [(key, value) for key, value in param_map.items()],
            key=lambda x: x[0]
        )

        sign = self.get_sign(param_map)

        pay_params = '&'.join(['='.join(x) for x in sort_param])
        pay_params += "&sign=" + sign

        data = {
            "prepay_id": prepay_id,
            'pay_params': pay_params
        }
        return data

    def verify_notice_sign(self, xml):
        """
        校验签名
        """
        root = xml
        param_map = {}
        sign = ""
        for child in root:
            if child.tag != "sign":
                param_map[child.tag] = child.text
            else:
                sign = child.text

        we_sign = self.get_sign(param_map)

        if sign == we_sign:
            return True
        else:
            return False

    def mk_qr(self, content):
        """
        生成二维码图片
        :param content:
        :return:
        """
        # 1. make qr_image
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image()
        img = img.convert("RGBA")
        # img.save(img_path, quality=100)
        return img

    def get_qr_base64_code(self):
        """
        获取微信支付二维码
        :return:
        """
        # 微信支付验证签名，请求微信接口等
        self.do_pay_params()
        # 生成二维码
        img = self.mk_qr(self.code_url)
        # 二维码base64编码 reference：https://www.jianshu.com/p/2ff8e6f98257
        img = image_to_base64(img)
        img = 'data:image/png;base64,' + img.decode()
        return img


def image_to_base64(img):
    """
    图片转base64编码
    :param img:
    :return:
    """
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG', quality=100)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


def base64_to_image(base64_str, image_path=None):
    """
    base64文件解码  用于测试
    :param base64_str:
    :param image_path:
    :return:
    """
    import re
    from PIL import Image
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img
