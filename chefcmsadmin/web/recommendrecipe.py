from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from chefcmsadmin.tool.tooltime import curDatetime
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.recipetype')
dbins = DbOperate.instance()


class RecipeTypeListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取推荐分类列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await recipetype_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class RecipeTypeAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加推荐分类 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipetype_add(arg_key)
        self.send_cms_msg(code, msg)

class RecipeTypeEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改推荐分类 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipetype_edit(arg_key)
        self.send_cms_msg(code, msg)

class RecipeTypeDeleteHandler(BaseHandler):
    ''' 删除推荐分类 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipetype_del(arg_key)
        self.send_cms_msg(code, msg)

class RecipeTypeSetHandler(BaseHandler):
    ''' 设置推荐分类 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipetype_set(arg_key)
        self.send_cms_msg(code, msg)

class RecipeTypeRecipeListHandler(BaseHandler):
    ''' 推荐分类关联菜谱列表 '''
    @authenticated
    async def get(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await recipetype_recipe_list(arg_key)
        self.send_cms_msg(code, msg, result)

class RecipeTypeRelationAddListHandler(BaseHandler):
    ''' 推荐分类关联菜谱添加 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await recipetype_recipe_add(arg_key)
        self.send_cms_msg(code, msg, result)

class RecipeTypeRelationEditListHandler(BaseHandler):
    ''' 推荐分类关联菜谱编辑 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await recipetype_recipe_edit(arg_key)
        self.send_cms_msg(code, msg, result)

class RecipeTypeRelationDelListHandler(BaseHandler):
    ''' 推荐分类关联菜谱删除 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await recipetype_recipe_del(arg_key)
        self.send_cms_msg(code, msg, result)

async def recipetype_recipe_add(arg_dict):
    ''' 添加关联菜谱 '''
    recipetype_exists_sql = '''
    SELECT id FROM recommend_recipe_category WHERE id=?
    '''
    t_exists = await dbins.selectone(recipetype_exists_sql, arg_dict.get('recipetype_id'))
    if t_exists is None:
        return 1041,'错误的推荐分类数据', None

    insert_recipe_sql= '''
    INSERT INTO recommend_recipe
    (categoryid,
    recipeid,
    sort)
    VALUES(
    ?,
    ?,
    ?
    )
    '''
    insert_result = await dbins.execute(insert_recipe_sql, (
        arg_dict.get('recipetype_id'),
        arg_dict.get('recipeid'),
        arg_dict.get('sort')
        ))
    if insert_result is None:
        return 3001 , "添加失败", None
    else:
        return 0, "添加成功", None

async def recipetype_recipe_edit(arg_dict):
    ''' 编辑关联菜谱 '''
    edit_sql = '''
    UPDATE recommend_recipe
    SET
    recipeid = ?,
    sort = ?
    WHERE id = ? and categoryid = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('recipeid'),
        arg_dict.get('sort'),
        arg_dict.get('id'),
        arg_dict.get('recipetype_id')
        ))
    if up_result is None:
        return 3001 , "更新失败", None
    else:
        return 0 , "更新成功", None

async def recipetype_recipe_del(arg_dict):
    ''' 删除关联菜谱 '''
    del_sql = '''
    DELETE FROM recommend_recipe WHERE id = ? AND categoryid= ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id'),
        arg_dict.get('categoryid')
        ))
    if del_result is None:
        return 3001 , "删除失败", None
    else:
        return 0 , "删除成功", None

async def recipetype_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO recommend_recipe_category
    (
    title,
    sort,
    status
    )
    VALUES
    (
    ?,?,?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('title'),
        arg_dict.get('sort'),
        0
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def recipetype_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE recommend_recipe_category
    set
    title = ?,
    sort = ?,
    status = ?,
    updatetime = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('title'),
        arg_dict.get('sort'),
        1 if arg_dict.get('status')== '1' else 0,
        curDatetime(),
        arg_dict.get('id'),
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def recipetype_del(arg_dict):
    ''' 删除 '''
    del_relation_sql = '''
    DELETE FROM recommend_recipe
    WHERE categoryid = ?
    '''
    del_relation_result = await dbins.execute(del_relation_sql,
        (
        arg_dict.get('id')
        ))
    if del_relation_result is None:
        return 3001 , "删除子分类失败"

    del_sql = '''
    DELETE FROM recommend_recipe_category
    WHERE id = ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id')
        ))
    if del_result is None:
        return 3001 , "删除主分类失败"
    else:
        return 0 , "删除成功"

def recipetype_set_string(arg_dict):
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


async def recipetype_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = recipetype_set_string(arg_dict)
    up_sel = '''
    UPDATE recommend_recipe_category
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


def recipetype_search_string(arg_dict):
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

async def recipetype_list(arg_dict):
    ''' 推荐分类列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = recipetype_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    recipetype_count_sql = '''select count(1) as ctnum from recommend_recipe_category {}'''.format(where_str)
    b_cnum = await dbins.selectone(recipetype_count_sql, wvalue_list)

    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum',0) == 0:
        return 0, None

    recipetype_list_sql = '''
    SELECT
    *
    FROM
    recommend_recipe_category
    {}
    ORDER BY sort desc, id desc
    LIMIT ?,?
    '''.format(where_str)
    # ORDER BY status desc,sort desc
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(recipetype_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updateTime')
        b['updateTime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist

async def recipetype_recipe_list(arg_dict):
    ''' 推荐分类关联菜谱列表 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',50))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    recipetype_recipe_list_sql = '''
SELECT
recommend.id,
recommend.categoryid,
recommend.recipeid,
recommend.sort,
recommend.status,
recommend.createtime,
rei.title,
rei.status AS recipestatus,
rei.isEnable
FROM
recommend_recipe AS recommend
LEFT JOIN recipe_info AS rei
ON rei.id = recommend.recipeid
WHERE recommend.categoryid = ?
ORDER BY recommend.sort DESC
    '''
    blist = await dbins.select(recipetype_recipe_list_sql, (arg_dict.get('id')))
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

    async def test_recipetype_list():
        res = await recipetype_list(1,10)
        print(res)

    async def test_sql_like():
        # 测试 like 模糊搜索
        recipetype_count_sql = '''
        select id from recipetype_info where title like ?
        '''
        res = await dbins.selectone(recipetype_count_sql, ("%我的新推荐分类%"))
        print(res)

    async def test_recipetype_recipe_list():
        res = await recipetype_recipe_list({'page':1,'limit':100,'id':1})
        print(res)

    async def test_recipetype_set():
        res = await recipetype_set({"id":6, "status":0})

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_recipetype_set())
