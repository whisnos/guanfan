from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.cacheoperate import CacheUserinfo

log = applog.get_log('webhandler.common_action')
dbins = DbOperate.instance()


async def visit_plus_one(vtype, itemid):
    ''' 浏览数+1, vtype = 1, 2 id 项目ID'''
    if vtype == 1:
        # 食谱
        up_recipe_sql = 'update recipe_info set visitCount = visitCount + 1 where id=? and isenable=1 and `status` in (1,0)'
        up_res = await dbins.execute(up_recipe_sql, (itemid))

    if vtype == 2:
        # 主题
        up_topic_sql = 'update topic_info set visitCount = visitCount + 1 where id=? and isenable=1 and `status` != -1'
        up_res = await dbins.execute(up_topic_sql, (itemid)) 
    else:
        return False

async def is_my_id(userid, itemid, itemtype=1):
    ''' 是否是我发布的内容, 1 动态| 2 菜谱| 3 主题 | 4 评论 '''
    if userid == 0:
        # 未登录用户
        return False
    if itemtype == 1:
        # 是否我的动态
        sql = 'select id from moments_info where id=? and userid=? limit 1'
        exists_res = await dbins.selectone(sql, (itemid, userid))
        if exists_res is None:
            return False
        else:
            return True

    if itemtype == 2:
        # 是否我的菜谱
        sql = 'select id from recipe_info where id=? and userid=? limit 1'
        exists_res = await dbins.selectone(sql, (itemid, userid))
        if exists_res is None:
            return False
        else:
            return True

    if itemtype == 3:
        # 是否我的主题
        sql = 'select id from topic_info where id=? and userid=? limit 1'
        exists_res = await dbins.selectone(sql, (itemid, userid))
        if exists_res is None:
            return False
        else:
            return True

    if itemtype == 4:
        # 是否我的评论
        sql = 'select id from reply_info where id=? and userid=? limit 1'
        exists_res = await dbins.selectone(sql, (itemid, userid))
        if exists_res is None:
            return False
        else:
            return True
    return False

async def is_collectioned(userid, itemid, itemtype):
    ''' 是否收藏 收藏类型（1：动态，2：食谱,  3:主题)'''
    if userid == 0:
        # 未登录用户
        return False
    sql = 'select id from collection_info where userid=? and itemid=? and `type`= ? and status=0 limit 1'
    exists_res = await dbins.selectone(sql, (userid, itemid, itemtype))
    if exists_res is None:
        return False
    else:
        return True

async def is_addpurcha(userid, cpid):
    ''' 是否添加到采购清单(userid 用户ID, cpid 菜谱ID)'''
    if userid == 0:
        # 未登录用户
        return False
    sql = 'select id from purchase_info where userid=? and recipeid=? and status=0 limit 1'
    exists_res = await dbins.selectone(sql, (userid, cpid))
    if exists_res is None:
        return False
    else:
        return True

async def is_liked(userid, itemid, itemtype):
    ''' 是否点赞 itemtype 1 动态'''
    if userid == 0:
        # 未登录用户
        return False
    sql = 'select id from like_info where userid=? and itemid=? and `liketype`= ? and status=0 limit 1'
    exists_res = await dbins.selectone(sql, (userid, itemid, itemtype))
    if exists_res is None:
        return False
    else:
        return True

async def is_block(myid,beblockid):
    ''' 是否拉黑,是否在我的黑名单中 '''
    sql = '''
    SELECT id from block_info where userid=? and blockuserid=? limit 1
    '''
    result = await dbins.selectone(sql, (myid, beblockid))
    if result is None:
        return False
    else:
        return True

async def get_all_blocks(myid):
    """ 
    获取所有用户黑名单列表上线1000个
    """
    sql_all ='''
    SELECT blockuserid FROM block_info WHERE userid=? limit 1000
    '''
    result = await dbins.select(sql_all, (myid))
    if result is None:
        return None
    return [i.get('blockuserid',0) for i in result]


if __name__ == '__main__':

    async def test_add_visit():
        # res = await get_subjectlist('1')
        res = await visit_plus_one(2, 1)

    async def test_is_collectioned():
        # res = await get_subjectlist('1')
        res = await is_collectioned(1, 50038, 2)
        print(res)

    async def test_is_liked():
        # res = await get_subjectlist('1')
        res = await is_liked(4, 13, 2)
        print(res)

    async def test_get_all_blocks():
        res = await get_all_blocks(2)
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_all_blocks())