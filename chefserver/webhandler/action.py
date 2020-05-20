from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.tool.tooltime import curDatetime
from chefserver.config import TOKEN_TIME
from chefserver.tool.async_redis_pool import RedisOperate
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo
from chefserver.webhandler.publish import delete_dongtai, delete_recipe, update_all_point
from chefserver.webhandler.common_action import is_my_id
import time

log = applog.get_log('webhandler.action')
dbins = DbOperate.instance()



class TimeStampHandler(BaseHandler):
    ''' 返回时间戳 '''
    def post(self):
        self.send_message(True, 0, '', int(time.time()))

class HeartBeatHandler(BaseHandler):
    ''' 心跳, 保持token的生命时间 '''
    async def post(self):
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            return self.send_message(False, 0, '没有心跳')
        token = self.request.headers.get('token')
        key = "token:{}".format(token)
        # token_exists = await RedisOperate().instance().exists(key)
        rdget = await RedisOperate().instance().get_data(key)
        if rdget is not None:
            # 会话存在,给token续命
            rdsup = await RedisOperate().instance().exprie(key, TOKEN_TIME)
            if rdsup != 1:
                return self.send_message(False, 3101, '更新心跳出错,请重试')
                
            else:
                return self.send_message(True, 0, 'Heartbeat!')
                
        else:
            return self.send_message(False, 0, '没有心跳')


class ReplyHandler(BaseHandler):
    ''' 添加评论 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '评论项目类型', False, uchecklist=True, user_check_list=['1','2','3'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '被评论项目', False, is_num=True)
        commentid = self.verify_arg_legal(self.get_body_argument('commentid'), '上一级评论ID', False, is_num=True)
        beuserid = self.verify_arg_legal(self.get_body_argument('beuserid'), '被评论人ID', False, is_num=True)
        replyid = self.verify_arg_legal(self.get_body_argument('replyid'), '被回复ID', False, is_num=True)
        replyuserid = self.verify_arg_legal(self.get_body_argument('replyuserid'), '被回复userID', False, is_num=True)
        message = self.verify_arg_legal(self.get_body_argument('message'), '评论内容', True, islen=True, olen=200)
        success, code, message, result = await add_reply(userid, itemid, int(itemtype), message, int(commentid), int(beuserid), int(replyid), int(replyuserid))
        if success:
            # 处理积分
            await update_all_point(self, userid, point_type=2, bill_type=3, des='评论')
        return self.send_message(success, code, message, result)


class DelReplyHandler(BaseHandler):
    ''' 删除评论 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        replyid = self.verify_arg_legal(self.get_body_argument('replyid'), '评论id', False, is_num=True)
        success, code, message, result = await del_reply(userid, replyid)
        return self.send_message(success, code, message, result)


class CollectionHandler(BaseHandler):
    ''' 收藏 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '收藏项目类型', False, uchecklist=True, user_check_list=['1','2','3'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '收藏的项目ID', False, is_num=True)
        success, code, message, result = await add_collection(int(userid), int(itemid), int(itemtype))
        return self.send_message(success, code, message, result)
        

class UnCollectionHandler(BaseHandler):
    ''' 取消收藏 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '取消收藏项目类型', False, uchecklist=True, user_check_list=['1','2','3'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '取消收藏的项目ID', False, is_num=True)
        success, code, message, result = await cancel_collection(int(userid), int(itemid), int(itemtype))
        return self.send_message(success, code, message, result)


class LikeHandler(BaseHandler):
    ''' 点赞 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '点赞项目类型', False, uchecklist=True, user_check_list=['1'])
        # 点赞项目,暂时只有动态
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '点赞的项目ID', False, is_num=True)
        success, code, message, result = await add_like(int(userid), int(itemid), int(itemtype))
        return self.send_message(success, code, message, result)


class UnLikeHandler(BaseHandler):
    ''' 取消点赞 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '取消点赞项目类型', False, uchecklist=True, user_check_list=['1'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '取消点赞的项目ID', False, is_num=True)
        success, code, message, result = await cancel_like(int(userid), int(itemid), int(itemtype))
        return self.send_message(success, code, message, result)


class MessageReadHandler(BaseHandler):
    ''' 消息设置已读 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        msgid = self.verify_arg_legal(self.get_body_argument('messageid'), '消息ID', False, is_num=True)
        success, code, message, result = await message_read(userid, msgid)
        return self.send_message(success, code, message, result)


class MessageNumHandler(BaseHandler):
    ''' 未读消息数量 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        success, code, message, result = await message_num(userid)
        return self.send_message(success, code, message, result)


