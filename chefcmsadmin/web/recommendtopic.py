from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from chefcmsadmin.tool.tooltime import curDatetime
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.recommendtopic')
dbins = DbOperate.instance()


class RecommendTopicListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取推荐主题列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await recommendtopic_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class RecommendTopicAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加推荐主题 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recommendtopic_add(arg_key)
        self.send_cms_msg(code, msg)

class RecommendTopicEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改推荐主题 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recommendtopic_edit(arg_key)
        self.send_cms_msg(code, msg)

class RecommendTopicDeleteHandler(BaseHandler):
    ''' 删除推荐主题 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recommendtopic_del(arg_key)
        self.send_cms_msg(code, msg)


async def recommendtopic_add(arg_dict):
    ''' 增加 '''
    topicid = arg_dict.get('topicid')
    result = await exists_topic(topicid)
    if result is False:
        return 2010, "错误的主题数据"

    insert_sql='''
    INSERT INTO recommend_topic
    (
    topicid,
    recipenum,
    reason,
    sort,
    status
    )
    VALUES
    (
    ?,?,?,?,?
    )
    '''
    
    insert_result = await dbins.execute(insert_sql, (
        topicid,
        await topic_recipe_num(topicid),
        arg_dict.get('reason'),
        arg_dict.get('sort'),
        arg_dict.get('status') if arg_dict.get('status') in ['-1','0','1'] else '0'
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def exists_topic(topicid):
    ''' 查找主题是否存在 ''' 
    topic_exists_sql = '''select count(id) as ctnum from topic_info where id= ? '''
    exists_result = await dbins.selectone(topic_exists_sql, topicid)

    if exists_result is None:
        return False
    else:
        return True

async def topic_recipe_num(topicid):
    ''' 返回主题对应的菜谱数量 '''
    result = await exists_topic(topicid)
    if result is False:
        return 0
    topic_num_sql = '''select count(id) as ctnum from topic_recipe_relation where topicId= ? '''
    num_result = await dbins.selectone(topic_num_sql, topicid)
    if num_result is None:
        return 0
    else:
        return num_result.get('ctnum',0)

async def recommendtopic_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE recommend_topic
    set
    topicid = ?,
    recipenum = ?,
    reason=?,
    sort = ?,
    status = ?,
    updatetime = ?
    where id = ?
    '''
    topicid = arg_dict.get('topicid')
    up_result = await dbins.execute(edit_sql, (
        topicid,
        await topic_recipe_num(topicid),
        arg_dict.get('reason'),
        arg_dict.get('sort'),
        arg_dict.get('status') if arg_dict.get('status') in ['-1','0','1'] else '0',
        curDatetime(),
        arg_dict.get('id'),
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def recommendtopic_del(arg_dict):
    ''' 删除 '''
    del_topic_set_sql = '''
    UPDATE recommend_topic
    SET status=-1
    WHERE id = ?
    '''
    del_set_result = await dbins.execute(del_topic_set_sql,
        (
        arg_dict.get('id')
        ))
    if del_set_result is None:
        return 3001 , "删除推荐主题失败"
    return 0, "删除成功"


def recommendtopic_set_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    sql_update = []
    wvalue = []
    upid = 0
    if arg_dict.get('id'):
        # like 模糊搜索字段
        upid = arg_dict.get('id')
        arg_dict.pop('id')

    for k,v in arg_dict.items():
        if v!='':
            check_k = k.replace('_','') # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_update.append('{}=?'.format(k))
                wvalue.append(v)

    wvalue.append(upid)
    if len(sql_update)>0:
        return "{}".format(", ".join(sql_update)), wvalue
    else:
        return "",[]


async def recommendtopic_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = recommendtopic_set_string(arg_dict)
    up_sel = '''
    UPDATE recommend_topic
    SET {}
    where id = ?
    '''.format(update_str)
    up_result = await dbins.execute(up_sel,
        (
        upvalue_list
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"


def recommendtopic_search_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    if arg_dict.get('page'):
        arg_dict.pop('page')
    if arg_dict.get('limit'):
        arg_dict.pop('limit')

    sql_where = []
    wvalue = []

    for k,v in arg_dict.items():
        if v!='':
            check_k = k.replace('_','') # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_where.append('{}=?'.format(k))
                wvalue.append(v)

    sql_where.append('status!=-1')
    if len(sql_where)>0:
        return "where {}".format(" and ".join(sql_where)), wvalue
    else:
        return "",[]

async def recommendtopic_list(arg_dict):
    ''' 推荐主题列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = recommendtopic_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    recommendtopic_count_sql = '''select count(1) as ctnum from recommend_topic {}'''.format(where_str)
    b_cnum = await dbins.selectone(recommendtopic_count_sql, wvalue_list)

    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum',0) == 0:
        return 0, None

    recommendtopic_list_sql = '''
    SELECT
    retopic.id,
    tic.title,
    retopic.topicid,
    retopic.recipenum,
    retopic.sort,
    retopic.reason,
    retopic.status,
    retopic.updatetime,
    retopic.createtime
    FROM
    (SELECT * FROM recommend_topic {}) as retopic
    LEFT JOIN topic_info as tic ON retopic.topicid = tic.id and retopic.status!=-1
    ORDER BY retopic.status DESC,retopic.sort DESC
    LIMIT ?,?
    '''.format(where_str)
    # ORDER BY status desc,sort desc
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(recommendtopic_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    # print(blist)
    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updateTime')
        b['updateTime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist



if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)

    async def test_recommendtopic_list():
        res = await recommendtopic_list(1,10)
        print(res)

    async def test_sql_like():
        # 测试 like 模糊搜索
        recommendtopic_count_sql = '''
        select id from recommendtopic_info where title like ?
        '''
        res = await dbins.selectone(recommendtopic_count_sql, ("%我的新推荐主题%"))
        print(res)

    async def test_recommendtopic_recipe_list():
        res = await recommendtopic_recipe_list({'page':1,'limit':100,'id':1})
        print(res)

    async def test_recommendtopic_set():
        res = await recommendtopic_set({"id":6, "status":0})

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_recommendtopic_set())
