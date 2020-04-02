"""
# 阿里云视频点播相关接口使用
# 获取上传凭证接口
"""

import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.tool.asynchttp import async_http_response
from chefserver.sms.buildaliyunmediaurl import AliyunMediaAdapter
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.tooltime import curDatetime
from chefserver.config import VOD_APP_ID, VOD_WORKFLOW_ID, VOD_EVENT_CALLBACK_URL
from chefserver.config import VOD_CALLBACK_AUTH_KEY, VOD_VIDEO_CATEID
from chefserver.tool.async_redis_pool import RedisOperate
from tornado.escape import json_decode, json_encode
from chefserver.tool.function import MD5encrypt
import urllib.parse
import time



log = applog.get_log('webhandler.video')

cblog = applog.get_log('webhandler.vodcallback')

dbins = DbOperate.instance()
redisins = RedisOperate().instance()

video_temple_str = 'cache.video.{}.{}'

async def handle_video_upload_finish(postbody):
    '''
        视频上传结束后,处理函数
    '''
    vid = postbody.get('VideoId')

    up_video_result = await update_video_history(vid, 2, 
        fileurl=postbody.get("FileUrl",''),
        filesize=postbody.get("Size",''))
    if up_video_result is None:
        return 501, "视频id视频地址更新失败"

    videoinfo = await get_video_history(vid)
    if None is videoinfo:
         return 403, 'videoid不存在,{}'.format(vid)

    itemid = videoinfo.get('itemid')
    if itemid == 0:
        # 动态未创建不需要更新
        return 200, 'ok'

    up_moment_result = await update_moment_videoinfo(itemid, postbody.get("FileUrl",''))
    if up_moment_result is None:
        return 403, '更新到动态错误,{}'.format(vid)
    else:
        return 200, 'ok'


async def handle_video_screenshot_finish(postbody):
    '''
        视频截图完成后,处理函数
    '''
    vid = postbody.get('VideoId')
    snap_status = postbody.get('Status')
    if snap_status == "fail":
        # 截图返回状态
        return 501, postbody.get('ErrorCode')

    cover_url = postbody.get('CoverUrl','')
    cover_url = cover_url.split('?').pop(0) # 去掉图片地址后面的授权访问信息
    up_video_result = await update_video_history(vid, 3, 
        coverurl = cover_url)

    if up_video_result is None:
        return 501, "视频id截图更新失败"

    videoinfo = await get_video_history(vid)
    if None is videoinfo:
         return 403, 'videoid不存在,{}'.format(vid)

    itemid = videoinfo.get('itemid')
    if itemid == 0:
        # 动态未创建不需要更新
        return 200, 'ok'

    up_moment_result = await update_moment_videoinfo(itemid, None, cover_url)
    if up_moment_result is None:
        return 403, '更新到动态错误,{}'.format(vid)
    else:
        return 200, 'ok'


# 回调事件处理函数
event_handle_dict = {
    "FileUploadComplete": handle_video_upload_finish,
    "SnapshotComplete": handle_video_screenshot_finish
}

