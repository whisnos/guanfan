# -*- coding: utf-8 -*-
'''
Created on 2012-7-3

@author: lihao
'''
# import requests
from aiohttp_requests import requests
from chefserver.config import TAO_APP_KEY, TAO_APP_SECRET

try:
    import httplib
except ImportError:
    import http.client as httplib
import urllib
import time
import hashlib
import json
import itertools
import mimetypes

'''
定义一些系统变量
'''

SYSTEM_GENERATE_VERSION = "taobao-sdk-python-20200428"

P_APPKEY = "app_key"
P_API = "method"
P_SESSION = "session"
P_ACCESS_TOKEN = "access_token"
P_VERSION = "v"
P_FORMAT = "format"
P_TIMESTAMP = "timestamp"
P_SIGN = "sign"
P_SIGN_METHOD = "sign_method"
P_PARTNER_ID = "partner_id"

P_CODE = 'code'
P_SUB_CODE = 'sub_code'
P_MSG = 'msg'
P_SUB_MSG = 'sub_msg'

N_REST = '/router/rest'


def sign(secret, parameters):
    # ===========================================================================
    # '''签名方法
    # @param secret: 签名需要的密钥
    # @param parameters: 支持字典和string两种
    # '''
    # ===========================================================================
    # 如果parameters 是字典类的话
    if hasattr(parameters, "items"):
        keys = parameters.keys()
        # keys.sort()
        sorted(keys)

        parameters = "%s%s%s" % (secret,
                                 str().join('%s%s' % (key, parameters[key]) for key in keys),
                                 secret)
    sign = hashlib.md5(parameters.encode()).hexdigest().upper()
    return sign


def mixStr(pstr):
    if (isinstance(pstr, str)):
        return pstr
    elif (isinstance(pstr, unicode)):
        return pstr.encode('utf-8')
    else:
        return str(pstr)


class FileItem(object):
    def __init__(self, filename=None, content=None):
        self.filename = filename
        self.content = content


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = "PYTHON_SDK_BOUNDARY"
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, str(value)))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((mixStr(fieldname), mixStr(filename), mixStr(mimetype), mixStr(body)))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [part_boundary,
             'Content-Disposition: form-data; name="%s"' % name,
             'Content-Type: text/plain; charset=UTF-8',
             '',
             value,
             ]
            for name, value in self.form_fields
        )

        # Add the files to upload
        parts.extend(
            [part_boundary,
             'Content-Disposition: file; name="%s"; filename="%s"' % \
             (field_name, filename),
             'Content-Type: %s' % content_type,
             'Content-Transfer-Encoding: binary',
             '',
             body,
             ]
            for field_name, filename, content_type, body in self.files
        )

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class TopException(Exception):
    # ===========================================================================
    # 业务异常类
    # ===========================================================================
    def __init__(self):
        self.errorcode = None
        self.message = None
        self.subcode = None
        self.submsg = None
        self.application_host = None
        self.service_host = None

    def __str__(self, *args, **kwargs):
        sb = "errorcode=" + mixStr(self.errorcode) + \
             " message=" + mixStr(self.message) + \
             " subcode=" + mixStr(self.subcode) + \
             " submsg=" + mixStr(self.submsg) + \
             " application_host=" + mixStr(self.application_host) + \
             " service_host=" + mixStr(self.service_host)
        return sb


class RequestException(Exception):
    # ===========================================================================
    # 请求连接异常类
    # ===========================================================================
    pass


