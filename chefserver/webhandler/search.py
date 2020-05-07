import tornado.web
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.tooltime import curDatetime
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog

log = applog.get_log('webhandler.search')
dbins = DbOperate.instance()

class SearchHandler(BaseHandler):
    ''' 搜索菜谱 '''
    async def post(self):
        myid = 0 # 0 未关注 1 已关注 2 互相关注
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid = 0
        else:
            myid = user_session.get('id',0)

        keyword = self.verify_arg_legal(self.get_body_argument('key'), '食谱名', True, s_len=True, olen=80, is_not_null=True)
        sort = self.verify_arg_legal(self.get_body_argument('sort'), '排序类型', False, is_num=True, uchecklist=True, user_check_list=['1','2','3'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        # if len(keyword)<2:
        #     return self.send_message(False, 1002, '搜索的关键词过短', None)
            
        await add_hotkeyword(keyword)
        await add_key_history(myid, keyword)
        result = await search_keyword_recipe(keyword, int(sort), int(page))
        delrepeatlist = []
        temp_list = []
        for i in result:
            sid = i.get('id')
            if sid not in temp_list:
                temp_list.append(sid)
                delrepeatlist.append(i)
        return self.send_message(True, 0, 'success', delrepeatlist)


class SearchMemberHandler(BaseHandler):
    ''' 搜索用户 '''
    async def post(self):
        name = self.verify_arg_legal(self.get_body_argument('name'), '吃友名', True, s_len=True, olen=40)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        result = await search_member(name, int(page))
        return self.send_message(True, 0, 'success', result)


class keywordHandler(BaseHandler):
    ''' 返回热门词汇 '''
    # @check_login
    async def post(self):
        # page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_hotkeyword()
        return self.send_message(success, code, message, result)

async def search_member(name, pagenum, epage=20):
    ''' 搜索成员 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sh_user_sql ='''
select id, username as nickname, headimg as faceimg
from user
where MATCH (userName) AGAINST (? in boolean mode) and `status` = 0 limit ?,?
'''
    result = await dbins.select(sh_user_sql, (name, page, epage))

    if result is None:
        log.error('搜索吃友错误:{} {} {}'.format(name, page, epage))
        return []

    return result

async def search_keyword_recipe(keyword, sort_type, pagenum, epage=10):
    ''' 搜索菜谱, sort_type 1 综合最佳(收藏数+浏览数) 2 最多喜欢：收藏数最多 3 最新发布：发布时间按最新到最旧 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    if sort_type == 1:
            # 综合最佳
        search_keywrod_language_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg, 
    collectioncount as collections,
    (collectioncount + visitcount) as total,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? IN BOOLEAN MODE) and `status` in (0,1) and isEnable=1
    order by total desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by total desc
        '''
    if sort_type == 2:
            # 最多喜欢
        search_keywrod_language_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg, 
    collectioncount as collections,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? IN BOOLEAN MODE) and `status` in (0,1) and isEnable=1
    order by collections desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by collections desc
        '''
    if sort_type == 3:
            # 最新发布
        search_keywrod_language_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg,
    collectioncount as collections,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? IN BOOLEAN MODE) and `status` in (0,1) and isEnable=1
    order by createtime desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by createtime desc
    '''
    languate_result = await dbins.select(search_keywrod_language_mode, ('*'+keyword+'*', page, epage))
    if languate_result is None:
        log.error('自然搜索执行错误:{} {} {}'.format(keyword, page, epage))
        return []

    for p in languate_result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')

    return languate_result

async def search_keyword_recipe_backup(keyword, sort_type, pagenum, epage=10):
    ''' 搜索菜谱, sort_type 1 综合最佳(收藏数+浏览数) 2 最多喜欢：收藏数最多 3 最新发布：发布时间按最新到最旧 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    # 统计精准匹配搜索结果的数量
    exact_num = 0

    exact_search_sql = '''
SELECT count(1) as exact_num
FROM recipe_info
WHERE MATCH (title, tagKey) AGAINST (? in boolean mode) and `status` in (0,1) and isEnable=1;
    '''
    exact_result = await dbins.selectone(exact_search_sql, (keyword))
    if exact_result is None:
        exact_num = 0
    exact_num = exact_result.get('exact_num', 0)
    exact_len = exact_num%epage # 精准搜索结果余数
    cut = exact_num - page # 精准搜索结果结果余数  299 - 280 
    # print(exact_num, cut)
    if cut > 0:
        # 精准搜索结果数据>0
        if sort_type == 1:
            # 综合最佳
            search_keywrod_bool_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg, 
    collectioncount as collections,
    (collectioncount + visitcount) as total,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? in boolean mode) and `status` in (0,1) and isEnable=1
    order by total desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by total desc
        '''
        if sort_type == 2:
            # 最多喜欢
            search_keywrod_bool_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg, 
    collectioncount as collections,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? in boolean mode) and `status` in (0,1) and isEnable=1
    order by collections desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by collections desc
        '''
        if sort_type == 3:
            # 最新发布
            search_keywrod_bool_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg,
    collectioncount as collections,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? in boolean mode) and `status` in (0,1) and isEnable=1
    order by createtime desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by createtime desc
    '''
        result_res = await dbins.select(search_keywrod_bool_mode, (keyword, page, epage))
        if result_res is None:
            log.error('精确搜索执行错误:{} {} {}'.format(keyword, page, epage))
            return []

        for p in result_res:
            ct = p.get('createtime')
            p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        result = list(result_res)
    else:
        result = []

    return result
    # 精确搜索数量足够优先返回结果
    if cut >= epage:
        # 直接返回
        return result
    else:
        
        # 数量不够,用自然语言搜索结果拼凑
        exact_page = int(exact_num/epage)
        language_page = abs(exact_page - pagenum) # 自然语言搜索的页数
        lpage = 0 if language_page-1 <= 0 else language_page-1
        lpage = lpage*epage
        if lpage > 0:
            # 修正模糊搜索结果,每页起点数据
            # 第一页开始+精准搜索余数,后面页数七点要减去精准搜索的余数
            lpage = lpage - exact_len

        if sort_type == 1:
            # 综合最佳
            search_keywrod_language_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg, 
    collectioncount as collections,
    (collectioncount + visitcount) as total,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? IN NATURAL LANGUAGE MODE) and `status` in (0,1) and isEnable=1
    order by total desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by total desc
        '''
        if sort_type == 2:
            # 最多喜欢
            search_keywrod_language_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg, 
    collectioncount as collections,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? IN NATURAL LANGUAGE MODE) and `status` in (0,1) and isEnable=1
    order by collections desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by collections desc
        '''
        if sort_type == 3:
            # 最新发布
            search_keywrod_language_mode = '''
    select
    us.userName as nickname,
    us.headImg as faceImg,
    search.*
    from
    (
    SELECT id, userid, title, faceimg as cpimg,
    collectioncount as collections,
    createtime
    from recipe_info
    where MATCH (title, tagKey) AGAINST (? IN NATURAL LANGUAGE MODE) and `status` in (0,1) and isEnable=1
    order by createtime desc,id desc limit ?, ?
    ) as search
    inner join user as us
    on us.id = search.userid and us.`status`=0
    order by createtime desc
    '''
        languate_result = await dbins.select(search_keywrod_language_mode, (keyword, lpage, epage))
        if languate_result is None:
            log.error('自然搜索执行错误:{} {} {}'.format(keyword, lpage, epage))
            return []

        for p in languate_result:
            ct = p.get('createtime')
            p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        # print(exact_len, exact_page, language_page, lpage)

        if lpage == 0:
            # 把精准匹配最后几条和自然语言搜索组合起来
            step = epage-exact_len # 自然语言第一页显示多少条 每页数量 - 精准匹配剩余数量
            result.extend(languate_result[:step])
            return result

        return languate_result

async def add_hotkeyword(keyword):
    ''' 添加热词 '''
    up_key_sql = '''
    update hot_keyword set visitcount = visitcount + 1, updatetime = ? where keyword = ?
    '''
    curtime = curDatetime()
    result = await dbins.execute(up_key_sql, (curtime, keyword))
    if result is None:
        return False, 3001, '热词更新异常,请重试', None

    if result == 1:
        return True, 0, '更新成功', None

    if result == 0:
        # 新词
        ins_key_sql = '''
        INSERT INTO hot_keyword
        (keyword, visitCount, updateTime, createTime, sort, status)
        VALUES
        (?,         ?,          ?,          ?,          ?,          ?)
        '''
        ins_res = await dbins.execute(ins_key_sql, (keyword, 1, curtime, curtime, 0, 0))
        if ins_res is None:
            return False, 3002, '添加搜索词异常,请重试', None
        else:
            return True, 0, '添加成功', None

async def add_key_history(myid, keyword):
    ''' 添加搜索词历史信息 '''
    add_key_sql = '''
