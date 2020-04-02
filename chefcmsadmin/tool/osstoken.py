# -*- coding: UTF-8 -*-

import socket
import base64
import sys
import time
import datetime
import json
import hmac
import uuid
from hashlib import sha1 as sha
from chefcmsadmin.config import ALIYUN_SMS_ID,ALIYUN_SMS_KEY_SECRET,ALIYUN_OSS_HOST, ALIYUN_OSS_CALLBACK


APIVERSION='2015-04-01'
# 请填写您的AccessKeyId。
access_key_id = ALIYUN_SMS_ID
# 请填写您的AccessKeySecret。
access_key_secret = ALIYUN_SMS_KEY_SECRET

# host的格式为 bucketname.endpoint ，请替换为您的真实信息。
host = ALIYUN_OSS_HOST
# callback_url为 上传回调服务器的URL，请将下面的IP和Port配置为您自己的真实信息。
callback_url = ALIYUN_OSS_CALLBACK
# 用户上传文件时指定的前缀。
expire_time = 30


def get_iso_8601(expire):
    gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
    gmt += 'Z'
    return gmt


def get_token(startpath=''):
    now = int(time.time())
    expire_syncpoint = now + expire_time
    # expire_syncpoint = 1612345678
    expire = get_iso_8601(expire_syncpoint)

    policy_dict = {}
    policy_dict['expiration'] = expire
    condition_array = []
    array_item = []
    # array_item.append('eq') # 限制文件上传名字
    # array_item.append('$key')
    # array_item.append(startpath)
    array_item.append('starts-with') # 限制文件上传目录
    array_item.append('$key')
    array_item.append(startpath)
    condition_array.append(array_item)
    condition_length_item = []
    condition_length_item.append('content-length-range')
    condition_length_item.append(0)
    condition_length_item.append(10485760)
    condition_array.append(condition_length_item)
    policy_dict['conditions'] = condition_array

    policy = json.dumps(policy_dict).strip()
    policy_encode = base64.b64encode(policy.encode())
    h = hmac.new(access_key_secret.encode(), policy_encode, sha)
    sign_result = base64.encodestring(h.digest()).strip()

    # 阿里云图片上传回调
    # callback_dict = {}
    # callback_dict['callbackUrl'] = callback_url + '?authid=' + str(uuid.uuid4())
    # callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}' \
    #                                 '&height=${imageInfo.height}&width=${imageInfo.width}'
    # callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded'
    # callback_param = json.dumps(callback_dict).strip()
    # base64_callback_body = base64.b64encode(callback_param.encode())

    token_dict = {}
    token_dict['accessid'] = access_key_id
    token_dict['host'] = host
    token_dict['policy'] = policy_encode.decode()
    token_dict['signature'] = sign_result.decode()
    token_dict['expire'] = expire_syncpoint
    token_dict['dir'] = startpath
    # token_dict['callback'] = base64_callback_body.decode()
    # result = token_dict
    return token_dict

if __name__ == '__main__':
    print(get_token('haibao/config'))
