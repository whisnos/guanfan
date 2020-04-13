from chefserver.webhandler.basehandler import BaseHandler
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog

log = applog.get_log('webhandler.food_channel')
dbins = DbOperate.instance()


class ChannelListHandler(BaseHandler):
    ''' 美食列表详情页 '''
    async def post(self):
        id = self.verify_arg_legal(self.get_body_argument('id'), '频道列表id', False, is_num=True)
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        result = await search_food_channel(id, int(page))
        return self.send_message(True, 0, 'success', result)


async def search_food_channel(id, pagenum, epage=10):
    ''' 美食详情 '''
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage
    channel_base_sql = '''
    SELECT
	id as channel_id,
	title,
    IFNULL(mainInfoUrl,'') as mainImg,
    visitCount
FROM
    channel_info 
WHERE
    id = ?
    AND status=0;
    '''
    channel_base_result = await dbins.selectone(channel_base_sql, (id,))
    if channel_base_result is None:
        return False, 3008, '美食频道数据错误,请重试', None
    # 计算动态数
    cout_moments_num_sql = '''
    SELECT COUNT(*) as count 
    FROM channel_moment_relation
    WHERE channelId = ?
    '''
    count_num = await dbins.select(cout_moments_num_sql, (id,))
    channel_base_result.setdefault('hotCount', count_num[0]['count']+channel_base_result['visitCount'])
    content_list = await get_channel_content_list(id, page, epage)
    channel_base_result.setdefault('content', content_list)
    return channel_base_result


async def get_channel_content_list(channel_id, page, epage):
    '''
    获取美食频道内容图片相关信息
    '''
    sql = '''
    select
channel_la.*,
moments_info.momentsImgUrl as mmimg,
moments_info.momentsDescription as title,
moments_info.likeCount as likeCount,
moments_info.userid,
moments_info.createtime,
us.headImg as userfaceimg,
us.userName as nickName
from(
select
momentId
from channel_moment_relation where channelId = ? LIMIT ?,?
) as channel_la
inner join moments_info
on moments_info.id = channel_la.momentId and moments_info.`status`=0
inner join user as us
on us.id = moments_info.userid and us.`status` = 0;
    '''
    result = await dbins.select(sql, (channel_id, page, epage))
    if result is None:
        log.error('自然搜索执行错误:{} {} {}'.format(id, page, epage))
        return []
    for p in result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
    return result
