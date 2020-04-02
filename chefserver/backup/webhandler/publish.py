import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo
from chefserver.webhandler.myspace import get_relationship_status
from chefserver.webhandler.search import get_similar_recipe_tagkey
from chefserver.webhandler.campaign.campaignjoin import recipe_campaign_join, moment_campaign_join
from chefserver.webhandler.video.aliyunmediaapi import get_video_history, update_video_history
log = applog.get_log('webhandler.publish')
dbins = DbOperate.instance()


class PushRecipeHandler(BaseHandler):
    ''' 发布菜谱 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        # recip_optype  = self.verify_arg_legal(self.get_body_argument(型', False, is_len=True, olen=1, is_num=True)
        recip_optype = self.verify_arg_legal(self.get_body_argument('type'), '操作类型', False, uchecklist=True, user_check_list=['1', '2'])
        finish_img = self.verify_arg_legal(self.get_body_argument('cpimg'), '封面图片', False, is_len=True, olen=255)
        self.verify_arg_legal(finish_img, '封面图片', is_not_null=True, img=True)
        title = self.verify_arg_legal(self.get_body_argument('title'), '食谱名称', True, is_len=True, olen=100)
        story = self.verify_arg_legal(self.get_body_argument('story'), '菜的故事', True, is_len=True, olen=300)
        difficult = self.verify_arg_legal(self.get_body_argument('difficult'), '难度', False, is_len=True, olen=10, uchecklist=True, user_check_list=['入门', '中级', '高级'])
        spendtime = self.verify_arg_legal(self.get_body_argument('spendtime'), '耗时', False, is_len=True, olen=30, uchecklist=True, user_check_list=['10分钟以下', '10~30分钟', '30~60分钟', '1小时以上'])
        stuff_str = self.verify_arg_legal(self.get_body_argument('stuff'), '材料', True)
        step_str = self.verify_arg_legal(self.get_body_argument('step'), '步骤', True)
        campaignid = None
        try:
            campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        except tornado.web.MissingArgumentError as mise:
            log.error(mise)
        if title == '':
            return self.send_message(False, 1005, '食谱名称不能为空')

        if stuff_str == '':
            return self.send_message(False, 1001, '材料数据为空')

        if step_str == '':
            return self.send_message(False, 1002, '步骤数据为空')

        stuff_str = self.verify_arg_legal(
            stuff_str, '材料内容', True, is_len=True, olen=500)

        setup_list = step_str.split('|')
        for stl in setup_list:
            stl = stl.strip()
            if stl == '':
                continue
            slist = stl.split('#')
            # slist 0 sort 1 img 2 descrition

            if len(slist) != 3:
                return self.send_message(False, 1003, '菜谱步骤数据异常,缺少:步骤,图片,或描述')

            if slist[1] == 'null' or slist[1] == 'undefined':
                slist[1] = ''

            if slist[1] != '':
                self.verify_arg_legal(
                    slist[1], '步骤图片', is_not_null=True, img=True)
            # self.verify_arg_legal(stl, '菜谱步骤', True, is_len=True, olen=200)

        tip = self.verify_arg_legal(self.get_body_argument('tip'), '小贴士', True, is_len=True, olen=300)
        ispushweb = self.verify_arg_legal(self.get_body_argument('ispushweb'), '是否独家发布', False, is_num=True)
        ispushdt = self.verify_arg_legal(self.get_body_argument('ispushdt'), '是否发布动态', False, is_num=True)

        # print(setup_list)
        sucess, code, ins_id = await publish_recipe(userid, recip_optype, finish_img, title, story, difficult, spendtime, stuff_str, setup_list, tip, ispushweb, ispushdt)
        if sucess is False:
            # 菜谱保存失败
            return self.send_message(sucess, code, ins_id)

        step_sucess, step_code, ok_ins_step = await insert_recipe_step(ins_id, setup_list)

        if step_sucess is False:
            # 菜谱步骤保存失败
            # 将已插入的菜谱数据设置为删除状态
            d_res = await delete_recipe(userid, ins_id)
            if d_res:
                return self.send_message(step_sucess, step_code, ok_ins_step)
            else:
                # 菜谱删除状态设置失败
                return self.send_message(step_sucess, 3014, '菜谱步骤保存失败,菜谱数据更新失败')

        if recip_optype == '1':
            # 保存草稿, 不生成动态
            if campaignid is not None:
                # 参与活动, 草稿只添加记录不返回参与成功记录
                await recipe_campaign_join(userid, campaignid, ins_id)
            return self.send_message(sucess, code, '保存草稿成功')

        await CacheUserinfo(userid).set_shipu(1)  # 食谱缓存数量+1
        if ispushdt == '0':
            # 不生成动态
            if campaignid is not None:
                # 参与活动
                self.send_message(*await recipe_campaign_join(userid, campaignid, ins_id))

            return self.send_message(sucess, code, '发布菜谱成功')
        else:
            # 生成动态
            pdt_sucess, pdt_code, pdt_info, insert_id = await publish_dongtai(userid, story, 1, ins_id, finish_img)

            if campaignid is not None:
                # 参与活动
                self.send_message(*await recipe_campaign_join(userid, campaignid, ins_id))

            if pdt_sucess:
                # 动态生成成功
                return self.send_message(True, 0, '发布菜谱成功, 动态生成成功')
            else:
                return self.send_message(True, 0, '发布菜谱成功, 动态生成异常, 请重新发布动态')


class EditRecipesubmitHandler(BaseHandler):
    ''' 编辑发布菜谱 '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        cpid = self.verify_arg_legal(self.get_body_argument('cpid'), '菜谱ID', False, is_num=True)
        recip_optype = self.verify_arg_legal(self.get_body_argument('type'), '操作类型', False, uchecklist=True, user_check_list=['1', '2'])
        finish_img = self.verify_arg_legal(self.get_body_argument('cpimg'), '封面图片', False, is_len=True, olen=255)
        title = self.verify_arg_legal(self.get_body_argument('title'), '食谱名称', True, is_len=True, olen=100)
        story = self.verify_arg_legal(self.get_body_argument('story'), '菜的故事', True, is_len=True, olen=300)
        difficult = self.verify_arg_legal(self.get_body_argument('difficult'), '难度', False, is_len=True, olen=10, uchecklist=True, user_check_list=['入门', '中级', '高级'])
        spendtime = self.verify_arg_legal(self.get_body_argument('spendtime'), '耗时', False, is_len=True, olen=30, uchecklist=True, user_check_list=['10分钟以下', '10~30分钟', '30~60分钟', '1小时以上'])
        stuff_str = self.verify_arg_legal(self.get_body_argument('stuff'), '材料', True)
        step_str = self.verify_arg_legal(self.get_body_argument('step'), '步骤', True)
        self.verify_arg_legal(finish_img, '封面图片', is_not_null=True, img=True)

        if title == '':
            return self.send_message(False, 1005, '食谱名称不能为空')

        if stuff_str == '':
            return self.send_message(False, 1001, '材料数据为空')

        if step_str == '':
            return self.send_message(False, 1002, '步骤数据为空')

        stuff_str = self.verify_arg_legal(stuff_str, '材料内容', True, is_len=True, olen=500)

        setup_list = step_str.split('|')
        for stl in setup_list:
            stl = stl.strip()
            if stl == '':
                continue
            slist = stl.split('#')
            # slist 0 sort 1 img 2 descrition
            if len(slist) != 3:
                return self.send_message(False, 1003, '菜谱步骤数据异常,缺少:步骤,图片,或描述')

            if slist[1] == 'null' or slist[1] == 'undefined':
                slist[1] = ''

            if slist[1] != '':
                self.verify_arg_legal(
                    slist[1], '步骤图片', is_not_null=True, img=True)
            # self.verify_arg_legal(stl, '菜谱步骤', True, is_len=True, olen=200)

        tip = self.verify_arg_legal(self.get_body_argument('tip'), '小贴士', True, is_len=True, olen=300)
        ispushweb = self.verify_arg_legal(self.get_body_argument('ispushweb'), '是否独家发布', False, is_num=True)
        ispushdt = self.verify_arg_legal(self.get_body_argument('ispushdt'), '是否发布动态', False, is_num=True)

        sucess, code, msg = await recipe_edit_submit(cpid, userid, recip_optype, finish_img, title, story, difficult, spendtime, stuff_str, setup_list, tip, ispushweb, ispushdt)
        if sucess is False:
            # 菜谱更新失败
            return self.send_message(sucess, code, msg)

        # 更新菜谱成功,更新菜谱步骤
        d_res = await delete_step_recipe(cpid)
        if d_res is False:
            # 删除报错,
            return self.send_message(False, 3012, '菜谱步骤数据更新失败,请重试')

        step_sucess, step_code, ok_ins_step = await insert_recipe_step(cpid, setup_list)

        if step_sucess is False:
            # 菜谱步骤保存失败
            # 将已插入的菜谱数据设置为删除状态
            return self.send_message(step_sucess, 3013, '菜谱步骤保存失败,菜谱数据更新失败')

        await CacheUserinfo(userid).get_shipu(force_update=True)  # 食谱缓存数量获取最新值
        if recip_optype == '1':
            # 保存草稿, 不生成动态
            return self.send_message(sucess, code, '保存草稿成功!')

        if ispushdt == '0':
            # 不生成动态
            return self.send_message(sucess, code, '发布菜谱成功')
        else:
            # 生成动态
            pdt_sucess, pdt_code, pdt_info, insert_dt_sql = await publish_dongtai(userid, story, 1, cpid, finish_img)
            if pdt_sucess:
                # 动态生成成功
                return self.send_message(True, 0, '发布菜谱成功, 动态生成成功')
            else:
                return self.send_message(True, 0, '发布菜谱成功, 动态生成异常, 请重新发布动态')


