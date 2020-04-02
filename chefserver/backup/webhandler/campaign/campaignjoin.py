"""
# 活动模块
# 参加活动,参与列表

"""
import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.common_action import is_my_id
from chefserver.tool.tooltime import curDatetimeObj, curDatetime, curDate


log = applog.get_log('webhandler.campaign')
dbins = DbOperate.instance()


class CampaignJoinPKHandler(BaseHandler):
    ''' 活动PK参与 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        pkside = self.verify_arg_legal(self.get_body_argument('pkside'), 'pk站边', False, is_num=True, uchecklist=True, user_check_list= ['0','1'])
        success, code, message, result = await campaign_join_pk(myid, campaignid, int(pkside))
        return self.send_message(success, code, message, result)


class CampaignRecipeListAllHandler(BaseHandler):
    ''' 活动参与菜谱列表 '''
    async def post(self):
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            relationship = 0
            myid=0
        else:
            # 获取关注状态
            myid = user_session.get('id',0)
        campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        ctype = self.verify_arg_legal(self.get_body_argument('ctype'), '最热或最新', False, is_num=True, uchecklist=True, user_check_list= ['1','2'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_campaign_recipe_list(myid, campaignid, int(ctype), int(page))
        return self.send_message(success, code, message, result)


class CampaignMomentListAllHandler(BaseHandler):
    ''' 活动参与动态列表 '''
    async def post(self):
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            relationship = 0
            myid=0
        else:
            # 获取关注状态
            myid = user_session.get('id',0)

        campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        ctype = self.verify_arg_legal(self.get_body_argument('ctype'), '最热或最新', False, is_num=True, uchecklist=True, user_check_list= ['1','2'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_campaign_moment_list(myid, campaignid, int(ctype), int(page))
        return self.send_message(success, code, message, result)

class CampaignOpenPrizeHandler(BaseHandler):
    ''' 活动开奖 '''
    async def post(self):
        campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        success, code, message, result = await campaign_openprize(campaignid)
        return self.send_message(success, code, message, result)

async def campaign_openprize(campaignid):
    '''
    开奖结果
    '''
    campaign_status = await check_campaign_real(campaignid)
    if campaign_status == None:
        return False, 1665, '错误的活动内容,请核对后重试', None
    elif campaign_status == 0:
        return False, 1668, '活动尚未开始！', None
    elif campaign_status == 1:
        return False, 1668, '活动进行中！', None
    else:
        '''
        活动状态
        '''
        sql = '''
        SELECT id, imgurl, imgstyle, navtype, navid, extra
        FROM campaign_content WHERE campaignid=? and type=2
        '''
        result = await dbins.select(sql, (campaignid))
        if result is None:
            # 今天未投票
            return False, 3256, '获取开奖信息错误,请重试', None
        else:
            # 今天已投票
            return True, 0, "ok", result


async def get_campaign_moment_list(myid, campaignid, ctype, pagenum, epage=15):
    """ 
    获取活动动态列表
    campaignid 活动ID, ctype 1 最新， 2 最热
    pagenum 页数, epage=15 每页个数
    """
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    if ctype == 2:
        sql = '''

        SELECT
            moment.id,
            moment.momentsDescription AS description,
            moment.momentsImgUrl AS dtimg,
            moment.momentsVideoUrl AS videourl,
            moment.isvideo,
            moment.likecount,
            CASE WHEN ISNULL(lk.itemid) THEN false ELSE true END as isliked,
            us.id AS userid,
            us.headImg AS faceimg,
            us.userName AS nickname,
            camj.createtime as pushtime
        FROM
            ( SELECT userid, joinid, createtime FROM campaign_join WHERE campaignid = ? AND jointype = 1 ) AS camj
            INNER JOIN moments_info AS moment ON camj.joinid = moment.id 
            AND moment.`status` = 0
            INNER JOIN user AS us ON us.id = moment.userid AND us.`status` = 0
            LEFT JOIN like_info as lk ON lk.itemid=camj.joinid AND lk.userid=? AND lk.likeType=1 AND lk.`status` = 0
        ORDER BY likecount DESC, id DESC LIMIT ?, ?
        '''
    else:
        sql = '''
        SELECT
            moment.id,
            moment.momentsDescription AS description,
            moment.momentsImgUrl AS dtimg,
            moment.momentsVideoUrl AS videourl,
            moment.isvideo,
            moment.likecount,
            CASE WHEN ISNULL(lk.itemid) THEN false ELSE true END as isliked,
            us.id AS userid,
            us.headImg AS faceimg,
            us.userName AS nickname,
            camj.createtime as pushtime
        FROM
            ( SELECT userid, joinid, createtime FROM campaign_join WHERE campaignid = ? AND jointype = 1 ) AS camj
            INNER JOIN moments_info AS moment ON camj.joinid = moment.id 
            AND moment.`status` = 0
            INNER JOIN user AS us ON us.id = moment.userid AND us.`status` = 0
            LEFT JOIN like_info as lk ON lk.itemid=camj.joinid AND lk.userid=? AND lk.likeType=1 AND lk.`status` = 0

        ORDER BY id DESC LIMIT ?, ?
        '''
    result = await dbins.select(sql, (campaignid, myid, page, epage))
    if result is None:
        return False, 3202, '获取数据错误', None
    for b in result:
        pt = b.get('pushtime')
        b['pushtime'] = str(pt)
    return True, 0, 'success', result


async def get_campaign_recipe_list(myid,campaignid, ctype, pagenum, epage=15):
    """ 
    获取活动菜谱列表
    campaignid 活动ID, ctype 1 最新， 2 最热
    pagenum 页数, epage=15 每页个数
    """
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    if ctype == 2:
        sql = '''
        SELECT
            reci.id AS cpid,
            reci.title AS cptitle,
            reci.faceImg AS cpimg,
            reci.collectionCount AS collections,
            CASE WHEN ISNULL(coll.itemid) THEN false ELSE true END as iscollectioned,
            us.id AS userid,
            us.headImg AS faceimg,
            us.userName AS nickname,
            camj.createtime as pushtime
        FROM
            ( SELECT userid, joinid, createtime FROM campaign_join WHERE campaignid = ? AND jointype = 2 ) AS camj
            INNER JOIN recipe_info AS reci ON camj.joinid = reci.id 
            AND reci.`status` = 1 
            AND reci.isenable = 1
            INNER JOIN user AS us ON us.id = reci.userid 
            AND us.`status` = 0
            LEFT JOIN collection_info AS coll ON coll.itemId = camj.joinid and coll.type=2 AND coll.status=0 AND coll.userid=?
        ORDER BY collections DESC, cpid DESC LIMIT ?, ?
        '''
    else:
        sql = '''
        SELECT
            reci.id AS cpid,
            reci.title AS cptitle,
            reci.faceImg AS cpimg,
            reci.collectionCount AS collections,
            CASE WHEN ISNULL(coll.itemid) THEN false ELSE true END as iscollectioned,
            us.id AS userid,
            us.headImg AS faceimg,
            us.userName AS nickname,
            camj.createtime as pushtime
        FROM
            ( SELECT userid, joinid, createtime FROM campaign_join WHERE campaignid = ? AND jointype = 2 ) AS camj
            INNER JOIN recipe_info AS reci ON camj.joinid = reci.id 
            AND reci.`status` = 1 
            AND reci.isenable = 1
            INNER JOIN user AS us ON us.id = reci.userid 
            AND us.`status` = 0
            LEFT JOIN collection_info AS coll ON coll.itemId = camj.joinid and coll.type=2 AND coll.status=0 AND coll.userid=?
        ORDER BY cpid DESC LIMIT ?, ?
        '''
    result = await dbins.select(sql, (campaignid, myid, page, epage))
    if result is None:
        return False, 3202, '获取数据错误', None
    for b in result:
        pt = b.get('pushtime')
        b['pushtime'] = str(pt)
    return True, 0, 'success', result

async def is_join_pk_today(myid, campaignid, jointype=4):
    ''' 今天是否参与PK '''
    sql = '''
    SELECT id FROM campaign_join WHERE campaignid=? and jointype=4 AND userid=? AND createtime >= ? LIMIT 1
    '''
    result = await dbins.selectone(sql, (campaignid, myid, curDate()))
    if result is None:
        # 今天未投票
        return False
    else:
        # 今天已投票
        return True

async def add_pk_value(campaignid, pkside):
    ''' 增加PK方票数, campaignid 活动ID, pkside 活动选边 1 pkpositivevisit, 0 pknegativevisit'''
    if pkside == 1:
        sql = 'UPDATE campaign_info SET pkpositivevisit = pkpositivevisit + 1 WHERE id=?'
    else:
        sql = 'UPDATE campaign_info SET pknegativevisit = pknegativevisit + 1 WHERE id=?'
    result = await dbins.execute(sql,(campaignid))


async def campaign_join_pk(myid, campaignid, pkisde):
    '''
    用户参与PK选边，myid 用户ID, campaignid 活动ID, pkisde PK选边。 1 正方 0 反方
    '''
    today_is_pk = await is_join_pk_today(myid, campaignid)
    if today_is_pk is True:
        # 已投票参加过PK
        return False, 1033, '您今天已投票,谢谢参与!', None
    success, code, msg, resutl = await campaign_join(myid, campaignid, 4, pkisde)
    if success is True:
        # 投票成功, 增加一票
        await add_pk_value(campaignid, pkisde)
    return success, code, msg, resutl


async def check_campaign_real(campaignid):
    ''' 检测活动ID是否存在,不存在返回None,存在返回当前状态 '''
    real_id_sql ='''
    SELECT id, starttime, endtime FROM campaign_info WHERE id=? AND status = 1 LIMIT 1
    '''
    result = await dbins.selectone(real_id_sql, (campaignid))

    if result is None:
        return None
    else:
        status = -1
        now = curDatetimeObj()
        if now > result.get('endtime'):
            # 已结束
            status = 2
        elif now <= result.get('starttime'):
            # 未开始
            status = 0
        else:
            # 进行中
            status = 1
        return status

async def campaign_join(myid, campaignid, jointype, joinid):
    ''' 参加活动
    myid 用户ID, campaignid 主题ID, 
    jointype 参与类型(动态 主题 菜谱 等), 
    joinid 参与ID(动态 主题 菜谱 等)
    '''
    exists_id_status = await check_campaign_real(campaignid)
    if exists_id_status == None:
        return False, 1662, '错误的活动内容,请核对后重试', None
    elif exists_id_status == 0:
        return False, 1668, '活动尚未开始, 谢谢参与！', None
    elif exists_id_status == 2:
        return False, 1669, '活动已结束, 谢谢参与！', None
    elif exists_id_status != 1:
        return False, 1667, '未知活动状态,请核对后重试！', None

    join_sql = '''
    INSERT INTO campaign_join ( `campaignid`, `userid`, `jointype`, `joinid`,`createtime` )
    VALUES
        ( ?, ?, ?, ?, ? )
    '''
    add_like_res = await dbins.execute(join_sql, (campaignid, myid, jointype, joinid, curDatetime()))
    if add_like_res is None:
        return False, 3668, '活动参加失败,请重试', None
    return True, 0, '活动参与成功', None

async def recipe_campaign_join(myid, campaignid, joinid):
    ''' 菜谱参加活动 '''
    return await campaign_join(myid, campaignid, 2, joinid)

async def moment_campaign_join(myid, campaignid, joinid):
    ''' 动态参加活动 '''
    return await campaign_join(myid, campaignid, 1, joinid)


if __name__ == '__main__':
    import asyncio
    async def test_campaign_join():
    # myid, campaignid, jointype, joinid
        res = await campaign_join("1","15","2","50012")
        print(res)

    async def test_check_campaign_real():
        res = await check_campaign_real(15)
        print(res)

    async def test_campaign_join_pk():
        res = await campaign_join_pk(9,15,1)
        print(res)

    async def test_is_join_pk_today():
        res = await is_join_pk_today(1,15)
        print(res)

    async def test_add_campaign_vists():
        res = await add_campaign_vists(15)
        print(res)

    async def test_get_campaign_recipe_list():
        res = await get_campaign_recipe_list(15, 2, 1)
        print(res)

    async def test_get_campaign_moment_list():
        res = await get_campaign_moment_list(1,15, 2, 1)
        print(res)

    async def test_campaign_openprize():
        res = await campaign_openprize(15)
        print(res)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_campaign_moment_list())

