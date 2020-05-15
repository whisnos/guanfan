from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict

log = applog.get_log('web.taochannel')
dbins = DbOperate.instance()


class TaoChannelListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取频道列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await taochannel_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


class TaoChannelAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加频道 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taochannel_add(arg_key)
        self.send_cms_msg(code, msg)


class TaoChannelEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改频道 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taochannel_edit(arg_key)
        self.send_cms_msg(code, msg)


class TaoChannelDelHandler(BaseHandler):
    ''' 删除推荐频道 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taochannel_del(arg_key)
        self.send_cms_msg(code, msg)


class taochannelDeleteHandler(BaseHandler):
    ''' 删除频道 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taochannel_del(arg_key)
        self.send_cms_msg(code, msg)


class taochannelSetHandler(BaseHandler):
    ''' 设置频道 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taochannel_set(arg_key)
        self.send_cms_msg(code, msg)


class taochannelRecipeListHandler(BaseHandler):
    ''' 频道关联菜谱列表 '''

    @authenticated
    async def get(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await taochannel_recipe_list(arg_key)
        self.send_cms_msg(code, msg, result)


class taochannelRelationAddListHandler(BaseHandler):
    ''' 频道关联菜谱添加 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await taochannel_recipe_add(arg_key)
        self.send_cms_msg(code, msg, result)


class taochannelRelationEditListHandler(BaseHandler):
    ''' 频道关联菜谱编辑 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await taochannel_recipe_edit(arg_key)
        self.send_cms_msg(code, msg, result)


class taochannelRelationDelListHandler(BaseHandler):
    ''' 频道关联菜谱删除 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await taochannel_recipe_del(arg_key)
        self.send_cms_msg(code, msg, result)


async def taochannel_recipe_add(arg_dict):
    ''' 添加关联菜谱 '''
    taochannel_exists_sql = '''
    SELECT id FROM tao_channel_info WHERE id=?
    '''
    t_exists = await dbins.selectone(taochannel_exists_sql, arg_dict.get('relation_taochannele_id'))
    if t_exists is None:
        return 1041, '错误的频道数据', None

    insert_recipe_sql = '''
    INSERT INTO taochannel_recipe_relation
    (taochannelid,
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
        arg_dict.get('relation_taochannele_id'),
        arg_dict.get('recipeid'),
        arg_dict.get('reason'),
        arg_dict.get('sort')
    ))
    if insert_result is None:
        return 3001, "添加失败", None
    else:
        return 0, "添加成功", None


async def taochannel_recipe_edit(arg_dict):
    ''' 编辑关联菜谱 '''
    edit_sql = '''
    UPDATE taochannel_recipe_relation
    SET
    recipeid = ?,
    reason = ?,
    sort = ?
    WHERE id = ? AND taochannelid=?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('recipeid'),
        arg_dict.get('reason'),
        arg_dict.get('sort'),
        arg_dict.get('relation_id'),
        arg_dict.get('relation_taochannele_id'),
    ))
    if up_result is None:
        return 3001, "更新失败", None
    else:
        return 0, "更新成功", None


async def taochannel_recipe_del(arg_dict):
    ''' 删除关联菜谱 '''
    del_sql = '''
    DELETE FROM taochannel_recipe_relation WHERE id = ? AND taochannelid=?
    '''
    del_result = await dbins.execute(del_sql,
                                     (
                                         arg_dict.get('id'),
                                         arg_dict.get('taochannelid')
                                     ))
    if del_result is None:
        return 3001, "删除失败", None
    else:
        return 0, "删除成功", None


