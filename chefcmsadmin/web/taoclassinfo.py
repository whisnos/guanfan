from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool.tooltime import curDatetime
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.taoclassinfo')
dbins = DbOperate.instance()

class TaoClassInfoListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取菜谱步骤列表 '''
        # page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        # epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        blist = await taoclassinfo_list(arg_key)
        d_status = {"code":200,"message":"操作成功"} # dtree 数据格式的问题
        return self.send_cms_msg(0, 'success', blist,status=d_status)

class TaoClassInfoAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taoclassinfo_add(arg_key)
        return self.send_cms_msg(code, msg)

class TaoClassInfoEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taoclassinfo_edit(arg_key)
        return self.send_cms_msg(code, msg)

class TaoClassInfoDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await taoclassinfo_del(arg_key)
        return self.send_cms_msg(code, msg)

async def taoclassinfo_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO tao_channel_info
    (
    name,
    materialId,
    sort,
    iconImg,
    pid_id,
    pId,
    `level`
    )
    VALUES
    (
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
        arg_dict.get('name'),
        arg_dict.get('materialId'),
        arg_dict.get('sort'),
        arg_dict.get('iconImg'),
        arg_dict.get('pid_id'),
        arg_dict.get('pId'),
        int(arg_dict.get('level')),
    ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def taoclassinfo_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE tao_channel_info
    set
    name = ?,
    materialId = ?,
    iconImg = ?,
    sort = ?,
    is_banner = ?,
    recommendId = ?,
    is_top = ?,
    pid_id = ?,
    updatetime = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('name'),
        arg_dict.get('materialId'),
        arg_dict.get('is_banner'),
        arg_dict.get('recommendId'),
        arg_dict.get('is_top'),
        arg_dict.get('iconImg'),
        arg_dict.get('sort'),
        arg_dict.get('pid_id'),
        curDatetime(),
        arg_dict.get('id'),
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def taoclassinfo_del(arg_dict):
    ''' 删除 '''

    del_current_id_sql = '''
delete from tao_channel_info where id in 
(select id from
(
select id from tao_channel_info
where id=?
UNION
select id from tao_channel_info
where pid_id=?
UNION 
select cli.id from
(select id,pid_id from tao_channel_info
where pid_id=?) as subinfo
inner join tao_channel_info as cli
on cli.pid_id = subinfo.id
) tmp)
    '''
    del_id_result = await dbins.execute(del_current_id_sql,
        (
        arg_dict.get('id'),
        arg_dict.get('id'),
        arg_dict.get('id')
        ))

    if del_id_result is None:
        return 3001 , "删除当前分类失败"
    else:
        return 0, "成功"

async def taoclassinfo_list(arg_dict):
    ''' 轮播列表, 页数,每页个数 '''
    taoclassinfo_list_sql = '''
    select 
    id,
    name,
    materialId,
    is_banner,
    recommendId,
    level,
    iconImg,
    pId,
    pid_id,
    is_banner,
    recommendId,
    is_top,
    sort,
    status
    from tao_channel_info
    order by sort desc
    '''
    blist = await dbins.select(taoclassinfo_list_sql, ())
    if blist is None:
        return []

    for csub in blist:
        # 数据格式转换成dtree格式
        # dtree格式：{"id":"001","title": "湖南省","checkArr": "0","pId": "0"},
        # 数据库格式：{'id': 1, 'name': '热门', 'level': 1, 'iconimg': None, 'pid_id': 0, 'sort': 999, 'status': 0}
        csub.setdefault("title",csub.pop('name'))
        csub.setdefault("parentId",csub.pop('pId'))
        csub.setdefault("basicData",{
            # "id": csub.pop('id'),
            "pid_id": csub.pop('pid_id'),
            "sort": csub.pop('sort'),
            "materialId": csub.pop('materialId'),
            "is_banner": csub.pop('is_banner'),
            "iconImg": csub.pop('iconImg'),
            "recommendId": csub.pop('recommendId'),
            "is_top": csub.pop('is_top'),
            "level": csub.pop('level')
            })

    return blist

        
if __name__ == '__main__':
    # async def test_logincms():
    #     res = await logincms('admin', '123123')
    #     print(res)

    # async def test_taoclassinfo_list():
    #     res = await taoclassinfo_list({})
    #     print(res)

    # import asyncio
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_taoclassinfo_list())
    print(curDatetime())
    pass