class RestApi(object):
    # ===========================================================================
    # Rest api的基类
    # ===========================================================================

    def __init__(self, domain='http://gw.api.taobao.com/router/rest', port=80,KEY=None,SECRET=None):
        # =======================================================================
        # 初始化基类
        # Args @param domain: 请求的域名或者ip
        #      @param port: 请求的端口
        # =======================================================================
        self.__domain = domain
        self.__port = port
        self.__httpmethod = "POST"
        self.__app_key = KEY
        self.__secret = SECRET
        # if (top.getDefaultAppInfo()):
        #     self.__app_key = top.getDefaultAppInfo().appkey
        #     self.__secret = top.getDefaultAppInfo().secret

    def get_request_header(self):
        return {
            'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive",
        }

    def set_app_info(self, appinfo):
        # =======================================================================
        # 设置请求的app信息
        # @param appinfo: import top
        #                 appinfo top.appinfo(appkey,secret)
        # =======================================================================
        self.__app_key = appinfo.appkey
        self.__secret = appinfo.secret

    def getapiname(self):
        return ""

    def getMultipartParas(self):
        return [];

    def getTranslateParas(self):
        return {};

    def _check_requst(self):
        pass

    # 淘宝sign签名算法
    def get_Taobao_Sign(self, paramets):
        app_secret = self.__secret
        dict = sorted(paramets.items(), key=lambda d: d[0])
        # 遍历出排序好的数据
        string = ""
        print(6666666)
        for i in range(len(dict)):
            for j in range(len(dict[i])):
                # 把排序好的数据遍历出并拼接在一起
                string = string + dict[i][j]
        pinjie = app_secret + string + app_secret
        # 为拼接好的字符串加密形成sign签名
        sign = ''

        # 把拼接的字符串通过MD5加密
        md = hashlib.md5()
        md.update(pinjie.encode())
        sign = md.hexdigest()
        sign = sign.upper()
        # print "get_Taobao_sign=="+sign
        return sign

    # 公共参数
    def get_public_parameter(self):
        public_parameter = {
            P_FORMAT: 'json',
            P_APPKEY: self.__app_key,
            P_SIGN_METHOD: "md5",
            P_VERSION: '2.0',
            P_TIMESTAMP: str(int(time.time() * 1000)),
            # P_PARTNER_ID: SYSTEM_GENERATE_VERSION,
            P_API: self.getapiname(),
        }
        return public_parameter

    def get_other_parameter(self, public_parameter=None, data=None):
        if data:
            for k, v in data.items():
                public_parameter[k] = v
        return public_parameter


    async def repeat_try(self,data,public_parameter):
        for i in range(1, 4):
            print('无结果 尝试3次')
            print('第'+str(i)+'次')
            # res = await self.getResponse(data=data)
            response = await requests.post('http://gw.api.taobao.com/router/rest', params=public_parameter)
            text = await response.text()
            jsonobj = json.loads(text)
            print('jsonobj', jsonobj)
            if "error_response" not in jsonobj.keys():
                print("error_response...............首次获取失败，进入3次获取")
                return jsonobj
        return False

    async def getResponse(self, public_parameter=None, data=None, timeout=30):
        # =======================================================================
        # 获取response结果
        # =======================================================================
        public_parameter = self.get_public_parameter()

        public_parameter = self.get_other_parameter(public_parameter, data)
        application_parameter = self.getApplicationParameters()

        sign_parameter = public_parameter.copy()
        sign_parameter.update(application_parameter)

        public_parameter["sign"] = self.get_Taobao_Sign(sign_parameter)
        response = await requests.post('http://gw.api.taobao.com/router/rest', params=public_parameter)
        text = await response.text()
        if response.status is not 200:
            raise RequestException('invalid http status ' + str(response.status) + ',detail body:' + text)
        # result = response.read()
        # for a in text:
        #     print(99,a)
        jsonobj = json.loads(text)
        if "error_response" in jsonobj.keys():
            print("error_response...............首次获取失败，进入3次获取")
            res = await self.repeat_try(data,public_parameter)
            return res
        print('jsonobj',jsonobj)
        return jsonobj

    def getApplicationParameters(self):
        application_parameter = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__") and not key in self.getMultipartParas() and not key.startswith(
                    "_RestApi__") and value is not None:
                if (key.startswith("_")):
                    application_parameter[key[1:]] = value
                else:
                    application_parameter[key] = value
        # 查询翻译字典来规避一些关键字属性
        translate_parameter = self.getTranslateParas()
        for key, value in application_parameter.items():
            if key in translate_parameter:
                application_parameter[translate_parameter[key]] = application_parameter[key]
                del application_parameter[key]
        return application_parameter
