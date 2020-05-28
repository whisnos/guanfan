from playhouse.shortcuts import model_to_dict

from chefserver.models.point import User
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.tooltime import curDatetime
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
import tornado.web

from chefserver.webhandler.cacheoperate import CacheUserPointinfo, CacheUserinfo
from chefserver.webhandler.myspace import get_relationship_status

log = applog.get_log('webhandler.index')
dbins = DbOperate.instance()

class IndexBannerHandler(BaseHandler):
    ''' 首页海报 '''
    async def post(self):
        # myid = 0
        # user_session = await self.get_login()
        # if user_session is False:
        #     # 未登录
        #     myid = 0
        # else:
        #     myid = user_session.get('id',0)
        channel = self.verify_arg_legal(self.get_body_argument('channel'), '频道名称', False, uchecklist=True, user_check_list=['0','1'])
        # 0 app, 1 PC
        success, code, message, result = await banner_list(channel)
        return self.send_message(success, code, message, result)


class IndexRecomTopicHandler(BaseHandler):
    ''' 首页推荐主题 '''
    async def post(self):
        success, code, message, result = await recommend_topic_list()
        return self.send_message(success, code, message, result)


class IndexRecomRecipeHandler(BaseHandler):
    ''' 首页推荐食谱 '''
    async def post(self):
        success, code, message, result = await recommend_recipe_list()
        return self.send_message(success, code, message, result)


class IndexFeaturedRecipeHandler(BaseHandler):
    ''' 首页精选食谱 '''
    async def post(self):
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await futured_recipe_list(int(page))
        return self.send_message(success, code, message, result)

class IndexClassInfoAllHandler(BaseHandler):
    ''' 返回所有分类 '''
    async def post(self):
        success, code, message, result = await get_all_classinfo()
        return self.send_message(success, code, message, result)


class IndexChannelInfoAllHandler(BaseHandler):
    ''' 首页海报 '''
    async def post(self):
        success, code, message, result = await channel_list()
        return self.send_message(success, code, message, result)

async def get_all_classinfo():
    ''' 获取所有分类 '''
    classinfo_sql = '''
select id,classname,type,iconimg,pid,sort
from class_info
order by sort desc
'''
    classinfo_result = await dbins.select(classinfo_sql, ())
    if classinfo_result is None:
        return False, 3001, '获取评论列表错误,错误的内容', None

    # print(classinfo_result[:5])
    
    result_tp01 = []

    for info1 in classinfo_result:
        # 一级分类
        if info1.get('type') == 1:
            # print(info1)
            info_1_tmp = dict()
            info_1_tmp = info1.copy()
            info_1_tmp.setdefault('childlist',[])
            result_tp01.append(info_1_tmp)

    result_tp02 = []
    for info2 in classinfo_result:
        # 二级分类
        if info2.get('type') == 2:
            info_2_tmp = dict()
            info_2_tmp = info2.copy()
            info_2_tmp.setdefault('childlist',[])
            # info2.setdefault('childlist', [])
            result_tp02.append(info_2_tmp)


    for info3 in classinfo_result:
        # 三级分类,添加到2级分类子目录
        if info3.get('type') == 3:
            for rtp2 in result_tp02:
                if rtp2.get('id') == info3.get('pid'):
                    # info_3_tmp = dict()
                    # info_3_tmp = info3.copy()
                    rtp2.get('childlist').append(info3)

    for crtp2 in result_tp02:
        # 二级分类添加到根目录
            for rtp1 in result_tp01:
                if rtp1.get('id') == crtp2.get('pid'):
                    rtp1.get('childlist').append(crtp2)
    return True, 0, 'success', result_tp01


async def futured_recipe_list(pagenum, epage=10):
    ''' 获取被标记为精选的菜谱 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    futured_list_sql ='''
    SELECT
