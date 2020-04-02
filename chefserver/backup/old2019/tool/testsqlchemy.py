'''
 
from sqlalchemy import create_engine
import sqlalchemy as sa
engine = create_engine('mysql+pymysql://root:dzroot@127.0.0.1/masterchefmb4', echo=True)
metadata = sa.MetaData(engine)
tbl = sa.Table('tbl', metadata,
               sa.Column('id', sa.Integer, primary_key=True),
               sa.Column('val', sa.String(255)),
               )
metadata.create_all()
print(tbl.select())
'''



''' 集成 sqlalchemy 可以实现 pool 功能 '''
# '''
import asyncio
import aiomysql
import sqlalchemy as sa
from aiomysql.sa import create_engine
from chefserver.config import CONFIG_MYSQL


metadata = sa.MetaData()

tbl = sa.Table('tbl', metadata,
               sa.Column('id', sa.Integer, primary_key=True),
               sa.Column('val', sa.String(255)))


class ClassName(sa.Table):
    """docstring for ClassName"""
    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg
        

# async def mypool():
#     obj_pool = await aiomysql.create_pool(
#         host = CONFIG_MYSQL.get('host','127.0.0.1'),
#         port = CONFIG_MYSQL.get('port', 3306),
#         user = CONFIG_MYSQL['user'],
#         password = CONFIG_MYSQL['password'],
#         db = CONFIG_MYSQL['db'],
#         charset = CONFIG_MYSQL.get('charset', 'utf8'),
#         autocommit = CONFIG_MYSQL.get('autocommit', True),
#         maxsize = CONFIG_MYSQL.get('maxsize', 50),
#         minsize = CONFIG_MYSQL.get('minsize', 30)
#     )
#     await asyncio.sleep(10)
#     try:
#         async with (obj_pool.acquire()) as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute("INSERT INTO tbl(val) VALUES ('mypool1')")
#                 print(cur.description)
#                 (r,) = await cur.fetchone()
#                 assert r == 42
#                 await asyncio.sleep(20)
#     except BaseException as e:
#         print(e)
#         return None


async def go(loop):
    # engine = await create_engine(user='root', db='masterchefmb4',
    #                             # minsize=3,
    #                             # maxsize=10,
    #                             autocommit=True,
    #                             host='127.0.0.1', password='dzroot',echo=True, loop=loop)
    engine = await create_engine(
        # host = CONFIG_MYSQL.get('host','127.0.0.1'),
        host = '127.0.0.1',
        port = CONFIG_MYSQL.get('port', 3306),
        user = CONFIG_MYSQL['user'],
        password = CONFIG_MYSQL['password'],
        db = CONFIG_MYSQL['db'],
        charset = CONFIG_MYSQL.get('charset', 'utf8'),
        autocommit = CONFIG_MYSQL.get('autocommit', True),
        maxsize = CONFIG_MYSQL.get('maxsize', 50),
        minsize = CONFIG_MYSQL.get('minsize', 30)
    )


    for i in range(10):
        async with engine.acquire() as conn:
            # print(tbl.insert().values(val='abc'))

            await conn.execute(tbl.insert().values(val='abc'))
            # await conn.execute('commit')
            res = await conn.execute(tbl.insert().values(val='xyz'))
            await conn.execute('commit')
            # await conn.commit()
            print(res.rowcount)

            await conn.execute(tbl.insert(),{"id":None,"val":"v12"})
            # await conn.execute('commit')

            # async for row in conn.execute(tbl.select()):
            # # async for row in conn.execute("select * from tbl where id= %s ",("82';--",)):
            # # async for row in conn.execute("select * from tbl where id= %(id)s", {'id':82}):
            #     # 传统写法
        #     print(row.id, row.val)

    engine.close()
    await engine.wait_closed()


loop = asyncio.get_event_loop()
loop.run_until_complete(go(loop))
# loop.run_until_complete(mypool())


# '''

# yield from 版本
'''
    import asyncio
    import sqlalchemy as sa
    from aiomysql.sa import create_engine

    metadata = sa.MetaData()

    tbl = sa.Table('tbl', metadata,
                   sa.Column('id', sa.Integer, primary_key=True),
                   sa.Column('val', sa.String(255)))

    @asyncio.coroutine
    def go():
        engine = yield from create_engine(user='root', db='test_pymysql',
                                            host='127.0.0.1', password='',echo=True, loop=asyncio.get_event_loop())

        with (yield from engine) as conn:
            yield from conn.execute(tbl.insert().values(val='abc'))

            res = yield from conn.execute(tbl.select())
            result = yield from res.fetchall()
            for row in result:
                print(row.id, row.val)
            yield from conn.execute('commit')

    asyncio.get_event_loop().run_until_complete(go())
'''