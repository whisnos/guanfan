"""
# 主题模块
# 主题列表
# 添加主题
# 删除主题
# 编辑主题
"""
import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.common_action import is_my_id


log = applog.get_log('webhandler.mysbuject')
dbins = DbOperate.instance()

class MySubjectPublicListHandler(BaseHandler):
    ''' 主题公共列表 '''
    async def post(self):
        userid = self.verify_arg_legal(self.get_body_argument('userid'), '用户ID', False, is_num=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_subject_public_list(userid, int(page))
        return self.send_message(success, code, message, result)

class MySubjectListHandler(BaseHandler):
    ''' 主题列表 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_subject_list(myid, int(page))
        return self.send_message(success, code, message, result)


class MySubjectAddHandler(BaseHandler):
    ''' 主题添加 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        title = self.verify_arg_legal(self.get_body_argument('title'), '标题', is_sensword=True, is_len=True, olen=20, is_not_null=True)
        faceimg = self.verify_arg_legal(self.get_body_argument('topicimg'), '封面', is_sensword=False, is_len=True, olen=255, is_not_null=True)
        faceimg = faceimg.lower()
        if faceimg.startswith("{}/topic".format(myid)) is False:
            self.send_message(False, 1003, '封面图片数据错误', None)

        self.verify_arg_legal(faceimg.split('.')[-1], '封面图片文件格式',is_not_null=True, uchecklist=True, user_check_list=['jpg', 'jpeg', 'png', 'bmp'])

        introduction = self.verify_arg_legal(self.get_body_argument('introduction'), '介绍', is_sensword=True, is_len=True, olen=300, is_not_null=True)
        
        isEnable = 1 # 默认启用
        status = 1 # 默认审核 1 待审核 0 
        topic_type = 1 # 默认是图片 2 视频
        maininfourl = faceimg # 详情主图,默认一样
        relation_item = self.check_relation_recipe()
        if len(relation_item) == 0:
            self.send_message(False, 1008, "主题关联菜谱为空", None)
        # 校验,推荐主题列表:
        success, code, message, result = await add_subject(myid,
            title,
            faceimg,
            maininfourl,
            topic_type,
            introduction,
            status,
            isEnable,
            )

        if success:
            # 添加主题成功, result == 插入成功的ID
            relation_insert_result = await add_subject_relation_recipe(myid, result, relation_item)
            if relation_insert_result is False:
                self.send_message(False, 1009, "主题添加成功,添加关联菜谱失败", result)
            else:
                self.send_message(True, 0, "主题添加成功", result)
        else:
            self.send_message(success, code, message, result)

    def check_relation_recipe(self):
        ''' 校验关联菜谱数据格式,返回list '''
        relationrecipe = self.verify_arg_legal(self.get_body_argument('relationrecipe'), '推荐理由', is_sensword=True, is_not_null=True)
        relation_data = []
        relation_list = relationrecipe.split('|')
        for recipe in relation_list:
            reason_list = recipe.split('#')
            if len(reason_list) < 4:
                self.send_message(False, 1004, '推荐数据格式错误', result)
            self.verify_arg_legal(reason_list[0], '推荐关联ID',is_not_null=True, is_num=True)
            self.verify_arg_legal(reason_list[1], '推荐排序号',is_not_null=True, is_num=True)
            self.verify_arg_legal(reason_list[2], '推荐菜谱ID',is_not_null=True, is_num=True)
            self.verify_arg_legal(''.join(reason_list[3:]), '推荐理由', is_not_null=True, is_len=True, olen=100)
            relation_data.append([reason_list[0], reason_list[1], reason_list[2], ''.join(reason_list[3:])])
        return relation_data


class MySubjectEditHandler(BaseHandler):
    ''' 主题编辑 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        topicid = self.verify_arg_legal(self.get_body_argument('topicid'), '主题ID', False, is_num=True)
        title = self.verify_arg_legal(self.get_body_argument('title'), '标题', is_sensword=True, is_len=True, olen=20, is_not_null=True)
        faceimg = self.verify_arg_legal(self.get_body_argument('topicimg'), '封面', is_sensword=False, is_len=True, olen=255, is_not_null=True)
        faceimg = faceimg.lower()
        if faceimg.startswith("{}/topic".format(myid)) is False:
            self.send_message(False, 1003, '封面图片格式错误', None)

        self.verify_arg_legal(faceimg.split('.')[-1], '封面图片文件格式',is_not_null=True, uchecklist=True, user_check_list=['jpg', 'jpeg', 'png', 'bmp'])
        introduction = self.verify_arg_legal(self.get_body_argument('introduction'), '介绍', is_sensword=True, is_len=True, olen=300, is_not_null=True)
        maininfourl = faceimg
        topic_type = 1 # 默认是图片 2 视频
        relation_item_insert, relation_item_update = self.check_relation_recipe()
        # 更新主题
        success, code, message, result = await edit_subject(topicid, myid, title, faceimg, maininfourl, topic_type, introduction)
        if success:
            # 主题更新成功,更新或插入关联菜谱推荐
            relation_insert_result = await add_subject_relation_recipe(myid, topicid, relation_item_insert)
            relation_update_result = await edit_subject_relation_recipe(myid, topicid, relation_item_update)

            if relation_insert_result and relation_update_result:
                self.send_message(True, 0, "主题修改成功", result)
            elif relation_insert_result is False:
                self.send_message(False, 1009, "主题修改成功,添加关联菜谱失败", result)
            else:
                self.send_message(False, 1010, "主题修改成功,更新关联菜谱失败", result)
        else:
            self.send_message(success, code, message, result)

    def check_relation_recipe(self):
        ''' 校验关联菜谱数据格式,返回list '''
        relationrecipe = self.verify_arg_legal(self.get_body_argument('relationrecipe'), '推荐理由', is_sensword=True, is_not_null=True)
        relation_data_insert = []
        relation_data_update = []
        relation_list = relationrecipe.split('|')
        for recipe in relation_list:
            reason_list = recipe.split('#')
            if len(reason_list) < 4:
                self.send_message(False, 1004, '推荐数据格式错误', result)
            self.verify_arg_legal(reason_list[0], '推荐关联ID',is_not_null=True, is_num=True)
            self.verify_arg_legal(reason_list[1], '推荐排序号',is_not_null=True, is_num=True)
            self.verify_arg_legal(reason_list[2], '推荐菜谱ID',is_not_null=True, is_num=True)
            self.verify_arg_legal(''.join(reason_list[3:]), '推荐理由', is_not_null=True, is_len=True, olen=100)
            if reason_list[0] == '0':
                relation_data_insert.append([reason_list[0], reason_list[1], reason_list[2], ''.join(reason_list[3:])])
            else:
                relation_data_update.append([reason_list[0], reason_list[1], reason_list[2], ''.join(reason_list[3:])])
        return relation_data_insert, relation_data_update


class MySubjectDelHandler(BaseHandler):
    ''' 主题删除 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        topicid = self.verify_arg_legal(self.get_body_argument('topicid'), '主题ID', False, is_num=True)
        success, code, message, result = await del_subject(myid, topicid)
        return self.send_message(success, code, message, result)


class MySubjectDetailHandler(BaseHandler):
    ''' 主题详情 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        topicid = self.verify_arg_legal(self.get_body_argument('topicid'), '主题ID', False, is_num=True)
        success, code, message, result = await detail_subject(myid, topicid)
        return self.send_message(success, code, message, result)


class MySubjectDelRelationItemHandler(BaseHandler):
    ''' 删除推荐菜谱 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        topicid = self.verify_arg_legal(self.get_body_argument('topicid'), '主题ID', False, is_num=True)
        relationid = self.verify_arg_legal(self.get_body_argument('relationid'), '关联菜谱ID', False, is_num=True)
        success, code, message, result = await del_subject_relationitem(myid, topicid, relationid)
        return self.send_message(success, code, message, result)

async def detail_subject(myid, topicid):
    ''' 获取编辑详情 '''
    # 获取主题基本信息
    topic_base_sql =  '''
SELECT
    id,
    title,
    introduction,
    faceimg AS topicimg 
FROM
    topic_info 
WHERE
    id =? 
    AND userid =? 
    AND STATUS !=-1;
'''
    topic_base_result = await dbins.selectone(topic_base_sql, (topicid, myid))
    if topic_base_result is None:
        return False, 3008, '主题数据错误,请重试', None
    # print(topic_base_result)

    # 获取主题相关菜谱
    cplist = '''
SELECT
    topic_la.id,
    topic_la.recipeid,
    topic_la.reason,
    topic_la.sort,
    cpinfo.faceImg AS cpimg,
    cpinfo.title,
    cpinfo.collectionCount AS cpcollections 
FROM
    topic_recipe_relation AS topic_la
LEFT JOIN recipe_info AS cpinfo ON cpinfo.id = topic_la.recipeid 
    AND cpinfo.`status` = 1 
    AND cpinfo.isEnable =1
WHERE
        topic_la.topicId = ? 
ORDER BY
    topic_la.sort desc 
    LIMIT 30 
'''

    cplist_result = await dbins.select(cplist, (topicid))
    if cplist_result is None:
        return False, 3033, '获取主题相关菜谱数据错误', None

    topic_base_result.setdefault('cplist', cplist_result)

    return True, 0, 'success', topic_base_result


async def del_subject_relationitem(myid, topicid, relationid):
    ''' 删除推荐的菜谱 '''
    # 检查主题是否属于我
    is_my_topic = await is_my_id(myid, topicid, itemtype=3)
    if is_my_topic is False:
        # 不是自己的主题
        return False, 1008, "非法访问!!!", None

    item_del_sql = '''
    DELETE FROM topic_recipe_relation WHERE id=? AND topicid=?
    '''
    result = await dbins.execute(item_del_sql, (relationid, topicid))

    if result is None:
        return False, 3006, "删除失败,请重试", None
    elif result == 0:
        return False, 1001, "异常的数据,请检查", None
    elif result == 1:
        return True, 0, "删除成功", None
    else:
        log.error("删除参数值:{},{}".format(topicid, relationid))
        return True, 5001, "未知错误", None

async def edit_subject(topicid, myid, title, faceimg, maininfourl, topic_type, introduction):
    ''' 编辑个人发布的主题 '''
    is_my_topic = await is_my_id(myid, topicid, itemtype=3)
    if is_my_topic is False:
        # 不是自己的主题
        return False, 1008, "非法访问!!!", None
    edit_sql = '''
    UPDATE topic_info
    SET
    userid = ?,
    title = ?,
    faceimg = ?,
    maininfourl = ?,
    maininfotype= ?,
    introduction = ?,
    status = 1 # 编辑后,不需要重新审核，默认审核通过状态
    WHERE id = ? AND status!=-1
    '''
    up_result = await dbins.execute(edit_sql, (
        myid,
        title,
        faceimg,
        maininfourl,
        topic_type,
        introduction,
        topicid
        ))
    if up_result is None:
        return False, 3001 , "更新失败", None
    else:
        return True, 0, "更新成功", None


async def add_subject(myid, title, faceimg, maininfourl, topic_type, introduction, status, isEnable):
    ''' 添加个人发布的主题 '''
    insert_sql='''
    INSERT INTO topic_info
    (
    userid,
    title,
    faceimg,
    maininfourl,
    maininfotype,
    introduction,
    status,
    isenable
    )
    VALUES
    (
    ?,?,?,?,?,?,?,?
    )
    '''
    insert_tuple = (insert_sql,  (
        myid, title, faceimg, maininfourl, topic_type, introduction, status, isEnable))
    sqllist = []
    sqllist.append(insert_tuple)
    sqllist.append(('select last_insert_id()' ,()))
    insert_result = await dbins.execute_many(sqllist)
    # print(insert_result)
    # 返回值:[(1, None), (1, (12,))]
    if insert_result is None:
        return False, 3001 , "主题添加失败", None

    ins_id = insert_result[1][1][0] # 返回第二条,第二列,第一个列的ID 获取插入的ID

    return True, 0, "添加主题成功", ins_id

async def edit_subject_relation_recipe(myid, topic_id, relation_update_list):
    ''' 更新关联菜谱 topic_id 主题ID, relation_recipe_list = [id, sort ,recipeid, reason] 主题关联菜谱列表'''
    length = len(relation_update_list)
    if length == 0:
        # 没有需要更新的.返回成功
        return True

    update_sql = '''
    UPDATE topic_recipe_relation
    SET
    sort = ?,
    recipeid = ?,
    reason = ?
    WHERE id = ? AND topicid={};
    '''.format(topic_id)

    update_sql = update_sql * length # 根据更新的个数,执行多个update语句
    arg_list = list()
    for item in relation_update_list:
        relationid = item.pop(0)
        item.append(relationid)
        # 修改列表元素顺序:[sort, recipeid, reason, id]
        arg_list.extend(item)
    # print(arg_list)
    update_result = await dbins.execute(update_sql, arg_list)
    # print(update_result)
    if update_result is None:
        return False
    else:
        return True

async def add_subject_relation_recipe(myid, topic_id, relation_insert_list):
    ''' 添加关联菜谱,topic_id 主题ID, relation_insert_list = [id, sort ,recipeid, reason] 主题关联菜谱列表'''
    topic_exists_sql = '''
    SELECT id FROM topic_info WHERE id=? and userid=? LIMIT 1
    '''
    t_exists = await dbins.selectone(topic_exists_sql, (topic_id, myid))
    if t_exists is None:
        # 主题不存在
        return 1041,'错误的主题数据', None

    for i in relation_insert_list:
        # 第一列,关联ID换成, 主题ID,然后插入
        i[0] = topic_id


    insert_recipe_sql= '''
    INSERT INTO topic_recipe_relation
    (topicid,
    sort,
    recipeid,
    reason
    )
    VALUES(
    ?,
    ?,
    ?,
    ?
    )
    '''
    insert_result = await dbins.executes(insert_recipe_sql, relation_insert_list)
    if insert_result is None:
        return False
    else:
        return True

async def get_subject_public_list(userid, pagenum, epage=10):
    """ 
    获取个人主题公共列表 
    """
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql = '''
SELECT
    id AS topicid,
    title,
    faceimg AS topicimg,
    visitcount AS visits,
    collectioncount AS collections,
    updatetime
FROM
    topic_info 
WHERE
    userid = ?
    AND isenable = 1
    AND status = 1
ORDER BY
    updatetime DESC 
    LIMIT ?,?
    '''
    result = await dbins.select(sql, (userid, page, epage))
    if result is None:
        return False, 3002, '获取数据错误', None

    for p in result:
        # ct = p.get('createtime')
        # p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = p.get('updatetime')
        p['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result

async def get_subject_list(myid, pagenum, epage=10):
    """ 
    获取个人主题列表 
    """
    page = 0 if pagenum-1 <= 0 else pagenum-1
    page = page*epage
    sql = '''
SELECT
    id AS topicid,
    title,
    status,
    faceimg AS topicimg,
    visitcount AS visits,
    collectioncount AS collections,
    updatetime
FROM
    topic_info 
WHERE
    userid = ?
    AND isenable = 1
    AND status != -1
ORDER BY
    updatetime DESC 
    LIMIT ?,?
    '''
    result = await dbins.select(sql, (myid, page, epage))
    if result is None:
        return False, 3002, '获取数据错误', None

    for p in result:
        # ct = p.get('createtime')
        # p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
        ut = p.get('updatetime')
        p['updatetime'] = ut.strftime('%Y-%m-%d %H:%M:%S')
    return True, 0, 'success', result


async def del_subject(myid, topicid):
    ''' 删除 '''
    del_sql = '''
    UPDATE topic_info
    SET status=-1
    WHERE id = ? AND userid=?
    '''
    del_result = await dbins.execute(del_sql,
        (
        topicid,
        myid
        ))
    if del_result is None:
        return False, 3001, "删除失败", None

    elif del_result == 0:
        return False, 1001, "错误的数据或异常的数据,请检查!", None
    else:
        return True, 0, "删除成功", None


if __name__ == '__main__':
    import asyncio

    async def test_get_subject_public_list():
        res = await get_subject_public_list(25,1)
        print(res)

    async def test_get_subject_list():
        res = await get_subject_list(25,1)
        print(res)

    async def test_del_subject():
        res = await del_subject(25,2)
        print(res)

    async def test_add_subject():
        #  myid, title, faceimg, maininfourl, topic_type, introduction, status, isEnable
        res = await add_subject(
            1,
            'hello',
            '1/topic/a/f/3/af988aa20eba80d719c0e438a92e43e3.jpg',
            '1/topic/a/f/3/af988aa20eba80d719c0e438a92e43e3.jpg',
            1,
            'introduction',
            0,
            0,
            []
            )
        print(res)

    async def test_del_subject_relationitem():
        res = await del_subject_relationitem(1,16,3)
        print(res)

    async def test_edit_subject_relation_recipe():
        update_list = [['200', '99', '10029', '圣诞节吃火鸡,感恩节的人们如何想象_edit'], 
        ['201', '98', '40015', '星期五的狂欢节吃啥才能抢的多_edit']]
        res = await edit_subject_relation_recipe(1,25,update_list)
        print(res)

    async def test_detail_subject():
        res = await detail_subject(25,1)
        print(res)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_subject_public_list())
    # loop.run_until_complete(test_get_subject_list())


