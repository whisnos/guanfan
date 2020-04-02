import tornado.web
import urllib.parse
from tornado.escape import json_decode
from chefcmsadmin.tool import applog
from chefcmsadmin.tool.session import session_dict
from chefcmsadmin.config import SESSION_EXPIRE
# 会话管理
import tornado.options
import time

log = applog.get_log('web.basehandler')

class BaseHandler(tornado.web.RequestHandler):
    def options(self):
        # no body
        self.set_status(204)
        raise tornado.web.Finish()

    def get_current_user(self):
        ''' 验证用户是否登录 '''
        # return True # DEBUG, 不验证登录
        sessionbyte = self.get_secure_cookie("cmsadmincookie")
        if sessionbyte is None:
            # return None
            self.send_cms_msg(9999, '未登录,请先登录', None)
        sessionid = sessionbyte.decode('utf-8')
        # print("auth:",sessionid)
        # print("sessionlist:",session_dict)
        if session_dict.get(sessionid, False) is False:
            # 返回数据
            self.send_cms_msg(9999, '未登录,请先登录', None)
        else:
            stamp = time.time()
            if stamp - session_dict.get(sessionid).get('timestamp') > SESSION_EXPIRE:
                # 会话超时
                session_dict.pop(sessionid)
                self.set_secure_cookie('cmsadmincookie', '', expires=None)
                self.clear_cookie("cmsadmincookie")
                # self.send_cms_msg(9999, '会话已超时,请先登录', None)
                self.send_cms_msg(9999, '会话已超时,请先登录', None)
            else:
                # 更新会话时间
                session_dict.get(sessionid).update(timestamp=stamp)
                return sessionid
        # return self.get_secure_cookie("cmsadmincookie")


    def send_cms_msg(self, code, msg='ok', result=None, **kwargs):
        '''设置CMS接口回调内容'''
        responsedict = {}
        responsedict.setdefault('code', code)
        responsedict.setdefault('msg', msg)
        responsedict.setdefault('data', result)
        responsedict.update(kwargs)
        self.write(responsedict)
        raise tornado.web.Finish()

    def send_message(self, success, code, msg='ok', result=None):
        '''send error message'''
        responsedict = {}
        responsedict.setdefault('success', success)
        responsedict.setdefault('code', code)
        responsedict.setdefault('message', msg)
        responsedict.setdefault('result', result)
        self.write(responsedict)
        raise tornado.web.Finish()

    def set_default_headers(self):
        ''' 设置header头部 '''
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "*")


    def clear_user_session(self):
        '''清除用户的会话'''
        sessionbyte = self.get_secure_cookie("cmsadmincookie")
        sessionid = sessionbyte.decode('utf-8')
        if session_dict.get(sessionid):
            # 清除会话
            session_dict.pop(sessionid)
        # 删除COOKIE
        self.set_secure_cookie('cmsadmincookie', '', expires=None)
        self.clear_cookie("cmsadmincookie")

    def prepare(self):
        ''' 所有请求都经过这里 '''
        # print(self.request.headers)
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        # self.set_header('Access-Control-Allow-Methods', 'POST, GET')

        # if self.request.headers['Content-Type'] == 'application/x-json':
        #     self.args = json_decode(self.request.body)
        pass

    def verify_arg_legal(self, value, description, is_sensword=False, is_len=False, olen=10, **kwargs):
        ''' 校验参数是否合法 '''
        value = value.strip()
        if is_sensword:
            # 需要检查敏感词
            pass
            # for word in SENSTIVE_WORD:
            #     if word in value:
            #         return self.send_message(False, 1999, '操作失败! {},出现敏感词:{}'.format(description ,word))
            #     else:
            #         continue
        if is_len:
            # 需要判断长度
            if len(value) > olen:
                return self.send_message(False, 1998, '操作失败! {},内容长度大于:{}'.format(description ,olen))
            else:
                pass

        if kwargs.get('is_num'):
            # 判断是否是纯数字
            try:
                if isinstance(value, str):
                    int(value)
                else:
                    return self.send_message(False, 1995, '操作失败! {} 不是数字'.format(description))
            except ValueError as e:
                return self.send_message(False, 1997, '操作失败! {} 不是数字'.format(description))

        if kwargs.get('uchecklist'):
            # 列表内容校验
            if value not in kwargs.get('user_check_list'):
                return self.send_message(False, 1996, '操作失败! {} 内容不合法'.format(description))

        if kwargs.get('ucklist'):
            # 列表内容校验
            if value not in kwargs.get('user_check_list'):
                return self.send_message(False, 1996, '操作失败! {} 内容不合法'.format(description))
                
        if kwargs.get('img'):
            # 图片内容校验
            if value.endswith('.jpg') is False and value.endswith('.png') is False:
                return self.send_message(False, 1995, '操作失败! {} 内容不合法'.format(description))
            if value.count('/') !=4:
                return self.send_message(False, 1994, '操作失败! {} 内容格式错误'.format(description))

        return value
        
    def on_finish(self):
        ''' 所有请求调用结束时执行 '''
        # print(self.request.query,self.request.path, self.request.full_url)
        # print(dir(self.request))
        # log.info(self.request.protocol + '://' + self.request.host + self.request.uri)
        userid = None #未登录的用户
        # print(hasattr(self, 'token_session'))
        if hasattr(self, 'token_session'):
            token = self.get_session()
            userid = token.get('id', 0) # 0表示未知用户

        # print(self.request.remote_ip,type(self.request.remote_ip))
        log.info("port:{}| userid: {}| ip:{}| uri: {}| body: {}".format(
            tornado.options.options.port,
            userid,
            self.request.remote_ip,
            self.request.uri,
            urllib.parse.unquote(self.request.body.decode('utf-8'), errors='replace')))
