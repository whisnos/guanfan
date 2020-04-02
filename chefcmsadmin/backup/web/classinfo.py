from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool.tooltime import curDatetime
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.classinfo')
dbins = DbOperate.instance()

class ClassInfoListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取菜谱步骤列表 '''
        # page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        # epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        blist = await classinfo_list(arg_key)
        d_status = {"code":200,"message":"操作成功"} # dtree 数据格式的问题
        return self.send_cms_msg(0, 'success', blist,status=d_status)

class ClassInfoAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await classinfo_add(arg_key)
        return self.send_cms_msg(code, msg)

class ClassInfoEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await classinfo_edit(arg_key)
        return self.send_cms_msg(code, msg)

class ClassInfoDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await classinfo_del(arg_key)
        return self.send_cms_msg(code, msg)

async def classinfo_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO class_info
    (
    classname,
    `type`,
    pid,
    iconimg,
    sort,
    status
    )
    VALUES
    (
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
        int(arg_dict.get('type')),
        arg_dict.get('id'),
        arg_dict.get('iconimg'),
        arg_dict.get('sort'),
        0,
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def classinfo_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE class_info
    set
    classname = ?,
    iconimg = ?,
    sort = ?,
    updatetime = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('title'),
        arg_dict.get('iconimg'),
        arg_dict.get('sort'),
        curDatetime(),
        arg_dict.get('id'),
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def classinfo_del(arg_dict):
    ''' 删除 '''

    del_current_id_sql = '''
delete from class_info where id in 
(select id from
(
select id from class_info
where id=?
UNION
select id from class_info
where pid=?
UNION 
select cli.id from
(select id,pid from class_info
where pid=?) as subinfo
inner join class_info as cli
on cli.pid = subinfo.id
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

async def classinfo_list(arg_dict):
    ''' 轮播列表, 页数,每页个数 '''
    classinfo_list_sql = '''
    select 
    id,
    classname,
    type,
    iconimg,
    pid,
    sort,
    status
    from class_info
    order by sort desc
    '''
    blist = await dbins.select(classinfo_list_sql, ())
    if blist is None:
        return []

    for csub in blist:
        # 数据格式转换成dtree格式
        # dtree格式：{"id":"001","title": "湖南省","checkArr": "0","parentId": "0"},
        # 数据库格式：{'id': 1, 'classname': '热门', 'type': 1, 'iconimg': None, 'pid': 0, 'sort': 999, 'status': 0}
        csub.setdefault("title",csub.pop('classname'))
        csub.setdefault("parentId",csub.pop('pid'))
        csub.setdefault("basicData",{
            "sort":csub.pop('sort'),
            "iconimg":csub.pop('iconimg'),
            "type":csub.pop('type')
            })

    return blist

        
if __name__ == '__main__':
    # async def test_logincms():
    #     res = await logincms('admin', '123123')
    #     print(res)

    # async def test_classinfo_list():
    #     res = await classinfo_list({})
    #     print(res)

    # import asyncio
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_classinfo_list())
    print(curDatetime())
    pass