class VideoUploadAuthKeyHandler(BaseHandler):
    ''' 获取视频文件上传凭证和视频地址 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        # title = self.verify_arg_legal(self.get_body_argument('title'), '标题', True, is_len=True, olen=128)
        filename = self.verify_arg_legal(self.get_body_argument('filename'), '文件名', False, is_len=True, olen=255)
        filesize = self.verify_arg_legal(self.get_body_argument('filesize'), '文件大小', is_num=True)
        if int(filesize) > 31457280:
            self.send_message("False", 1012, "视频文件需要小于30M")
        success, code, message, result = await get_video_upload_key(myid, filename, filesize)
        return self.send_message(success, code, message, result)

class VideoProcessCallBackHandler(BaseHandler):
    ''' 视频回调服务 '''
    async def post(self):
        global event_handle_dict
        tstamp = self.request.headers.get("X-VOD-TIMESTAMP", False)
        signature = self.request.headers.get("X-VOD-SIGNATURE", False)
        if tstamp is False or signature is False:
            # 参数错误
            cblog.warning("参数错误:{},{}".format(signature, tstamp))
            self.set_status(400)
            self.write("参数错误")
            return

        alistamp = int(tstamp)
        curstamp = int(time.time())

        if curstamp - alistamp > 240:
            # 时间戳超时访问失败
            self.set_status(401)
            self.write("鉴权失败,out time!")
            return

        auth_is_ok = video_callback_auth_signature(signature, tstamp)
        if auth_is_ok is False:
            # 鉴权失败
            cblog.warning("鉴权失败:{},{}".format(signature, tstamp))
            self.set_status(401)
            self.write("鉴权失败")
            return

        try:
            res_str = self.request.body.decode('utf-8')
            bodyjson = json_decode(res_str)
            cblog.info(res_str)
        except Exception as e:
            cblog.warning("阿里云回调内容转码失败:{}".format(self.request.body))
            self.set_status(402)
            self.write("错误的返回值")
            return

        #   cblog.info("aliyun 回调内容:{}".format(urllib.parse.unquote(self.request.body.decode('utf-8'), errors='replace')))
        video_event = bodyjson.get('EventType', False)
        if video_event is False:
            cblog.warning("错误的返回值:{}".format(bodyjson))

            self.set_status(402)
            self.write("错误的返回值")
            return

        handler_function = event_handle_dict.get(video_event, False)

        if handler_function is False:
            cblog.warning("错误的事件:{}".format(bodyjson))

            self.set_status(402)
            self.write("错误的事件:{}".format(video_event))
            return

        code, message= await handler_function(bodyjson)
        if code!=200:
            cblog.warning("\nresponse:{}\n{}\n{}".format(bodyjson, code, message))
            self.set_status(200)
            self.write("处理异常:{}".format(code))
            return

        self.set_status(code)
        self.write("处理结果:{}".format(message))


def video_callback_auth_signature(signature, timestamp):
    ''' 验证回调的签名
        signature,签名 | timestamp, UNIX时间戳 整数
    '''
    sign_text = "{}|{}|{}".format(VOD_EVENT_CALLBACK_URL, timestamp, VOD_CALLBACK_AUTH_KEY)
    gen_server_signature = MD5encrypt(sign_text)
    # print(gen_server_signature)
    if gen_server_signature == signature:
        return True
    else:
        return False

async def get_video_upload_key(myid, filename, filesize):
    ''' 获取视频上传的凭证和地址
        # myid, 用户ID, title, 文件标题, 文件名称,
    '''
    # cache_result = await check_video_cache_already(myid, filename)
    # if cache_result:
    #     # 当前文件名存在缓存凭证，则返回缓存凭证
    #     return True, 0, "ok", cache_result

    media = AliyunMediaAdapter()
    param = []
    param.append(("Title", 'userid:' + str(myid) + ':' + filename[:110]))
    param.append(("FileName", filename))
    param.append(("Tags", str(myid)))
    param.append(("AppId", VOD_APP_ID))
    param.append(("CateId", VOD_VIDEO_CATEID))
    param.append(("WorkflowId", VOD_WORKFLOW_ID))
    extend = {"MessageCallback":{"CallbackURL": VOD_EVENT_CALLBACK_URL}, "Extend":{"userid":myid, "appid": VOD_APP_ID}}
    param.append(("UserData", json_encode(extend)))
    signtureURL = media.get_signature_url("CreateUploadVideo", param)
    # print(signtureURL)
    success, result = await async_http_response(signtureURL, datatype='json')
    if success:
        # 获取凭证成功
        create_success, msg = await create_video_id(myid, result.get('VideoId') ,filename, filesize)
        if create_success:
            # 凭证创建成功,创建凭证缓存
            # rdkey = video_temple_str.format(myid, filename)
            # rdsave = await redisins.set_and_expire(rdkey, json_encode(result), 3400)
            # if rdsave is False:
            #     log.warning('redis cahce 数据更新失败')
            return True, 0, "ok", result
        else:
            return False, 3001, '保存视频ID失败', None
    else:
        # 获取凭证失败
        log.error("获取上传凭证失败:{}".format(result))
        return False, 2010, "请求失败", result

async def create_video_id(myid, videoid, filename, filesize):
    ''' 新建阿里云视频ID,以及相关信息 '''
    insert_video_sql = "INSERT INTO video_info (`userid`, `videoid`, `filename`, `filesize`, `updatetime`, `createtime`)" \
                                 "VALUES(?,          ?,        ?,         ?,     ?,            ?)"
    curtime = curDatetime()
    video_result = await dbins.execute(insert_video_sql, (myid, videoid, filename, filesize, curtime,curtime ))

    if video_result is None:
        log.warning("视频记录失败,userid:{}, videoid:{}".format(myid, videoid))
        return False, "视频记录失败"
    else:
        return True, "ok"

async def check_video_cache_already(userid, filename):
    ''' 检查当前用户是否存在视频上传凭证 '''
    rdkey = video_temple_str.format(userid, filename)
    video_certificate = await redisins.get_data(rdkey)
    if video_certificate is None:
        return False
    else:
        return json_decode(video_certificate)


async def update_moment_videoinfo(momentid, fileurl, converimg=None):
    ''' 用于更新动态封面和视频地址 '''
    sql_base = "update moments_info set {} where id=?"
    if None == converimg:
        # 更新视频文件地址
        sql_patch = "momentsVideoUrl=?"
        return await dbins.execute(sql_base.format(sql_patch), (fileurl, momentid))
    else:
        # 更新视频截图地址
        sql_patch = "momentsImgUrl=?"
        return await dbins.execute(sql_base.format(sql_patch), (converimg, momentid))

async def update_video_history(videoid, status, **kw):
    ''' 更新视频历史记录 
        status = 1 # 动态创建 2 上传完成, 3 截图完成, 4 删除
    '''
    sql_base = "update video_info set {} where videoid=?"
    if 1 == status:
        # 更新ID
        sql_patch = "itemid = ?, status = 1, mark = concat(mark,'动态创建|')"
        return await dbins.execute(sql_base.format(sql_patch), (kw.get('itemid'), videoid))
    elif 2 == status:
        # 事件通知,上传完成
        sql_patch = "fileurl = ?, status = 2, realsize = ?, mark = concat(mark,'上传完成|')"
        return await dbins.execute(sql_base.format(sql_patch), (kw.get('fileurl'), kw.get('filesize'), videoid))
    elif 3 == status:
        # 事件通知,截图完成
        sql_patch = "coverurl = ?, status = 3, mark = concat(mark,'截图完成|')"
        return await dbins.execute(sql_base.format(sql_patch), (kw.get('coverurl'), videoid))

    elif 4 == status:
        sql_patch = " status = 4, mark = concat(mark,'删除|')"
        return await dbins.execute(sql_base.format(sql_patch), (videoid,))
    else:
        sql_patch = " status = ?, mark = concat(mark, ?)"
        return await dbins.execute(sql_base.format(sql_patch), (status, kw.get('mark'), videoid))

async def get_video_history(videoid, userid=None):
    ''' 获取视频记录 '''
    sql = '''
    SELECT * from video_info where videoid = ? {} LIMIT 1
    '''.format('' if userid is None else 'and userid=' + str(userid))
    return await dbins.selectone(sql, (videoid,))


if __name__ == '__main__':
    import asyncio
    async def test_get_video_upload_key():
        res = await get_video_upload_key('1',
            'test2020011001.avi',
            "20010"
            )
        print(res)

    async def test_create_video_id():
        res = await create_video_id('1',
            '13123',
            'test111sdfsdf.avi',
            "20010"
            )
        print(res)

    async def test_get_video_history():
        res = await get_video_history('zx')
        print(res)

    async def test_update_video_history():
        res = await update_video_history('897c697d85c24b3eb08b08bf9e',1, itemid=50)
        res = await update_video_history('897c697d85c24b3eb08b08bf9e',2, fileurl='fileurl', filesize='10025')
        res = await update_video_history('897c697d85c24b3eb08b08bf9e',3, coverurl='coverurl')
        res = await update_video_history('897c697d85c24b3eb08b08bf9e',4)
        res = await update_video_history('897c697d85c24b3eb08b08bf9e',5, mark="截图失败|")
        print(res)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_video_upload_key())

    import time
    start = int(time.time())
    print(start)
    sign_text = "{}|{}|{}".format(VOD_EVENT_CALLBACK_URL, start, VOD_CALLBACK_AUTH_KEY)
    gen_server_signature = MD5encrypt(sign_text)
    print(gen_server_signature)
    # print(time.time() - start)