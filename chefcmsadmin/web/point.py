from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict

log = applog.get_log('web.point')
dbins = DbOperate.instance()


class PointListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取主题列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await point_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


class PointAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加主题 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await point_add(arg_key)
        self.send_cms_msg(code, msg)


class PointEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改主题 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await point_edit(arg_key)
        self.send_cms_msg(code, msg)


class PointDeleteHandler(BaseHandler):
    ''' 删除主题 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await point_del(arg_key)
        self.send_cms_msg(code, msg)


class PointSetHandler(BaseHandler):
    ''' 设置主题 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await point_set(arg_key)
        self.send_cms_msg(code, msg)


class PointRecipeListHandler(BaseHandler):
    ''' 主题关联菜谱列表 '''

    @authenticated
    async def get(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await point_recipe_list(arg_key)
        self.send_cms_msg(code, msg, result)


class PointRelationAddListHandler(BaseHandler):
    ''' 主题关联菜谱添加 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await point_recipe_add(arg_key)
        self.send_cms_msg(code, msg, result)


class PointRelationEditListHandler(BaseHandler):
    ''' 主题关联菜谱编辑 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await point_recipe_edit(arg_key)
        self.send_cms_msg(code, msg, result)


class PointRelationDelListHandler(BaseHandler):
    ''' 主题关联菜谱删除 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await point_recipe_del(arg_key)
        self.send_cms_msg(code, msg, result)


async def point_recipe_add(arg_dict):
    ''' 添加关联菜谱 '''
    point_exists_sql = '''
    SELECT id FROM point_info WHERE id=?
    '''
    t_exists = await dbins.selectone(point_exists_sql, arg_dict.get('relation_pointe_id'))
    if t_exists is None:
        return 1041, '错误的主题数据', None

    insert_recipe_sql = '''
    INSERT INTO point_recipe_relation
    (pointid,
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
        arg_dict.get('relation_pointe_id'),
        arg_dict.get('recipeid'),
        arg_dict.get('reason'),
        arg_dict.get('sort')
    ))
    if insert_result is None:
        return 3001, "添加失败", None
    else:
        return 0, "添加成功", None


async def point_recipe_edit(arg_dict):
    ''' 编辑关联菜谱 '''
    edit_sql = '''
    UPDATE point_recipe_relation
    SET
    recipeid = ?,
    reason = ?,
    sort = ?
    WHERE id = ? AND pointid=?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('recipeid'),
        arg_dict.get('reason'),
        arg_dict.get('sort'),
        arg_dict.get('relation_id'),
        arg_dict.get('relation_pointe_id'),
    ))
    if up_result is None:
        return 3001, "更新失败", None
    else:
        return 0, "更新成功", None


async def point_recipe_del(arg_dict):
    ''' 删除关联菜谱 '''
    del_sql = '''
    DELETE FROM point_recipe_relation WHERE id = ? AND pointid=?
    '''
    del_result = await dbins.execute(del_sql,
                                     (
                                         arg_dict.get('id'),
                                         arg_dict.get('pointid')
                                     ))
    if del_result is None:
        return 3001, "删除失败", None
    else:
        return 0, "删除成功", None


async def point_add(arg_dict):
    ''' 增加 '''
    insert_sql = '''
    INSERT INTO point_info
    (
    point_type,
    grade_no,
    status
    )
    VALUES
    (
    ?,?,?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('point_type'),
        arg_dict.get('grade_no'),
        arg_dict.get('status'),
    ))
    if insert_result is None:
        return 3001, "添加失败"
    else:
        return 0, "添加成功"


async def point_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE 
    point_setting ps, 
    point_info pi
    set
    pi.point_type = ?,
    pi.grade_no = ?,
    ps.options_type = ?,
    ps.count = ?,
    pi.`status` = ?
    where 
    pi.id= ? and ps.pointinfo_id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('point_type'),
        arg_dict.get('grade_no'),
        arg_dict.get('options_type'),
        arg_dict.get('count'),
        arg_dict.get('status'),
        arg_dict.get('id'),
        arg_dict.get('id'),
    ))
    if up_result is None:
        return 3001, "更新失败"
    else:
        return 0, "更新成功"


async def point_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE point_info
    SET status=-1
    where id = ?
    '''
    del_result = await dbins.execute(del_sql,
                                     (
                                         arg_dict.get('id')
                                     ))
    if del_result is None:
        return 3001, "删除失败"
    else:
        return 0, "删除成功"


def point_set_string(arg_dict):
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


async def point_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = point_set_string(arg_dict)
    up_sel = '''
    UPDATE point_info
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


def point_search_string(arg_dict):
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

    for k, v in arg_dict.items():
        if v != '':
            check_k = k.replace('_', '')  # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_where.append('{}=?'.format(k))
                wvalue.append(v)

    if len(sql_where) > 0:
        return "where {}".format(" and ".join(sql_where)), wvalue
    else:
        return "", []


async def point_list(arg_dict):
    ''' 主题列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page', 1))
    epage = int(arg_dict.get('limit', 10))
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage

    where_str, wvalue_list = point_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    point_count_sql = '''select count(1) as ctnum from point_info {}'''.format(where_str)
    b_cnum = await dbins.selectone(point_count_sql, wvalue_list)

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

    point_list_sql = '''
    select
    pi.id, 
    pi.point_type, 
    pi.grade_no, 
    pi.`status`, 
    ps.count, 
    ps.options_type,
    pi.createTime
    from
    point_info pi
    LEFT JOIN point_setting ps
    on ps.pointinfo_id=pi.id
    where pi.`status` !=-1
    {}
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(point_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist


async def point_recipe_list(arg_dict):
    ''' 主题关联菜谱列表 '''
    pagenum = int(arg_dict.get('page', 1))
    epage = int(arg_dict.get('limit', 50))
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage

    point_recipe_list_sql = '''
SELECT
    pointrela.id,
    pointrela.pointid,
    pointrela.recipeid,
    pointrela.reason,
    pointrela.sort,
    pointrela.createtime,
    rei.title,
    rei.status AS recipestatus,
    rei.isEnable 
FROM
    point_recipe_relation AS pointrela
    LEFT JOIN recipe_info AS rei ON rei.id = pointrela.recipeid 
WHERE
    pointrela.pointid = ?
ORDER BY
    pointrela.sort
    '''
    blist = await dbins.select(point_recipe_list_sql, (arg_dict.get('id')))
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


    async def test_point_list():
        res = await point_list(1, 10)
        print(res)


    async def test_sql_like():
        # 测试 like 模糊搜索
        point_count_sql = '''
        select id from point_info where title like ?
        '''
        res = await dbins.selectone(point_count_sql, ("%我的新主题%"))
        print(res)


    async def test_point_recipe_list():
        res = await point_recipe_list({'page': 1, 'limit': 100, 'id': 1})
        print(res)


    async def test_point_set():
        res = await point_set({"id": 6, "status": 0})


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_point_set())
