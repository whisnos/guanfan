from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from chefcmsadmin.tool.tooltime import curDatetime
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict


log = applog.get_log('web.recipe')
dbins = DbOperate.instance()

class UserListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取用户列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await user_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class UserCheckHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 审核高级认证 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await user_check(arg_key)
        self.send_cms_msg(code, msg)


class UserVerifyInfoHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 高级认证内容返回 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg, result = await user_verify_info(arg_key)
        self.send_cms_msg(code, msg, result)

class UserPointEditListHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 设置点赞数量 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await user_set_point_count(arg_key)
        self.send_cms_msg(code, msg)

class UserPointAddListHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 设置点赞数量 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await user_add_point_count(arg_key)
        self.send_cms_msg(code, msg)


class UserDeleteHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 删除用户 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await user_del(arg_key)
        self.send_cms_msg(code, msg)

async def user_check(arg_dict):
    ''' 审核用户高级认证 '''
    up_user_verify_sql = '''
    UPDATE user
    SET
    certificationStatus =?,
    updatetime = ?
    WHERE id = ?
    '''
    up_user_result = await dbins.execute(up_user_verify_sql, (
        2 if arg_dict.get('verify') == '1' else 3, # 认证通过或者失败
        curDatetime(),
        arg_dict.get("userid")
        )
    )
    if up_user_result is None:
        return 3021, "更新用户认证状态失败"

    up_verify_sql = '''
    UPDATE certification_apply
    SET
    status = ?,
    updatetime = ?
    WHERE id = ?
    '''
    up_verify_result = await dbins.execute(up_verify_sql, (
        2 if arg_dict.get('verify') == '1' else -1, # 认证通过或者失败
        curDatetime(),
        arg_dict.get("id")
        )
    )
    if up_verify_result is None:
        return 3022, "更新用户认证资料状态失败"
    else:
        return 0, '更新成功'

async def user_verify_info(arg_dict):
    ''' 返回申请的内容 '''
    get_verify_sql = '''
    SELECT 
    id,
    userid,
    certifiedid,
    realname,
    phone,
    address,
    docurl,
    personalprofile,
    status,
    updatetime,
    createtime
    FROM certification_apply
    where userid = ? order by id desc limit 1
    '''
    verify_result = await dbins.selectone(get_verify_sql,
        (
        arg_dict.get('userid')
        ))
    if verify_result is None:
        return 0 , '没有内容或错误', None
    ct = verify_result.get('createtime')
    verify_result['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    ut = verify_result.get('updatetime')
    verify_result['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return 0, "返回成功", verify_result


async def user_del(arg_dict):
    ''' 修改用户状态 '''
    set_sql = '''
    UPDATE user
    SET status = ?,
    updatetime = ?
    WHERE id = ?
    '''
    set_result = await dbins.execute(set_sql,
        (
        0 if arg_dict.get('status') == '0' else -1,
        curDatetime(),
        arg_dict.get('id')
        ))
    if set_result is None:
        return 3001 , "修改失败"
    else:
        return 0 , "修改成功"

async def user_add_point_count(arg_dict):
    ''' 新增积分账户数量 '''
    print('---------start------user_add_point_count')
    add_pointcount_sql = '''
    INSERT INTO user_point
    (
        point,
        user_id
    )
    VALUES
    (
        ?,
        ?
    )
    '''
    add_pointcount_result = await dbins.execute(add_pointcount_sql,
        (
        arg_dict.get('grade_no'),
        arg_dict.get('id')
        ))

    insert_pointcount_sql = '''
    INSERT INTO user_pointbill
    (
        bill_type,
        grade_no,
        user_id
    )
    VALUES
    (
        ?,
        ?,
        ?
    )
    '''
    print("------------start_insert_pointcount_sql---------1111")
    insert_pointcount_result = await dbins.execute(insert_pointcount_sql,
                                                   (
                                                       arg_dict.get('bill_type'),
                                                       arg_dict.get('grade_no'),
                                                       arg_dict.get('id')
                                                   ))

    if (add_pointcount_result, insert_pointcount_result) is None:
        return 3001, "修改失败"
    else:
        return 0, "修改成功"

async def user_set_point_count(arg_dict):
    ''' 设置积分账户数量 '''
    print('---------start------user_set_point_count')
    set_pointcount_sql = '''
    UPDATE user_point
    SET point = ? + ?
    where user_id = ?
    '''
    print(arg_dict.get('bill_type'), 1111111111111)
    print(('-' + arg_dict.get('grade_no')), 11111122222222)
    if int(arg_dict.get('bill_type')) > 0:
        print(arg_dict.get('grade_no'), 343434343)
        set_pointcount_result = await dbins.execute(set_pointcount_sql,
            (
            arg_dict.get('point'),
            arg_dict.get('grade_no'),
            arg_dict.get('id')
            ))
    else:
        print(('-' + arg_dict.get('grade_no')), 23232323)
        set_pointcount_result = await dbins.execute(set_pointcount_sql,
            (
            arg_dict.get('point'),
            ('-' + arg_dict.get('grade_no')),
            arg_dict.get('id')
            ))

    insert_pointcount_sql = '''
    INSERT INTO user_pointbill
    (
        bill_type,
        grade_no,
        user_id
    )
    VALUES
    (
        ?,
        ?,
        ?
    )
    '''
    print("------------start_insert_user_pointbill_sql---------2222")
    insert_pointcount_result = await dbins.execute(insert_pointcount_sql,
        (
        arg_dict.get('bill_type'),
        arg_dict.get('grade_no'),
        arg_dict.get('id')
        ))

    if (set_pointcount_result, insert_pointcount_result) is None:
        return 3001 , "修改失败"
    else:
        return 0 , "修改成功"

def user_search_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    if arg_dict.get('page'):
        arg_dict.pop('page')
    if arg_dict.get('limit'):
        arg_dict.pop('limit')

    sql_where = []
    wvalue = []
    if arg_dict.get('username'):
        # like 模糊搜索字段
        t = arg_dict.get('username')
        wvalue.append('%' + t + '%')
        sql_where.append("title like ?")
        arg_dict.pop('username')

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


async def user_list(arg_dict):
    ''' 用户列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = user_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    recipe_count_sql = '''select count(1) as ctnum from user {}'''.format(where_str)
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
        
    recipe_list_sql = '''
    select
    DISTINCT u.id,
    username,
    headimg,
    mobile,
    up.point,
    sex,
    birthday,
    tag,
    taste,
    status,
    certificationstatus,
    address,
    personalprofile,
    u.updatetime,
    u.createtime
    from
    user u 
    left JOIN user_point up 
    on u.id = up.user_id
    {}
    limit ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(recipe_list_sql, wvalue_list)

    for b in blist:
        ct = b.get('createtime')
        b['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = b.get('updatetime')
        b['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')

    if blist is not None:
        return b_cnum.get('ctnum', 0), blist
    else:
        return 0, []

if __name__ == '__main__':
    async def test_recipe_list():
        # res = await recipe_list(1,10) #旧参数
        # print(res)

        res = await recipe_list({
            'page':'1',
            'limit':'10'}) #旧参数
        print(res)

    async def test_user_verify_info():
        res = await user_verify_info({'userid':5})
        print(res)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_user_verify_info())
