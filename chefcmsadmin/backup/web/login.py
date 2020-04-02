from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from chefcmsadmin.tool.session import session_dict
from tornado.web import authenticated
import uuid,time

log = applog.get_log('web.login')
dbins = DbOperate.instance()

class LoginHandler(BaseHandler):
    async def get(self):
        username = self.verify_arg_legal(self.get_argument('username'), '用户名', False, is_len=True, olen=20)
        password = self.verify_arg_legal(self.get_argument('password'), '密码', False, is_len=True, olen=20)
        # print(username, password)
        login_result = await logincms(username, password)
        if login_result:
            randid = str(uuid.uuid4())
            if not self.get_secure_cookie("cmsadmincookie"):
                self.clear_cookie("cmsadmincookie")

            self.set_secure_cookie("cmsadmincookie", randid, expires=None)
            # print("设置安全安全cookie:",self.get_secure_cookie('cmsadmincookie'), randid)
            session_dict.setdefault(randid, {"timestamp":time.time(), "username":username})
            self.send_cms_msg(0, '登入成功', {"access_token":"loginsuccess"})
        else:
            self.send_cms_msg(9999, 'login faile', None)

class UserInfoHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取个人用户信息 '''
        if not self.get_secure_cookie("cmsadmincookie"):
            self.set_secure_cookie("cmsadmincookie", "administrator")
        username = self.get_argument('username')
        password = self.get_argument('password')
        # print(username, password)
        self.send_cms_msg(0, 'success', {"access_token":"safwe9fw293287dsfa0f709adf927"})

class LogoutHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 退出登录 '''
        self.clear_user_session()
        self.send_cms_msg(0, 'login out success', None)

class SessionHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 确定用户是否登录 '''
        self.send_cms_msg(0, 'success', {"username": "管理员", "sex": "男", "role": 0})

async def logincms(username, password):
    ''' 登录CMS '''
    login_sql = '''
    select id from sys_user where name = ? and password= ? and status = 1 limit 1
    '''
    cms_login_result = await dbins.selectone(login_sql, (username, password))
    # print(cms_login_result)
    if cms_login_result:
        # 找到用户
        return True
    else:
        return False

if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)


    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_logincms())