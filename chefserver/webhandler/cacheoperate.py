'''
# 缓存操作模块, 之后所有的缓存相关的业务操作都在这里进行

'''
from chefserver.tool.async_redis_pool import RedisOperate
from chefserver.tool.dbpool import DbOperate
from tornado.escape import json_decode, json_encode
from chefserver.tool import applog

log = applog.get_log('webhandler.cache')

class CacheBase(object):
    """ 缓存操作基类 """
    def __init__(self):
        super(CacheBase, self).__init__()
        self.redis = RedisOperate.instance()
        # self.dbmysql = DbOperate.instance()


class CachePapeHotDongtai(CacheBase):
    ''' 动态广场热门缓存 '''
    def __init__(self):
        super(CachePapeHotDongtai, self).__init__()
        self.basekey = "hotdongtai:"

    async def exists(self, argkey):
        ''' key是否存在,argkey=广场类型+页数 '''
        result = await self.redis.exists(self.basekey + argkey)
        return result == 1

    async def set(self, argkey, value):
        ''' 设置值,argkey=广场类型+页数'''
        result = await self.redis.set_and_expire(self.basekey + argkey, json_encode(value), 120) 
        # 设置过期时间半小时
        return result

    async def get(self, argkey):
        ''' 获取值 argkey, value '''
        result = await self.redis.get_data(self.basekey + argkey)
        return json_decode(result)

class CacheRecommedDongtai(CacheBase):
    ''' 动态广场动态推荐缓存类 '''
    def __init__(self):
        super(CacheRecommedDongtai, self).__init__()
        self.basekey = "recommenddongtai"
        self.exprie_time = 3600 * 12

    async def exists(self):
        result = await self.redis.exists(self.basekey)
        return result == 1

    async def create_cache_recommend_dongtai(self):
        ''' 创建随机推荐动态总列表 '''
        exists = await self.exists()
        if exists:
            # 已存在或者未过期,返回
            return True, "ok"
        # 获取数据库数据
        sql = '''SELECT id from moments_info where `status` = 0 ORDER BY id desc limit 1000'''
        db_res = await DbOperate().instance().select(sql, ())
        if db_res is None:
            return False, "获取数据错误"
        if len(db_res) == 0:
            return False, "动态推荐数据为空"

        t = tuple([i.get('id') for i in db_res])
        # 数据加入redis set集合
        rds_result = await self.redis.set_sadd(self.basekey, *t)
        if rds_result is None:
            return False, "保存动态缓存错误"
        else:
            rds_timeout = await self.redis.exprie(self.basekey, self.exprie_time)
            return True, rds_result

    async def get_random(self, num=30):
        ''' 获取值随机数量的推荐动态 '''
        success, res = await self.create_cache_recommend_dongtai()
        if success is False:
            log.error("创建动态推荐缓存错误:{}".format(res))
        rds_rand_list = await self.redis.set_srand(self.basekey, num)
        return rds_rand_list


class CacheFans(CacheBase):
    ''' 用户关注列表缓存redis SET '''
    def __init__(self, setid):
        super(CacheFans, self).__init__()
        self.key = "fans:{}".format(setid)

    async def exists(self):
        ''' key是否存在 '''
        result = await self.redis.exists(self.key)
        return result == 1

    async def add(self, fanid):
        ''' 添加关注 '''
        result = await self.redis.set_sadd(self.key, fanid)
        return result is not None

    async def size(self):
        ''' 返回关注数量 '''
        result = await self.redis.set_size(self.key)
        return result

class CacheFollow(CacheBase):
    ''' 用户粉丝缓存列表redis SET '''
    def __init__(self, setid):
        super(CacheFollow, self).__init__()
        self.key = "follow:{}".format(setid)

    async def exists(self):
        ''' key是否存在 '''
        result = await self.redis.exists(self.key)
        return result == 1

    async def add(self, fanid):
        ''' 添加粉丝 '''
        result = await self.redis.set_sadd(self.key, fanid)
        return result is not None

    async def size(self):
        ''' 返回粉丝数量 '''
        result = await self.redis.set_size(self.key)
        return result

