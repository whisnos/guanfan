"""
# 第三方登录
# 第三方绑定
"""
import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.asynchttp import async_http_response
# from chefserver.webhandler.common_action import is_my_id
from chefserver.tool.tooltime import curDatetime,curTimeStamp
from chefserver.tool.function import get_uuid
from chefserver.tool.async_redis_pool import RedisOperate
from chefserver.webhandler.cacheoperate import CacheUserinfo
from chefserver.config import APPLE_PUBLIC_KEY_PEM, APPLE_GUANFAN_CLIEND_ID
import random
# import jwt
import python_jwt as jwt
log = applog.get_log('webhandler.authverify')
dbins = DbOperate.instance()


class AuthVerifyHandler(BaseHandler):
    ''' 第三方验证以及登录 '''
    async def post(self):
        openid = self.verify_arg_legal(self.get_body_argument('openid'), '第三方用户ID', False, is_len=True, olen=200)
        platform = self.verify_arg_legal(self.get_body_argument('platform'), '平台', False, uchecklist=True, user_check_list=['1','2','3'])
        if platform == '3':
            access_token = self.verify_arg_legal(self.get_body_argument('access_token'), '授权码', False, is_len=True, olen=1000)
        else:
            access_token = self.verify_arg_legal(self.get_body_argument('access_token'), '授权码', False, is_len=True, olen=200)

        success, code, message, result = await auth_verify_login(openid, access_token, platform)
        return self.send_message(success, code, message, result)

class AuthBindHandler(BaseHandler):
    ''' 注册+登录绑定 '''
    async def post(self):
        # myid = self.get_session().get('id', 0)
        openid = self.verify_arg_legal(self.get_body_argument('openid'), '第三方用户ID', False, is_len=True, olen=200)
        platform = self.verify_arg_legal(self.get_body_argument('platform'), '平台', False, uchecklist=True, user_check_list=['1','2','3'])
        if platform == '3':
            access_token = self.verify_arg_legal(self.get_body_argument('access_token'), '授权码', False, is_len=True, olen=1000)
        else:
            access_token = self.verify_arg_legal(self.get_body_argument('access_token'), '授权码', False, is_len=True, olen=200)

        faceimg = self.verify_arg_legal(self.get_body_argument('faceimg'), '头像地址', False, is_len=True, olen=254)
        nickname = self.verify_arg_legal(self.get_body_argument('nickname'), '昵称', False, is_len=True, olen=40)
        phone = self.verify_arg_legal(self.get_body_argument('phone'), '手机号', False, is_not_null=True)
        verify = self.verify_arg_legal(self.get_body_argument('verify'), '验证码', False, is_len=True, olen=6, is_not_null=True)
        success, code, message, result = await auth_bind_user(openid, access_token, platform,
            faceimg,
            nickname,
            phone,
            verify)
        self.send_message(success, code, message, result)

async def auth_bind_user(openid, access_token, platform,
            faceimg,
            nickname,
            phone,
            verify):
    ''' 绑定第三方用户 '''
    # 校验 绑定验证码是否正确
    access_token = access_token[:100]

    rdskey = "phone.verify.{}:{}".format("bind", phone)
    rdget = await RedisOperate().instance().get_data(rdskey)
    if rdget != verify:
        # 手机验证码正确
        return False, 1036, "错误的验证码", None
    else:
        # 验证码正确的话，删除
        await RedisOperate().instance().del_data(rdskey)

    # 判断第三方信息是否已存在
    plat_user = await check_openid_exists(openid, platform, access_token)
    # print(openid, platform, access_token)
    if plat_user is False:
        # 不存在绑定信息
        return False, 1037, "错误的第三方登录信息,绑定失败", None

    # 获取根据手机号获取用户ID
    ures, userid = await get_userid(phone)
    nickname_only = await nickname_rename(nickname,userid)

    if ures is False:
        # 未注册用户,插入用户
        insert_auth_sql = "INSERT INTO user (`username`, `headImg`, `mobile`, `sex`, `createTime`, `updateTime`)" \
                                     "VALUES(?,          ?,        ?,         ?,     ?,            ?)"
        sqllist = []
        sqllist.append((insert_auth_sql, (nickname_only, faceimg, phone, 0, curDatetime(),curDatetime())))
        sqllist.append(('select last_insert_id() as nid',()))
        result = await dbins.execute_many(sqllist)
        if result is None:
            return False, 3015, "添加用户失败,请重试", None
        userid = result[1][1][0]
    else:
        # 已注册的用户,先校验是否绑定了第三方登录账号
        bind_is_exists, bindchekmsg = await check_user_already_bind(userid, platform, plat_user.get('id', 0))
        if bind_is_exists:
            if '1' == platform:
                log.warning("手机号:{} 已绑定微信账号".format(phone))
                return False, 1047, "该手机号已绑定微信账号", None
            else:
                log.warning("手机号:{} 已绑定微博账号".format(phone))
                return False, 1048, "该手机号已绑定微博账号", None

        # 已注册用户,更新用户信息
        up_auth_sql = "UPDATE user set headImg = ?, username = ? where id = ? "
        up_user_result = await dbins.execute(up_auth_sql, (faceimg, nickname_only, userid))
        if up_user_result is None:
            return False, 3016, "更新用户数据失败", None

    # 更新绑定信息
    bind_sql = "UPDATE auth_info set userid=? where id=?"
    bind_sql_result = await dbins.execute(bind_sql, (userid, plat_user.get("id")))

    if bind_sql_result is None:
        log.error("绑定用户失败,userid:{}, openid:{}".format(userid, openid))
        return False, 3017, "绑定用户失败", None
    else:
        # return True, 0, '绑定成功', None
        # 绑定成功后直接去登录
        success, token = await login_create_token(userid)
        if success:
            return True, 0, '登录成功', {'token': token.replace('token:', '')}
        else:
            return False, 3099, token, None


