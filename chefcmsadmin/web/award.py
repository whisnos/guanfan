from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict
from chefcmsadmin.tool.tooltime import curDatetime, nowDaysAfter

log = applog.get_log('web.award')
dbins = DbOperate.instance()


class AwardListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取积分奖品列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await award_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


class AwardAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加积分奖品 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_add(arg_key)
        self.send_cms_msg(code, msg)


class AwardEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改积分奖品 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_edit(arg_key)
        self.send_cms_msg(code, msg)


class AwardDeleteHandler(BaseHandler):
    ''' 删除积分奖品 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_del(arg_key)
        self.send_cms_msg(code, msg)


class AwardSetHandler(BaseHandler):
    ''' 设置积分奖品 '''

    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_set(arg_key)
        self.send_cms_msg(code, msg)


async def award_add(arg_dict):
    ''' 增加 '''
    insert_sql = '''
    INSERT INTO product_point
    (
    title
    )
    VALUES
    (
    ?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('title'),
    ))
    if insert_result is None:
        return 3001, "添加失败"
    else:
        return 0, "添加成功"


async def award_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE product_point
    set
    front_image = ?,
    title = ?,
    grade_no = ?,
    sku_no = ?,
    sort = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('front_image'),
        arg_dict.get('title'),
        arg_dict.get('grade_no'),
        arg_dict.get('sku_no'),
        arg_dict.get('sort'),
        arg_dict.get('id'),
    ))
    if up_result is None:
        return 3001, "更新失败"
    else:
        return 0, "更新成功"


async def award_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE product_point
    SET status=-1
    where id = ?
    '''
    del_result = await dbins.execute(del_sql,
                                     (
                                         arg_dict.get('id')
                                     ))
    if del_result is None:
        return 3002, "删除失败"
    else:
        return 0, "删除成功"


def award_set_string(arg_dict):
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


async def award_set(arg_dict):
    ''' 设置上下架 '''
    update_str, upvalue_list = award_set_string(arg_dict)
    up_sel = '''
    UPDATE product_point
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


def award_search_string(arg_dict):
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

    sql_where.append('status!=-1')
    if len(sql_where) > 0:
        return "where {}".format(" and ".join(sql_where)), wvalue
    else:
        return "", []


async def award_list(arg_dict):
    ''' 积分奖品列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page', 1))
    epage = int(arg_dict.get('limit', 10))
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage

    where_str, wvalue_list = award_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    award_count_sql = '''select count(1) as ctnum from product_point {}'''.format(where_str)
    b_cnum = await dbins.selectone(award_count_sql, wvalue_list)

    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum', 0) == 0:
        return 0, None

    # 实现倒排,最新的在前面
    # page = int(b_cnum.get('ctnum', 0)) - page - epage
    # if page < 0:
    #     # 第一页, page设置为0, epage 设置为 abs(-8)
    #     epage = epage - abs(page)
    #     page = 0


    award_list_sql = '''
    SELECT
    id, 
    title, 
    front_image, 
    grade_no, 
    sku_no, 
    sort,
    status
    FROM
    product_point
    {}
    ORDER BY id 
    LIMIT ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(award_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = str(ct)

        ut = b.get('updatetime')
        b['updatetime'] = str(ut)

        st = b.get('starttime')
        b['starttime'] = str(st)

        et = b.get('endtime')
        b['endtime'] = str(et)
    return b_cnum.get('ctnum', 0), blist