class DelRecipeHandler(BaseHandler):
    ''' 删除菜谱 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        cpid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        success, code, message, result = await del_recipe_api(userid, cpid)
        return self.send_message(success, code, message, result)


class DelDongtaiHandler(BaseHandler):
    ''' 删除动态 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        dtid = self.verify_arg_legal(self.get_body_argument('dtid'), '动态ID', False, is_num=True)
        success, code, message, result = await del_dongtai_api(userid, dtid)
        return self.send_message(success, code, message, result)


class JubaoHandler(BaseHandler):
    ''' 举报 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '举报项目类型', False, uchecklist=True, user_check_list=['1','2','3','4'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '举报项目ID', False, is_num=True)
        reporttype = self.verify_arg_legal(self.get_body_argument('reporttype'), '举报类型', False, islen=True, olen=40)
        dscription = self.verify_arg_legal(self.get_body_argument('dscription'), '举报描述', False, islen=True, olen=500)
        success, code, message, result = await add_jubao(userid, itemtype, itemid, reporttype, dscription)
        return self.send_message(success, code, message, result)
        

async def add_jubao(userid, itemtype, itemid, reporttype, dscription):
    ''' 添加举报信息 '''
    jubao_insert_sql = '''
    INSERT INTO report_info(
    userid, `type`, itemid, reportreason, reportdescription)
    VALUES
    (?,      ?,       ?,       ?,               ?)
    '''
    jubao_ins_res = await dbins.execute(jubao_insert_sql, (userid, itemtype, itemid, reporttype, dscription))
    if jubao_ins_res is None:
        return False, 3019, '举报添加失败,请重试', None
    else:
        return True, 0, '举报成功', None

async def del_recipe_api(myid, cpid):
    ''' 删除菜谱 '''
    cp_exists_sql ='''
    select id from recipe_info where id=? and userid=? and `status`!=-1 limit 1
    '''
    cp_exists_res = await dbins.selectone(cp_exists_sql, (cpid, myid))
    if cp_exists_res is None:
        return False, 1022, '菜谱数据异常,请核对后重试', None
    result =  await delete_recipe(myid, cpid)
    if result:
        return True, 0, '删除成功', None
    else:
        return False, 1002, '删除异常,请重试', None


async def del_recipe_api(myid, cpid):
    ''' 删除菜谱 '''
    cp_exists_sql ='''
    select id from recipe_info where id=? and userid=? and `status`!=-1 limit 1
    '''
    cp_exists_res = await dbins.selectone(cp_exists_sql, (cpid, myid))
    if cp_exists_res is None:
        return False, 1022, '菜谱数据异常,请核对后重试', None
    result =  await delete_recipe(myid, cpid)
    if result:
        return True, 0, '删除成功', None
    else:
        return False, 1002, '删除异常,请重试', None
     

async def del_dongtai_api(myid, dtid):
    ''' 删除动态 '''
    dt_exists_sql ='''
    select id from moments_info where id=? and userid=? and `status`!=-1 limit 1
    '''
    dt_exists_res = await dbins.selectone(dt_exists_sql, (dtid, myid))
    if dt_exists_res is None:
        return False, 1022, '动态数据异常,请核对后重试', None
    result = await delete_dongtai(myid, dtid)
    if result:
        return True, 0, '删除成功', None
    else:
        return False, 1002, '删除异常,请重试', None


async def message_read(myid, msgid):
    ''' 将消息设置为已读 '''
    msg_exists_sql ='''
select id from reply_info
where
id = ?
and haveRead=0
and status=0
and userid!=?
and ((beUserId=? ) or (itemUserID=? and beuserid=0)) limit 1;
'''
    msg_exists_res = await dbins.selectone(msg_exists_sql, (msgid, myid, myid, myid))
    if msg_exists_res is None:
        return False, 1022, '消息数据异常,请核对后重试', None

    up_msg_sql = 'update reply_info set haveRead = 1, updatetime=? where id=?' 
    up_msg_res = await dbins.execute(up_msg_sql, (curDatetime(),msgid))
    if up_msg_res is None:
        return False, 3019, '消息已读失败,请重试', None
    else:
        return True, 0, '消息已读', None


async def message_num(myid):
    ''' 未读消息数量 '''
#     msg_num_sql ='''
# select count(id) as cnum from reply_info
# where
# haveRead=0
# and status=0
# and userid!=?
# and ((beUserId=? ) or (itemUserID=? and beuserid=0));
# '''
    # 20191118 增加黑名单过滤消息数量
    msg_num_sql = '''
select count(*) as cnum
from(
select id,userid from reply_info
where
haveRead=0
and userid!=?
and status=0
and ((beUserId=?) or (itemUserID=? and beuserid=0))
) as reply
left join 
(select BlockUserId from block_info where userid=?) as bli
on bli.BlockUserId=reply.userid
where bli.BlockUserId is null
    '''
    msg_exists_res = await dbins.selectone(msg_num_sql, (myid , myid, myid, myid))
    if msg_exists_res is None:
        return False, 1023, '获取消息数量异常,请核对后重试', None
    else:
        return True, 0, 'success', msg_exists_res.get('cnum', 0)


