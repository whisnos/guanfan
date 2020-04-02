from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.recipestep')
dbins = DbOperate.instance()

class RecipeStepListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取菜谱步骤列表 '''
        # page = self.verify_arg_legal(self.get_argument('page'), '页码', False, is_num=True)
        # epage = self.verify_arg_legal(self.get_argument('limit'), '每页数', False, is_num=True)
        # print(username, password)
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        blist = await recipe_step_list(arg_key)
        self.send_cms_msg(0, 'success', blist)

class RecipeStepAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipe_step_add(arg_key)
        self.send_cms_msg(code, msg)

class RecipeStepEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipe_step_edit(arg_key)
        self.send_cms_msg(code, msg)

class RecipeStepDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除菜谱步骤 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await recipe_step_del(arg_key)
        self.send_cms_msg(code, msg)

async def recipe_step_add(arg_dict):
    ''' 增加 '''
    recipe_exists_sql = '''select id from recipe_info where id=? limit 1'''
    recipeid_exists_result = await dbins.selectone(recipe_exists_sql, (arg_dict.get('id')))

    if recipeid_exists_result is None:
        return 3003, "菜谱不存在"

    insert_sql='''
    INSERT INTO recipe_step_info
    (
    recipeid,
    stepimg,
    description,
    sort
    )
    VALUES
    (
    ?,
    ?,
    ?,
    ?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('id'),
        arg_dict.get('stepimg'),
        arg_dict.get('description'),
        arg_dict.get('sort')
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def recipe_step_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE recipe_step_info
    set
    stepimg = ?,
    description = ?,
    sort = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('stepimg'),
        arg_dict.get('description'),
        arg_dict.get('sort'),
        arg_dict.get('id')
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def recipe_step_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    delete from recipe_step_info where id = ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id')
        ))
    if del_result is None:
        return 3001 , "删除失败"
    else:
        return 0 , "删除成功"

async def recipe_step_list(arg_dict):
    ''' 轮播列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',50))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    recipe_step_list_sql = '''
    select 
    id,
    stepimg,
    description,
    sort
    from recipe_step_info
    where recipeid = ?
    order by sort
    limit ?,?
    '''
    blist = await dbins.select(recipe_step_list_sql, (arg_dict.get('recipeid'), page,epage))
    if blist is not None:
        return blist
    else:
        return []


if __name__ == '__main__':
    async def test_logincms():
        res = await logincms('admin', '123123')
        print(res)

    async def test_recipe_step_list():
        res = await recipe_step_list(1,10)
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_recipe_step_list())