class CacheUserinfo(CacheBase):
    """ 用户个人信息相关Cache,类型 HASH """
    def __init__(self, userid):
        super(CacheUserinfo, self).__init__()
        self.userid = userid
        self.key = "userinfo:{}".format(userid)

    async def mget(self, *field):
        ''' 获取键值 '''
        return await self.redis.hash_mget(self.key, *field)

    async def get(self, field):
        ''' 获取键值 '''
        return await self.redis.hash_get(self.key, field)

    async def add(self, *fv):
        ''' 添加键值 '''
        return await self.redis.hash_set(*fv)

    async def get_dongtai(self, force_update=False):
        ''' 获取动态值没有就更新到缓存 '''
        await self.createCache()
        result = await self.redis.hash_hexists(self.key,'num_dt')
        if result == 1 and force_update is False:
            # 已存在，返回值
            return await self.get('num_dt')
        else:
            # 不存在,从数据库中更新
            sql= '''select count(id) as num from moments_info where userid=? and status=0 limit 1'''
            db_res = await DbOperate().instance().select(sql, (self.userid))
            if len(db_res)<=0:
                return False
            else:
                moment_num = db_res[0].get('num',0)
                result = await self.add(self.key, 'num_dt',moment_num)
                if result == 'OK':
                    return moment_num
                else:
                    return False

    async def set_dongtai(self, value=1):
        ''' 设置动态值+1 '''
        return await self.redis.hash_hincrby(self.key, 'num_dt', value)

    async def get_follow(self, force_update=False):
        ''' 获取关注人数 '''
        await self.createCache()
        result = await self.redis.hash_hexists(self.key,'num_follow')
        if result == 1 and force_update is False:
            # 已存在，返回值
            return await self.get('num_follow')
        else:
            # 不存在,从数据库中更新关注人数
            sql= '''select count(id) as num from focus_info where userid=? and unfollow=0 limit 1'''
            db_res = await DbOperate().instance().select(sql, (self.userid))
            if len(db_res)<=0:
                return False
            else:
                follow_num = db_res[0].get('num',0)
                result = await self.add(self.key, 'num_follow',follow_num)
                if result == 'OK':
                    return follow_num
                else:
                    return False

    async def set_follow(self, value=1):
        ''' 关注+1 '''
        return await self.redis.hash_hincrby(self.key, 'num_follow', value)

    async def get_fans(self, force_update=False):
        ''' 获取粉丝数 '''
        await self.createCache()
        result = await self.redis.hash_hexists(self.key,'num_fans')
        if result == 1 and force_update is False:
            # 已存在，返回值
            return await self.get('num_fans')
        else:
            # 不存在,从数据库中更新关注人数
            sql= '''select count(id) as num from focus_info where focusUserId=? and unfollow=0 limit 1'''
            db_res = await DbOperate().instance().select(sql, (self.userid))
            if len(db_res)<=0:
                return False
            else:
                fan_num = db_res[0].get('num',0)
                result = await self.add(self.key, 'num_fans',fan_num)
                if result == 'OK':
                    return fan_num
                else:
                    return False

    async def set_fans(self, value=1):
        ''' 粉丝+1 '''
        return await self.redis.hash_hincrby(self.key, 'num_fans', value)

    async def get_shipu(self, force_update=False):
        ''' 获取食谱数量 '''
        await self.createCache()
        result = await self.redis.hash_hexists(self.key,'num_shipu')
        if result == 1 and force_update is False:
            # 已存在，返回值
            return await self.get('num_shipu')
        else:
            # 不存在,从数据库中更新关注人数
            sql= '''select count(id) as num from recipe_info where userid=? and status!=-1 and status!=2 and isEnable=1 limit 1'''
            db_res = await DbOperate().instance().select(sql, (self.userid))
            if len(db_res)<=0:
                return False
            else:
                shipu_num = db_res[0].get('num',0)
                result = await self.add(self.key, 'num_shipu',shipu_num)
                if result == 'OK':
                    return shipu_num
                else:
                    return False

    async def set_shipu(self, value=1):
        ''' 粉丝+1 '''
        return await self.redis.hash_hincrby(self.key, 'num_shipu', value)

    async def exists(self):
        ''' key是否存在 '''
        result = await self.redis.exists(self.key)
        return result == 1

    async def createCache(self, force_update=False):
        ''' 创建hash '''
        if await self.exists() and force_update is False:
            ''' 已存在不创建 '''
            return True
        ''' 创建userinfocache'''
        return await self.updateBasicCache()

    async def updateBasicCache(self):
        ''' 创建 用户相关 hash 缓存'''
        sql= '''select username, headimg, mobile, sex, birthday, address, personalProfile, tag, status, certificationStatus,certified from user where id=? limit 1 '''
        useinfo = await DbOperate().instance().select(sql, (self.userid))
        # print(useinfo)
        # add_res = await self.add(tuple(useinfo[0].items()))
        if len(useinfo) == 0 or useinfo is None:
            return False
        arglist = []
        arglist.append(self.key)
        dkvl = useinfo[0]
        dk = dkvl.keys()
        dv = dkvl.values()
        for k,v in zip(dk,dv):
            arglist.append(k)
            arglist.append(str(v))
        add_res = await self.add(*tuple(arglist))
        if add_res == 'OK':
            await self.get_dongtai(force_update=True)
            await self.get_shipu(force_update=True)
            await self.get_fans(force_update=True)
            await self.get_follow(force_update=True)
            return True
        else:
            return False


