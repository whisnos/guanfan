import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo, cache_up_follow, cache_up_fans, cache_up_caipu, cache_up_dongtai
from chefserver.webhandler.myspace import get_relationship_status
from chefserver.webhandler.common_action import visit_plus_one, is_liked, is_collectioned, is_addpurcha, is_my_id

log = applog.get_log('webhandler.detail')
dbins = DbOperate.instance()

class DongtaiDetailHandler(BaseHandler):
    ''' 获取动态详情 '''
    # @check_login
    async def post(self):
        did = self.verify_arg_legal(self.get_body_argument('did'), '动态ID', False, is_num=True)
        # 判断用户与自己的状态:
        relationship = 0 # 0 未关注 1 已关注 2 互相关注
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid = 0
        else:
            myid = user_session.get('id',0)
        success, code, message, result = await get_dongtai_detail(did, myid)
        return self.send_message(success, code, message, result)


class RecipeDetailHandler(BaseHandler):
    ''' 获取菜谱详情 '''
    # @check_login
    async def post(self):
        cpid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        # 判断用户与自己的状态:
        relationship = 0 # 0 未关注 1 已关注 2 互相关注
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid = 0
        else:
            myid = user_session.get('id',0)
        success, code, message, result = await recipe_detail_view(myid, cpid)
        if success:
            await visit_plus_one(1, cpid)
        return self.send_message(success, code, message, result)

class RecipeEditDetailHandler(BaseHandler):
    ''' 获取用户编辑菜谱详情 '''
    @check_login
    async def post(self):
        cpid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        # 判断用户与自己的状态:
        myid = self.get_session().get('id', 0)
        success, code, message, result = await user_recipe_edit_detail(myid, cpid)
        return self.send_message(success, code, message, result)

class RecipeShowlistHandler(BaseHandler):
    ''' 获取菜谱相关作品列表 '''
    # @check_login
    async def post(self):
        cpid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_recipe_shows_list(cpid, int(page))
        return self.send_message(success, code, message, result)


