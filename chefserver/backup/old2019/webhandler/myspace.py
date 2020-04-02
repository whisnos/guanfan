import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo, cache_up_follow, cache_up_fans, cache_up_caipu, cache_up_dongtai
from chefserver.webhandler.common_action import is_block
from chefserver.tool.tooltime import curDatetime
import time

log = applog.get_log('webhandler.myspace')
db_ins = DbOperate.instance()

class MyspaceIndexHandler(BaseHandler):
    ''' 个人空间首页 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        success, code, message, result = await myspace_index(userid)
        # 更新草稿箱数量
        temp_num = await get_caipu_temp_num(userid)
        result.setdefault('tempnum', temp_num)
        # 更新采购清单数量
        qingdan_num = await get_caipu_qingdan_num(userid)
        result.setdefault('qingdannum', qingdan_num)
        return self.send_message(success, code, message, result)

class FriendSpaceHandler(BaseHandler):
    ''' 好友空间首页 '''
    # @check_login
    async def post(self):
        uid = self.verify_arg_legal(self.get_body_argument('uid'), '用户', False, is_num=True)
        # 判断用户与自己的状态:
        relationship = 0 # 0 未关注 1 已关注 2 互相关注
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            relationship = 0
            myid=0
        else:
            # 获取关注状态
            myid = user_session.get('id',0)
            relationship = await get_relationship_status(myid, uid)
        
        # 是否是黑名单,禁止访问
        if myid != 0:
            isblock = await is_block(uid, myid)
            if isblock:
                # 在访问人在黑名单中,禁止访问
                self.send_message(False, 4003, '禁止访问', None)

        success, code, message, result = await myspace_index(uid)
        if success:
            # result.update(moments=0) # 2019.12.13 PC端个人首页要显示这两个数据
            # result.update(follows=0) # 2019.12.13 PC端个人首页又要显示了
            result.update(relationship=relationship)
            if myid == int(uid):
                result.update(ismyown=1)
            else:
                result.update(ismyown=0)
        return self.send_message(success, code, message, result)

class MyCaipuListIndexHandler(BaseHandler):
    ''' 获取菜谱列表 '''
    async def post(self):
        ''' 获取个人菜谱列表 '''
        suid = self.verify_arg_legal(self.get_body_argument('uid'), '用户', False, is_num=True)
        spage = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        if len(suid)>20 or len(spage)>19:
            return self.send_message(False, 1001, '参数错误')
        try:
            uid  = int(suid)
            page = int(spage)
        except ValueError:
            return self.send_message(False, 1002, '参数错误')
        if uid == 0:
            session = await self.get_login()
            if session is False:
                return self.send_message(False, 9999, '请先登录')
            userid = self.get_session()
            if userid is None:
                return self.send_message(False, 9999, '请先登录')
            uid = self.get_session().get('id', 0)
            success, code, message, result = await myspace_get_caipu_list(uid, page)
            return self.send_message(success, code, message, result)
        else:
            success, code, message, result = await myspace_get_caipu_list(uid, page, status=2)
            return self.send_message(success, code, message, result)


class MyDongtaiHandler(BaseHandler):
    ''' 获取动态列表 '''
    async def post(self):
        ''' 获取个人动态列表 '''
        suid = self.verify_arg_legal(self.get_body_argument('uid'), '用户', False, is_num=True)
        spage = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        if len(suid)>20 or len(spage)>19:
            return self.send_message(False, 1001, '参数错误')
        try:
            uid  = int(suid)
            page = int(spage)
        except ValueError:
            return self.send_message(False, 1002, '参数错误')

        if uid == 0:
            session = await self.get_login()
            if session is False:
                return self.send_message(False, 9999, '请先登录')
            userid = self.get_session()
            if userid is None:
                return self.send_message(False, 9999, '请先登录')
            uid = self.get_session().get('id', 0)
            success, code, message, result = await myspace_get_dongtai_list(uid, page, 10)
            return self.send_message(success, code, message, result)
        else:
            success, code, message, result = await myspace_get_dongtai_list(uid, page)
            return self.send_message(success, code, message, result)


class MyfansListIndexHandler(BaseHandler):
    ''' 粉丝列表 '''
    @check_login
    async def post(self):
        spage = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        if len(spage)>19:
            return self.send_message(False, 1003, '参数错误')
        try:
            page = int(spage)
        except ValueError:
            return self.send_message(False, 1004, '参数错误')
        userid = self.get_session().get('id', 0)
        success, code, message, result = await myspace_fanslist(userid, page)
        return self.send_message(success, code, message, result)


class MyfollowListIndexHandler(BaseHandler):
    ''' 关注列表 '''
    @check_login
    async def post(self):
        spage = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        if len(spage)>19:
            return self.send_message(False, 1003, '参数错误')
        try:
            page = int(spage)
        except ValueError:
            return self.send_message(False, 1004, '参数错误')
        userid = self.get_session().get('id', 0)
        success, code, message, result = await myspace_followlist(userid, page)
        return self.send_message(success, code, message, result)

class MyFriendListIndexHandler(BaseHandler):
    ''' 好友列表 '''
    @check_login
    async def post(self):
        spage = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        if len(spage)>19:
            return self.send_message(False, 1003, '参数错误')
        try:
            page = int(spage)
        except ValueError:
            return self.send_message(False, 1004, '参数错误')
        userid = self.get_session().get('id', 0)
        success, code, message, result = await myspace_friendlist(userid, page)
        # print(success, code, message, result)
        return self.send_message(success, code, message, result)

class FollowHandler(BaseHandler):
    ''' 关注 '''
    @check_login
    async def post(self):
        fid = self.verify_arg_legal(self.get_body_argument('fid'), '关注用户', False, is_num=True)
        if len(fid) > 19:
            return self.send_message(False, 1003, '参数错误')
        try:
            ufid = int(fid)
        except ValueError:
            return self.send_message(False, 1004, '参数错误')
        userid = self.get_session().get('id', 0)

        # 是否是黑名单,禁止访问
        if userid != 0:
            isblock = await is_block(ufid, userid)
            if isblock:
                # 在访问人在黑名单中,禁止关注
                self.send_message(False, 4003, '禁止关注', None)

        success = await myspace_follow(userid, ufid)

        if success:
            return self.send_message(success, 0, '关注成功')
        else:
            return self.send_message(success, 1001, '关注失败,数据异常或操作失败')

class UnFollowHandler(BaseHandler):
    ''' 取消关注 '''
    @check_login
    async def post(self):
        fid = self.get_body_argument('fid')
        if len(fid) > 19:
            return self.send_message(False, 1003, '参数错误')
        try:
            ufid = int(fid)
        except ValueError:
            return self.send_message(False, 1004, '参数错误')
        userid = self.get_session().get('id', 0)
        success = await myspace_unfollow(userid, ufid)
        if success:
            return self.send_message(success, 0, '取消关注成功')
        else:
            return self.send_message(success, 1001, '取消关注失败,数据异常或操作失败')


class CollectionListHandler(BaseHandler):
    ''' 收藏列表 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        itemtype = self.verify_arg_legal(self.get_body_argument('ctype'), '收藏类型', False, uchecklist=True, user_check_list=['1','2','3'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await collection_list(int(userid), int(itemtype), int(page))
        return self.send_message(success, code, message, result)


class MessageListHandler(BaseHandler):
    ''' 消息列表 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await message_list(int(userid), int(page))
        return self.send_message(success, code, message, result)


class MessageDelHandler(BaseHandler):
    ''' 删除消息(更新haveread字段为-1) '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        msgid = self.verify_arg_legal(self.get_body_argument('messageid'), '消息ID', False, is_num=True)
        success, code, message, result = await message_del(int(userid), int(msgid))
        return self.send_message(success, code, message, result)


class CaipuTempListHandler(BaseHandler):
    ''' 菜谱草稿列表 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_caipu_temp_list(int(userid), int(page))
        return self.send_message(success, code, message, result)


class PurchaListHandler(BaseHandler):
    ''' 采购清单列表 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_purcha_list(int(userid), int(page))
        return self.send_message(success, code, message, result)

class AddPurchaHandler(BaseHandler):
    ''' 添加采购清单 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        cpid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        success, code, message, result = await add_purcha(int(userid), int(cpid))
        return self.send_message(success, code, message, result)


class DelPurchaHandler(BaseHandler):
    ''' 删除采购清单 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        recipeid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        success, code, message, result = await del_purcha(int(userid), int(recipeid))
        return self.send_message(success, code, message, result)


class SetPurchaBuyHandler(BaseHandler):
    ''' 设置采购清单购买状态 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id')
        purchaid = self.verify_arg_legal(self.get_body_argument('purchaid'), '采购清单ID', False, is_num=True)
        status = self.verify_arg_legal(self.get_body_argument('status'), '状态', False, is_num=True, uchecklist=True, user_check_list=['0','1'])
        success, code, message, result = await up_purcha_isbuy(int(userid), int(purchaid), int(status))
        return self.send_message(success, code, message, result)

async def add_purcha(myid, recipeid):
    ''' 添加清单列表 '''
    exists_recipe_sql ='''select id,ingredientsList from recipe_info where id=?'''
    exists_recipe_res = await db_ins.selectone(exists_recipe_sql, (recipeid))
    if exists_recipe_res is None:
        # 菜谱是否存在
        return False, 3034, '错误的菜谱,请重试', None

    already_add_recipe_sql ='''select id from purchase_info where recipeid=? and userid=? and status=0 limit 1'''
    already_add_recipe_res = await db_ins.selectone(already_add_recipe_sql, (recipeid, myid))
    if already_add_recipe_res:
        # 菜谱是否已经添加
        return False, 1091, '该菜谱清单已添加', None

    purchastr = exists_recipe_res.get('ingredientsList')

    purchalist = []

    for pur in purchastr.split('|'):
        tmp = pur.split('#')
        if tmp[0] == '':
            continue
        stuff = tmp[0]
        amount = tmp[1] if len(tmp) > 1 else ''
        purchalist.append((myid,recipeid,stuff,amount,0))

    if len(purchalist) == 0:
        return False, 1092, '没有食材需要添加', None

    purcha_insert_sql = '''
    INSERT INTO purchase_info
    (userid, recipeid, stuff, amount, isbuy)
    VALUES
    (?,      ?,         ?,      ?,      ?)
    '''
    purcha_ins_res = await db_ins.executes(purcha_insert_sql, purchalist)
    if purcha_ins_res is None:
        return False, 3019, '采购清单添加失败,请重试', None
    else:
        return True, 0, '采购清单添加成功', None


async def del_purcha(myid, recipeid):
    ''' 删除采购清单 '''
    sql = 'update purchase_info set `status`=-1, updateTime=? where recipeid=? and userid=?'
    result = await db_ins.execute(sql, (time.strftime('%Y-%m-%d %H:%M:%S'), recipeid, myid))
    # print('update result:', result, rid, unfollow, mutualConcern)
    # print(result)
    if result is None:
        return False, 3033, '删除采购清单失败,数据更新异常', None
    if result==0:
        return False, 1033, '错误的数据或其它,请重试', None
    else:
        return True, 0, '删除成功', None

async def up_purcha_isbuy(myid, purchaid, isbuy=1):
    ''' 清单是否购买更新, isbuy:默认设置为已购买 '''
    sql = 'update purchase_info set isbuy=?, updateTime=? where id=? and userid=? and status=0'
    result = await db_ins.execute(sql, (isbuy, time.strftime('%Y-%m-%d %H:%M:%S'), purchaid, myid))
    # print('update result:', result, rid, unfollow, mutualConcern)
    if result is None:
        return False, 3033, '更新清单购买状态失败,数据更新异常', None

    if result==0:
        return False, 1033, '错误的数据或其它,请重试', None
    else:
        return True, 0, '更新成功', None



async def get_purcha_list(myid, pagenum, epage=10):
    ''' 获取采购清单列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    purcha_sql = '''
select 
rsi.title,
purinfo.id,
purinfo.recipeid as cpid,
purinfo.stuff,
purinfo.amount,
purinfo.isbuy,
purinfo.createtime
from
(select distinct recipeid as rid from purchase_info where userid=? limit ?, ?) as drecipe
inner join purchase_info as purinfo
on drecipe.rid=purinfo.recipeid and purinfo.userid=? and `status`=0
inner join recipe_info as rsi
on drecipe.rid = rsi.id
ORDER BY purinfo.createtime desc,purinfo.id
    '''

    result = await db_ins.select(purcha_sql, (myid, page, epage, myid))
    if result is None:
        return False, 3101, '获取采购数据错误,请重试！', None

    # print(result)
    tempkey = dict()
    final_result = []
    for p in result:
        if tempkey.get(p.get('cpid'), False) is False:
            # 添加菜谱大类
            ct = p.get('createtime')
            final_result.append({'cpid':p.get('cpid'), 'title':p.get('title'), 'createtime':ct.strftime('%Y-%m-%d %H:%M:%S'), "purchaselist":[]})
            tempkey.setdefault(p.get('cpid'),True)

    for f in result:
        for purcha in final_result:
            # 添加菜谱对应的采购清单
            if purcha.get('cpid') == f.get('cpid'):
                purcha.get('purchaselist').append({'id':f.get('id'), 'isbuy':f.get('isbuy'), 'stuff':f.get('stuff'), 'amount':f.get('amount')})

    return True, 0, 'success', final_result


async def message_list(myid, pagenum, epage=15):
    ''' 获取消息列表,用户登录后获取未读和已读的评论信息(haveread!=-1 消息已删除不显示) '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    msg_sql = '''
SELECT
us.userName AS nickname,
us.headImg AS faceimg,
reply.itemid,
reply.itemtype,
reply.userid,
reply.message,
reply.id,
reply.haveread,
reply.createTime AS pushtime,
mmi.momentsImgUrl AS dtimg,
reci.faceImg AS cpimg,
topic.faceImg AS topicimg
FROM
(
SELECT * FROM reply_info
WHERE
haveRead!=-1
AND status=0
AND userid!=?
AND ((beUserId=? ) OR (itemUserID=? AND beuserid=0))
ORDER BY haveread,id DESC LIMIT ?,?)
AS reply
INNER JOIN user AS us
ON us.id = reply.userid AND us.`status`=0
LEFT JOIN moments_info AS mmi
ON mmi.id = reply.itemid AND reply.itemType=1
LEFT JOIN recipe_info AS reci
ON reci.id = reply.itemid AND reci.`status` in (0,1) AND reci.isEnable=1 AND reply.itemType=2
LEFT JOIN topic_info AS topic
ON topic.id = reply.itemid AND topic.`status` !=-1 AND topic.isEnable=1 AND reply.itemType=3
LEFT JOIN (SELECT BlockUserId FROM block_info WHERE userid=?) AS bli # 20191118增加黑名单过滤
ON bli.BlockUserId=reply.userid
WHERE bli.BlockUserId is null
ORDER BY reply.haveread,reply.createTime DESC
    '''
    # result = await db_ins.select(msg_sql, (myid, myid, myid, myid, page, epage))
    result = await db_ins.select(msg_sql, (myid, myid, myid, page, epage ,myid))

    # print(result, userid, page, epage)
    if result is None:
        return False, 3101, '获取消息数据错误', None
    for p in result:
        ct = p.get('pushtime')
        p['pushtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result


async def message_del(myid, msgid):
    ''' 将消息设置为删除, haveread 标记为 -1'''
    msg_exists_sql ='''
select id from reply_info
where
id = ?
and haveRead!=-1
and status=0
and userid!=?
and ((beUserId=? ) or (itemUserID=? and beuserid=0)) limit 1;
'''
    msg_exists_res = await db_ins.selectone(msg_exists_sql, (msgid, myid, myid, myid))
    if msg_exists_res is None:
        # 不属于你的消息或者异常的数据
        return False, 1102, '消息数据异常,请核对后重试', None

    up_msg_sql = 'update reply_info set haveRead = -1, updatetime=? where id=?' 
    up_msg_res = await db_ins.execute(up_msg_sql, (curDatetime(), msgid))
    if up_msg_res is None:
        return False, 3102, '消息删除失败,请重试', None
    else:
        return True, 0, '消息已删除', None


async def collection_list(userid, ctype, pagenum, epage=10):
    ''' 收藏列表 itemtype的类型: 1 动态,2 食谱,3 主题 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    if ctype == 1:
        # 动态
        sql = '''
select
*
from 
(
select
base.id,
base.dtid,
base.description,
base.dtimg,
base.createTime as collection_time,
count(lk.id) as lk_num
FROM
(
select
collection.*,
mmi.momentsDescription as 'description',
mmi.momentsImgUrl as 'dtimg',
mmi.id as 'dtid'
from
(
select
id,
itemid,createTime from collection_info
where userid=? and `type`=1 and `status`=0 order by createTime desc limit ?,?) as collection
inner join moments_info as mmi
on mmi.id=collection.itemid
) as base
LEFT JOIN like_info as lk
on lk.itemid = base.dtid and lk.`status`=0
GROUP BY base.id
) as result
ORDER BY collection_time desc
    '''
        result = await db_ins.select(sql, (userid, page, epage))
        # print(result, userid, page, epage)
        if result is None:
            return False, 3101, '获取动态数据错误', None
        for p in result:
            ct = p.get('collection_time')
            p['collection_time'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        return True, 0, 'success', result

    if ctype == 2:
        # 食谱
        sql = '''
select
collection.*,
reci.title,
reci.faceimg as cpimg,
reci.collectionCount as collections,
us.userName as nickname,
us.headImg as faceimg
from
(
select
id,
itemid as cpid,createtime as collection_time from collection_info
where userid=? and `type`=2 and `status`=0 ORDER BY createtime desc limit ?,?) as collection
inner join recipe_info as reci
on reci.id = collection.cpid and reci.`status` in (0,1) and reci.isEnable=1
inner join user as us
on reci.userid = us.id and us.`status`=0
ORDER BY collection.collection_time desc
        '''
        result = await db_ins.select(sql, (userid, page, epage))
        # print(result, userid, page, epage)
        if result is None:
            return False, 3102, '获取菜谱数据错误', None
        for p in result:
            ct = p.get('collection_time')
            p['collection_time'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        return True, 0, 'success', result

    if ctype == 3:
        # 主题
        sql = '''
select
collection.*,
topic.title,
topic.faceimg as topicimg,
topic.collectionCount as collections,
us.userName as nickname,
us.headImg as faceimg
from
(
select
id,
itemid as topicid,createtime as collection_time from collection_info
where userid=? and `type`=3 and `status`=0 ORDER BY createtime desc limit ?,?) as collection
inner join topic_info as topic
on topic.id = collection.topicid and topic.`status` !=-1 and topic.isEnable=1
inner join user as us
on topic.userid = us.id and us.`status`=0
ORDER BY collection.collection_time desc;
        '''
        result = await db_ins.select(sql, (userid, page, epage))
        if result is None:
            return False, 3103, '获取主题数据错误', None
        for p in result:
            ct = p.get('collection_time')
            p['collection_time'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        return True, 0, 'success', result


async def myspace_index(userid):
    ''' 个人空间首页,获取信息'''
    # 获取 动态 食谱 粉丝数量 关注 昵称、标签、头像
    # id,username, headimg, mobile, sex, birthday, address,personalProfile, tag, status,
    result = {}
    cacheojb = CacheUserinfo(userid)
    cres = await cacheojb.createCache()
    if cres is False:
        return False, 1001, '获取数据失败', None
    name, img, tag, personalprofile, certificationStatus, sex = await cacheojb.mget('username', 'headimg', 'tag', 'personalProfile', 'certificationStatus', 'sex')
    result.setdefault('nickname', name)
    result.setdefault('imgurl', img)
    result.setdefault('tag', tag)
    result.setdefault('personalprofile', personalprofile)
    result.setdefault('certificationstatus', certificationStatus)
    result.setdefault('sex', sex)

    n_dt = await cacheojb.get_dongtai()
    n_gz = await cacheojb.get_follow()
    n_fs = await cacheojb.get_fans()
    n_sp = await cacheojb.get_shipu()

    # 获取主题数量
    n_zt = await get_topic_num(userid)

    result.setdefault('moments', n_dt)
    result.setdefault('follows', n_gz)
    result.setdefault('fans', n_fs)
    result.setdefault('recipes', n_sp)
    result.setdefault('topics', n_zt)
    return True, 0, 'success', result


async def get_topic_num(userid):
    ''' 主题数量 '''
    sql = '''
SELECT
    count(id) as cnum
FROM
    topic_info
WHERE
    userid = ?
    AND isenable = 1
    AND status = 1
    '''
    result = await db_ins.selectone(sql, (userid))
    if result is None:
        # 报错返回0
        return 0
    return result.get('cnum', 0)

async def myspace_get_dongtai_list(userid, pagenum, epage=10):
    ''' 获取用户动态列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    # sql = '''select id, momentsDescription as 'dtinfo', type as 'dtype', momentsVideoUrl as 'videourl',
    # momentsImgUrl as 'imgurllist', itemId as 'cpid', createtime
    # from moments_info
    # where userid=? and status=0
    # ORDER BY id desc limit ?,?'''
    sql = '''
select mmi.* from 
(select id, momentsDescription as 'dtinfo', type as 'dtype', momentsVideoUrl as 'videourl',
    momentsImgUrl as 'imgurllist', itemId as 'cpid', likeCount as cnum, createtime
    from moments_info
    where userid=? and status=0
ORDER BY id desc limit ?,?) as mmi
ORDER BY mmi.id desc
    '''
    result = await db_ins.select(sql, (userid, page, epage))
    # print(result, userid, page, epage)
    if result is None:
        return False, 3001, '获取数据错误', None
    for p in result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result


async def get_caipu_temp_num(userid):
    ''' 获取用户个人菜谱草稿箱的数量 '''
    if userid==0:
        return 0
    temp_num_sql = '''
    select count(id) as cnum 
    from recipe_info
    where userid=? and `status`=2 and isEnable=1
    '''
    result = await db_ins.selectone(temp_num_sql, (userid))
    if result is None:
        # 报错返回0
        return 0
    return result.get('cnum', 0)


async def get_caipu_qingdan_num(userid):
    ''' 获取用户个人菜谱清单的数量 '''
    if userid == 0:
        return 0
    qingdan_num_sql = '''
    SELECT COUNT(1) AS cnum
    FROM (
    SELECT DISTINCT recipeid
    FROM purchase_info
    WHERE userid=? AND `status`=0) AS result
    '''
    result = await db_ins.selectone(qingdan_num_sql, (userid))
    if result is None:
        # 报错返回0
        return 0
    return result.get('cnum', 0)


async def get_caipu_temp_list(userid, pagenum, epage=10):
    ''' 获取 菜谱草稿箱 列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    caipu_temp_sql = '''
select
id, 
title,
faceimg as cpimg,
createtime
from recipe_info
where userid=? and `status`=2 and isEnable=1 ORDER BY createtime desc limit ?,?
    '''
    result = await db_ins.select(caipu_temp_sql, (userid, page, epage))
    if result is None:
        return False, 3012, '获取草稿数据错误', None
    for p in result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    
    return True, 0, 'success', result


async def myspace_get_caipu_list(userid, pagenum, status=1, epage=10):
    ''' 返回用户菜谱列表, status=1 状态(个人用户可以看除删除以外的所有), epage 表示每页数量'''
    # 返回 菜谱 名字，缩略图，创建时间，审核状态
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    if status == 1:
        # 用户可以看到自己的，被管理禁用的菜谱
        sql = 'select id, title, faceimg, isEnable, collectionCount as keepnum, visitCount as visitnum, createtime from recipe_info where userid=? and (status=1 or status=0) ORDER BY id desc limit ?,?'
    else:
        sql = 'select id, title, faceimg, isEnable, collectionCount as keepnum, visitCount as visitnum, createtime from recipe_info where userid=? and (status=1 or status=0) and isEnable=1 ORDER BY id desc limit ?,?'

    # print(sql,start,end)
    result = await db_ins.select(sql, (userid, page, epage))
    if result is None:
        return False, 3001, '获取数据错误', None

    for p in result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    
    return True, 0, 'success', result

async def myspace_fanslist(userid, pagenum, epage=20):
    ''' 粉丝列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql = '''
    select user.userName as 'nickname', user.headimg as 'headimg', fo.userid as 'fansid', fo.mutualConcern as 'isfriend', fo.createTime as 'focustime'
    from focus_info as fo INNER JOIN `user` on fo.userid = user.id
    where fo.focusUserId=? and user.`status`=0 and fo.unfollow=0 order by fo.id desc limit ?,?;
    '''
    result = await db_ins.select(sql, (userid, page, epage))
    if result is None:
        return False, 3002, '获取数据错误', None

    for p in result:
        ct = p.get('focustime')
        p['focustime'] = ct.strftime('%Y-%m-%d %H:%M:%S')

    return True, 0, 'success', result

async def myspace_followlist(userid, pagenum, epage=20):
    ''' 关注列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql = '''
    select user.userName as 'nickname', user.headimg as 'headimg', fo.focusUserId as 'followid', fo.mutualConcern as 'isfriend', fo.createTime as 'focustime'
    from focus_info as fo INNER JOIN `user` on fo.focusUserId = user.id
    where fo.userid=? and user.`status`=0 and fo.unfollow=0 order by fo.id desc limit ?,?;
    '''
    result = await db_ins.select(sql, (userid, page, epage))
    if result is None:
        return False, 3003, '获取数据错误', None

    for p in result:
        ct = p.get('focustime')
        p['focustime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result


async def myspace_friendlist(userid, pagenum, epage=20):
    ''' 好友列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
#     sql = '''select user.userName as 'nickname', user.headimg as 'headimg',fo.focusUserId as 'friendID', fo.mutualConcern as 'isfriend', fo.createTime as 'focustime'
# from focus_info as fo INNER JOIN `user` on fo.focusUserId = user.id
# where fo.userid=? and user.`status`=0 and fo.mutualConcern=1 order by fo.id desc limit ?,?;
#     '''
    sql = '''
    select user.userName as nickname, user.headimg as 'headimg', friend.* from user inner join
    (select fans.id, follow.focusUserId as friendID, fans.mutualConcern as isfriend from 
    (select userId, focusUserId, mutualConcern FROM focus_info WHERE userId=? and unfollow=0) as follow inner join
    (select id,userId, focusUserId, mutualConcern FROM focus_info WHERE focusUserId=?) as fans
    on follow.focusUserId = fans.userId and follow.mutualConcern = 1) as friend
    on user.id = friend.friendID ORDER BY id desc limit ?, ?;
    '''
    # result = await db_ins.select(sql, (userid, page, epage))
    result = await db_ins.select(sql, (userid, userid, page, epage))
    # print(result,  (userid, userid, page, epage))
    if result is None:
        log.error("获取好友失败:{}, {}".format(sql, (userid, page, epage)))
        return False, 3004, '获取数据错误', None

    # for p in result:
    #     ct = p.get('focustime')
    #     p['focustime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result

async def myspace_follow(userid, follow_user_id):
    ''' 点击关注 '''
    # 用户是否存在和合法
    user = await exists_user(follow_user_id)
    if user is False or userid == follow_user_id:
        log.warning("关注失败, 用户不存在或不合法,id:{}".format(follow_user_id))
        return False

    # 是否存在粉丝记录
    fanid, fan_user_id, fan_status_unfollow = await exists_fans_record(userid, follow_user_id)
    # 是否存在关注记录
    followid, record_follow_user_id, follow_status_unfollow = await exists_follow_record(userid, follow_user_id)
    # print("粉丝记录:", fanid, fan_user_id, fan_status_unfollow)
    # print("关注记录:", followid, record_follow_user_id, follow_status_unfollow)
    if follow_status_unfollow == 0 and followid!=0:
        # 目前是已关注状态，不需要重复点击关注
        return False
    if record_follow_user_id == follow_user_id:
        # 之前已经关注过,更新关注记录
        if fanid == 0:
            # 对方没有关注你的记录
            up_follow_result = await update_follow(followid, mutualConcern=0)
            up_fan_result = True
        else:
            # 对方有关注你的记录
            # 两条记录都更新
            if fan_status_unfollow == 0:
                # 有记录,并且对方也有关注你, 设置互相关注
                up_follow_result = await update_follow(followid, mutualConcern=1)
                up_fan_result = await update_follow(fanid, 1)
            else:
                # 有记录,但没关注你
                up_follow_result = await update_follow(followid, mutualConcern=0)
                up_fan_result = True

        if up_follow_result and up_fan_result:
            # 更新 关注数量+1,对面 粉丝数量 + 1
            await cache_up_follow(userid, 1)
            await cache_up_fans(follow_user_id, 1)
            return True
        else:
            # 部分数据更新异常
            return False
    else:
        # 之前未关注过
        # 插入一条数据
        if fanid == 0:
            # 对方没有关注你的记录, 插入非互相关注状态 0)
            add_follow_result = await insert_follow(userid, follow_user_id, 0, 0)

            if add_follow_result:
                await cache_up_follow(userid, 1)
                await cache_up_fans(follow_user_id, 1)
                return True
            else:
                return False
        else:
            # 对方有关注你的记录
            if fan_status_unfollow == 0:
                # 有记录,并且对方也有关注你, 插入互相关注. 1, 更新对方互相关注状态)
                add_follow_result = await insert_follow(userid, follow_user_id, 0, mutualConcern=1)
                up_fan_result = await update_follow(fanid, 1)
            else:
                # 有记录,但没关注你。 插入一条关注记录。
                add_follow_result = await insert_follow(userid, follow_user_id, 0, mutualConcern=0)
                up_fan_result = True

            if add_follow_result and up_fan_result:
                # 更新 关注数量+1,对面 粉丝数量 + 1
                await cache_up_follow(userid, 1)
                await cache_up_fans(follow_user_id, 1)
                return True
            else:
                # 部分数据更新异常
                return False

async def myspace_unfollow(userid, follow_user_id):
    ''' 取消关注 '''
    user = await exists_user(follow_user_id)
    if user is False or userid == follow_user_id:
        log.warning("关注失败, 用户不存在或不合法,id:{}".format(follow_user_id))
        return False
    # 是否存在粉丝记录
    fanid, fan_user_id, fan_status_unfollow = await exists_fans_record(userid, follow_user_id)
    # 是否存在关注记录
    followid, record_follow_user_id, follow_status_unfollow = await exists_follow_record(userid, follow_user_id)
    # print("粉丝记录:", fanid, fan_user_id, fan_status_unfollow)
    # print("关注记录:", followid, record_follow_user_id, follow_status_unfollow)
    if followid == 0:
        # 不存在关注记录,取消关注错误
        return False
    if follow_status_unfollow == 1:
        # 状态已是取消关注,取消关注错误
        return False
    else:
        # 存在记录,取消关注
        up_unfollow_result = await update_unfollow(followid, mutualConcern=0)
        if up_unfollow_result:
            # 取消关注成功
            await cache_up_follow(userid, -1)
            await cache_up_fans(follow_user_id, -1)

            if fanid == 0:
                # 不存在粉丝记录
                up_unfans_result = True
                return True
            else:
                # 存在粉丝记录,更新粉丝记录为 非互相关注状态
                up_unfans_result = await update_mutualConcern(fanid, mutualConcern=0)
                if up_unfans_result:
                    # 对方粉丝数量-1
                    return True
                else:
                    return False
        else:
            # 取消关注,更新失败,返回false 
            return False


async def insert_follow(userid, followid, unfollow=0, mutualConcern=0):
    ''' 插入关注的值, 用户ID, 被关注人ID, 0 默认关注状态, 0 默认不互粉不是好友 '''
    insert_sql = "INSERT into focus_info (`userId`, `focusUserId`, `mutualConcern`, `unfollow`) values (?, ?, ?, ?)"
    result = await db_ins.execute(insert_sql, (userid, followid, mutualConcern, unfollow))
    if result is None:
        log.error('插入数据失败,{}, {}'.format(insert_sql, (userid, followid, mutualConcern, unfollow)))
        return False
    else:
        return True

async def update_follow(rid, mutualConcern=0):
    ''' 根据follow关注记录,更新对应的值 '''
    sql = 'update focus_info set unfollow=0, mutualConcern=?, updateTime=? where id=?'
    result = await db_ins.execute(sql, (mutualConcern, time.strftime('%Y-%m-%d %H:%M:%S'), rid))
    # print('update result:', result, rid, unfollow, mutualConcern)
    if result is None:
        log.error('更新数据失败,{},{}'.format(sql, (mutualConcern, time.strftime('%Y-%m-%d %H:%M:%S'), rid)))
        return False
    else:
        return True

async def update_unfollow(rid, mutualConcern=0):
    ''' 根据follow关注记录,更新对应的值 '''
    sql = 'update focus_info set unfollow=1, mutualConcern=?, updateTime=? where id=?'
    result = await db_ins.execute(sql, (mutualConcern, time.strftime('%Y-%m-%d %H:%M:%S'), rid))
    # print('update result:', result, rid, unfollow, mutualConcern)
    if result is None:
        log.error('更新数据失败,{},{}'.format(sql, (mutualConcern, time.strftime('%Y-%m-%d %H:%M:%S'), rid)))
        return False
    else:
        return True

async def update_mutualConcern(rid,mutualConcern):
    # 取消粉丝互相关注的状态
    sql = 'update focus_info set mutualConcern=?, updateTime=? where id=?'
    result = await db_ins.execute(sql, (mutualConcern, time.strftime('%Y-%m-%d %H:%M:%S'), rid))
    # print("取消互相关注状态:",rid,mutualConcern,result)
    if result is None:
        log.error('更新数据失败,{},{}'.format(sql, ( mutualConcern, time.strftime('%Y-%m-%d %H:%M:%S'), rid)))
        return False
    else:
        return True

async def exists_user(follow_user_id):
    # 用户是否存在
    user_sql = 'select id from user where id=? and status=0 limit 1'
    result = await db_ins.select(user_sql, (follow_user_id))
    if result is None:
        log.error('查询数据失败,{},{}'.format(user_sql, (follow_user_id)))
        return False
    if len(result) > 0:
        return True
    else:
        return False

async def get_relationship_status(myid, uid):
    ''' 获取两个用户的关注关系,返回值 0 未关注 1 你关注了他 2 他关注了你 3 互相关注 '''
    isfollow = await exists_follow(myid, uid)
    isfans = await exists_fans(myid, uid)
    if myid == 0 or uid ==0:
        # 非法的数据,未登录等 都是未关注
        return 0
    relationship = 0 # 默认未关注状态
    if isfollow>0:
        # 已关注
        relationship = 1

    if isfans > 0:
        # 是粉丝
        relationship = 2

    if isfollow>0 and isfans>0:
        # 互相关注
        relationship = 3
    return relationship


async def exists_follow_record(userid, follow_user_id):
    ''' 是否存在关注记录 '''
    # 是否有关注
    sql = 'select id, focusUserId, unfollow from focus_info where userid=? and focusUserId=? limit 1'
    result = await db_ins.selectone(sql, (userid, follow_user_id))
    if result is None:
        log.error('查询数据失败,{},{}'.format(sql, (userid, follow_user_id)))
        return 0,0,0
    return result.get('id', 0), result.get('focusUserId'), result.get('unfollow')


async def exists_fans_record(userid, follow_user_id):
    ''' 是否存在粉丝记录 '''
    # 是否是粉丝
    sql = 'select id, userid, unfollow from focus_info where focusUserId=? and userid=? limit 1'
    result = await db_ins.selectone(sql, (userid, follow_user_id))
    if result is None:
        log.error('查询数据失败,{},{}'.format(sql, (userid, follow_user_id)))
        return 0,0,0
    return result.get('id', 0), result.get('userid'), result.get('unfollow')


async def exists_follow(userid, follow_user_id):
    ''' 是否是关注 '''
    # 是否有关注
    sql = 'select id from focus_info where userid=? and focusUserId=? and unfollow=0 limit 1'
    result = await db_ins.select(sql, (userid, follow_user_id))
    if result is None:
        log.error('查询数据失败,{},{}'.format(sql, (userid, follow_user_id)))
        return 0
    if len(result) > 0:
        return result[0].get('id', 0)
    else:
        return 0

async def exists_fans(userid, follow_user_id):
    ''' 是否是粉丝 '''
    # 是否是粉丝
    sql = 'select id from focus_info where focusUserId=? and userid=? and unfollow=0 limit 1'
    result = await db_ins.select(sql, (userid, follow_user_id))
    if result is None:
        log.error('查询数据失败,{},{}'.format(sql, (userid, follow_user_id)))
        return 0
    if len(result) > 0:
        return result[0].get('id', 0)
    else:
        return 0


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(myspace_get_caipu_list(0, 1))
    async def test_myspace_follow():
        res = await myspace_follow(1,2)
        print(res)
        res = await myspace_follow(1,3)
        print(res)
        res = await myspace_follow(1,6)
        print(res)
        res = await myspace_follow(6,1)
        print(res)
        res = await myspace_follow(2,1)
        print(res)
        res = await myspace_follow(7,2)
        print(res)
        res = await myspace_follow(8,2)
        print(res)
    # loop.run_until_complete(test_myspace_follow())

    async def test_myspace_unfollow():
        res = await myspace_unfollow(1,2)
        print(res)
        res = await myspace_unfollow(1,3)
        print(res)
        res = await myspace_unfollow(1,6)
        print(res)
        res = await myspace_unfollow(6,1)
        print(res)
        res = await myspace_unfollow(2,1)
        print(res)
        res = await myspace_unfollow(4,1)
        print(res)
        res = await myspace_unfollow(7,2)
        print(res)
        res = await myspace_unfollow(8,2)
        print(res)


    async def test_message_list():
        res = await message_list(1,1)
        print(res)

    async def test_myspace_get_dongtai_list():
        res = await myspace_get_dongtai_list(1,1)
        print(res)

    async def test_message_del():
        res = await message_del(1,26)
        print(res)
        
    loop.run_until_complete(test_message_del())

