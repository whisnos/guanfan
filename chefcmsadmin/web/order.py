from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict

log = applog.get_log('web.order')
dbins = DbOperate.instance()


class OrderListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取兑换订单列表 '''
        page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await order_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


class OrderAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加兑换订单 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await order_add(arg_key)
        self.send_cms_msg(code, msg)


class OrderEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改兑换订单 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        # code, msg = await order_edit(arg_key)
        code, msg = await order_set(arg_key)

        self.send_cms_msg(code, msg)


class OrderDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除兑换订单 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await order_del(arg_key)
        self.send_cms_msg(code, msg)


async def order_add(arg_dict):
    ''' 增加 '''
    return 0, "空"
    # insert_sql='''
    # INSERT INTO banner
    # (
    # title,
    # bannerimg,
    # linkurl,
    # orderid,
    # type,
    # sort,
    # status
    # )
    # VALUES
    # (
    # ?,
    # ?,
    # ?,
    # ?,
    # ?,
    # ?,
    # ?
    # )
    # '''
    # insert_result = await dbins.execute(insert_sql, (
    #     arg_dict.get('title'),
    #     arg_dict.get('bannerimg'),
    #     arg_dict.get('linkurl'),
    #     arg_dict.get('orderid'),
    #     arg_dict.get('type'),
    #     arg_dict.get('sort'),
    #     1 if arg_dict.get('status') == "on" else 0,
    #     ))
    # if insert_result is None:
    #     return 3001 , "添加失败"
    # else:
    #     return 0, "添加成功"


async def order_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE my_exchange_info
    set
    userid = ?,
    title = ?,
    faceimg = ?,
    story = ?,
    tagKey = ?,
    difficult = ?,
    timeConsuming = ?,
    ingredientsList = ?,
    tips = ?,
    isExclusive = ?,
    isFeatured = ?,
    isEnable = ?,
    status = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get("userid"),
        arg_dict.get("title"),
        arg_dict.get("faceimg"),
        arg_dict.get("story"),
        arg_dict.get("tagKey"),
        arg_dict.get("difficult"),
        arg_dict.get("timeConsuming"),
        arg_dict.get("ingredientsList"),
        arg_dict.get("tips"),
        arg_dict.get("isExclusive"),
        arg_dict.get("isFeatured"),
        arg_dict.get("isEnable"),
        arg_dict.get("status"),
        arg_dict.get('id')
    ))
    if up_result is None:
        return 3001, "更新失败"
    else:
        return 0, "更新成功"


async def order_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE my_exchange_info
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


def order_search_string(arg_dict):
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
        wvalue.append(t)
        sql_where.append("MATCH (title, tagKey) AGAINST (? in boolean mode)")
        arg_dict.pop('title')

    if arg_dict.get('user_id'):
        arg_dict.update({'mha.user_id': arg_dict.pop("user_id")})

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


async def order_list(arg_dict):
    ''' 轮播列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page', 1))
    epage = int(arg_dict.get('limit', 10))
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage

    where_str, wvalue_list = order_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    order_count_sql = '''select 
    count(1) as ctnum from my_history_address mha
    LEFT JOIN my_exchange_info mei
    on mha.exchangeorder_id = mei.id {}'''.format(where_str)
    b_cnum = await dbins.selectone(order_count_sql, wvalue_list)

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

    # print(page, epage)
    order_list_sql = '''
    SELECT 
    mha.exchangeorder_id, 
    mha.user_id, 
    CONCAT_WS('---', u.headImg,u.userName,u.mobile) AS ume, 
    total.front_image, 
    total.grade_no, 
    CONCAT_WS('-', mha.name, mha.mobile, mha.province, mha.city, mha.area, mha.address) AS deliveryAddress, 
    total.remark, 
    total.createTime, 
    total.express_status, 
    total.logisticsInfo
    FROM my_history_address mha 
        LEFT JOIN user u
        ON mha.user_id = u.id
    LEFT JOIN
        (SELECT 
            mei.id, 
            pp.front_image, 
            pp.grade_no, 
            mei.remark, 
            mei.createTime, 
            mei.express_status, 
            CONCAT_WS('-', totalExp.createTime,totalExp.name, totalExp.express_no) as logisticsInfo
            FROM my_exchange_info mei
            LEFT JOIN product_point pp
            ON mei.product_point_id = pp.id
            LEFT JOIN 
                (SELECT 
                    mpi.id, 
                    ei.createTime, 
                    ei.name, 
                    mpi.express_no from my_express_info mpi 
                    LEFT JOIN 
                    express_info ei ON
                    mpi.express_info_id = ei.id 
                    ) AS totalExp
            ON mei.express_id = totalExp.id) AS total
    ON mha.exchangeorder_id = total.id
    {}
    ORDER BY mha.exchangeorder_id DESC
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(order_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        # ut = b.get('updatetime')
        # b['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist


def order_set_string(arg_dict):
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


async def order_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = order_set_string(arg_dict)
    up_sel = '''
    UPDATE my_exchange_info
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


if __name__ == '__main__':
    async def test_order_list():
        # res = await order_list(1,10) #旧参数
        # print(res)

        res = await order_list({
            'page': '1',
            'limit': '10'})  # 旧参数
        print(res)

        # res = await order_list({
        #     'id':'1',
        #     'page':'1',
        #     'limit':'10'}) #旧参数
        # print(res)


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_order_list())