reci.id as cpid,
reci.title as cptitle,
reci.faceImg as cpimg,
reci.collectionCount as collections,
us.id as userid,
us.headImg as faceimg,
us.userName as nickname
from recipe_info as reci
inner join user as us
on us.id = reci.userid and us.`status` = 0 and reci.`status` != -1 and reci.`status` !=2 and reci.isFeatured = 1 and reci.isenable=1
order by reci.updatetime desc, reci.id desc
limit ?,?
'''
    result = await dbins.select(futured_list_sql, (page, epage))
    if result is None:
        return False, 3003, '获取主题推荐异常,请重试', None
    else:
        return True, 0, 'success', result

async def recommend_recipe_list():
    ''' 首页推荐精选分类下的食谱 '''
    recommend_recipe_sql = '''
SELECT
recipe_cate.*,
rom_recipe.sort as cpsort,
reci.id as cpid,
reci.title as cptitle,
reci.faceImg as cpimg,
reci.collectionCount as collections,
us.id as userid,
us.headImg as faceimg,
us.userName as nickname
from
(
select id, title as catename, sort from recommend_recipe_category where `status` = 1
) as recipe_cate
inner join recommend_recipe as rom_recipe
on recipe_cate.id = rom_recipe.categoryid and rom_recipe.`status` = 0
inner join recipe_info as reci
on rom_recipe.recipeid = reci.id and reci.`status` != -1 and reci.`status` !=2
inner join user as us
on us.id = reci.userid and us.`status` = 0
    '''
    result = await dbins.select(recommend_recipe_sql, ())
    if result is None:
        return False, 3003, '获取主题推荐异常,请重试', None

    # 设置主分类:
    result_list = []
    temp_dict = {}
    for res in result:
        # 添加精选分类主键
        if temp_dict.get(res.get('id'),False) is False:
            temp_dict.setdefault(res.get('id'),True)
            result_list.append({"id":res.get('id'), "name":res.get('catename'), "sort": res.get('sort')})

    # result_list = sorted(result_list,key = lambda s:s['sort']) 
    # result_list
    def numsort(k):
        # 用于排序
        return k.get('sort', 0)

    def cpnumsort(k):
        # 用于菜谱排序
        return k.get('cpsort', 0)

    result_list = sorted(result_list, key=numsort, reverse=True)
    for k in result_list:
        # 给分类添加推荐的菜谱
        temp = list()
        for recipe in result:
            if recipe.get('catename') == k.get('name',''):
                item = recipe.copy()
                item.pop('id')
                item.pop('catename')
                item.pop('sort')
                temp.append(item)
        # 将菜谱列表添加进分类中
        k.setdefault('cplist',sorted(temp, key=cpnumsort, reverse=True))

    return True, 0, 'success', result_list

async def recommend_topic_list():
    ''' 推荐主题列表 '''
    recommend_topic_sql = '''
