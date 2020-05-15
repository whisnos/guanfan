from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict

log = applog.get_log('web.taobanner')
dbins = DbOperate.instance()

class TaoBannerListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取轮播列表 '''
        # page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        # epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # self.get_argument('limit')
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await taobanner_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


class TaoBannerAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加轮播 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taobanner_add(arg_key)
        self.send_cms_msg(code, msg)


class TaoBannerEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改轮播 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taobanner_edit(arg_key)
        self.send_cms_msg(code, msg)


class TaoBannerDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除轮播 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taobanner_del(arg_key)
        self.send_cms_msg(code, msg)

async def taobanner_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO taobanner
    (
    title,
    taobannerimg,
    linkurl,
    recipeid,
    type,
    sort,
    channel,
    status
    )
    VALUES
    (
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('title'),
        arg_dict.get('taobannerimg'),
        arg_dict.get('linkurl'),
        arg_dict.get('recipeid'),
        arg_dict.get('type'),
        arg_dict.get('sort'),
        arg_dict.get('channel'),
        1 if arg_dict.get('status') == "on" else 0,
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def taobanner_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE taobanner
    set
    title = ?,
    taobannerimg = ?,
    linkurl = ?,
    recipeid = ?,
    type = ?,
    sort = ?,
    channel = ?,
    status = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('title'),
        arg_dict.get('taobannerimg'),
        arg_dict.get('linkurl'),
        arg_dict.get('recipeid'),
        arg_dict.get('type'),
        arg_dict.get('sort'),
        arg_dict.get('channel'),
        1 if arg_dict.get('status') == "on" else 0,
        arg_dict.get('id')
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def taobanner_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE taobanner
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

def taobanner_search_string(arg_dict):
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

async def taobanner_list(arg_dict):
    ''' 轮播列表, 页数,每页个数, channel 频道默认 = 0 '''
    # print(arg_dict)
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = taobanner_search_string(arg_dict)
    taobanner_count_sql = '''select count(1) as ctnum from topic_info {}'''.format(where_str)
    b_cnum = await dbins.selectone(taobanner_count_sql, wvalue_list)
    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum',0) == 0:
        return 0, None

    taobanner_list_sql = '''
    select id, title, img, content, sort, status, createTime
    from tao_banner_info
    where `status`!=-1
    order by id desc
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(taobanner_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    for b in blist:
        ct = b.get('createTime')
        b['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return b_cnum.get('ctnum', 0), blist



if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)

    async def test_taobannerlist():
        res = await taobanner_list({'page':1})
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_taobannerlist())
