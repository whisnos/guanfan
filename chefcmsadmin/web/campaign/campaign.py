from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict
from chefcmsadmin.tool.tooltime import curDatetime,nowDaysAfter


log = applog.get_log('web.campaign')
dbins = DbOperate.instance()

class CampaignListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取活动列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await campaign_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class CampaignAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加活动 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_add(arg_key)
        self.send_cms_msg(code, msg)

class CampaignEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改活动 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_edit(arg_key)
        self.send_cms_msg(code, msg)

class CampaignDeleteHandler(BaseHandler):
    ''' 删除活动 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_del(arg_key)
        self.send_cms_msg(code, msg)

class CampaignSetHandler(BaseHandler):
    ''' 设置活动 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_set(arg_key)
        self.send_cms_msg(code, msg)

async def campaign_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO campaign_info
    (
    name,
    starttime,
    endtime,
    createtime,
    updatetime
    )
    VALUES
    (
    ?,?,?,?,?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('name'),
        nowDaysAfter(10),
        nowDaysAfter(20),
        curDatetime(),
        curDatetime()
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def campaign_edit(arg_dict):
    ''' 修改 '''
    edit_sql = '''
    UPDATE campaign_info
    set
    userid = ?,
    title = ?,
    faceimg = ?,
    maininfourl = ?,
    introduction = ?
    where id = ?
    '''
    up_result = await dbins.execute(edit_sql, (
        arg_dict.get('userid'),
        arg_dict.get('title'),
        arg_dict.get('faceimg'),
        arg_dict.get('maininfourl'),
        arg_dict.get('introduction'),
        arg_dict.get('id'),
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"

async def campaign_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    UPDATE campaign_info
    SET status=-1
    where id = ?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id')
        ))
    if del_result is None:
        return 3002 , "删除失败"
    else:
        return 0 , "删除成功"

def campaign_set_string(arg_dict):
    ''' 返回搜索条件,arg_dict:所有请求的键值对数据,返回值 (1 where条件语句, 2 where条件对应的值) '''
    sql_update = []
    wvalue = []
    upid = 0
    if arg_dict.get('id'):
        # like 模糊搜索字段
        upid = arg_dict.get('id')
        arg_dict.pop('id')


    for k,v in arg_dict.items():
        if v!='':
            check_k = k.replace('_','') # 字段名只有'_' + 字母数字
            if check_k.isalnum():
                # 过滤 下划线后,只有数字和字母。合法的表名
                sql_update.append('{}=?'.format(k))
                wvalue.append(v)

    wvalue.append(upid)
    if len(sql_update)>0:
        return "{}".format(", ".join(sql_update)), wvalue
    else:
        return "",[]


async def campaign_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = campaign_set_string(arg_dict)
    up_sel = '''
    UPDATE campaign_info
    SET {}
    where id = ?
    '''.format(update_str)
    up_result = await dbins.execute(up_sel,
        (
        upvalue_list
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"


def campaign_search_string(arg_dict):
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

    sql_where.append('status!=-1')
    if len(sql_where)>0:
        return "where {}".format(" and ".join(sql_where)), wvalue
    else:
        return "",[]


async def campaign_list(arg_dict):
    ''' 活动列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = campaign_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    campaign_count_sql = '''select count(1) as ctnum from campaign_info {}'''.format(where_str)
    b_cnum = await dbins.selectone(campaign_count_sql, wvalue_list)

    if b_cnum is None:
        return 0, None

    if b_cnum.get('ctnum',0) == 0:
        return 0, None

        
    campaign_list_sql = '''
    SELECT
    *,
(
CASE
	WHEN UNIX_TIMESTAMP(starttime) > UNIX_TIMESTAMP(NOW()) THEN 0
	WHEN UNIX_TIMESTAMP(endtime) >= UNIX_TIMESTAMP(NOW()) AND UNIX_TIMESTAMP(starttime) <= UNIX_TIMESTAMP(NOW()) THEN 1
	WHEN UNIX_TIMESTAMP(endtime) < UNIX_TIMESTAMP(NOW()) AND UNIX_TIMESTAMP(NOW()) <= UNIX_TIMESTAMP(sel_starttime) THEN 2
    WHEN UNIX_TIMESTAMP(sel_endtime) >= UNIX_TIMESTAMP(NOW()) AND UNIX_TIMESTAMP(sel_starttime) <= UNIX_TIMESTAMP(NOW()) THEN 3
    WHEN UNIX_TIMESTAMP(sel_endtime) < UNIX_TIMESTAMP(NOW()) THEN 4
END
)AS statustime
    FROM
    campaign_info
    {}
    ORDER BY statustime asc, id desc
    LIMIT ?,?
    '''.format(where_str)
    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(campaign_list_sql, wvalue_list)

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

        sel_st = b.get('sel_starttime')
        b['sel_starttime'] = str(sel_st)

        sel_et = b.get('sel_endtime')
        b['sel_endtime'] = str(sel_et)
    return b_cnum.get('ctnum', 0), blist