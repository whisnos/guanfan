"""
# 黑名单模块
# 黑名单列表, 
# 添加黑名单,
# 删除黑名单,
# 返回黑名单ID列表,
# 是否在黑名单中,
"""
import tornado.web
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.webhandler.cacheoperate import CacheUserinfo

from chefserver.webhandler.myspace import myspace_unfollow

log = applog.get_log('webhandler.block')
dbins = DbOperate.instance()


class BlocklistHandler(BaseHandler):
    ''' 黑名单列表 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        page = self.verify_arg_legal(
            self.get_body_argument('page'), '页数', False, is_num=True)
        success, code, message, result = await get_block_list(myid, int(page))
        return self.send_message(success, code, message, result)


class BlockAddHandler(BaseHandler):
    ''' 黑名单添加 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        beblockid = self.verify_arg_legal(self.get_body_argument('beblockid'), '被拉黑用户', False, is_num=True)
        success, code, message, result = await add_block(myid, beblockid)
        # 取消互相关注状态
        if success:
            # 拉黑成功,取消互相关注的状态
            # 取消我关注他的状态
            mfres = await myspace_unfollow(myid, beblockid)
            # 取消他关注我的状态
            bfres = await myspace_unfollow(beblockid, myid)
            log.warning("取消我关注:{},取消他关注我:{}".format(mfres, bfres))
        return self.send_message(success, code, message, result)


class BlockDelHandler(BaseHandler):
    ''' 黑名单删除 '''
    @check_login
    async def post(self):
        myid = self.get_session().get('id', 0)
        beblockid = self.verify_arg_legal(self.get_body_argument('beblockid'), '被拉黑用户', False, is_num=True)
        success, code, message, result = await del_block(myid, beblockid)
        return self.send_message(success, code, message, result)


async def del_block(myid, beblockid):
    ''' 拉黑名单 '''
    isadd = await is_block(myid, beblockid)
    if isadd is False:
        return True, 1002, '错误的数据,请核对后重试', None
    delete_sql = '''
    DELETE from block_info where userid=? and blockuserid=? limit 1
    '''
    result = await dbins.execute(delete_sql, (myid, beblockid))
    if result is None:
        return False, 3002, '删除失败,请重试', None
    else:
        return True, 0, '删除成功', None


async def add_block(myid, beblockid):
    ''' 拉黑名单 '''
    isadd = await is_block(myid, beblockid)
    if isadd:
        return True, 1001, '请勿重复添加', None
    insert_sql = '''
    INSERT INTO block_info (userid,blockuserid) VALUES (?,?)
    '''
    result = await dbins.execute(insert_sql, (myid, beblockid))
    # print(result)
    if result is None:
        return False, 3001, '添加失败,请重试', None
    else:
        return True, 0, '添加成功', None


async def is_block(myid, beblockid):
    ''' 是否拉黑 '''
    sql = '''
    SELECT id from block_info where userid=? and blockuserid=? limit 1
    '''
    result = await dbins.selectone(sql, (myid, beblockid))
    if result is None:
        return False
    else:
        return True


async def get_block_list(myid, pagenum, epage=10):
    """ 
    获取黑名单列表 
    """
    page = 0 if pagenum - 1 <= 0 else pagenum - 1
    page = page * epage
    sql = '''
    SELECT blo.id, blo.blockuserid, blo.createtime,user.userName AS 'nickname', user.headimg AS 'headimg'
    FROM
    (
    SELECT id,blockuserid,createtime FROM block_info WHERE userid=? ORDER BY id desc LIMIT ?,?
    ) AS blo
    LEFT JOIN user ON blo.blockuserid = user.id
    '''
    result = await dbins.select(sql, (myid, page, epage))
    if result is None:
        return False, 3002, '获取数据错误', None

    for p in result:
        ct = p.get('createtime')
        p['createtime'] = ct.strftime('%Y-%m-%d %H:%M:%S')

    return True, 0, 'success', result


if __name__ == '__main__':
    import asyncio

    async def test_get_block_list():
        res = await get_block_list(1, 1)
        print(res)

    async def test_is_block():
        res = await is_block(1, 2)
        print(res)

    async def test_add_block():
        res = await add_block(1, 5)
        print(res)
        res = await add_block(1, 980)

    async def test_del_block():
        res = await del_block(1, 5)
        print(res)

    async def test_get_all_blocks():
        res = await get_all_blocks(1)
        print(res)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_all_blocks())