async def check_user_already_bind(userid, platform, authid=0):
    ''' 判断用户是否已经绑定一个对应平台的第三方账号 '''
    userid_auth_exists_sql = "SELECT id from auth_info where userid=? and platform=? LIMIT 1"
    result = await dbins.selectone(userid_auth_exists_sql, (userid, platform))
    if result is None:
        return False, "未绑定"
    else:
        # 获取auth ID
        if authid == 0:
            return True, "已绑定"
        elif authid == result.get('id'):
            return False, "authid 相同,未绑定"
        else:
            return True, '已绑定'

async def nickname_rename(nickname,userid):
    ''' 获取不重复的昵称 '''
    nick_sql = "SELECT id from user where id!=? and username=? and status=0 LIMIT 1"
    result = await dbins.selectone(nick_sql, (userid, nickname))

    if result is None:
        return nickname
    else:
        return nickname + '_' +''.join(random.sample('1z2yx5w6v7u8t9srqpon3m4lkji0hgfedcba',5))


async def get_userid(phone):
    ''' 获取用户手机号 '''
    userid_sql = "SELECT id from user where mobile=? and status=0 LIMIT 1"
    result = await dbins.selectone(userid_sql, (phone))

    if result is None:
        return False, "未知用户"
    else:
        # 获取用户ID
        return True, result.get("id")


async def auth_verify_login(openid, access_token, platform):
    ''' 验证accesstoken合法性数据'''
    if '1' == platform:
        success, result = await auth_verify_weixin(openid, access_token)
    elif '2' == platform:
        success, result = await auth_verify_weibo(openid, access_token)
    elif '3' == platform:
        success, result =  auth_verify_apple(openid, access_token)
    else:
        return True, 1011, '未知平台类型', None

    access_token = access_token[:100]
    # success = True
    if success:
        # 认证通过
        db_res = await check_openid_exists(openid, platform) # 查询openid是否已存在
        if db_res is False:
            # 未添加过的openid,直接插入
            insert_sql = "INSERT INTO auth_info (`openid`, `access_token`, `platform`, `updatetime`, `createtime`)" \
                                       " VALUES (?,         ?,              ?,          ?,           ?)"
            sql_result = await dbins.execute(insert_sql, (openid, access_token, platform, curDatetime(), curDatetime()))
            if sql_result is not None:
                return True, 0, '认证添加成功', None
            else:
                return False, 3089, '添加失败,请重试', None
        else:
            # 已存在openid,更新accesstoken,并登录系统返回管饭token
            userid = db_res.get("userid")
            recordid = db_res.get("id")
            update_accesstoken_sql = "UPDATE auth_info set access_token=? WHERE id=?"
            update_result = await dbins.execute(update_accesstoken_sql, (access_token, recordid))
            if update_result is None:
                return False, 3089, '更新失败,请重试', None
            else:
                # 创建token 登录成功并返回
                if userid == 0:
                    ''' 认证成功,未绑定的用户 '''
                    return True, 0, '认证更新成功', None

                success, token = await login_create_token(userid)
                if success:
                    return True, 1, '登录成功', {'token': token.replace('token:', '')}
                else:
                    return False, 3099, token, None
    else:
        # 认证失败
        return False, 2088, '认证失败', result


