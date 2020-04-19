# -*- coding: utf-8 -*-
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file: file_downloder.py
@time: 2020/4/19 11:13

这一行开始写关于本文件的说明与解释


"""
import os
import requests
import tqdm
import logging


def download(url, dst):
    """
    给定 url，目标路径，stream 下载，附进度条
    :param url: str，下载 url
    :param dst: str，目标路径
    :return: 文件大小
    """
    try:
        with requests.get(url, stream=True, timeout=3) as r:
            if r.status_code == 404:
                return 0
            if r.headers.get('Content-Length'):
                file_size = int(r.headers.get('Content-Length'))
            else:
                file_size = 0
    except Exception as e:
        logging.warning(e)
        return 0
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size and file_size:
        return file_size
    logging.info('--- %s is downloading... ---' % url)
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    pbar = tqdm.tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=url.split('/')[-1])
    try:
        req = requests.get(url, headers=header, stream=True, timeout=500)
    except Exception as e:
        logging.warning(e)
        return 0
    with(open(dst, 'ab')) as f:
        try:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        except Exception as e:
            logging.warning(e)
            pbar.close()
    return file_size
