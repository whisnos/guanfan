import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo,CachePapeHotDongtai
from chefserver.webhandler.common_action import get_all_blocks

log = applog.get_log('webhandler.dongtaiplaza')
dbins = DbOperate.instance()

class DtPlazaHandler(BaseHandler):
    ''' 动态广场！ 最新，推荐列表 '''
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
                # print(cache)
                if userblock is not None:
                    self.send_message(True, 0, "success", [i for i in cache if i.get('userid') not in userblock])
                return self.send_message(True, 0, "success", cache)
            else:
                # 返回缓存失败,写日志执行sql返回
                log.warning('获取动态热门缓存失败,类型:{}, 页面:{}'.format(plazatype,page))

        success, code, message, result = await dongtai_plaza_list(int(plazatype), int(page))
        if success:
            # 没有命中缓存,更新缓存
            await hotdtpage.set(argkey, result)
            if userblock is not None:
                # 黑名单过滤
                self.send_message(True, 0, "success", [i for i in result if i.get('userid') not in userblock])

        return self.send_message(success, code, message, result)


class DtPlazafocusHandler(BaseHandler):
    ''' 个人关注的好友的最新动态 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await focus_plaza_list(userid, int(page))
        return self.send_message(success, code, message, result)

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
mmi.momentsVideoUrl as dtvideo,
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
momentsVideoUrl as dtvideo,
createTime as pushtime,
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
(CASE when (reply.replynum IS NULL) then 0 else reply.replynum end) + mmi.likecount as total
from
(
select id,userid,momentsDescription,momentsImgUrl,likecount from moments_info where likecount>0 and status=0 
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
reply.replynum + mmi.likecount as total
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


    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_focus_plaza_list())