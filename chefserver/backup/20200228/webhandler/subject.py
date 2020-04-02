import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo, cache_up_follow, cache_up_fans, cache_up_caipu, cache_up_dongtai
from chefserver.webhandler.myspace import get_relationship_status
from chefserver.webhandler.common_action import visit_plus_one, is_collectioned

log = applog.get_log('webhandler.subject')
dbins = DbOperate.instance()

class SubjectListHandler(BaseHandler):
    ''' 主题列表 '''
    async def post(self):
        order_type = self.verify_arg_legal(self.get_body_argument('topictype'), '主题列表类型', False, uchecklist=True, user_check_list=['1','2'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_subjectlist(order_type, int(page))
        return self.send_message(success, code, message, result)

class SubjectDetailHandler(BaseHandler):
    ''' 主题详情 '''
    async def post(self):
        topicid = self.verify_arg_legal(self.get_body_argument('topicid'), '主题ID', False, is_num=True)
        # 判断用户与自己的状态: 
        myid = 0 # 0 未关注 1 已关注 2 互相关注
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid = 0
        else:
            myid = user_session.get('id',0)
        success, code, message, result = await get_subject_detail(myid, topicid)
        if success:
            await visit_plus_one(2, topicid)
        return self.send_message(success, code, message, result)

async def get_subjectlist(order_type, pagenum=1, epage=10):
    ''' 专题列表 order_type 1 按时间新到旧排序 2 按收藏数+浏览数 高到低排序 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    if order_type == '1':
        slist_sql = '''
select topic.*,
us.userName as nickname,
us.headImg as faceimg
from
(
select
id as topicid,
userid,
title,
faceimg as topicimg,
visitCount as visits,
collectionCount as collections,
createTime as pushtime
FROM topic_info
WHERE isEnable = 1 AND `status`=1
order by updateTime desc limit ?, ?
) as topic
inner join user as us on topic.userid = us.id;
        '''
    else:
        slist_sql = '''
select topic.*,
us.userName as nickname,
us.headImg as faceimg
from
(
select
id as topicid,
userid,
title,
faceimg as topicimg,
visitCount as visits,
collectionCount as collections,
visitCount + collectionCount as hot,
createTime as pushtime
FROM topic_info
WHERE isEnable = 1 AND `status`=1
order by hot desc limit ?, ?
) as topic
inner join user as us on topic.userid = us.id;
'''
    topic_result = await dbins.select(slist_sql, (page, epage))
    if topic_result is None:
        return False, 3001, '不存在的主题或数据错误', None

    for t in topic_result:
        pt = t.get('pushtime').strftime('%Y-%m-%d %H:%M:%S')
        t.update(pushtime=pt)
    return True, 0, 'success',topic_result


async def get_subject_detail(myid,topicid):
    ''' 主题详情 '''
    # 获取主题基本信息
    topic_base_sql =  '''
select
tpi.id as topicid,
tpi.userid,
us.userName as nickname,
us.headImg as faceimg,
us.certificationstatus,
tpi.title,
tpi.introduction,
tpi.faceimg as topicimg,
tpi.mainInfoUrl as topicmainimg,
tpi.visitCount as visits,
tpi.collectionCount as collections,
tpi.createTime as pushtime
FROM topic_info as tpi
inner join user as us
on tpi.userid=us.id
WHERE tpi.isEnable = 1 AND tpi.`status`=1 and tpi.id = ?;
'''
    topic_base_result = await dbins.selectone(topic_base_sql, (topicid))
    if topic_base_result is None:
        return False, 3001, '主题数据异常,未审核或不存在等', None
    pt = topic_base_result.get('pushtime').strftime('%Y-%m-%d %H:%M:%S')
    topic_base_result.update(pushtime=pt)
    # print(topic_base_result)

    # 获取主题相关菜谱|用户等信息
    cplist = '''
select
topic_la.*,
cpinfo.faceImg as cpimg,
cpinfo.title,
cpinfo.collectionCount as cpcollections,
cpinfo.userid,
us.headImg as userfaceimg,
us.userName as nickName,
us.certificationstatus
from(
select
recipeid,
reason,
sort
from topic_recipe_relation where topicId = ? ORDER BY sort LIMIT 30
) as topic_la
inner join recipe_info as cpinfo
on cpinfo.id = topic_la.recipeid and cpinfo.`status` in (0,1) and cpinfo.isEnable=1
inner join user as us
on us.id = cpinfo.userid and us.`status` = 0
'''
    # 判断用户与主题发布人的关系
    releation = await get_relationship_status(myid, topic_base_result.get('userid', 0))
    topic_base_result.setdefault('relationship', releation)


    # 判断是否是用户自己发布的主题
    if topic_base_result.get('userid') == myid:
        topic_base_result.setdefault('ismyown', True)
    else:
        topic_base_result.setdefault('ismyown', False)

    # 判断用户是否已收藏主题
    is_collection = await is_collectioned(myid, topicid, 3)
    if is_collection:
        # 已收藏
        topic_base_result.setdefault('iscollectioned', True)
    else:
        topic_base_result.setdefault('iscollectioned', False)


    cplist_result = await dbins.select(cplist, (topicid))
    if cplist_result is None:
        return False, 30033, '获取主题相关菜谱数据错误', None

    topic_base_result.setdefault('cplist', cplist_result)


    return True, 0, 'success', topic_base_result


if __name__ == '__main__':
    async def test_subject_list():
        # res = await get_subjectlist('1')
        res = await get_subjectlist('2')

    async def test_subject_detail():
        # res = await get_subjectlist('1')
        res = await get_subject_detail(5,'10')
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_subject_detail())