class PushDongtaiHandler(BaseHandler):
    ''' 发布动态(图片) '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        dt_type = self.verify_arg_legal(self.get_body_argument('type'), '动态类型', False, uchecklist=True, user_check_list=['0', '1', '2', '3'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '关联作品', False, is_len=True, olen=20)
        description = self.verify_arg_legal(self.get_body_argument('description'), '动态描述', True, is_len=True, olen=800)
        dtimgall = self.get_body_argument('dtimg')
        dtimgall = self.verify_arg_legal(dtimgall, '图片地址', False, is_len=True, olen=1000)
        # videourl = self.verify_arg_legal(self.get_body_argument('videourl'), '视频地址', True, is_len=True, olen=255)
        videourl = ''
        campaignid = None  # 活动ID

        if dtimgall == '' and description == '':
            return self.send_message(False, 1010, '图片或文字必须有一项不为空')

        if dtimgall == '' and videourl == '':
            return self.send_message(False, 1010, '图片或食谱必须有一项不为空')

        if dtimgall != '':
            for iimg in dtimgall.split('|'):
                self.verify_arg_legal(iimg, '动态图片', img=True)
            try:
                campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
            except tornado.web.MissingArgumentError as mise:
                log.error(mise)

        if dt_type == '0':
            # 纯动态,itemid为0
            itemid = 0

        success, code, message, insert_dt_id = await publish_dongtai(userid, description, dt_type, itemid, dtimgall, videourl)
        if success:
            if campaignid is not None:
                # 参与活动
                self.send_message(*await moment_campaign_join(userid, campaignid, insert_dt_id))
        return self.send_message(success, code, message)


class PushVideoDongtaiHandler(BaseHandler):
    ''' 发布动态(视频) '''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        dt_type = self.verify_arg_legal(self.get_body_argument('type'), '动态类型', False, uchecklist=True, user_check_list=['0', '1', '2', '3'])
        itemid = self.verify_arg_legal(self.get_body_argument('itemid'), '关联作品', False, is_len=True, olen=20)
        description = self.verify_arg_legal(self.get_body_argument('description'), '动态描述', True, is_len=True, olen=800)
        videoid = self.verify_arg_legal(self.get_body_argument('videoid'), '视频ID', False, is_len=True, olen=50)
        campaignid = None  # 活动ID

        if videoid == '':
            self.send_message(False, '1013', '视频ID不能为空')

        try:
            campaignid = self.verify_arg_legal(self.get_body_argument('campaignid'), '活动ID', False, is_num=True)
        except tornado.web.MissingArgumentError as mise:
            log.error(mise)

        if dt_type == '0':
            # 纯动态,itemid为0
            itemid = 0

        success, code, message, insert_dt_id = await publish_video_dongtai(userid, description, videoid, dt_type, itemid)
        if success:
            if campaignid is not None:
                # 参与活动
                print(success, code, message, insert_dt_id)
                self.send_message(*await moment_campaign_join(userid, campaignid, insert_dt_id))
        self.send_message(success, code, message)


async def publish_video_dongtai(userid, dtinfo, videoid, dt_type=0, itemid=0):
    ''' 发布视频动态 '''
    video_info = await get_video_history(videoid, userid)
    if video_info is None:
        return False, 1014, '视频ID不存在', 0

    insert_dt_sql = '''INSERT INTO moments_info 
    (`userId`, `momentsDescription`, `type`, `itemId`, `likeCount`, `status`, `isvideo`)
    VALUES 
    (?,        ?,                     ?,      ?,         ?,         ?, 1)
    '''

    sqllist = []
    sqllist.append(
        (insert_dt_sql, (userid, dtinfo, dt_type, itemid, 0, 0)))
    sqllist.append(('select last_insert_id()', ()))


    result = await dbins.execute_many(sqllist)

    # result = await dbins.execute(insert_dt_sql, (userid, dtinfo, imgliststr, videourl, dt_type, itemid, 0, 0))
    if result is None:
        # 动态发布失败
        log.error('视频动态发布失败,sql:{},{}'.format(insert_dt_sql,
                                            (userid, dtinfo, dt_type, itemid, 0, 0)))
        return False, 3016, '视频动态发布失败', 0
    else:
        await CacheUserinfo(userid).set_dongtai(1)  # 动态缓存数量+1
        ins_id = result[1][1][0]  # 返回第二条,第二列,第一个列的ID 获取插入的ID
        if video_info.get('status') > 1:
            # 阿里云已回调处理过视频, 那么更新视频地址和封面
            sql_base = "update moments_info set momentsVideoUrl=?,momentsImgUrl=? where id=?"
            up_video = await dbins.execute(sql_base, (video_info.get('fileurl'), video_info.get('coverurl'), ins_id))
            if up_video is None:
                await delete_dongtai(userid, ins_id)
                return False, 3018, "更新视频信息失败,请重试", None

        video_up_res = await update_video_history(videoid, 1, itemid=ins_id)
        if video_up_res is None:
            # 更新视频ID失败, 删除动态
            await delete_dongtai(userid, ins_id)
            return False, 3017, "更新视频状态失败,请重试", None
        return True, 0, '发布成功', ins_id


async def delete_recipe(userid, recipeid):
    ''' 删除菜谱(设置标志位) '''
    recipe_status_sql = '''
    SELECT id,status FROM recipe_info WHERE id = ? AND userid = ? LIMIT 1
    '''
    caipu_status_result = await dbins.selectone(recipe_status_sql, (recipeid, userid))

    if caipu_status_result is None:
        # 没有返回数据或者执行错误
        return False
    cpstatus = caipu_status_result.get('status', -1)
    up_sql = 'UPDATE recipe_info set status=-1 where id=? and userid=?'
    result = await dbins.execute(up_sql, (recipeid, userid))
    if result is None:
        return False
    else:
        if result == 1 and cpstatus != 2 and cpstatus != - 1:
            await CacheUserinfo(userid).set_shipu(-1)  # 食谱缓存数量-1
        return True


async def delete_dongtai(userid, dtid):
    ''' 删除动态(设置标志位) '''
    up_sql = 'UPDATE moments_info set status=-1 where id=? and userid=?'
    result = await dbins.execute(up_sql, (dtid, userid))
    if result is None:
        return False
    else:
        if result == 1:
            await CacheUserinfo(userid).set_dongtai(-1)  # 食谱缓存数量-1
        return True


async def publish_dongtai(userid, dtinfo, dt_type=0, itemid=0, imgliststr=None, videourl=None):
    ''' 发布动态 '''
    insert_dt_sql = '''INSERT INTO moments_info 
    (`userId`, `momentsDescription`, `momentsImgUrl`, `momentsVideoUrl`, `type`, `itemId`, `likeCount`, `status`)
    VALUES 
    (?,        ?,                     ?,               ?,                  ?,      ?,         ?,         ?)
    '''
    # print(userid, dtinfo, imgliststr, videourl, dt_type, itemid, 0)

    sqllist = []
    sqllist.append(
        (insert_dt_sql, (userid, dtinfo, imgliststr, videourl, dt_type, itemid, 0, 0)))
    sqllist.append(('select last_insert_id()', ()))

    result = await dbins.execute_many(sqllist)

    # result = await dbins.execute(insert_dt_sql, (userid, dtinfo, imgliststr, videourl, dt_type, itemid, 0, 0))
    if result is None:
        # 动态发布失败
        log.error('动态发布失败,sql:{},{}'.format(insert_dt_sql,
                                            (userid, dtinfo, imgliststr, videourl, dt_type, itemid, 0)))
        return False, 3015, '动态发布失败', 0
    else:
        await CacheUserinfo(userid).set_dongtai(1)  # 食谱缓存数量+1
        ins_id = result[1][1][0]  # 返回第二条,第二列,第一个列的ID 获取插入的ID
        return True, 0, 'success', ins_id


async def publish_recipe(userid, recip_optype, finish_img, title, story, difficult, spendtime, stuff_all, setup_list, tip, ispushweb, ispushdt):
    ''' 发布菜谱 '''
    insert_sql = '''INSERT INTO recipe_info(
`userId`,
`title`,
`faceImg`,
`finishedProductImg`,
`mainInfoType`,
`introduction`,
`story`,
`oneClass`,
`twoClass`,
`tagClass`,
`tagKey`,
`difficult`,
`timeConsuming`,
`ingredientsList`,
`tips`,
`isExclusive`,
`isFeatured`,
`isEnable`,
`status`
)
values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
    # 判断是否需要审核
    recipe_review = await is_need_comfirm()
    recipe_status = 1 if recipe_review is False else 0  # 需要审核.状态设置为 0待审核, 否则 1 直接已审核通过
    if recip_optype == '1':
        # 保存草稿. 状态设置为草稿,
        recipe_status = 2
    else:
        # 发布, 根据前面的 recipe_review是否审核设置判定菜谱的状态
        pass

    oneclass = 1  # 主分类
    twoclass = 5  # 子分类
    taglass = ''  # 父类标签
    tagkey = ''  # 标签

    # 自动匹配标签
    similar_tagkey = await get_similar_recipe_tagkey(title)
    tagkey = similar_tagkey

    sqllist = []
    sqllist.append((insert_sql, (userid, title, finish_img,
                                 '', 1, None, story, oneclass, twoclass,
                                 taglass, tagkey,
                                 difficult, spendtime, stuff_all, tip,
                                 ispushweb, 0, 1, recipe_status)))
    sqllist.append(('select last_insert_id()', ()))

    dbresult = await dbins.execute_many(sqllist)
    if dbresult is None:
        # 执行dbresult
        log.error('菜谱发布失败,sql:{}'.format(sqllist))

        return False, 3001, '菜谱保存失败,请重试'

    ins_id = dbresult[1][1][0]  # 返回第二条,第二列,第一个列的ID 获取插入的ID
    return True, 0, ins_id
    # dbsave = await dbins.execute(insert_sql,
    #     (userid, title, finish_img,
    #      '', 1, None, story, oneclass, twoclass,
    #     taglass, tagkey,
    #     difficult, spendtime, stuff_all, tip,
    #     ispushweb, 0, 1, recipe_status))
    # if dbsave is not None:
    #     return True, 0, '菜谱提交成功'
    # else:
    #     return False, 3001, '菜谱保存失败'


