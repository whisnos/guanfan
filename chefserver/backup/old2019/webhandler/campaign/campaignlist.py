"""
# 活动模块
# 活动列表

"""
import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.common_action import is_my_id
from chefserver.tool.tooltime import curDatetimeObj


log = applog.get_log('webhandler.campaign')
dbins = DbOperate.instance()

class CampaignListHandler(BaseHandler):
    ''' 活动入口 '''
    async def post(self):
        # myid = self.get_session().get('id', 0)
        success, code, message, result = await get_campaign_list()
        return self.send_message(success, code, message, result)

class CampaignListAllHandler(BaseHandler):
    ''' 活动列表 '''
    async def post(self):
        # myid = self.get_session().get('id', 0)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_campaign_list_all(int(page))
        return self.send_message(success, code, message, result)


class CampaignDetailHandler(BaseHandler):
    ''' 活动详情 '''
    async def post(self):
        campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        success, code, message, result = await detail_campaign(campaignid)
        if success:
            await add_campaign_vists(campaignid)
        return self.send_message(success, code, message, result)


class CampaignSponsorDetailHandler(BaseHandler):
    ''' 赞助商信息 '''
    async def post(self):
        sponsorid = self.verify_arg_legal(self.get_body_argument('sponsorid'), '活动ID', False, is_num=True)
        success, code, message, result = await campaign_sponsor_info(sponsorid)
        return self.send_message(success, code, message, result)


async def campaign_sponsor_info(sponsorid):
    ''' 获取赞助商(用户)信息 '''
    get_sponsor_sql = '''
    SELECT username AS nickname, headimg AS imgurl, personalprofile, certificationstatus
    FROM user
    WHERE id = ? AND status=0 LIMIT 1
    '''
    sponsor_result = await dbins.selectone(get_sponsor_sql, (sponsorid))
    if sponsor_result is None:
        return False, 1008, '错误的赞助商信息或者其它,请重试!', None
    return True, 0, 'success', sponsor_result

async def add_campaign_vists(campaignid):
    ''' 统计访问量 '''
    sql = 'UPDATE campaign_info SET visitcount = visitcount + 1 WHERE id=? and status=1'
    await dbins.execute(sql,(campaignid))


async def detail_campaign(campaignid):
    ''' 获取活动详情 '''
    campaign_base_sql ='''
SELECT
    name,
    keyname,
    sponsorid,
    mainimg,
    joinimg,
    openimg,
    type,
    ispk,
    pkpositive,
    pkpositivevisit,
    pknegative,
    pknegativevisit,
    visitcount,
    sort,
    starttime,
    endtime,
    createtime as pushtime
FROM
    campaign_info 
WHERE
    id = ?
    AND status=1;
'''
    campaign_base_result = await dbins.selectone(campaign_base_sql, (campaignid))
    if campaign_base_result is None:
        return False, 3008, '活动数据错误,请重试', None
    
    now = curDatetimeObj()
    if now > campaign_base_result.get('endtime'):
        # 已结束
        campaign_base_result.setdefault('status', 2)
    elif now <= campaign_base_result.get('starttime'):
        # 未开始
        campaign_base_result.setdefault('status', 0)
    else:
        # 进行中
        campaign_base_result.setdefault('status', 1)

    ct = campaign_base_result.get('pushtime')
    campaign_base_result['pushtime'] = str(ct)

    st = campaign_base_result.get('starttime')
    campaign_base_result['starttime'] = str(st)

    et = campaign_base_result.get('endtime')
    campaign_base_result['endtime'] = str(et)

    content_list = await get_campaign_content_list(campaignid)

    campaign_base_result.setdefault('content', content_list)
    
    return True, 0, 'success', campaign_base_result


async def get_campaign_content_list(campaignid):
    '''
    获取活动内容图片相关信息
    '''
    sql = '''
    SELECT id, imgurl, imgstyle, navtype, navid, extra
     FROM campaign_content WHERE campaignid=? and type=1
    '''
    result = await dbins.select(sql, (campaignid))
    return result

async def get_campaign_list_all(pagenum, epage=15):
    """ 
    获取活动列表
    """
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql = '''
SELECT
    id,
    name,
    keyname,
    sponsorid,
    mainimg,
    joinimg,
    openimg,
    type,
    ispk,
    pkpositive,
    pkpositivevisit,
    pknegative,
    pknegativevisit,
    visitcount,
    sort,
    starttime,
    endtime,
    createtime as pushtime
FROM
    campaign_info 
WHERE
    status = 1
ORDER BY createtime desc LIMIT ?,?
    '''
    result = await dbins.select(sql, (page, epage))
    if result is None:
        return False, 3002, '获取数据错误', None

    now = curDatetimeObj()
    for b in result:
        if now > b.get('endtime'):
            # 已结束
            b.setdefault('status', 2)
        elif now <= b.get('starttime'):
            # 未开始
            b.setdefault('status', 0)
        else:
            # 进行中
            b.setdefault('status', 1)

        st = b.get('starttime')
        b['starttime'] = str(st)

        et = b.get('endtime')
        b['endtime'] = str(et)

        pt = b.get('pushtime')
        b['pushtime'] = str(pt)
    return True, 0, 'success', result

async def get_campaign_list():
    """ 
    获取活动入口内容
    """
    sql = '''
SELECT
    id,
    NAME,
    keyname,
    sponsorid,
    mainimg,
    joinimg,
    openimg,
    type,
    ispk,
    pkpositive,
    pkpositivevisit,
    pknegative,
    pknegativevisit,
    visitcount,
    sort,
    starttime,
    endtime,
    createtime AS pushtime 
FROM
    campaign_info 
WHERE
    STATUS = 1 
ORDER BY
    sort DESC 
    LIMIT 10
    '''
    result = await dbins.select(sql, ())
    if result is None:
        return False, 3002, '获取数据错误', None

    now = curDatetimeObj()
    for b in result:
        if now > b.get('endtime'):
            # 已结束
            b.setdefault('status', 2)
        elif now <= b.get('starttime'):
            # 未开始
            b.setdefault('status', 0)
        else:
            # 进行中
            b.setdefault('status', 1)

        st = b.get('starttime')
        b['starttime'] = str(st)

        et = b.get('endtime')
        b['endtime'] = str(et)

        pt = b.get('pushtime')
        b['pushtime'] = str(pt)
    return True, 0, 'success', result


if __name__ == '__main__':
    import asyncio
    async def test_get_campaign_list():
        res = await get_campaign_list()
        print(res)


    async def test_detail_campaign():
        res = await detail_campaign(15)
        print(res)

    async def test_get_campaign_list_all():
        res = await get_campaign_list_all(1)
        print(res)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_campaign_list())


