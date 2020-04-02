from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from chefcmsadmin.tool.tooltime import curDatetime
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.dongtai')
dbins = DbOperate.instance()

class DongtaiListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取动态列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await dongtai_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class DongtaiDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除动态 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await dongtai_del(arg_key)
        self.send_cms_msg(code, msg)

class DongtaiSetLikeHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 设置点赞数量 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await dongtai_set_like_num(arg_key)
        self.send_cms_msg(code, msg)


async def dongtai_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE moments_info
    SET status=-1,
        updatetime= ?
    where id = ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        curDatetime(),
        arg_dict.get('id')
        ))
    if del_result is None:
        return 3001 , "删除失败"
    else:
        return 0 , "删除成功"

async def dongtai_set_like_num(arg_dict):
    ''' 设置动态点赞数量 '''
    set_likenum_sql = '''
    UPDATE moments_info
    SET likeCount = ?
    where id = ?
    '''
    set_likenum_result = await dbins.execute(set_likenum_sql,
        (
        arg_dict.get('likeCount'),
        arg_dict.get('id')
        ))
    if set_likenum_result is None:
        return 3001 , "修改失败"
    else:
        return 0 , "修改成功"


def dongtai_search_string(arg_dict):
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

    if len(sql_where)>0:

        return "WHERE {}".format(" AND ".join(sql_where)), wvalue
    else:
        return "",[]


async def dongtai_list(arg_dict):
    ''' 轮播列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = dongtai_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    dongtai_count_sql = '''select count(1) as ctnum from moments_info {}'''.format(where_str)
    b_cnum = await dbins.selectone(dongtai_count_sql, wvalue_list)

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

    dongtai_list_sql = '''
    SELECT
    id,
    userid,
    momentsdescription,
    momentsimgurl,
    momentsvideourl,
    isvideo,
    type,
    itemid,
    likecount,
    status,
    updatetime,
    createtime
    FROM
    moments_info
    {}
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(dongtai_list_sql, wvalue_list)

    if blist is None:
        return 0, []
    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updatetime')
        b['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')

    return b_cnum.get('ctnum', 0), blist


if __name__ == '__main__':
    async def test_dongtai_list():
        # res = await dongtai_list(1,10) #旧参数
        # print(res)

        res = await dongtai_list({
            'page':'1',
            'limit':'10'}) #旧参数
        print(res)

        # res = await dongtai_list({
        #     'id':'1',
        #     'page':'1',
        #     'limit':'10'}) #旧参数
        # print(res)

    async def test_dongtai_set_like_num():
        res = await dongtai_set_like_num({
            'id':1,
            'likeCount':1091
            })
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_dongtai_set_like_num())