SELECT
recom.*,
topic.title,
topic.faceimg as topicimg,
topic.collectionCount as collections,
us.userName as nickname,
us.headImg as faceimg
from
(
select
id,
topicid,
sort
from recommend_topic
where `status`=1) as recom
inner join topic_info as topic
on topic.id = recom.topicid and topic.`status` !=-1 and topic.isEnable=1
inner join user as us
on topic.userid = us.id and us.`status`=0
ORDER BY recom.sort desc;
    '''
    result = await dbins.select(recommend_topic_sql, ())
    if result is None:
        return False, 3003, '获取主题推荐异常,请重试', None
    else:
        return True, 0, 'success', result

async def banner_list(chl):
    ''' 获取海报列表 '''
    banner_list_sql = '''
    SELECT id, title, type, bannerimg, linkurl, recipeid, sort
    from banner
    where `channel`=? and `status`=1 order by sort desc;
    '''
    result = await dbins.select(banner_list_sql, (chl,))
    if result is None:
        return False, 3003, '获取海报异常,请重试', None
    else:
        return True, 0, 'success', result

async def channel_list():
    ''' 获取频道列表 '''
    banner_list_sql = '''
    SELECT id, title, faceImg, mainInfoUrl, sort, visitCount, status
    from channel_info
    where `status`=0 order by sort desc;
    '''
    result = await dbins.select(banner_list_sql, ())
    if result is None:
        return False, 3003, '获取频道列表异常,请重试', None
    else:
        result = await count_channel_num(result)
        return True, 0, 'success', result

async def count_channel_num(result):
    ''' 获取频道热度'''
    cout_moments_num_sql = '''
    SELECT COUNT(*) as count 
    FROM channel_moment_relation
    WHERE channelId = ?
    '''
    for p in result:
        channel_id = p.get('id')
        count_num = await dbins.select(cout_moments_num_sql, (channel_id,))
        p['hotCount'] = count_num[0]['count']+p['visitCount']
    return result


class IndexFoodManAllHandler(BaseHandler):
    ''' 首页吃货达人 '''

    @check_login
    async def post(self):
        result = []
        sort = self.verify_arg_legal(self.get_body_argument('sort'), '排序类型', False, is_num=True, uchecklist=True,
                                     user_check_list=['0',])
        page = self.verify_arg_num(self.get_argument('page'), '页数', is_num=True)
        userid = self.get_session().get('id', 0)
        # 查找吃货达人
        user_query = User.select().order_by().where(User.certificationStatus == 2, User.status == 0)
        users_wrappers = await self.application.objects.execute(user_query)

        for user in users_wrappers:
            user_dict = model_to_dict(user)

            cacheojb = CacheUserinfo(user.id)
            cres = await cacheojb.createCache()
            if cres is False:
                log.error("用户{}-积分缓存创建失败。".format(userid))
            n_dt = await cacheojb.get_dongtai()
            n_fs = await cacheojb.get_fans()
            n_sp = await cacheojb.get_shipu()
            name, img, tag, personalprofile, certificationStatus, sex = await cacheojb.mget('username', 'headimg',
                                                                                            'tag',
                                                                                            'personalProfile',
                                                                                            'certificationStatus',
                                                                                            'sex')
            the_num = int(n_dt) + int(n_fs) + int(n_sp)
            user_dict['name']=name
            user_dict['img']=img
            user_dict['n_dt']=n_dt
            user_dict['n_fs']=n_fs
            user_dict['n_sp']=n_sp
            user_dict['sort']=the_num
            user_dict.pop('createTime')
            result.append(user_dict)
        new_s = sorted(result, key=lambda e: e.__getitem__('sort'), reverse=True)
        # 每页数量
        page_num = 20
        page1 = 0 if page - 1 <= 0 else page - 1
        pagenum = page1 * page_num
        new_s = new_s[pagenum:pagenum+page_num]
        # 补充食谱信息
        for obj in new_s:
            # 判断是否关注 ''' 获取两个用户的关注关系,返回值 0 未关注 1 你关注了他 2 他关注了你 3 互相关注 '''
            relationship = await get_relationship_status(userid, obj['id'])
            obj['relationship'] = relationship
            sql = 'select id, title, faceimg from recipe_info where userid={} and status=1 ORDER BY id desc limit 3'.format(obj['id'])
            result = await DbOperate.instance().select(sql, ())
            obj['recipe_info']=result

        return self.send_message(True, 0, '操作成功', new_s)

async def search_foodman__list(userid, pagenum, epage=20):
    ''' 获取用户动态列表 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    # collect_query = User.select().where(User.certificationStatus == 2, User.status == 0).paginate(int(page), 20)
    # collects_wrappers = await self.application.objects.execute(collect_query)
    # sql = '''
    # select * from
    # user
    # where certificationStatus=2 and status=0
    # ORDER BY mmi.id desc
    #     '''
    # result = await db_ins.select(sql, (userid, page, epage))
    # # print(result, userid, page, epage)
    # if result is None:
    #     return False, 3001, '获取数据错误', None
    # for p in result:
    #     ct = p.get('createtime')
if __name__ == '__main__':
    async def test_banner_list():
        res = await banner_list(0)
        print(res)

    async def test_recommend_topic_list():
        res = await recommend_topic_list()
        print(res)

    async def test_recommend_recipe_list():
        res = await recommend_recipe_list()
        print(res)

    async def test_get_all_classinfo():
        res = await get_all_classinfo()
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_all_classinfo())