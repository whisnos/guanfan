from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.topic')
dbins = DbOperate.instance()


class TopicListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取主题列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await topic_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class TopicAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加主题 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await topic_add(arg_key)
        self.send_cms_msg(code, msg)

class TopicEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改主题 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await topic_edit(arg_key)
        self.send_cms_msg(code, msg)

class TopicDeleteHandler(BaseHandler):
    ''' 删除主题 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await topic_del(arg_key)
        self.send_cms_msg(code, msg)

class TopicSetHandler(BaseHandler):
    ''' 设置主题 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await topic_set(arg_key)
        self.send_cms_msg(code, msg)

class TopicRecipeListHandler(BaseHandler):
    ''' 主题关联菜谱列表 '''
    @authenticated
    async def get(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await topic_recipe_list(arg_key)
        self.send_cms_msg(code, msg, result)

class TopicRelationAddListHandler(BaseHandler):
    ''' 主题关联菜谱添加 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await topic_recipe_add(arg_key)
        self.send_cms_msg(code, msg, result)

class TopicRelationEditListHandler(BaseHandler):
    ''' 主题关联菜谱编辑 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await topic_recipe_edit(arg_key)
        self.send_cms_msg(code, msg, result)

class TopicRelationDelListHandler(BaseHandler):
    ''' 主题关联菜谱删除 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await topic_recipe_del(arg_key)
        self.send_cms_msg(code, msg, result)

async def topic_recipe_add(arg_dict):
    ''' 添加关联菜谱 '''
    topic_exists_sql = '''
    SELECT id FROM topic_info WHERE id=?
    '''
    t_exists = await dbins.selectone(topic_exists_sql, arg_dict.get('relation_topice_id'))
    if t_exists is None:
        return 1041,'错误的主题数据', None

    insert_recipe_sql= '''
    INSERT INTO topic_recipe_relation
    (topicid,
    recipeid,
    reason,
    sort)
    VALUES(
    ?,
    ?,
    ?,
    ?
    )
    '''
    insert_result = await dbins.execute(insert_recipe_sql, (
        arg_dict.get('relation_topice_id'),
        arg_dict.get('recipeid'),
        arg_dict.get('reason'),
        arg_dict.get('sort')
        ))
    if insert_result is None:
        return 3001 , "添加失败", None
    else:
        return 0, "添加成功", None

async def topic_recipe_edit(arg_dict):
    ''' 编辑关联菜谱 '''
    edit_sql = '''
    UPDATE topic_recipe_relation
    SET
    recipeid = ?,
    reason = ?,
    sort = ?
    WHERE id = ? AND topicid=?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('recipeid'),
        arg_dict.get('reason'),
        arg_dict.get('sort'),
        arg_dict.get('relation_id'),
        arg_dict.get('relation_topice_id'),
        ))
    if up_result is None:
        return 3001 , "更新失败", None
    else:
        return 0 , "更新成功", None

async def topic_recipe_del(arg_dict):
    ''' 删除关联菜谱 '''
    del_sql = '''
    DELETE FROM topic_recipe_relation WHERE id = ? AND topicid=?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id'),
        arg_dict.get('topicid')
        ))
    if del_result is None:
        return 3001 , "删除失败", None
    else:
        return 0 , "删除成功", None

async def topic_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO topic_info
    (
    userid,
    title,
    faceimg,
    maininfourl,
    introduction,
    maininfotype,
    isrecommend,
    isenable,
    status
    )
    VALUES
    (
    ?,?,?,?,?,?,?,?,?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('userid'),
        arg_dict.get('title'),
        arg_dict.get('faceimg'),
        arg_dict.get('maininfourl'),
        arg_dict.get('introduction'),
        1,
        0,
        0,
        0
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def topic_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE topic_info
    set
    userid = ?,
    title = ?,
    faceimg = ?,
    maininfourl = ?,
    introduction = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('userid'),
        arg_dict.get('title'),
        arg_dict.get('faceimg'),
        arg_dict.get('maininfourl'),
        arg_dict.get('introduction'),
        arg_dict.get('id'),
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def topic_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE topic_info
    SET status=-1
    where id = ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id')
        ))
    if del_result is None:
        return 3001 , "删除失败"
    else:
        return 0 , "删除成功"

def topic_set_string(arg_dict):
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


async def topic_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = topic_set_string(arg_dict)
    up_sel = '''
    UPDATE topic_info
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


def topic_search_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    if arg_dict.get('page'):
        arg_dict.pop('page')
    if arg_dict.get('limit'):
        arg_dict.pop('limit')

    sql_where = []
    wvalue = []
    if arg_dict.get('title'):
        # like 模糊搜索字段
        t = arg_dict.get('title')
        wvalue.append('%' + t + '%')
        sql_where.append("title like ?")
        arg_dict.pop('title')


    for k,v in arg_dict.items():
        if v!='':
            check_k = k.replace('_','') # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_where.append('{}=?'.format(k))
                wvalue.append(v)

    if len(sql_where)>0:
        return "where {}".format(" and ".join(sql_where)), wvalue
    else:
        return "",[]
async def topic_list(arg_dict):
    ''' 主题列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = topic_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    topic_count_sql = '''select count(1) as ctnum from topic_info {}'''.format(where_str)
    b_cnum = await dbins.selectone(topic_count_sql, wvalue_list)

    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum',0) == 0:
        return 0, None

    # 实现倒排,最新的在前面
    page = int(b_cnum.get('ctnum',0)) - page - epage
    if page < 0:
        # 第一页, page设置为0, epage 设置为 abs(-8)
        epage = epage - abs(page)
        page = 0
        
    topic_list_sql = '''
    select
    id,
    userid,
    title,
    faceimg,
    maininfourl,
    maininfotype,
    introduction,
    visitcount,
    collectioncount,
    isrecommend,
    isenable,
    status,
    updatetime,
    createtime
    from
    topic_info
    {}
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(topic_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updatetime')
        b['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist

async def topic_recipe_list(arg_dict):
    ''' 主题关联菜谱列表 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',50))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    topic_recipe_list_sql = '''
SELECT
    topicrela.id,
    topicrela.topicid,
    topicrela.recipeid,
    topicrela.reason,
    topicrela.sort,
    topicrela.createtime,
    rei.title,
    rei.status AS recipestatus,
    rei.isEnable 
FROM
    topic_recipe_relation AS topicrela
    LEFT JOIN recipe_info AS rei ON rei.id = topicrela.recipeid 
WHERE
    topicrela.topicid = ?
ORDER BY
    topicrela.sort
    '''
    blist = await dbins.select(topic_recipe_list_sql, (arg_dict.get('id')))
    if blist is None:
        return 0, '查询异常', []

    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')


    return 0, '成功返回数据', blist


if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)

    async def test_topic_list():
        res = await topic_list(1,10)
        print(res)

    async def test_sql_like():
        # 测试 like 模糊搜索
        topic_count_sql = '''
        select id from topic_info where title like ?
        '''
        res = await dbins.selectone(topic_count_sql, ("%我的新主题%"))
        print(res)

    async def test_topic_recipe_list():
        res = await topic_recipe_list({'page':1,'limit':100,'id':1})
        print(res)

    async def test_topic_set():
        res = await topic_set({"id":6, "status":0})

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_topic_set())