async def taochannel_add(arg_dict):
    ''' 增加 '''
    insert_sql = '''
    INSERT INTO tao_channel_info
    (
    title,
    faceImg,
    mainInfoUrl,
    sort
    )
    VALUES
    (
    ?,?,?,?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('title'),
        arg_dict.get('faceImg'),
        arg_dict.get('mainInfoUrl'),
        arg_dict.get('sort')
    ))
    if insert_result is None:
        return 3001, "添加失败"
    else:
        return 0, "添加成功"


async def taochannel_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE tao_channel_info
    set
    title = ?,
    faceImg = ?,
    mainInfoUrl = ?,
    sort = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('title'),
        arg_dict.get('faceImg'),
        arg_dict.get('mainInfoUrl'),
        arg_dict.get('sort'),
        arg_dict.get('id'),
    ))
    if up_result is None:
        return 3001, "更新失败"
    else:
        return 0, "更新成功"



def taochannel_set_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    sql_update = []
    wvalue = []
    upid = 0
    if arg_dict.get('id'):
        # like 模糊搜索字段
        upid = arg_dict.get('id')
        arg_dict.pop('id')

    for k, v in arg_dict.items():
        if v != '':
            check_k = k.replace('_', '')  # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_update.append('{}=?'.format(k))
                wvalue.append(v)

    wvalue.append(upid)
    if len(sql_update) > 0:
        return "{}".format(", ".join(sql_update)), wvalue
    else:
        return "", []


async def taochannel_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = taochannel_set_string(arg_dict)
    up_sel = '''
    UPDATE tao_channel_info
    SET {}
    where id = ?
    '''.format(update_str)
    up_result = await dbins.execute(up_sel,
                                    (
                                        upvalue_list
                                    ))
    if up_result is None:
        return 3001, "更新失败"
    else:
        return 0, "更新成功"


def taochannel_search_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    if arg_dict.get('page'):
        arg_dict.pop('page')
    if arg_dict.get('limit'):
        arg_dict.pop('limit')

    sql_where = []
    wvalue = []

    for k, v in arg_dict.items():
        if v != '':
            check_k = k.replace('_', '')  # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_where.append('{}=?'.format(k))
                wvalue.append(v)

    # sql_where.append('status!=-1')
    if len(sql_where) > 0:
        return "where {}".format(" and ".join(sql_where)), wvalue
    else:
        return "", []


async def taochannel_list(arg_dict):
    ''' 频道列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page', 1))
    epage = int(arg_dict.get('limit', 10))
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage

    where_str, wvalue_list = taochannel_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    taochannel_count_sql = '''select count(1) as ctnum from tao_channel_info {}'''.format(where_str)
    b_cnum = await dbins.selectone(taochannel_count_sql, wvalue_list)

    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum', 0) == 0:
        return 0, None

    # 实现倒排,最新的在前面
    page = int(b_cnum.get('ctnum', 0)) - page - epage
    if page < 0:
        # 第一页, page设置为0, epage 设置为 abs(-8)
        epage = epage - abs(page)
        page = 0

    taochannel_list_sql = '''
    SELECT 
    id, 
    pid_id, 
    materialId, 
    name, 
    iconImg,
    recommendId,
    is_banner, 
    sort, 
    createTime,
    updateTime
    FROM 
    tao_channel_info
    {}
    order by id desc
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(taochannel_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updateTime')
        b['updateTime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist


async def taochannel_recipe_list(arg_dict):
    ''' 频道关联菜谱列表 '''
    pagenum = int(arg_dict.get('page', 1))
    epage = int(arg_dict.get('limit', 50))
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage

    taochannel_recipe_list_sql = '''
SELECT
    taochannelrela.id,
    taochannelrela.taochannelid,
    taochannelrela.recipeid,
    taochannelrela.reason,
    taochannelrela.sort,
    taochannelrela.createtime,
    rei.title,
    rei.status AS recipestatus,
    rei.isEnable 
FROM
    taochannel_recipe_relation AS taochannelrela
    LEFT JOIN recipe_info AS rei ON rei.id = taochannelrela.recipeid 
WHERE
    taochannelrela.taochannelid = ?
ORDER BY
    taochannelrela.sort
    '''
    blist = await dbins.select(taochannel_recipe_list_sql, (arg_dict.get('id')))
    if blist is None:
        return 0, '查询异常', []

    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')

    return 0, '成功返回数据', blist


async def taochannel_del(arg_dict):
    ''' 删除 '''
    del_taochannel_set_sql = '''
    UPDATE tao_channel_info
    SET status=-1
    WHERE id = ?
    '''
    del_set_result = await dbins.execute(del_taochannel_set_sql,
                                         (
                                             arg_dict.get('id')
                                         ))
    if del_set_result is None:
        return 3001, "删除频道频道失败"
    return 0, "删除成功"


if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)


    async def test_taochannel_list():
        res = await taochannel_list(1, 10)
        print(res)


    async def test_sql_like():
        # 测试 like 模糊搜索
        taochannel_count_sql = '''
        select id from tao_channel_info where title like ?
        '''
        res = await dbins.selectone(taochannel_count_sql, ("%我的新频道%"))
        print(res)


    async def test_taochannel_recipe_list():
        res = await taochannel_recipe_list({'page': 1, 'limit': 100, 'id': 1})
        print(res)


    async def test_taochannel_set():
        res = await taochannel_set({"id": 6, "status": 0})


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_taochannel_set())