async def login_create_token(userid):
    ''' 创建管饭用户会话 '''
    if userid == 0:
        return False, "未绑定用户"

    sql_user = "SELECT mobile, username FROM user WHERE id=? and status=0 LIMIT 1"
    sql_user_result = await dbins.selectone(sql_user, (userid))
    if sql_user_result is None:
        log.error("不合法或不存在的用户,userid:{}".format(userid))
        return False, "不合法或不存在的用户"

    uid = get_uuid()
    key = "token:{}".format(uid)
    value = {'id':userid, 'phone': sql_user_result.get('mobile'),'nickname': sql_user_result.get('username'), 'login': curTimeStamp(), 'loginby':2}
    rdsave_result = await RedisOperate().instance().set_data(key, value)
    if rdsave_result != 'OK':
        log.error("创建管饭TOKEN失败,userid:{}".format(userid))
        return False, "创建会话失败"
    cachinfo_res = await CacheUserinfo(userid).createCache(force_update=True)
    
    if cachinfo_res is False:
        log.warning("用户个人信息缓存创建失败,userid:{}".format(userid))
    return True, key


async def check_openid_exists(openid,  platform, access_token=None):
    ''' 检测openid是否存在,不存在返回 False,存在返回ID '''
    if access_token is None:
        # 只校验openid
        sql = "SELECT id,userid FROM auth_info WHERE openid=? AND platform=? LIMIT 1"
        get_bind_id_result = await dbins.selectone(sql, (openid, platform))
        if get_bind_id_result is not None:
            return get_bind_id_result
        else:
            return False
    else:
        # 同时校验 access_token 和 openid
        verify_sql = "SELECT id,userid FROM auth_info WHERE openid=? AND platform=? AND access_token=? LIMIT 1"
        get_bind_id_result = await dbins.selectone(verify_sql, (openid, platform, access_token))
        # print (openid, platform, access_token)
        if get_bind_id_result is not None:
            return get_bind_id_result
        else:
            return False


async def auth_verify_weixin(openid, access_token):
    ''' 验证微信  '''
    url = "https://api.weixin.qq.com/sns/auth?access_token={1}&openid={0}".format(openid, access_token)
    success, result = await async_http_response(url, datatype="json")
    if success:
        if 0 == result.get('errcode'):
            return True, 'ok'
        else:
            return False, result.get('errmsg')
    else:
        log.error("微信:{},{},请求失败,错误类型:{}".format(openid, access_token, result))
        return False, "验证超时或失败，请重试"


async def auth_verify_weibo(openid, access_token):
    ''' 验证微博 '''
    url = "https://api.weibo.com/oauth2/get_token_info"
    post_str = "access_token={}".format(access_token)

    success, result = await async_http_response(url, method="POST", post_data=post_str, datatype="json")
    # print(success, result)
    if success:
        if str(result.get('uid')) == openid:
            return True, 'ok'
        else:
            return False, "用户ID不匹配"
    else:
        log.error("微博:{},{},请求失败,错误类型:{}".format(openid, access_token, result))
        return False, result

def auth_verify_apple(openid, access_token):
    ''' 验证苹果第三方登录(APP端) '''
    global apple_public_key_pem
    try:
        header, token_info = jwt.process_jwt(access_token.encode('utf-8'))
        # token_info = jwt.decode(access_token.encode('utf-8'), APPLE_PUBLIC_KEY_PEM,
        #     algorithms=['RS256'],
        #     verify=True,
        #     options={"verify_aud": True}, audience=APPLE_GUANFAN_CLIEND_ID)
        # print(token_info, type(token_info))
        t_sub = token_info.get('sub',False)
        if t_sub:
            if t_sub != openid:
                return False, "错误的sub apple id"
        else:
            return False, "没有找到subid" 

        t_iss = token_info.get('iss',False)

        if t_iss:
            if t_iss.startswith("https://appleid.apple.com") is False:
                return False, "错误的iss签发单位"
        else:
            return False, "没有找到iss签发单位" 

        t_aud = token_info.get('aud',False)
        if t_aud:
            if t_aud != APPLE_GUANFAN_CLIEND_ID:
                return False, "错误的aud客户端ID"
        else:
            return False, "没有找到aud客户端ID"

        t_exp = token_info.get('exp',False)
        if t_exp:
            # print(t_exp, int(curTimeStamp()))
            if t_exp < int(curTimeStamp()):
                return False, "已过期"
        else:
            return False, "错误的时间格式！"

        return True, 'ok'
    except jwt.exceptions.InvalidTokenError as e:
        log.warning("苹果:{},{},验证失败1,错误类型:{}".format(openid, access_token[:100], e.args[0]))
        # print(e)
        return False, e.args[0]
    except ValueError as ve:
        log.warning("苹果:{},{},验证失败2,错误类型:{}".format(openid, access_token[:100], ve.args[0]))
        return False, ve.args[0]
    except Exception as e:
        log.warning("苹果:{},{},验证失败3,错误类型:{}".format(openid, access_token[:100], e))
        return False, e.args[0]

