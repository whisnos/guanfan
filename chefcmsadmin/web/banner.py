from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict

log = applog.get_log('web.banner')
dbins = DbOperate.instance()

class BannerListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取轮播列表 '''
        # page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        # epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # self.get_argument('limit')
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await banner_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


class BannerAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加轮播 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await banner_add(arg_key)
        self.send_cms_msg(code, msg)


class BannerEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改轮播 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await banner_edit(arg_key)
        self.send_cms_msg(code, msg)


class BannerDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除轮播 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await banner_del(arg_key)
        self.send_cms_msg(code, msg)

async def banner_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO banner
    (
    title,
    bannerimg,
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
        arg_dict.get('bannerimg'),
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

async def banner_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE banner
    set
    title = ?,
    bannerimg = ?,
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
        arg_dict.get('bannerimg'),
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

async def banner_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE banner
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

async def banner_list(arg_dict):
    ''' 轮播列表, 页数,每页个数, channel 频道默认 = 0 '''
    # print(arg_dict)
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    banner_count_sql = '''select count(1) as ctnum from banner where `status`!=-1 and channel= ?'''
    b_cnum = await dbins.selectone(banner_count_sql, (arg_dict.get('channel',0), ))
    # print(banner_count_sql,arg_dict.get('channel',0), b_cnum)
    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum',0) == 0:
        return 0, None

    banner_list_sql = '''
    select id, title, bannerimg, linkurl, type, recipeid, sort, channel, `status`, createtime
    from banner
    where `status`!=-1 and channel= ?
    order by sort desc, id desc
    limit ?,?
    '''
    blist = await dbins.select(banner_list_sql, (arg_dict.get('channel',0), page, epage))


    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')

    if blist is not None:
        return b_cnum.get('ctnum', 0), blist
    else:
        return 0, []


if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)

    async def test_bannerlist():
        res = await banner_list({'page':1})
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_bannerlist())
