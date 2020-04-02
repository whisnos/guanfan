import tornado.web
from chefserver.webhandler.basehandler import BaseHandler,check_login
from chefserver.tool import applog,tooltime
from chefserver.sms import aliyun_sts
from chefserver.tool.async_redis_pool import RedisOperate
from tornado.escape import json_decode, json_encode

log = applog.get_log('webhandler.getsts')


class UploadPhotoHandler(BaseHandler):
    @check_login
    async def post(self):
        sts_type = self.get_body_argument('type')
        userid = self.get_session().get('id', 0)
        # sessionname = "uid.{}".format(userid)
        sessionname = userid

        if sts_type == '1':
            # 上传菜谱图片
            success, code, message, result = await get_caipu_sts(userid, sessionname)
            # print(success, code, message, result)
            # return self.send_message(success, code, message, result)
        elif sts_type == '2':
            # 上传动态图片
            success, code, message, result = await get_dongtai_sts(userid, sessionname)
            # return self.send_message(success, code, message, result)
        elif sts_type == '3':
            # 上传个人头像
            success, code, message, result = await get_person_img_sts(userid, sessionname)
            # return self.send_message(success, code, message, result)
        elif sts_type == '4':
            # 上传高级验证需要
            success, code, message, result = await get_person_auth_sts(userid, sessionname)
            # return self.send_message(success, code, message, result)
        elif sts_type == '5':
            # 上传主题封面图片
            success, code, message, result = await get_topic_sts(userid, sessionname)

            # success, code, message, result = await get_person_auth_img_sts(userid, sessionname)
            # return self.send_message(success, code, message, result)
        else:
            return self.send_message(False, 1002, '参数错误')

        if success:
            # 增加用户空间字段
            result.setdefault('spaceid', sessionname)
            return self.send_message(success, code, message, result)
            
        else:
            return self.send_message(success, code, message, result)



async def get_caipu_sts(user_id, sessionname):
    ''' 获取菜谱上传STS权限 '''
    rdkey = 'sts.caipu.{}'.format(user_id)
    outtime = 900
    sts_get = await RedisOperate().instance().get_data(rdkey)
    if sts_get is None:
        # 没有现有的STS，需要重新从阿里云获取
        success, result = await aliyun_sts.upload_caipu_sts_token(sessionname, str(outtime))
        if success:
            # 获取到STS，保存到redis,更新过期时间
            log.info("菜谱上传,userid:{}, sts:{}".format(user_id, result))
            rdsave = await RedisOperate().instance().set_and_expire(rdkey, json_encode(result), outtime-20)
            if rdsave is False:
                log.warning('redis sts 数据更新失败')
            return True, 0, 'success', result.get('Credentials')
        else:
            log.warning('获取菜谱STS异常:{}'.format(result))
            return False, 2001, result, None

    sts_obj = json_decode(sts_get)
    return True,0,'success', sts_obj.get('Credentials')

async def get_dongtai_sts(user_id, sessionname):
    ''' 获取发送动态图片上传STS权限 '''
    rdkey = 'sts.dongtai.{}'.format(user_id)
    outtime = 900
    sts_get = await RedisOperate().instance().get_data(rdkey)
    if sts_get is None:
        # 没有现有的STS，需要重新从阿里云获取
        success, result = await aliyun_sts.upload_dongtai_sts_token(sessionname, str(outtime))
        if success:
            # 获取到STS，保存到redis,更新过期时间
            log.info("动态,userid:{}, sts:{}".format(user_id, result))
            rdsave = await RedisOperate().instance().set_and_expire(rdkey, json_encode(result), outtime-20)
            if rdsave is False:
                log.warning('redis sts 数据更新失败')
            return True, 0, 'success', result.get('Credentials')
        else:
            log.warning('获取动态STS异常:{}'.format(result))
            return False, 2001, result, None

    sts_obj = json_decode(sts_get)
    return True,0,'success', sts_obj.get('Credentials')