INSERT INTO search_keyword(`keyword`, `userId`)
VALUES(?, ?)
    '''
    result = await dbins.execute(add_key_sql, (keyword, myid))
    if result is None:
        log.error('添加搜索记录异常:{} {} {}'.format(add_key_sql, myid, keyword))
        # return False, 3002, '添加搜索词异常,请重试', None
    else:
        return
        # return True, 0, '添加成功', None


async def get_hotkeyword(pagenum=0, epage=10):
    ''' 获取热搜词汇 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql = '''
    select keyword from hot_keyword where status=0 order by visitCount desc limit ?,?
    '''
    result = await dbins.select(sql, (page, epage))
    if result is None:
        return False, 3003, '获取热词异常,请重试', None

    res_list =[]
    for i in result:
        res_list.append(i.get('keyword'))
    return True, 0, 'success',  res_list


async def get_similar_recipe_tagkey(recipename):
    ''' 获取菜谱类似菜谱名字的标签数据'''
    search_boolean_tagkey_sql = '''
SELECT tagkey,
(collectioncount + visitcount) as total
from recipe_info
where MATCH (title, tagKey) AGAINST (? in boolean mode)
and `status` in (0,1) and isEnable=1 and tagkey!=''
order by total desc limit 1
    '''
    exact_result = await dbins.selectone(search_boolean_tagkey_sql, (recipename))

    if exact_result:
        return exact_result.get('tagkey')

    search_language_tagkey_sql = '''
SELECT tagkey,
(collectioncount + visitcount) as total
from recipe_info
where MATCH (title, tagKey) AGAINST (? IN NATURAL LANGUAGE MODE)
and `status` in (0,1) and isEnable=1 and tagkey!=''
order by total desc limit 1
    '''
    language_result = await dbins.selectone(search_language_tagkey_sql, (recipename))
    # print(language_result)
    if language_result:
        return language_result.get('tagkey')
    else:
        return ''