async def cancel_like(userid, itemid, itemtype):
    ''' 取消点赞 '''
    # 判断是否已点赞
    exists_sql = 'select id,`status` from like_info where userid=? and `likeType`=? and itemid=? limit 1'
    exists_res = await dbins.selectone(exists_sql, (userid, itemtype, itemid))
    if exists_res is None:
        return False, 3018, '取消点赞失败,请重试', None

    if exists_res.get('status') == -1:
        # 已存在
        return True, 0, '已取消点赞', None

    if exists_res.get('status') == 0:
        # 已存在
        # 动态likeCount 点赞数字+1
        if itemtype == 1:
            likes_num_result = await likes_num_update(itemid, -1, itemtype)
            if likes_num_result is False:
                return False, 3010, '点赞失败,请重试', None
        coid = exists_res.get('id')
        up_collection_sql = 'update like_info set `status` = -1, createtime=? where id=?' 
        cancel_like_res = await dbins.execute(up_collection_sql, (curDatetime(),coid))
        if cancel_like_res is None:
            likes_num_result = await likes_num_update(itemid, +1, itemtype)
            return False, 3011, '取消点赞失败,请重试', None
        else:
            return True, 0, '取消点赞成功', None
    else:
        return False, 1021, '错误的点赞数据', None


async def add_like(userid, itemid, itemtype):
    ''' 添加点赞 itemid 收藏ID, itemtype的类型: 1 动态,2 食谱,3 主题'''
    res_exists = await item_exists(itemid, itemtype)
    if res_exists is False:
        return False, 3006, '点赞的数据不存在或不合法,请核对后重试', None

    # 判断是否已点赞
    exists_sql = 'select id,`status` from like_info where userid=? and `likeType`=? and itemid=? limit 1'
    exists_res = await dbins.selectone(exists_sql, (userid, itemtype, itemid))

    if exists_res:
        if exists_res.get('status') == 0:
            # 已存在
            return True, 0, '已点赞', None

        if exists_res.get('status') == -1:
            # 已存在
            # 动态likeCount 点赞数字+1
            if itemtype == 1:
                likes_num_result = await likes_num_update(itemid, 1, itemtype)
                if likes_num_result is False:
                    return False, 3010, '点赞失败,请重试', None

            coid = exists_res.get('id')
            up_collection_sql = 'update like_info set `status` = 0, createtime=? where id=?' 
            add_like_res = await dbins.execute(up_collection_sql, (curDatetime(), coid))
            if add_like_res is None:
                likes_num_result = await likes_num_update(itemid, -1, itemtype)
                return False, 3009, '点赞失败,请重试', None
            else:
                return True, 0, '点赞成功', None

    # 添加点赞
    if itemtype == 1:
        likes_num_result = await likes_num_update(itemid, 1, itemtype)
        if likes_num_result is False:
            return False, 3010, '点赞失败,请重试', None

    add_collection_sql = '''
    insert into like_info(userid, `likeType`, itemid, `status`)
                        values(?,       ?,          ?,      ?)
    '''
    add_like_res = await dbins.execute(add_collection_sql, (userid, itemtype, itemid, 0))
    if add_like_res is None:
        return False, 3008, '点赞失败,请重试', None

    return True, 0, '点赞成功', None


async def likes_num_update(itemid, num, itemtype=1):
    '''目前只有动态有点赞, 增加点赞数量,num = 1 或 num = -1, itemtype = 1 '''
    likes_num_sql = '''
    update moments_info set likeCount = likeCount + ? where id = ? and `status` = 0
    '''
    likes_num_res = await dbins.execute(likes_num_sql, (num, itemid))
    if likes_num_res is None:
        return False
    return True