async def delete_step_recipe(cpid):
    ''' 删除旧步骤 '''
    d_sql = '''
    delete from recipe_step_info where recipeId=?;
    '''
    dbsave = await dbins.execute(d_sql, (cpid))
    if dbsave is None:
        return False
    else:
        return True


async def insert_recipe_step(recipe_id, step_list):
    ''' 插入菜谱步骤 '''
    insert_list = []
    for step in step_list:
        slist = step.split('#')
        insert_list.append((recipe_id, slist[1], slist[2], slist[0]))

    if len(insert_list) == 0:
        return True, 0, '步骤数据为空, 菜谱添加完成'
    else:
        insert_step_sql = 'INSERT INTO recipe_step_info (`recipeid`, `stepimg`, `description`, `sort`) values (?, ?, ?, ?)'
        dbsave = await dbins.executes(insert_step_sql, insert_list)
        if dbsave is None:
            log.error('菜谱发布失败,sql:{},{}'.format(insert_step_sql, insert_list))

            return False, 3001, '步骤数据保存失败,请检查步骤数据内容'
        else:
            return True, 0, 'success'


async def is_need_comfirm(re_type=1):
    ''' 是否需要审核, re_type = 1 食谱 或者 主题 '''
    if re_type == 1:
        res = await dbins.select('select recipeReview from sys_review_set order by id desc limit 1', ())
    else:
        res = await dbins.select('select topicReview from sys_review_set order by id desc limit 1', ())
    if len(res) > 0:
        if re_type == 1:
            # 菜谱审核
            if res[0].get('recipeReview') == 1:
                # 开启菜谱审核
                return True
            else:
                return False
        else:
            # 主题审核
            if res[0].get('topicReview') == 1:
                # 开启主题审核
                return True
            else:
                return False
    else:
        # 默认没有记录,选择直接审核通过
        return False