if __name__ == '__main__':
    import asyncio
    async def test_auth_verify_weixin():
        res = await auth_verify_weixin('myopenidtest1231s23', 'sodfoiw3299d9823898fww9832')
        print(res)

    async def test_auth_verify_weibo():
        res = await auth_verify_weibo('myopenidtest1231s23', 'sodfoiw3299d9823898fww9832')
        print(res)

    async def test_login_create_token():
        res = await login_create_token(1)
        print(res)

    async def test_auth_verify_login():
        res = await auth_verify_login('myopenidtest1231s231', '123456769', '1')
        print(res)

    async def test_auth_bind_user():
        res = await auth_bind_user('myopenidtest1231s231', '123456769', '1',
            "http://www.weixin.com/img/xxx.jpg",
            "昵称",
            "18910101010",
            "861902"
            )
        print(res)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_auth_bind_user())

    # identityToken = "eyJraWQiOiJBSURPUEsxIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoiY2hpdGVzdCIsImV4cCI6MTU3ODM4NjM2MSwiaWF0IjoxNTc4Mzg1NzYxLCJzdWIiOiIwMDE3MzUuZjkxNzdiYWNmODQwNGVkYmIyZDk5NDUzMTEwNjJhZmIuMDk0MyIsImNfaGFzaCI6IjZ4Q1pSWmhmZGhtVWVGbnkzVm9ZN2ciLCJlbWFpbCI6ImxhbmZ1bGluZ0BpY2xvdWQuY29tIiwiZW1haWxfdmVyaWZpZWQiOiJ0cnVlIiwiYXV0aF90aW1lIjoxNTc4Mzg1NzYxfQ.KRiZqg-cbXE0zZ49p_5WSC3p2nx0f0crSbw01K_qgWiJUEWlWaKEXzBd4HWIRSa_BstVN49HKmNiNeZ-Zh9iL92KL83t8eziUrdSGAHnyGAg_CWISTUwRjiNFTwraarf5Lrkv-Imdz8ODEkGkmnXYfPe9iElBdm1-UjjyjES8dpvi0FQvJlyGFHSapDfiVQs3CIVBgkjkUlxOtL55m9Utksa2gWYiLRS_WA_erxFVPvzWgZmejKOLvybXdoIquBacASpYh4MftEUC5j4GP61zXANfCqC-mE2Io4aK25yYStJP22YY-574fWu4idPw4YVkOme7-tQ49XXLgfae5-trQ"
    identityToken = "eyJraWQiOiJBSURPUEsxIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoiY2hpdGVzdCIsImV4cCI6MTU3ODM5MDYzMiwiaWF0IjoxNTc4MzkwMDMyLCJzdWIiOiIwMDE3MzUuZjkxNzdiYWNmODQwNGVkYmIyZDk5NDUzMTEwNjJhZmIuMDk0MyIsImNfaGFzaCI6IlJFV3lhQ3ZvZFlQSURLT0hmTXlzOWciLCJlbWFpbCI6ImxhbmZ1bGluZ0BpY2xvdWQuY29tIiwiZW1haWxfdmVyaWZpZWQiOiJ0cnVlIiwiYXV0aF90aW1lIjoxNTc4MzkwMDMyfQ.ef1BRaru0EFbtHRhn1FG1ztK2P-KWuxa790YgsVcxwdH-qdEsV-saOyU1B71W-LIoy6vtldLRsGdkp0bZOS2wBJG6zAOyFRTKJfPcLWT0HdY1_mNpOkeJf32bFrsTDbqBxih7V-wn6vIaK4_UsNniO51MOCFbujYuaV5zHBmyRv5PT-L9m0yOgCycGk4_q3ERyJnR0t_pcWQCWOh7ZEvGUawtX_DTNvNbpQY33SpSvEP8CzFt2gK8q81k7rJ4m1LMisUszdAflAu0iIoQRJe0FTIAhQdH2aP1i1i0adbAkec85hr7UwbsYajW1VcsDfTmFi0Y5mkZv4UXztSHYYSYg"

    # res = auth_verify_apple('idddddd', identityToken)
    # print(res)
    def test_apple_auth(tokenid):
        from jose import jws
        res = jws.verify(tokenid, APPLE_PUBLIC_KEY_PEM, algorithms=['RS256'])
        print(res)
        import json
        b = json.loads(res.decode('utf-8'))
        print(b.get('iss'))
        
    res = test_apple_auth(identityToken)
    print(res)