async def cache_up_follow(userid, num=1):
    ''' 更新用户缓存,关注数量 '''
    cache = CacheUserinfo(userid)
    await cache.set_follow(num)

async def cache_up_fans(userid, num=1):
    ''' 更新用户缓存,粉丝数量 '''
    cache = CacheUserinfo(userid)
    await cache.set_fans(num)

async def cache_up_caipu(userid, num=1):
    ''' 更新用户缓存,菜谱数量 '''
    cache = CacheUserinfo(userid)
    await cache.set_shipu(num)

async def cache_up_dongtai(userid, num=1):
    ''' 更新用户缓存,动态数量 '''
    cache = CacheUserinfo(userid)
    await cache.set_dongtai(num)


if __name__ == '__main__':
    async def test_create():
        obj = CacheUserinfo(55)        
        rdget = await obj.createCache()
        print(rdget)

    async def test_getdongtai():
        r = await obj.get_dongtai()
        print("动态:", r, type(r))
        r = await obj.get_follow()
        print("关注:",r,type(r))
        r = await obj.get_fans()
        print("粉丝:",r,type(r))
        r = await obj.get_shipu()
        print("食谱:",r,type(r))

        sr= await obj.set_dongtai()
        print("动态:", sr, type(sr))
        sr= await obj.set_follow()
        print("关注:", sr, type(sr))
        sr= await obj.set_fans()
        print("粉丝:", sr, type(sr))
        sr= await obj.set_shipu()
        print("食谱:", sr, type(sr))

    async def test_getpagehotdongtai():
        ''' 获取热门动态 '''
        hotcache = CachePapeHotDongtai()
        print(hotcache)
        res = await hotcache.exists('2'+'1')
        print('exists:', res)

        res = await hotcache.set('2'+'1','{"id":10086}')
        print('set:', res)

        res = await hotcache.get('2'+'1')
        print('get:', res)

    async def test_getrecommenddongtai():
        ''' 获取热门动态 '''
        recommendcache = CacheRecommedDongtai()
        res = await recommendcache.create_cache_recommend_dongtai()
        print(res)


    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_getrecommenddongtai())

    # d = {'a': 1, 'b': None, 'c': 3}
    # # k = 
    # # t = tuple([(k,v) for k,v in d.items()])
    # print(d.keys())
    # print(d.values())