async def get_person_img_sts(user_id, sessionname):
    ''' 获取用户图片上传STS权限 '''
    rdkey = 'sts.personimg.{}'.format(user_id)
    outtime = 900
    sts_get = await RedisOperate().instance().get_data(rdkey)
    if sts_get is None:
        # 没有现有的STS，需要重新从阿里云获取
        success, result = await aliyun_sts.upload_person_img_sts_token(sessionname, str(outtime))
        if success:
            # 获取到STS，保存到redis,更新过期时间
            log.info("个人图像上传,userid:{}, sts:{}".format(user_id, result))
            rdsave = await RedisOperate().instance().set_and_expire(rdkey, json_encode(result), outtime-20)
            if rdsave is False:
                log.warning('redis sts 数据更新失败')
            return True, 0, 'success', result.get('Credentials')
        else:
            log.warning('获取用户头像STS异常:{}'.format(result))
            return False, 2001, result, None

    sts_obj = json_decode(sts_get)
    return True,0,'success', sts_obj.get('Credentials')

async def get_person_auth_sts(user_id, sessionname):
    ''' 获取用户高级认证STS权限 '''
    rdkey = 'sts.personauth.{}'.format(user_id)
    outtime = 900
    sts_get = await RedisOperate().instance().get_data(rdkey)
    if sts_get is None:
        # 没有现有的STS，需要重新从阿里云获取
        success, result = await aliyun_sts.upload_person_auth_img_sts_token(sessionname, str(outtime))
        if success:
            # 获取到STS，保存到redis,更新过期时间
            log.info("高级认证上传,userid:{}, sts:{}".format(user_id, result))
            rdsave = await RedisOperate().instance().set_and_expire(rdkey, json_encode(result), outtime-20)
            if rdsave is False:
                log.warning('redis sts 数据更新失败')
            return True, 0, 'success', result.get('Credentials')
        else:
            log.warning('获取高级认证上传STS异常:{}'.format(result))
            return False, 2001, result, None

    sts_obj = json_decode(sts_get)
    return True,0,'success', sts_obj.get('Credentials')


async def get_topic_sts(user_id, sessionname):
    ''' 获取用户高级认证STS权限 '''
    rdkey = 'sts.topic.{}'.format(user_id)
    outtime = 900
    sts_get = await RedisOperate().instance().get_data(rdkey)
    if sts_get is None:
        # 没有现有的STS，需要重新从阿里云获取
        success, result = await aliyun_sts.upload_topic_img_sts_token(sessionname, str(outtime))
        if success:
            # 获取到STS，保存到redis,更新过期时间
            log.info("主题图片上传,userid:{}, sts:{}".format(user_id, result))
            rdsave = await RedisOperate().instance().set_and_expire(rdkey, json_encode(result), outtime-20)
            if rdsave is False:
                log.warning('redis sts 数据更新失败')
            return True, 0, 'success', result.get('Credentials')
        else:
            log.warning('主题图片上传STS异常:{}'.format(result))
            return False, 2001, result, None

    sts_obj = json_decode(sts_get)
    return True,0,'success', sts_obj.get('Credentials')


async def get_person_auth_img_sts(user_id, sessionname):
    ''' 获取用户高级认证资料下载STS权限 '''
    rdkey = 'sts.personauth.getimg.{}'.format(user_id)
    outtime = 900
    sts_get = await RedisOperate().instance().get_data(rdkey)
    if sts_get is None:
        # 没有现有的STS，需要重新从阿里云获取
        success, result = await aliyun_sts.get_person_auth_img_sts_token(sessionname, str(outtime))
        if success:
            # 获取到STS，保存到redis,更新过期时间
            log.info("高级认证下载,userid:{}, sts:{}".format(user_id, result))
            rdsave = await RedisOperate().instance().set_and_expire(rdkey, json_encode(result), outtime-20)
            if rdsave is False:
                log.warning('redis sts 数据更新失败')
            return True, 0, 'success', result.get('Credentials')
        else:
            log.warning('获取高级认证资料下载  STS异常:{}'.format(result))
            return False, 2001, result, None

    sts_obj = json_decode(sts_get)
    return True,0,'success', sts_obj.get('Credentials')