async def cancel_collection(userid, itemid, itemtype):
    ''' 取消收藏 '''
    # 判断是否已收藏
    exists_sql = 'select id,status from collection_info where userid=? and `type`=? and itemid=? limit 1'
    exists_res = await dbins.selectone(exists_sql, (userid, itemtype, itemid))
    if exists_res:
        # 取消收藏已存在
        if exists_res.get('status') == -1:
            # 有记录,但本身就是取消收藏的
            return True, 0, '已取消收藏', None

        coid = exists_res.get('id')
        up_collection_sql = 'update collection_info set `status` = -1, createtime=? where id=?' 
        cancel_collection_res = await dbins.execute(up_collection_sql, (curDatetime(), coid))
        if cancel_collection_res is None:
            return False, 3010, '取消收藏失败,请重试', None
        else:
            if itemtype == 2:
                # 食谱 收藏-1
                up_recipe_sql = 'update recipe_info set collectionCount = collectionCount - 1 where id=? and isenable=1 and `status` in (1,0)'
                up_res = await dbins.execute(up_recipe_sql, (itemid))

            if itemtype == 3:
                # 主题 收藏-1
                up_topic_sql = 'update topic_info set collectionCount = collectionCount - 1 where id=? and isenable=1 and `status` != -1'
                up_res = await dbins.execute(up_topic_sql, (itemid)) 
            return True, 0, '取消收藏成功', None
    else:
        return False, 1021, '错误的收藏数据', None


async def add_collection(userid, itemid, itemtype):
    ''' 添加收藏 itemid 收藏ID, itemtype的类型: 1 动态,2 食谱,3 主题'''
    res_exists = await item_exists(itemid, itemtype)
    if res_exists is False:
        return False, 3006, '收藏的数据不存在或不合法,请核对后重试', None

    # 判断是否已收藏
    exists_sql = 'select id,status from collection_info where userid=? and `type`=? and itemid=? limit 1'
    exists_res = await dbins.selectone(exists_sql, (userid, itemtype, itemid))
    if exists_res:
        # 已存在
        if exists_res.get('status') == 0:
            # 有记录,但本身就是收藏专题的
            return True, 0, '已收藏', None
        coid = exists_res.get('id')
        up_collection_sql = 'update collection_info set `status` = 0, createtime=? where id=?' 
        add_collection_res = await dbins.execute(up_collection_sql, (curDatetime(), coid))
        if add_collection_res is None:
            return False, 3009, '收藏失败,请重试', None
        else:
            if itemtype == 2:
                # 食谱 收藏+1
                up_recipe_sql = 'update recipe_info set collectionCount = collectionCount + 1 where id=? and isenable=1 and `status` in (1,0)'
                up_res = await dbins.execute(up_recipe_sql, (itemid))

            if itemtype == 3:
                # 主题 收藏+1
                up_topic_sql = 'update topic_info set collectionCount = collectionCount + 1 where id=? and isenable=1 and `status` != -1'
                up_res = await dbins.execute(up_topic_sql, (itemid)) 

            return True, 0, '收藏成功', None

    # 添加收藏
    add_collection_sql = '''
    insert into collection_info(userid, `type`, itemid, `status`)
                        values(?,       ?,          ?,      ?)
    '''
    add_collection_res = await dbins.execute(add_collection_sql, (userid, itemtype, itemid, 0))
    if add_collection_res is None:
        return False, 3008, '收藏失败,请重试', None


    if itemtype == 2:
        # 食谱 收藏+1
        up_recipe_sql = 'update recipe_info set collectionCount = collectionCount + 1 where id=? and isenable=1 and `status` in (1,0)'
        up_res = await dbins.execute(up_recipe_sql, (itemid))

    if itemtype == 3:
        # 主题 收藏+1
        up_topic_sql = 'update topic_info set collectionCount = collectionCount + 1 where id=? and isenable=1 and `status` != -1'
        up_res = await dbins.execute(up_topic_sql, (itemid)) 

    return True, 0, '收藏成功', None