class SearchMomentHandler(BaseHandler):
    ''' 搜索动态 '''

    async def post(self):
        myid = 0  # 0 未关注 1 已关注 2 互相关注
        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid = 0
        else:
            myid = user_session.get('id', 0)

        keyword = self.verify_arg_legal(self.get_body_argument('key'), '动态名', True, s_len=True, olen=80,
                                        is_not_null=True)
        sort = self.verify_arg_legal(self.get_body_argument('sort'), '排序类型', False, is_num=True, uchecklist=True,
                                     user_check_list=['1', '2', '3'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)

        await add_hotkeyword(keyword)
        await add_key_history(myid, keyword)
        result = await search_keyword_moment(keyword, int(sort), int(page))
        delrepeatlist = []
        temp_list = []
        for i in result:
            sid = i.get('id')
            if sid not in temp_list:
                temp_list.append(sid)
                delrepeatlist.append(i)
        return self.send_message(True, 0, 'success', delrepeatlist)

async def search_keyword_moment(keyword, sort_type, pagenum, epage=10):
    ''' 搜索动态, sort_type 1 综合最佳(收藏数+浏览数) 2 最多点赞 3 最新发布：发布时间按最新到最旧 '''
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    if sort_type == 1:
            # 综合最佳
        search_keywrod_language_mode = '''
select
us.userName as nickname,
us.headImg as faceImg,
search.*
from
(
SELECT id, userId, momentsDescription, momentsImgUrl as mmimg, 
likeCount as collections,
(likeCount + visitcount) as total,
createtime
from moments_info
where MATCH (momentsDescription) AGAINST (? in boolean mode) and `status`=0
order by total desc,id desc limit ?, ?
) as search
inner join user as us
on us.id = search.userId and us.`status`=0
order by total desc
        '''
    if sort_type == 2:
            # 最多点赞
        search_keywrod_language_mode = '''
    select
us.userName as nickname,
us.headImg as faceImg,
search.*
from
(
SELECT id, userId, momentsDescription, momentsImgUrl as mmimg, 
likeCount as collections,
(likeCount + visitcount) as total,
createtime
from moments_info
where MATCH (momentsDescription) AGAINST (? in boolean mode) and `status`=0
order by collections desc,id desc limit ?, ?
) as search
inner join user as us
on us.id = search.userid and us.`status`=0
order by collections desc
        '''
    if sort_type == 3:
            # 最新发布
        search_keywrod_language_mode = '''
select
us.userName as nickname,
us.headImg as faceImg,
search.*
from
(
SELECT id, userId, momentsDescription, momentsImgUrl as mmimg, 
likeCount as collections,
(likeCount + visitcount) as total,
createtime
from moments_info
where MATCH (momentsDescription) AGAINST (? in boolean mode) and `status`=0
order by createtime desc,id desc limit ?, ?
) as search
inner join user as us
on us.id = search.userid and us.`status`=0
order by createtime desc
    '''
    languate_result = await dbins.select(search_keywrod_language_mode, ('*'+keyword+'*', page, epage))
    if languate_result is None:
        log.error('自然搜索执行错误:{} {} {}'.format(keyword, page, epage))
        return []

    for p in languate_result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')

    return languate_result

if __name__ == '__main__':
    async def test_get_hotkeyword():
        res = await get_hotkeyword(1)
        print(res)

    async def test_add_hotkeyword():
        res = await add_hotkeyword('天山雪莲')
        print(res)

    async def test_search_keyword_recipe():
        res = await search_keyword_recipe('宇宙超级爱心卷', 1, 1)
        print(res)

    async def test_get_similar_recipe_tagkey():
        res = await get_similar_recipe_tagkey('90211cf3')
        print(res)

    async def  test_add_key_history():
        res = await add_key_history(1,'拍黄瓜')
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_search_keyword_recipe())