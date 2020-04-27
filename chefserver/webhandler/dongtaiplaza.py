import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CachePapeHotDongtai, CacheRecommedDongtai
from chefserver.tool.async_redis_pool import RedisOperate
from chefserver.webhandler.common_action import get_all_blocks

log = applog.get_log('webhandler.dongtaiplaza')
dbins = DbOperate.instance()
cachins = RedisOperate.instance()

class DtPlazaHandler(BaseHandler):
    ''' 动态广场！ 最新，最热列表 '''
    async def post(self):
        userblock = None
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            relationship = 0
            myid=0
        else:
            # 获取关注状态
            myid = user_session.get('id',0)
            userblock = await get_all_blocks(myid)

        plazatype = self.verify_arg_legal(self.get_body_argument('plazatype'), '动态广场列表类型', False, uchecklist=True, user_check_list=['1','2'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        hotdtpage = CachePapeHotDongtai()
        argkey = plazatype + page
        if await hotdtpage.exists(argkey):
            # 命中缓存
            cache = await hotdtpage.get(argkey)
            if cache is not None:
                # 返回缓存
                await plaza_focus_process(myid, cache) # 增加是否关注
                await plaza_like_process(myid, cache) # 增加是否点赞
                if userblock is not None:
                    cache = [i for i in cache if i.get('userid') not in userblock]
                    # self.send_message(True, 0, "success", [i for i in result if i.get('userid') not in userblock])
                return self.send_message(True, 0, "success", cache)
            else:
                # 返回缓存失败,写日志执行sql返回
                log.warning('获取动态热门缓存失败,类型:{}, 页面:{}'.format(plazatype,page))

        success, code, message, result = await dongtai_plaza_list(int(plazatype), int(page))
        if success:
            # 没有命中缓存,更新缓存
            await hotdtpage.set(argkey, result)
            await plaza_focus_process(myid, result) # 增加是否关注
            await plaza_like_process(myid, result) # 增加是否点赞
            if userblock is not None:
                # 黑名单过滤
                result = [i for i in result if i.get('userid') not in userblock]
                # self.send_message(True, 0, "success", [i for i in result if i.get('userid') not in userblock])
        return self.send_message(success, code, message, result)


class DtPlazaRecommendHandler(BaseHandler):
    ''' 动态广场！ 推荐列表 '''
    async def post(self):
        userblock = None
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            relationship = 0
            myid = 0
        else:
            # 获取关注状态
            myid = user_session.get('id',0)
            userblock = await get_all_blocks(myid)

        dtlist = self.verify_arg_legal(self.get_body_argument('dtlist'), '当前动态列表', False, is_len=True, olen=180)
        success, code, message, result = await get_recommend_dtrandomlist(myid, dtlist)
        if success:
            # 返回成功
            await plaza_focus_process(myid, result) # 增加是否关注
            await plaza_like_process(myid, result) # 增加是否点赞
        # await plaza_like_process(userid, result) # 增加是否点赞
        self.send_message(success, code, message, result)


class DtPlazafocusHandler(BaseHandler):
    ''' 个人关注的好友的最新动态 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await focus_plaza_list(userid, int(page))
        await plaza_like_process(userid, result) # 增加是否点赞
        return self.send_message(success, code, message, result)


async def get_recommend_dtrandomlist(myid, dtlist):
    ''' 返回随机动态推荐列表
        myid:用户是否登录ID
        dtlist:当前动态列表
    '''
    # 获取随机ID.数量= dtlist长度 * 2
    dt_id_list = dtlist.split(",")
    dt_nums = len(dt_id_list)
    re_nums = dt_nums * 2 if dt_nums * 2 >= 30 else dt_nums + 15
    rand_res_list = await CacheRecommedDongtai().get_random(re_nums)
    end_res_set = set(rand_res_list) - set(dt_id_list)
    if len(end_res_set) == 0:
        return False, 1002, '推荐数据为空', []
    end_res_list = list(end_res_set)
    end_res_str = str(end_res_list[:15]).lstrip('[').rstrip(']').replace('\'','')
    sql = '''
select
us.userName as nickname,
us.headImg as faceimg,
mmi.*,
(case when rpl.replynum is null then 0 else rpl.replynum end) as replynum
from
(
select
id,
userid,
momentsDescription as description,
momentsImgUrl as dtimg,
momentsVideoUrl as videourl,
createTime as pushtime,
isvideo,
likecount
from moments_info
where id in ({}) and `isvideo` =1
) as mmi
inner join user as us
on us.id = mmi.userid and us.`status` = 0
left join (SELECT itemid as dtid,count(id) as replynum from reply_info where itemType=1 and itemid in ({}) and `status` = 0 group by itemid) as rpl on mmi.id = rpl.dtid
    '''
    sql = sql.format(end_res_str,end_res_str)
    result = await dbins.select(sql, ())
    # print(result, userid, page, epage)
    if result is None:
        return False, 3013, '获取动态推荐数据错误', None
    for p in result:
        ct = p.get('pushtime')
        p['pushtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result

async def plaza_focus_process(myid, reslist):
    ''' 返回动态广场返回结果中,增加是否有关注'''
    [m.setdefault('isfollow', False) for m in reslist]
    if myid == 0:
        return
    userlist = [str(m.get('userid')) for m in reslist if m.get('userid')!=myid] 
    sql_check_like = "select focususerid as itemid from focus_info where userid={} and unfollow=0 and focususerid in ({})"
    if len(userlist) == 0:
        return
    sql_check_like = sql_check_like.format(myid, ",".join(userlist))

    result = await dbins.select(sql_check_like, ())
    if result is None:
        return
    itemkey = {t.get('itemid'):True for t in result}
    # print("关注",itemkey)
    for v in reslist:
        # print(itemkey.get(v.get('userid'), False))
        v.update(isfollow=itemkey.get(v.get('userid'), False))
    return


async def plaza_like_process(myid, reslist):
    ''' 返回动态广场返回结果中,增加是否有点赞'''
    [m.setdefault('isliked', False) for m in reslist]
    if myid == 0:
        return
    # momentlist = [m.get('id') for m in reslist if m.get('likecount') > 0]
    momentlist = [str(m.get('id')) for m in reslist if m.get('likecount') > 0]
    
    if len(momentlist) == 0:
        return
    sql_check_like = "select itemid from like_info where userid={} and status=0 and itemid in ({})"
    sql_check_like = sql_check_like.format(myid, ",".join(momentlist))
    result = await dbins.select(sql_check_like, ())
    if result is None:
        return
    itemkey = {t.get('itemid'):True for t in result}
    # print("点赞",itemkey)
    for v in reslist:
        v.update(isliked=itemkey.get(v.get('id'), False))
    return


async def focus_plaza_list(myid, pagenum, epage=15):
    ''' 我关注的好友最新动态 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql='''
select
follows.*,
mmi.id,
mmi.momentsImgUrl as dtimg,
mmi.likecount,
mmi.momentsDescription as description,
mmi.isvideo,
mmi.momentsVideoUrl as videourl,
mmi.createTime as pushtime
from
moments_info as mmi
inner join
(
select user.userName as 'nickname', user.headimg as 'faceimg', fo.focusUserId as 'followid'
from focus_info as fo INNER JOIN `user` on fo.focusUserId = user.id
where fo.userid=? and user.`status`=0 and fo.unfollow=0 order by fo.id desc limit 0,15
) as follows
on follows.followid = mmi.userid and mmi.`status`= 0
order by pushtime desc limit ?,?
    '''
    result = await dbins.select(sql, (myid, page, epage))
    # print(result, userid, page, epage)
    if result is None:
        return False, 3001, '获取好友动态最新数据错误', None
    for p in result:
        ct = p.get('pushtime')
        p['pushtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result


async def dongtai_plaza_list(plazatype, pagenum, epage=15):
    ''' 动态广场动态列表数据 plazatype: 1 最新，2 最热 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    if plazatype == 1:
        # 最新
        sql = '''
select
us.userName as nickname,
us.headImg as faceimg,
mmi.*
from
(
select
id,
userid,
momentsDescription as description,
momentsImgUrl as dtimg,
momentsVideoUrl as videourl,
createTime as pushtime,
isvideo,
likecount
from moments_info
where `status` = 0
ORDER BY pushtime DESC limit ?,?
) as mmi
inner join user as us
on us.id = mmi.userid and us.`status` = 0
order by mmi.pushtime desc
        '''
        result = await dbins.select(sql, (page, epage))
        # print(result, userid, page, epage)
        if result is None:
            return False, 3001, '获取动态广场最新数据错误', None
        for p in result:
            ct = p.get('pushtime')
            p['pushtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        return True, 0, 'success', result

    if plazatype == 2:
        # 最热
        sql = '''
select
us.userName as nickname,
us.headImg as faceimg,
result.*
from
(
select
mmi.id,
mmi.userid,
mmi.momentsDescription as description,
mmi.momentsImgUrl as dtimg,
(CASE when (reply.replynum IS NULL) then 0 else reply.replynum end) as replynum,
mmi.likecount,
(CASE when (reply.replynum IS NULL) then 0 else reply.replynum end) + mmi.likecount as total,
mmi.isvideo
from
(
select id,userid,momentsDescription,momentsImgUrl,likecount,isvideo from moments_info where likecount>0 and status=0 
) as mmi
left join
(select itemId, count(id) as replynum from reply_info where itemType=1 and `status`=0 GROUP BY itemId) as reply # 获取所有点赞>0的动态数据
on mmi.id = reply.itemid
union DISTINCT
select
reply.id,
mmi.userid,
mmi.momentsDescription as description,
mmi.momentsImgUrl as dtimg,
reply.replynum,
mmi.likecount,
reply.replynum + mmi.likecount as total,
mmi.isvideo
from moments_info as mmi
inner join 
(select itemId as id,count(id) as replynum from reply_info where itemType=1 and `status`=0 GROUP BY itemId) as reply # 获取评论>0的动态数据
on reply.id= mmi.id and mmi.status=0
) as result # 关联两张表
inner join user as us
on result.userid = us.id and us.`status` = 0
        '''
        result = await dbins.select(sql, ())
        # print(result, userid, page, epage)

        if result is None:
            return False, 3102, '获取动态广场最热数据错误', None

        sort_result = sorted(result, key=lambda x:x.get('total'), reverse=True)

        return True, 0, 'success', sort_result[page:page+epage]
    
    return False, 1003, '未知操作类型', None


if __name__ == '__main__':
    async def test_dongtai_plaza_list():
        # res = await dongtai_plaza_list(1,1)
        # print(res)
        res = await dongtai_plaza_list(2,1)
        # print(res)

    async def test_focus_plaza_list():
        res= await focus_plaza_list(1,1)
        # print(res)


    async def test_plaza_like_process():
        l = [{'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 1, 'userid': 3, 'description': 'ffffffffffffffffffffffffffff', 'dtimg': 'blob:http://localhost:8081/6634d5e9-7c44-4dfb-b4cc-739d313ac7ac', 'replynum': 0, 'likecount': 1091, 'total': 1091, 'isvideo': 0},
 {'nickname': '紫枫叶', 'faceimg': '26/userimg/a/2/7/a264f711d4235d70a3cb784544192dc7.jpg', 'id': 115, 'userid': 26, 'description': '超级简单的电饭锅卤鸡爪！色泽诱人，口感Q弹，你也可以拥有！', 'dtimg': '26/caipu/3/0/0/30dabd60833eb3a43e3685ad87fd9fb0.jpg', 'replynum': 3, 'likecount': 997, 'total': 1000, 'isvideo': 0},
 {'nickname': 'u091901', 'faceimg': 'userimg/8/6/e/864b58472ad3762a77f213735c27d01e.jpg', 'id': 73, 'userid': 14, 'description': '例如', 'dtimg': '14/caipu/4/d/e/4d3eb6c0649269c16d0d84c740c3864e.jpg', 'replynum': 0, 'likecount': 222, 'total': 222, 'isvideo': 0},
 {'nickname': '可爱小白', 'faceimg': '27/userimg/d/0/b/d092a5dbba36d244d4c321cedbb22d1b.jpg', 'id': 110, 'userid': 27, 'description': '爱吃饼干就自己烤⊙∀⊙！', 'dtimg': '27/caipu/d/1/b/d1218e67b0e52c25830735ac2a7d65db.jpg', 'replynum': 5, 'likecount': 3, 'total': 8, 'isvideo': 0},
 {'nickname': '昵称', 'faceimg': '', 'id': 126, 'userid': 1, 'description': '2019.12.11 test moments2', 'dtimg': '25/caipu/1/d/3/1dcdaf217cfb7afeed563bb8fb3bdc63.jpg', 'replynum': 0, 'likecount': 6, 'total': 6, 'isvideo': 0},
 {'nickname': '可爱小白', 'faceimg': '27/userimg/d/0/b/d092a5dbba36d244d4c321cedbb22d1b.jpg', 'id': 74, 'userid': 27, 'description': '吃鸽子吗', 'dtimg': '27/pushimg/3/0/6/30149bb7020ff1c93b64d70b23a50b96.jpg', 'replynum': 0, 'likecount': 3, 'total': 3, 'isvideo': 0},
 {'nickname': 'u091901', 'faceimg': 'userimg/8/6/e/864b58472ad3762a77f213735c27d01e.jpg', 'id': 72, 'userid': 14, 'description': '踏踏实实', 'dtimg': '14/caipu/7/9/8/79b1f5a3f15ef3715c4032649acbccd8.jpg', 'replynum': 0, 'likecount': 2, 'total': 2, 'isvideo': 0},
 {'nickname': '青菜萝卜', 'faceimg': '25/userimg/9/0/8/90a4c8f628c404a4f2905ae8ddf59b38.jpg', 'id': 118, 'userid': 25, 'description': '党', 'dtimg': '25/pushimg/b/a/c/ba8df4b25b2ceb60250171cad6daa29c.jpg', 'replynum': 0, 'likecount': 2, 'total': 2, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 116, 'userid': 3, 'description': '多图舞动后', 'dtimg': '3/pushimg/3/b/b/3b47f2980c58438c7f21f5fac7fe4a4b.jpg|3/pushimg/7/c/9/7c2a0ef4e7eba89a0a03fa0939099ab9.jpg|3/pushimg/5/8/3/58f1dc031a66c68e66664ef977325633.jpg', 'replynum': 2, 'likecount': 0, 'total': 2, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 41, 'userid': 3, 'description': '反反复复反反复复反反复复反反复复反反复复反反复复反反复复反反复复发放发放付付付付付付付付付付付付付付付', 'dtimg': 'undefined|undefined|undefined|undefined|3/pushimg/3/2/f/32c3802444d4ec84f98c88c8e12f61ef.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 42, 'userid': 3, 'description': '嘎嘎嘎嘎嘎过过过过过过过过', 'dtimg': 'undefined|undefined|undefined|3/pushimg/1/1/3/116722296eb802d9997277e9dd6a4023.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': 'u091901', 'faceimg': 'userimg/8/6/e/864b58472ad3762a77f213735c27d01e.jpg', 'id': 71, 'userid': 14, 'description': '海流', 'dtimg': '14/pushimg/1/b/8/1bb57ba708bc7c7f322fa87e31c6d5a8.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 104, 'userid': 3, 'description': '顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶', 'dtimg': '3/pushimg/1/8/1/1833cce1c3fabe2a5049dc827030c711.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '小吃货', 'faceimg': '28/userimg/f/9/a/f9b0a02cf2c5b4a5e8b0d76c547dd83a.jpg', 'id': 109, 'userid': 28, 'description': '好吃', 'dtimg': '28/pushimg/7/4/4/74c04db3a2838f36327a6ead8cdc3334.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '昵称', 'faceimg': '', 'id': 134, 'userid': 1, 'description': '2019.12.11 test moments3', 'dtimg': '25/caipu/1/d/3/1dcdaf217cfb7afeed563bb8fb3bdc63.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0}]
        # print(len(l))
        res = await plaza_like_process(1, l)
        # print(l)

    async def test_plaza_focus_process():
        l = [{'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 1, 'userid': 3, 'description': 'ffffffffffffffffffffffffffff', 'dtimg': 'blob:http://localhost:8081/6634d5e9-7c44-4dfb-b4cc-739d313ac7ac', 'replynum': 0, 'likecount': 1091, 'total': 1091, 'isvideo': 0},
 {'nickname': '紫枫叶', 'faceimg': '26/userimg/a/2/7/a264f711d4235d70a3cb784544192dc7.jpg', 'id': 115, 'userid': 26, 'description': '超级简单的电饭锅卤鸡爪！色泽诱人，口感Q弹，你也可以拥有！', 'dtimg': '26/caipu/3/0/0/30dabd60833eb3a43e3685ad87fd9fb0.jpg', 'replynum': 3, 'likecount': 997, 'total': 1000, 'isvideo': 0},
 {'nickname': 'u091901', 'faceimg': 'userimg/8/6/e/864b58472ad3762a77f213735c27d01e.jpg', 'id': 73, 'userid': 14, 'description': '例如', 'dtimg': '14/caipu/4/d/e/4d3eb6c0649269c16d0d84c740c3864e.jpg', 'replynum': 0, 'likecount': 222, 'total': 222, 'isvideo': 0},
 {'nickname': '可爱小白', 'faceimg': '27/userimg/d/0/b/d092a5dbba36d244d4c321cedbb22d1b.jpg', 'id': 110, 'userid': 27, 'description': '爱吃饼干就自己烤⊙∀⊙！', 'dtimg': '27/caipu/d/1/b/d1218e67b0e52c25830735ac2a7d65db.jpg', 'replynum': 5, 'likecount': 3, 'total': 8, 'isvideo': 0},
 {'nickname': '昵称', 'faceimg': '', 'id': 126, 'userid': 1, 'description': '2019.12.11 test moments2', 'dtimg': '25/caipu/1/d/3/1dcdaf217cfb7afeed563bb8fb3bdc63.jpg', 'replynum': 0, 'likecount': 6, 'total': 6, 'isvideo': 0},
 {'nickname': '可爱小白', 'faceimg': '27/userimg/d/0/b/d092a5dbba36d244d4c321cedbb22d1b.jpg', 'id': 74, 'userid': 27, 'description': '吃鸽子吗', 'dtimg': '27/pushimg/3/0/6/30149bb7020ff1c93b64d70b23a50b96.jpg', 'replynum': 0, 'likecount': 3, 'total': 3, 'isvideo': 0},
 {'nickname': 'u091901', 'faceimg': 'userimg/8/6/e/864b58472ad3762a77f213735c27d01e.jpg', 'id': 72, 'userid': 14, 'description': '踏踏实实', 'dtimg': '14/caipu/7/9/8/79b1f5a3f15ef3715c4032649acbccd8.jpg', 'replynum': 0, 'likecount': 2, 'total': 2, 'isvideo': 0},
 {'nickname': '青菜萝卜', 'faceimg': '25/userimg/9/0/8/90a4c8f628c404a4f2905ae8ddf59b38.jpg', 'id': 118, 'userid': 25, 'description': '党', 'dtimg': '25/pushimg/b/a/c/ba8df4b25b2ceb60250171cad6daa29c.jpg', 'replynum': 0, 'likecount': 2, 'total': 2, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 116, 'userid': 3, 'description': '多图舞动后', 'dtimg': '3/pushimg/3/b/b/3b47f2980c58438c7f21f5fac7fe4a4b.jpg|3/pushimg/7/c/9/7c2a0ef4e7eba89a0a03fa0939099ab9.jpg|3/pushimg/5/8/3/58f1dc031a66c68e66664ef977325633.jpg', 'replynum': 2, 'likecount': 0, 'total': 2, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 41, 'userid': 3, 'description': '反反复复反反复复反反复复反反复复反反复复反反复复反反复复反反复复发放发放付付付付付付付付付付付付付付付', 'dtimg': 'undefined|undefined|undefined|undefined|3/pushimg/3/2/f/32c3802444d4ec84f98c88c8e12f61ef.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 42, 'userid': 3, 'description': '嘎嘎嘎嘎嘎过过过过过过过过', 'dtimg': 'undefined|undefined|undefined|3/pushimg/1/1/3/116722296eb802d9997277e9dd6a4023.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': 'u091901', 'faceimg': 'userimg/8/6/e/864b58472ad3762a77f213735c27d01e.jpg', 'id': 71, 'userid': 14, 'description': '海流', 'dtimg': '14/pushimg/1/b/8/1bb57ba708bc7c7f322fa87e31c6d5a8.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '小僵尸-gg', 'faceimg': 'uid.3/userimg/e/b/e/eb049f0b2972c0079fac0703670cea5e.jpg', 'id': 104, 'userid': 3, 'description': '顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶顶', 'dtimg': '3/pushimg/1/8/1/1833cce1c3fabe2a5049dc827030c711.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '小吃货', 'faceimg': '28/userimg/f/9/a/f9b0a02cf2c5b4a5e8b0d76c547dd83a.jpg', 'id': 109, 'userid': 28, 'description': '好吃', 'dtimg': '28/pushimg/7/4/4/74c04db3a2838f36327a6ead8cdc3334.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0},
 {'nickname': '昵称', 'faceimg': '', 'id': 134, 'userid': 1, 'description': '2019.12.11 test moments3', 'dtimg': '25/caipu/1/d/3/1dcdaf217cfb7afeed563bb8fb3bdc63.jpg', 'replynum': 0, 'likecount': 1, 'total': 1, 'isvideo': 0}]
        print(len(l))
        res = await plaza_focus_process(1, l)
        print(l)

    async def test_get_recommend_dtrandomlist():
        res = await get_recommend_dtrandomlist(0,"1,2,3,4,hello")
        print(res)


    import asyncio
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_plaza_focus_process())
    loop.run_until_complete(test_get_recommend_dtrandomlist())
