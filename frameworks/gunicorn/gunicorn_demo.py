# -*- coding: utf-8 -*-
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file: gunicorn_demo.py
@time: 2019-07-09 20:48

这一行开始写关于本文件的说明与解释
"""

from flask import Flask

app = Flask(__name__)


@app.route('/demo', methods=['GET'])
def demo():
    return "gunicorn and flask demo"