class ReplylistHandler(BaseHandler):
    ''' 评论列表 '''
    async def post(self):
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid = 0
        else:
            # 获取用户ID
            myid = user_session.get('id',0)

        itemtype = self.verify_arg_legal(self.get_body_argument('itemtype'), '评论类型', False, uchecklist=True, user_check_list=['1','2','3'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '评论id', False, isnum=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, isnum=True)

        success, code, message, result = await get_reply_list(myid, itemid, itemtype, int(page))
        return self.send_message(success, code, message, result)

async def get_reply_list(myid, itemid, itemtype, pagenum=1, epage=10):
    ''' 评论列表 itemid 项目ID, itemtype 项目类型 1 动态 2 食谱 3 主题 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    reply_list_sql = '''
SELECT
us.headImg AS faceimg,
us.userName AS nickname,
reply.id,
reply.commentid,
reply.userid,
reply.beuserid,
replyus.username AS bereplynickname,
reply.message,
reply.createtime AS pushtime
FROM(
SELECT
id
FROM reply_info
where itemid=? AND itemtype=? AND `status` = 0 AND commentid=0 ORDER BY id DESC LIMIT ?,?) AS rei
INNER JOIN reply_info AS reply
ON reply.id = rei.id OR reply.commentid = rei.id AND reply.status=0
INNER JOIN user AS us
ON us.id = reply.userid AND us.`status` = 0
LEFT JOIN user AS replyus
ON reply.beuserid = replyus.id AND replyus.`status` = 0
left join (SELECT BlockUserId FROM block_info WHERE userid=?) AS bli # 20191118 增加评论列表黑名单过滤
ON bli.BlockUserId=reply.userid
where bli.BlockUserId is null
ORDER BY reply.id DESC
'''

    # reply_list_result = await dbins.select(reply_list_sql, (itemid, itemtype, page, epage))
    reply_list_result = await dbins.select(reply_list_sql, (itemid, itemtype, page, epage, myid))
    if reply_list_result is None:
        return False, 3001, '获取评论列表错误,错误的内容', None

    result_list = list()

    for reply in reply_list_result:
        # 添加主评论
        pt = reply.get('pushtime').strftime('%Y-%m-%d %H:%M:%S')
        reply.update(pushtime=pt)

        if myid == reply.get('userid', -1):
            # 是否是自己发布的内容
            reply.setdefault('ismyid', True)
        else:
            reply.setdefault('ismyid', False)

        if reply.get('commentid') == 0:
            # 主评论
            reply.setdefault('subreplylist',[])
            result_list.append(reply)


    for mainreply in result_list:
        # 给主评论添加子评论
        for re in reply_list_result:
            if mainreply.get('id') == re.get('commentid'):
                if re.get('beuserid') == mainreply.get('userid'):
                    # 不是回复的,被回复人消息设置为0;
                    re.update(bereplynickname=None)
                mainreply.get('subreplylist').append(re)


    return True, 0, 'success', result_list


async def get_recipe_shows_list(recipeid, pagenum=1, epage=20):
    ''' 菜谱 厨艺秀 查看全部 动态列表 '''
    sucess, code, msg, show_base_list = await get_recipe_shows(recipeid, pagenum, epage)
    if sucess is False:
        return False, 1003, '没有动态数据', None

    for showdt in show_base_list:
        # 获取评论数量 和 点赞数量
        lknum = await get_count_likes_num(showdt.get('id'), 1)
        rpnum = await get_count_reply_num(showdt.get('id'), 1)
        showdt.setdefault('like_num', lknum)
        showdt.setdefault('reply_num', rpnum)
    return True, 0, 'success', show_base_list


async def get_dongtai_detail(did, myid):
    ''' 返回动态详情, did 动态id, releation, 与用户的关系'''
    # 返回动态明细
    dt_dict_result = dict()
    dt_sql = '''
select
dt.userid,
dt.description,
dt.dtype,
dt.videourl,
dt.dtimg,
dt.itemid,
dt.likecount as like_num,
dt.createtime as pushtime,
us.username as nickname,
us.headImg as faceimg,
us.certificationstatus
from
(select
id,
userId,
type as 'dtype',
momentsImgUrl as dtimg,
momentsVideoUrl as videourl,
momentsDescription as description,
itemid,
likecount,
createtime
from moments_info
where id=? and status=0) as dt
inner join `user` as us on us.id = dt.userid;
    '''

    dt_detail_res = await dbins.selectone(dt_sql, (did))
    if dt_detail_res is None:
        return False, 3011, '动态不存在或已删除', None
    ptime = dt_detail_res.get('pushtime')
    dt_detail_res.update(pushtime=ptime.strftime('%Y-%m-%d %H:%M:%S'))

    # 获取是与动态用户之间的关系
    releation = await get_relationship_status(myid, dt_detail_res.get('userId'))
    dt_detail_res.setdefault('relationship', releation)

    # 是否是自己发布的动态
    if dt_detail_res.get('userId') == myid:
        dt_detail_res.setdefault('ismyown', True)
    else:
        dt_detail_res.setdefault('ismyown', False)

    # 是否是已点赞
    lk = await is_liked(myid, did, 1)
    if lk:
        dt_detail_res.setdefault('isliked', True)
    else:
        dt_detail_res.setdefault('isliked', False)

    # 获取关联项目
    dtype = dt_detail_res.get('dtype', 0)
    if dtype == 0:
        # 没有关联项目
        dt_detail_res.setdefault('relation_item', None)
    elif dtype == 1 or dtype == 3:
        # 关联菜谱(菜谱 和 作品 相关的动态都是 菜谱)
        cp_sql = '''
select
id,
title, 
faceimg as cpimg, 
ingredientsList as stuff
from recipe_info
where id=?
and isEnable=1 and status!=-1 and status!=2 limit 1
'''
        cp_res = await dbins.selectone(cp_sql, (dt_detail_res.get('itemid')))
        if cp_res is not None:
            dt_detail_res.setdefault('relation_item', cp_res)
        else:
            dt_detail_res.setdefault('relation_item', None)
    elif dtype == 2:
        # 关联作品,目前暂时不关联
        dt_detail_res.setdefault('relation_item', None)
    else:
        # 未知的类型
        dt_detail_res.setdefault('relation_item', None)

    # # 获取动态点赞数量
    # like_count_sql='''
    # select count(id) as like_num from like_info where itemid=? and likeType=1
    # '''
    # lk_num_res = await dbins.selectone(like_count_sql, (did))
    # if lk_num_res is None:
    #     dt_detail_res.setdefault('like_num', 0)
    # dt_detail_res.setdefault('like_num', lk_num_res.get('like_num', 0))

    # if lk_num_res.get('like_num', 0) == 0:
    #     dt_detail_res.setdefault('like_people_list', [])
    #     return True, 0, 'success', dt_detail_res

    # 获取点赞人头像
    like_people_sql='''
select us.id as userid, us.headImg as faceimg, lkuser.id as sortid
from
(select id,userid from like_info where itemid=? and likeType=1 and status=0 order by id desc limit 8) as lkuser
INNER JOIN `user` as us on lkuser.userid = us.id and us.`status` = 0
order by sortid desc
    '''
    lk_people_res = await dbins.select(like_people_sql, (did))
    # print(lk_people_res)

    # like_count_sql = '''
    # select count(id) as cnum from like_info where itemid=? and likeType=1 and status=0 limit 1
    # '''
    # lk_count_res = await dbins.selectone(like_count_sql, (did))

    # if lk_people_res is None or lk_count_res is None:
    #     dt_detail_res.setdefault('like_num', 0)
    #     dt_detail_res.setdefault('like_people_list', [])
    if lk_people_res is None:
        dt_detail_res.setdefault('like_people_list', [])

    dt_detail_res.setdefault('like_people_list', lk_people_res)
    return True, 0, 'success', dt_detail_res


async def user_recipe_edit_detail(myid, recipeid):
    ''' 显示用户的菜谱编辑详情, 需要显示菜谱状态.'''
    user_own_recipe_result = await get_recipe_detail(myid, recipeid, detail_type=2)
    if user_own_recipe_result is False:
        return False, 3012, '错误的菜谱或用户', None
    return True, 0, 'success', user_own_recipe_result


async def recipe_detail_view(myid, recipeid):
    ''' 菜谱详情 '''
    # 获取菜谱+步骤详情
    # 获取菜谱发布用户相关信息
    my_exist = await is_my_id(myid, recipeid, itemtype=2)
    print(my_exist, myid, recipeid)
    if my_exist:
        # 自己的
        recipe_res = await get_recipe_detail(myid, recipeid, detail_type=2)
    else:
        recipe_res = await get_recipe_detail(myid, recipeid, detail_type=1)

    if recipe_res is False:
        return False, 3013, '错误的菜谱或用户', None

    # 获取与用户关系 relationship
    relation = await get_relationship_status(myid, recipe_res.get('userid',0))
    recipe_res.setdefault('relationship', relation)

    # 判断是否是用户自己发布的菜谱
    if recipe_res.get('userid') == myid:
        recipe_res.setdefault('ismyown', True)
    else:
        recipe_res.setdefault('ismyown', False)

    # 判断用户是否已收藏
    is_collection = await is_collectioned(myid, recipeid, 2)
    if is_collection:
        # 已收藏
        recipe_res.setdefault('iscollectioned', True)
    else:
        recipe_res.setdefault('iscollectioned', False)

    # 判断是否添加到采购
    is_purchaexists = await is_addpurcha(myid, recipeid)
    if is_purchaexists:
        # 已添加
        recipe_res.setdefault('ispurcha', True)
    else:
        recipe_res.setdefault('ispurcha', False)

    # 获取厨艺秀列表
    success, code, msg, result = await get_recipe_shows(recipeid, 1, 3)
    if success is False:
        recipe_res.setdefault('shows', [])
    recipe_res.setdefault('shows', result)
    return True, 0, 'success', recipe_res

async def get_recipe_shows(recipeid, pagenum=1, epage=20):
    ''' 获取菜谱的作品秀(目前改成动态列表) '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

#     recipe_works_sql ='''
# select
# us.userName as nickname,
# us.headImg as faceimg,
# mmi.*
# from
# (select
# id,
# userid,
# momentsImgUrl as dtimg,
# momentsVideoUrl as videourl,
# momentsDescription as description,
# updateTime as pushtime
# from moments_info
# where itemid=? and `status`=0 and type=1) as mmi
# inner join user as us on us.id = mmi.userid and us.status=0
# ORDER BY id desc
# limit ?, ?;
#     '''
    # recipe_works_result = await dbins.select(recipe_works_sql, (recipeid, page, epage))
    # 去掉用户自己发的动态秀
    recipe_works_sql = '''
select
us.userName as nickname,
us.headImg as faceimg,
mmi.*
from
(select
id,
userid,
momentsImgUrl as dtimg,
momentsVideoUrl as videourl,
momentsDescription as description,
updateTime as pushtime
from moments_info
where itemid= ? and `status`=0 and type=1) as mmi
inner join 
(
select userid from recipe_info WHERE id = ?
) as reci
on mmi.userid!=reci.userid
inner join user as us
on us.id = mmi.userid and us.status=0
ORDER BY id desc
limit ?, ?;
    '''
    recipe_works_result = await dbins.select(recipe_works_sql, (recipeid, recipeid, page, epage))

    if recipe_works_result is None:
        return False, 1001, '该菜谱没有动态数据', None

    for show in recipe_works_result:
        pt = show.get('pushtime').strftime('%Y-%m-%d %H:%M:%S')
        show.update(pushtime=pt)
    return True, 0, 'success', recipe_works_result


async def get_recipe_detail(userid, recipeid, detail_type=1):
    ''' 获取菜谱详情, userid 用户ID, recipeid 菜谱ID, detail_type=1 看别人的, !=1 看自己的'''

    # 默认,不需要返回菜谱状态,但需要过滤有效的
    cut_sql = ' and `status` !=2 and `status`!=-1 and isenable=1', ''

    if detail_type !=1 and userid!=0:
        # 查看自己的菜谱,需要返回菜谱状态,但不过滤失效的
        cut_sql = 'and `status`!=-1', 'and us.id={}'.format(userid)

    recipe_detail_sql = '''
select
us.username as nickname,
us.headImg as faceimg,
us.certificationstatus,
recipe.*
from
(
select
userid,
title,
faceimg as cpimg,
story,
tagClass,
tagKey,
difficult,
timeConsuming as spendtime,
ingredientsList as stuff,
tips as tip,
collectionCount as collections,
visitCount as visits,
isfeatured,
updateTime as pushtime,
isExclusive as ispushweb,
isenable
from
recipe_info 
where  `status`!=-1 and id=? {}
limit 1) as recipe
inner join `user` as us on us.id = recipe.userid {} and us.status=0 ;
    '''.format(*cut_sql)

    # print(recipe_detail_sql)

    recipe_result = await dbins.selectone(recipe_detail_sql, (recipeid))
    if recipe_result is None:
        # 没有找到数据
        return False

    ptime = recipe_result.get('pushtime').strftime('%Y-%m-%d %H:%M:%S')
    recipe_result.update(pushtime=ptime)

    # 获取菜谱步骤
    recipe_step_sql ='''
    select id as stid,stepImg,description,sort from recipe_step_info where recipeId=? order by sort;
    '''
    # print(recipe_step_sql)
    recipe_step_result = await dbins.select(recipe_step_sql, (recipeid))
    if recipe_step_result is None:
        recipe_result.setdefault('step',[])
        return recipe_result

    if len(recipe_step_result)==0:
        recipe_result.setdefault('step',[])
        return recipe_result

    recipe_result.setdefault('step', recipe_step_result)
    return recipe_result

async def get_count_likes_num(itemid, item_type=1):
    ''' 获取 动态|评论 的点赞数量, itemid 动态或评论ID item_type=1 动态类型, item_type=2 评论类型'''
    like_count_sql='''
    select count(id) as like_num from like_info where itemid=? and likeType=? and status=0
    '''
    lk_num_res = await dbins.selectone(like_count_sql, (itemid, item_type))
    if lk_num_res is None:
        return 0
    return lk_num_res.get('like_num',0)


async def get_count_reply_num(itemid, item_type=1):
    ''' 获取 动态|菜谱|主题 的 评论数量 itemid 类型ID, item_type 1 动态 2 菜谱 3 主题'''
    collection_count_sql='''
    select count(id) as reply_num from reply_info where itemid=? and itemType=? and status=0
    '''
    reply_num_res = await dbins.selectone(collection_count_sql, (itemid, item_type))
    if reply_num_res is None:
        return 0
    return reply_num_res.get('reply_num',0)


if __name__ == '__main__':
    async def test_recipe_detail():
        ''' 测试或菜谱基本内容 '''
        res = await get_recipe_detail(0, 48836)
        print(res)

    async def test_recipe_shows():
        ''' 测试菜谱作品 '''
        res = await get_recipe_shows(50036,2,3)
        print(res)

    async def test_recipe_view():
        ''' 测试菜谱详情 '''
        # res = await recipe_detail_view(0, 50036)
        # print(res)
        res = await recipe_detail_view(1, 50055)
        print(res)

    async def test_recipe_edit_detail():
        ''' 测试菜谱详情 '''
        # res = await recipe_detail_view(0, 50036)
        # print(res)
        res = await user_recipe_edit_detail(1, 50055)
        print(res)

    async def test_likes_num():
        ''' 测试 点赞数量数量 '''
        # res = await recipe_detail_view(0, 50036)
        # print(res)
        res = await get_count_likes_num(3,1)
        print(res)
        res = await get_count_likes_num(1,2)
        print(res)
        res = await get_count_reply_num(13,1)
        print(res)

    async def test_get_recipe_shows_list():
        res = await get_recipe_shows_list(50036)
        print(res)

    async def test_get_reply_list():
        res = await get_reply_list(1,45,1,1,10)
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_recipe_view())