async def add_reply(userid, itemid, itemtype, message, commentid=0, beuserid=0, replyid=0, replyuserid=0):
    ''' 添加评论 itemid, itemtype的类型: 1 动态,2 食谱,3 主题'''
    item_userid = 0
    if itemtype==1:
        # 是否存在的动态
        sql = 'SELECT id,userid FROM moments_info WHERE id=? AND status=0 LIMIT 1'
        exists_res = await dbins.selectone(sql, (itemid))
        if exists_res is None:
            return False, 3001, '错误的动态数据,请核对后重试', None
        else:
            item_userid = exists_res.get('userid')

    if itemtype==2:
        # 是否存在的食谱
        sql = 'SELECT id,userid FROM recipe_info WHERE id=? AND status!=-1 AND status!=2 AND isEnable=1 limit 1'
        exists_res = await dbins.selectone(sql, (itemid))
        if exists_res is None:
            return False, 3002, '错误的食谱数据,请核对后重试', None
        else:
            item_userid = exists_res.get('userid')
    if itemtype==3:
        # 是否存在的主题
        sql = 'SELECT id,userid FROM topic_info WHERE id=? AND status!=-1 AND isEnable=1 limit 1'
        exists_res = await dbins.selectone(sql, (itemid))
        if exists_res is None:
            return False, 3003, '错误的主题数据,请核对后重试', None
        else:
            item_userid = exists_res.get('userid')

    if commentid == 0:
        # 如果被评论的ID为0
        beuserid = 0
    else:
        # commentid beuserid
        if replyid == 0:
            # 不是回复,添加子评论
            check_id_exists_sql = '''
            SELECT id FROM reply_info WHERE id=? AND userid=? AND itemid=? AND itemtype=? AND commentid=0
            '''
            exists_res = await dbins.selectone(check_id_exists_sql, (commentid, beuserid, itemid, itemtype))
            if exists_res is None:
                return False, 3004, '被评论数据不存在或不合法,请核对后重试', None
        else:
            # 回复他人
            check_id_exists_sql = '''
            SELECT id FROM reply_info WHERE id=? AND userid=? AND itemid=? AND itemtype=? AND commentid=?
            '''
            exists_res = await dbins.selectone(check_id_exists_sql, (replyid, replyuserid, itemid, itemtype, commentid))
            if exists_res is None:
                return False, 3004, '被回复数据不存在或不合法,请核对后重试', None
            beuserid = replyuserid

    # 插入评论
    add_re_sql = '''
    INSERT INTO reply_info(itemid, itemtype, itemUserId, commentid, userid, beuserid, message, haveread, status)
                    VALUES(?,       ?,        ?,          ?,            ?,      ?,      ?,          ?,      ?)
    '''
    add_re_res = await dbins.execute(add_re_sql, (itemid, itemtype, item_userid, commentid, userid, beuserid, message, 0, 0))
    if add_re_res is None:
        return False, 3004, '添加评论失败,请重试', None
    else:
        return True, 0, '添加评论成功', None


async def del_reply(myid, replyid):
    ''' 删除自己发布的评论 '''
    my_id_exists = await is_my_id(myid, replyid, 4)
    if my_id_exists is False:
        return False, 1088, "错误的评论数据,请核对后重试", None

    up_del_reply_sql = 'UPDATE reply_info set `status` = -1 where id= ? and userid = ?'
    up_del_res = await dbins.execute(up_del_reply_sql, (replyid , myid))

    if up_del_res is None:
        return False, 3088, "删除评论异常,请重试", None
    return True, 0, "删除评论成功", None


async def item_exists(itemid, itemtype):
    ''' 项目是否存在,是否合法,itemtype的类型: 1 动态,2 食谱,3 主题 '''
    if itemtype==1:
        # 是否存在的动态
        sql = 'SELECT id FROM moments_info WHERE id=? AND status=0 limit 1'
        exists_res = await dbins.selectone(sql, (itemid))
        if exists_res is None:
            return False
    if itemtype==2:
        # 是否存在的食谱
        sql = 'SELECT id FROM recipe_info WHERE id=? AND status!=-1 AND status!=2 AND isenable=1 LIMIT 1'
        exists_res = await dbins.selectone(sql, (itemid))
        # print(exists_res, itemid)
        if exists_res is None:
            return False

    if itemtype==3:
        # 是否存在的主题
        sql = 'SELECT id FROM topic_info WHERE id=? AND status=1 AND isenable=1 LIMIT 1'
        exists_res = await dbins.selectone(sql, (itemid))
        if exists_res is None:
            return False
    return True


class PointShareHandler(BaseHandler):
    ''' 分享操作 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        # 处理积分
        await update_all_point(self, userid, point_type=4, bill_type=5, des='分享')
        return self.send_message(True, 0, '分享成功', {})


if __name__ == '__main__':
    async def test_add_reply():
        # res = await get_subjectlist('1')
        res = await add_reply(20, 13, 1, "hello id 20 come", 9, 8)
        print(res)

    async def test_add_collection():
        # res = await get_subjectlist('1')
        res = await add_collection(1, 3, 3)
        print(res)

        res = await add_collection(2, 90, 3)
        print(res)

    async def test_cancel_collection():
        res = await cancel_collection(1, 3, 3)
        print(res)

    async def test_message_num():
        res = await message_num(11)
        print(res)

    async def test_del_reply():
        res = await del_reply(1, 12)
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_message_num())