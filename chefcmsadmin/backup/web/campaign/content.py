from chefcmsadmin.tool.basehandler import BaseHandler
from chefcmsadmin.tool.dbpool import DbOperate
from chefcmsadmin.tool import applog
from tornado.web import authenticated
from chefcmsadmin.tool.urlcommon import change_byte_to_dict
from chefcmsadmin.tool.tooltime import curDatetime,nowDaysAfter


log = applog.get_log('web.campaign.content')
dbins = DbOperate.instance()

class CampaignContentListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取活动内容内容列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await campaign_content_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class CampaignContentAddHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 增加活动内容 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_content_add(arg_key)
        self.send_cms_msg(code, msg)

class CampaignContentEditHandler(BaseHandler):
    @authenticated
    async def post(self):
        ''' 修改活动内容 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_content_set(arg_key)
        self.send_cms_msg(code, msg)

class CampaignContentDeleteHandler(BaseHandler):
    ''' 删除活动内容 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_content_del(arg_key)
        self.send_cms_msg(code, msg)


class CampaignJoinListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取活动参与列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await campaign_join_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)

class CampaignJoinDeleteHandler(BaseHandler):
    ''' 删除活动参与作品内容 '''
    @authenticated
    async def post(self):
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        code, msg = await campaign_join_del(arg_key)
        self.send_cms_msg(code, msg)

class CampaignPkListHandler(BaseHandler):
    @authenticated
    async def get(self):
        ''' 获取活动pk列表 '''
        arg_key = change_byte_to_dict(self.request.body, self.request.query)
        count, blist = await campaign_pk_list(arg_key)
        self.send_cms_msg(0, 'success', blist, count=count)


async def campaign_pk_list(arg_dict):
    ''' 活动内容列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = campaign_content_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    campaign_count_sql = '''select count(1) as ctnum from campaign_join {}'''.format(where_str)
    # print(campaign_count_sql, arg_dict)
    b_cnum = await dbins.selectone(campaign_count_sql, wvalue_list)

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
        
    campaign_list_sql = '''
    SELECT
    *
    FROM
    campaign_join
    {}
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

    return b_cnum.get('ctnum', 0), blist

async def campaign_join_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    DELETE FROM campaign_join
    where id = ? AND joinid=?
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id'),
        arg_dict.get('joinid')
        ))
    if del_result is None:
        return 3002 , "删除失败"
    else:
        return 0 , "删除成功"

def campaign_join_recipe_search_string(arg_dict):
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

async def campaign_join_list(arg_dict):
    '''
    参与活动的菜谱列表
    '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = campaign_join_recipe_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    campaign_count_sql = '''select count(1) as ctnum from campaign_join {}'''.format(where_str)
    # print(campaign_count_sql, arg_dict)
    b_cnum = await dbins.selectone(campaign_count_sql, wvalue_list)

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
    if arg_dict.get('jointype') == '2':
        # 获取参与菜谱
        campaign_join_list_sql = '''
            SELECT
                camjoin.*,
                reci.title AS title,
                reci.faceImg AS img,
                reci.collectionCount AS cnum 
            FROM
                ( SELECT id, userid, jointype, joinid FROM campaign_join {} LIMIT ?, ? ) camjoin
                LEFT JOIN recipe_info AS reci ON camjoin.joinid = reci.id 
                AND reci.`status` = 1 
                AND reci.isEnable = 1
        '''.format(where_str)
    else:
        campaign_join_list_sql = '''
            SELECT
                camjoin.*,
                dt.momentsDescription AS title,
                dt.momentsImgUrl AS img,
                dt.likeCount AS cnum
            FROM
                ( SELECT id, userid, jointype, joinid FROM campaign_join {} LIMIT ?, ? ) camjoin
                LEFT JOIN moments_info AS dt ON camjoin.joinid = dt.id 
                AND dt.`status` = 0
        '''.format(where_str)

    wvalue_list.append(page)
    wvalue_list.append(epage)
    blist = await dbins.select(campaign_join_list_sql, wvalue_list)

    if blist is None:
        return 0, []

    # for b in blist:
    #     ct = b.get('createtime')
    #     b['createtime'] = str(ct)

    return b_cnum.get('ctnum', 0), blist

async def campaign_content_add(arg_dict):
    ''' 增加 '''
    insert_sql='''
    INSERT INTO campaign_content
    (
    campaignid,
    type,
    imgurl,
    imgstyle,
    navid,
    navtype,
    extra,
    createtime
    )
    VALUES
    (
    ?,?,?,?,?,?,?,?
    )
    '''
    insert_result = await dbins.execute(insert_sql, (
        arg_dict.get('campaignid'),
        arg_dict.get('type'),
        arg_dict.get('imgurl'),
        arg_dict.get('imgstyle'),
        0 if arg_dict.get('navid') == '' else arg_dict.get('navid'),
        0 if arg_dict.get('navtype') == '' else arg_dict.get('navtype'),
        arg_dict.get('extra'),
        curDatetime()
        ))
    if insert_result is None:
        return 3001 , "添加失败"
    else:
        return 0, "添加成功"

async def campaign_content_del(arg_dict):
    ''' 删除 '''
    del_sql = '''
    DELETE FROM campaign_content
    where id = ? AND campaignid=? 
    '''
    del_result = await dbins.execute(del_sql,
        (
        arg_dict.get('id'),
        arg_dict.get('campaignid')
        ))
    if del_result is None:
        return 3002 , "删除失败"
    else:
        return 0 , "删除成功"

def campaign_content_set_string(arg_dict):
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


async def campaign_content_set(arg_dict):
    ''' 更新 '''
    update_str, upvalue_list = campaign_content_set_string(arg_dict)
    up_sel = '''
    UPDATE campaign_content
    SET {}
    where id = ?
    '''.format(update_str)

    # print(up_sel,update_str, upvalue_list)
    up_result = await dbins.execute(up_sel,
        (
        upvalue_list
        ))
    if up_result is None:
        return 3001 , "更新失败"
    else:
        return 0 , "更新成功"


def campaign_content_search_string(arg_dict):
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


async def campaign_content_list(arg_dict):
    ''' 活动内容列表, 页数,每页个数 '''
    pagenum = int(arg_dict.get('page',1))
    epage = int(arg_dict.get('limit',10))
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage

    where_str, wvalue_list = campaign_content_search_string(arg_dict)
    # log.warning("{},{}".format(where_str, wvalue_list))
    campaign_count_sql = '''select count(1) as ctnum from campaign_content {}'''.format(where_str)
    # print(campaign_count_sql, arg_dict)
    b_cnum = await dbins.selectone(campaign_count_sql, wvalue_list)

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
        
    campaign_list_sql = '''
    SELECT
    *
    FROM
    campaign_content
    {}
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
    return b_cnum.get('ctnum', 0), blist

if __name__ == '__main__':
    pass