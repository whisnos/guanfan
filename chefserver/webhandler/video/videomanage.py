"""
# 阿里云视频应用管理
# 
"""

from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.tool.asynchttp import async_http_response
from chefserver.tool.tooltime import curDatetime
from tornado.escape import json_decode, json_encode

import uuid
import datetime
import hmac
import base64
from urllib.parse import urlencode, quote
from chefserver.config import ALIYUN_SMS_ID, ALIYUN_SMS_KEY_SECRET
import datetime

class AliyunMediaAdapter(object):
    def __init__(self):
        self.format = "JSON"
        self.version = "2017-03-21"
        self.key = ALIYUN_SMS_ID
        self.secret = ALIYUN_SMS_KEY_SECRET
        self.signature_method = "HMAC-SHA1"
        self.signature_version = "1.0"
        self.signature_nonce = str(uuid.uuid4())
        self.timestamp = datetime.datetime.utcnow().isoformat("T")
        self.region_id = 'cn-shanghai'
        self.gateway = 'http://vod.cn-shanghai.aliyuncs.com'
        self.action = "CreateAppInfo"
        self.params = [] # 获取参数元祖参数对[("Title","你好未来"),('a','b')]

    def get_signature_url(self, action, params):
        self.action = action
        self.params = params
        query_string = self.build_query_string()
        url = self.gateway + '/?' + query_string
        return url

    def build_query_string(self):
        query = []
        query.append(("Format", self.format))
        query.append(("Version", self.version))
        query.append(("AccessKeyId", self.key))
        query.append(("SignatureMethod", self.signature_method))
        query.append(("SignatureVersion", self.signature_version))
        query.append(("SignatureNonce", self.signature_nonce))
        query.append(("Timestamp", self.timestamp))
        query.append(("Action", self.action))
        query.extend(self.params)
        query = sorted(query, key=lambda key: key[0])
        query_string = ""
        for item in query:
            query_string += quote(item[0], safe="~") + "=" + quote(item[1], safe="~") + "&"
        query_string = query_string[:-1]
        tosign = "GET&%2F&" + quote(query_string, safe="~")
        secret = self.secret + "&"
        hmb = hmac.new(secret.encode("utf-8"), tosign.encode("utf-8"), "sha1").digest()
        signature_str = quote(base64.standard_b64encode(hmb).decode("ascii"), safe="~")
        query_string += "&" + "Signature=" + signature_str
        return query_string

async def create_app():
    # 创建视频应用
    media = AliyunMediaAdapter()
    param = []
    param.append(("AppName", '管饭现网短视频'))
    param.append(("Description", '管饭现网短视频,用于现网视频相关数据存储'))

    signtureURL = media.get_signature_url("CreateAppInfo", param)
    print(signtureURL)
    success, result = await async_http_response(signtureURL, datatype='json')
    print(success, result)


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_app())