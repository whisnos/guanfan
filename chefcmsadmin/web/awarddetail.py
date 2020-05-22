from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.recipestep')
dbins = DbOperate.instance()

class AwardDetailListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取奖品详情步骤列表 '''
        # page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        # epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        blist = await award_detail_list(arg_key)
        self.send_cms_msg(0, 'success', blist)

class AwardDetailAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加奖品详情步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_detail_add(arg_key)
        self.send_cms_msg(code, msg)

class AwardDetailEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改奖品详情步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_detail_edit(arg_key)
        self.send_cms_msg(code, msg)

class AwardDetailDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除奖品详情步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await award_detail_del(arg_key)
        self.send_cms_msg(code, msg)

async def award_detail_add(arg_dict):
    ''' 增加 '''
    recipe_exists_sql = '''select id from product_point_detail where id=? limit 1'''
    recipeid_exists_result = await dbins.selectone(recipe_exists_sql, (arg_dict.get('id')))

    # if recipeid_exists_result is None:
    #     return 3003, "奖品详情不存在"

    insert_sql='''
    INSERT INTO product_point_detail
    (
    product_point_id,
    image
    )
    VALUES
    (
    ?,
    ?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('id'),
        arg_dict.get('image')
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def award_detail_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE product_point_detail
    set
    image = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('image'),
        arg_dict.get('id')
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def award_detail_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    delete from product_point_detail where id = ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id')
        ))
    if del_result is None:
        return 3001 , "删除失败"
    else:
        return 0 , "删除成功"

def recipe_search_string(arg_dict):
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


async def award_detail_list(arg_dict):
    ''' 轮播列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',50))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = recipe_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    recipe_count_sql = '''select count(1) as ctnum from product_point_detail {}'''.format(where_str)
    b_cnum = await dbins.selectone(recipe_count_sql, wvalue_list)

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


    award_detail_list_sql = '''
    select 
    ppd.id,
    ppd.image,
    ppd.createTime,
    ppd.updatetime
    from product_point_detail ppd
		left JOIN product_point pp
		on pp.id = ppd.product_point_id
    where ppd.product_point_id = ?
    order by ppd.id
    limit ?,?
    '''
    blist = await dbins.select(award_detail_list_sql, (arg_dict.get('product_point_id'), page,epage))
    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updatetime')
        b['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return blist



if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)

    async def test_award_detail_list():
        res = await award_detail_list(1,10)
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_award_detail_list())