async def exists_recipe(cpid, userid):
    ''' 检查菜谱是否属于用户 '''
    exists_recipe_sql = '''
    select id from recipe_info where id = ? and userid = ? and status!=-1
    '''
    exists_recipe_res = await dbins.selectone(exists_recipe_sql, (cpid, userid))
    if exists_recipe_res is None:
        # 不存在或者错误的菜谱数据
        return False
    else:
        return True


async def recipe_edit_submit(cpid, userid, recip_optype, finish_img, title, story, difficult, spendtime, stuff_all, setup_list, tip, ispushweb, ispushdt):
    ''' 菜谱编辑提交 cpid, 菜谱ID, userid 用户ID, recip_optype=1 草稿,2发布'''
    exists_recipe_res = await exists_recipe(cpid, userid)
    if exists_recipe_res is False:
        return False, 1033, '错误的菜谱或用户数据'

    update_sql = '''
update recipe_info
set `title`= ?,
`faceImg`= ?,
`finishedProductImg`= ?,
`mainInfoType`= ?,
`introduction`= ?,
`story`= ?,
`difficult`= ?,
`timeConsuming`= ?,
`ingredientsList`= ?,
`tips`= ?,
`isExclusive`= ?,
`isFeatured`= ?,
`isEnable`= ?,
`status`= ?
where id = ? and userid = ? and status!=-1
'''
    # 判断是否需要审核
    recipe_review = await is_need_comfirm()
    recipe_status = 1 if recipe_review is False else 0  # 需要审核.状态设置为 0待审核, 否则 1 直接已审核通过
    if recip_optype == '1':
        # 保存草稿. 状态设置为草稿,
        recipe_status = 2
    else:
        # 发布, 根据前面的 recipe_review是否审核设置判定菜谱的状态
        pass

    args = (title,
            finish_img,
            '',
            1,
            None,
            story,
            difficult,
            spendtime,
            stuff_all,
            tip,
            ispushweb,
            0,
            1,
            recipe_status,  # 设置参数
            cpid,  # 菜谱ID
            userid  # 查询条件 用户ID
            )

    dbresult = await dbins.execute(update_sql, args)
    # print(dbresult,update_sql,args)
    if dbresult is None:
        # 执行dbresult
        return False, 3001, '菜谱保存失败,请重试'

    return True, 0, '更新成功'

if __name__ == '__main__':
    # async def test_publish_dongtai():
    #     ''' 测试发布菜谱 '''
    #     # userid, dtinfo, dt_type=0, itemid=0, imgliststr=None, videourl=None):
    #     res = await publish_dongtai(1, '这个菜,是南方的特色菜之一,主要的做法是炒', 1, 50099, 'http://www.xxx.com/xx1.jpg|http://www.xxx.com/xx2.jpg' )
    #     print(res)

    # import asyncio
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_publish_dongtai())
    pass
