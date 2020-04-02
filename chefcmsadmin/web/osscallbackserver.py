# -*- coding: utf-8 -*-
from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict
from urllib import parse, request
import base64
import hashlib
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5

log = applog.get_log('web.osscallbackhandler')


class OssCallBackHandler(BaseHandler):
    async def post(self):
        # arg_key = change_byte_to_dict(self.request.body, self.request.query)
        # print(self.request.body.decode('utf-8'))
        log.debug("header:{}".format(self.request.headers))
        log.debug("uri:{}".format(self.request.uri))
        log.debug("body:{}".format(self.request.body.decode('utf-8')))
        # responsedict = {"Status":"OK"} # 图片校验正确,返回给OSS正常
        auth_str = get_message(
            self.request.uri, self.request.body.decode('utf-8'))
        log.debug("auth_str:{}".format(auth_str))
        res = oss_auth_crypto_verify(auth_str,
                                     self.request.headers['Authorization'],
                                     self.request.headers['X-Oss-Pub-Key-Url']
                                     )
        log.debug("结果:{}".format(res))
        responsedict = {"Status": "fail", "msg": res}  # 图片校验正确,返回给OSS正常
        self.write(responsedict)


def oss_auth_crypto_verify(auth_str, authorizationbs64, pub_key_url_bs64):
    authorization = base64.b64decode(authorizationbs64)
    pub_key_url = ''
    try:
        # pub_key_url = base64.b64decode(bytes(pub_key_url_bs64, 'utf-8')).decode()
        # url_reader = request.urlopen(pub_key_url)
        # pub_key = url_reader.read()
        # print(pub_key)
        with open('../callback_pub_key_v1.pem', 'rb') as kread:
            pub_key = kread.read()
            # print(pub_key)
    except Exception as ex:
        log.error("未获取到阿里pem公钥:{}".format(ex))
        return False
    try:
        verifier = Signature_pkcs1_v1_5.new(RSA.import_key(pub_key))
        digest = MD5.new(bytes(auth_str, 'utf-8'))
        result = verifier.verify(digest, authorization)
    except Exception as e:
        log.error("公钥验证执行错误:{}".format(e))
        result = False
    return result


def get_message(urlpath, callback_body):
    '''
        获取要验证的文本
        urlpath = /api/osscallguanfanback?authid=c26ecc32-435d-4d9b-b08f-badda672f0b2
        body=filename=test%2Fcaipu%2F1%2F4%2F5%2F149c3bcb6cb7a57abe87d8372f265e35.jpg&size=
        10606&mimeType=image%2Fjpeg&height=400&width=650
    '''
    auth_str = ''
    pos = urlpath.find('?')
    if -1 == pos:
        auth_str = urlpath + '\n' + callback_body
    else:
        auth_str = request.unquote(
            urlpath[0:pos]) + urlpath[pos:] + '\n' + callback_body
    return auth_str


if __name__ == '__main__':
    oss_public_key_url = "aHR0cHM6Ly9nb3NzcHVibGljLmFsaWNkbi5jb20vY2FsbGJhY2tfcHViX2tleV92MS5wZW0="
    authorization = "WxTga53k31TD59o6JF1jh9zcrInTDlfodb0OgQuzlO5Qaf18NxcqxlcpU4gMuhUrQ0lTmWrXji8gFVTKIc9JJQ=="
    uri = '/api/osscallguanfanback?authid=4af091d4-c5c9-4e18-bbdc-2fe489f4887f'
    callback_body = "filename=test%2Fcaipu%2F5%2Fa%2F2%2F5aa308723660421a560fcc062d745502.jpg" \
        "&size=10606&mimeType=image%2Fjpeg&height=400&width=650"
    auth_str = get_message(uri, callback_body)
    log.info("auth_str:{}".format(auth_str))
    res = oss_auth_crypto_verify(auth_str, authorization, oss_public_key_url)
    print(res)
    # import traceback
    # try:
    #     base64.b64decode("sfasdfasfsadf")
    # except base64.binascii.Error as e:
    #     log.info(e)
    #     print(traceback.print_exception())
    #     # traceback.print_exc()
    # else:
    #     print("else")
    # finally:
    #     print("finally")