from peewee_async import transaction, savepoint
from playhouse.shortcuts import JOIN, model_to_dict

from chefserver.config import PAGE_SIZE, DATABASE
from chefserver.models.point import User, User_Point, User_PointBill, BILL_TYPE_DICT, Product_Point_Detail, \
    Product_Point, My_Exchange_Info, My_History_Address, My_Express_Info, Area, My_Address
from chefserver.tool.function import verify_num
from chefserver.webhandler.basehandler import BaseHandler, check_login
from chefserver.tool.tooltime import curDatetime
from chefserver.tool.dbpool import DbOperate
from chefserver.tool import applog
import tornado.web

log = applog.get_log('webhandler.point')
dbins = DbOperate.instance()


class MyPointHandler(BaseHandler):
    ''' 我的积分 '''

    @check_login
    async def post(self, *args, **kwargs):
        result = {}
        userid = self.get_session().get('id', 0)
        try:
            user_point_obj = await self.application.objects.get(User_Point, user_id=userid)
        except User_Point.DoesNotExist:
            user_point_obj = await self.application.objects.create(User_Point, user_id=userid)
        sucess, code, message = True, 0, '获取成功'
        result['point'] = user_point_obj.point
        return self.send_message(sucess, code, message, result)


class MyPointBillHandler(BaseHandler):
    ''' 我的积分 '''

    @check_login
    async def post(self, *args, **kwargs):
        result = []
        userid = self.get_session().get('id', 0)
        sort = self.get_argument("sort", None)
        # print(self.get_argument('page'))
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        try:
            user_pointbill_query = User_PointBill.extend().filter(User_PointBill.user_id == userid).order_by(
                User_PointBill.createTime.desc())
            if sort:
                if sort < '0':
                    user_pointbill_query = user_pointbill_query.filter(User_PointBill.bill_type < 0)
                else:
                    user_pointbill_query = user_pointbill_query.filter(User_PointBill.bill_type > 0)
            if page:
                user_pointbill_query = user_pointbill_query.paginate(int(page), PAGE_SIZE)
            print('user_pointbill_query', user_pointbill_query)
            user_pointbills = await self.application.objects.execute(user_pointbill_query)
            for bill in user_pointbills:
                bill_dict = model_to_dict(bill)
                ct = bill_dict.get('createTime', None)
                # bill_dict['bill_type'] = BILL_TYPE_DICT.get(bill_dict.get('bill_type'))
                if ct:
                    bill_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
                result.append(bill_dict)
        except Exception as e:
            return self.send_message(False, 400, '获取失败', '')
        sucess, code, message = True, 0, '获取成功'
        return self.send_message(sucess, code, message, result)


class MyPointProductHandler(BaseHandler):
    ''' 积分 - 商品列表 '''

    @check_login
    async def post(self, *args, **kwargs):
        result = []
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        products_query = Product_Point.select(Product_Point.id, Product_Point.title, Product_Point.grade_no,
                                              Product_Point.front_image, Product_Point.createTime).order_by(
            Product_Point.id.desc()).paginate(int(page), PAGE_SIZE)
        print('products_query', products_query)
        products = await self.application.objects.execute(products_query)
        for p in products:
            p_dict = model_to_dict(p)
            ct = p_dict.get('createTime', None)
            # p_dict['bill_type'] = BILL_TYPE_DICT.get(p_dict.get('bill_type'))
            if ct:
                p_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
            result.append(p_dict)
        sucess, code, message = True, 0, '获取成功'
        return self.send_message(sucess, code, message, result)


class ProductPointDetailHandler(BaseHandler):
    ''' 获取积分商品详情 '''

    @check_login
    async def post(self):
        result = []
        did = self.verify_arg_legal(self.get_body_argument('did'), '动态ID', False, is_num=True)
        product_query = Product_Point.select().order_by(Product_Point.id).where(Product_Point.id == did)
        product = await self.application.objects.execute(product_query)
        p_dict = {}
        if product:
            for p in product:
                p_dict = model_to_dict(p)
                ct = p_dict.get('createTime', None)
                if ct:
                    p_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
                p_dict.pop('updatetime')
                result.append(p_dict)
                pdetailimg_query = await self.application.objects.execute(p.product_points)
                p_dict['imgs'] = []
                for p1 in pdetailimg_query:
                    p_dict['imgs'].append(p1.image)
            success, code, message, result = True, 0, '获取成功', p_dict
            return self.send_message(success, code, message, result)
        else:
            return self.send_message(False, 404, '商品不存在', result)
        # pdetail_query = Product_Point_Detail.extend()
        # groups = await self.application.objects.execute(pdetail_query)
        # dict_obj=[]
        # dict_img={}
        # dict_img['img']=[]
        # for group in groups:
        #     group_dict = model_to_dict(group)
        #     if hasattr(dict_obj,'id'):
        #         dict_img['img']=group_dict['image']
        #         dict_obj.append(dict_img)
        #     else:
        #         dict_img=group_dict['product_point']
        #         dict_img['img']=group_dict['image']
        #         dict_obj.append(dict_img)
        #     result.append(dict_img)
        # return self.send_message(False, 404, '商品部存在', dict_obj)

async def process_the_history(name, mobile, province, city, area, address):
    sql_ = '''
        SELECT
        t1.name as p_name,
        t2.name as c_name,
        t3.name as a_name
        from
        (select
        name
        from area
        where id=?) as t1
        inner join area as t2
        on t2.id = ?
        inner join area as t3
        on t3.id = ?'''
    address_result = await dbins.select(sql_, (province, city, area))
    if address_result is None:
        return False,  None
    address_detail = address_result[0]
    return True, address_detail

class MyPointPorderHandler(BaseHandler):
    ''' 获取积分商品列表 '''

    @check_login
    async def post(self):
        result = {}
        userid = self.get_session().get('id', 0)
        address_id = self.verify_arg_num(self.get_body_argument('address_id'), '地址id', is_num=True)
        product_id = self.verify_arg_num(self.get_body_argument('product_id'), '商品id', is_num=True)
        num = self.verify_arg_num(self.get_body_argument('num'), '数量', is_num=True)
        total = self.verify_arg_num(self.get_body_argument('total'), '总积分', is_num=True)
        remark = self.verify_arg_legal(self.get_body_argument('remark',''), '备注', True, 49)

        # 验证地址
        try:
            address_obj = await self.application.objects.get(My_Address, id=address_id, user_id=userid, is_delete=False)
            product_obj = await self.application.objects.get(Product_Point, id=product_id)

            if product_obj.sku_no < num:
                return self.send_message(False, 400, '商品库存不足', result)
            # 验证商品 数据库的 数量 和 积分 是否和传过来的积分一致
            if product_obj.grade_no != total:
                return self.send_message(False, 400, '商品积分参数错误', result)
            # 验证用户积分是否大于商品积分
            user_point_obj = await self.application.objects.get(User_Point, user_id=userid)
            if user_point_obj.point < total:
                return self.send_message(False, 400, '积分不足', result)
            address_data = {
            }

            status,address_res = await process_the_history(address_obj.name, address_obj.mobile, address_obj.province_id, address_obj.city_id, address_obj.area_id, address_obj.address)

            if status is False:
                return self.send_message(False, 400, '用户地址参数错误', result)

            try:
                async with await DATABASE.transaction() as transaction:
                    # 处理商品库存
                    query = (Product_Point.use(transaction).update({Product_Point.sku_no: Product_Point.sku_no - num})
                             .where(Product_Point.id == product_id, Product_Point.sku_no >= num))
                    product_unum=await query.execute()
                    # # 处理用户积分 User_Point 扣积分
                    query1 = (User_Point.use(transaction).update({User_Point.point: User_Point.point - total})
                             .where(User_Point.user_id == userid, User_Point.point >= total))
                    userpoint_unum=await query1.execute()

                    if product_unum == 0 or userpoint_unum == 0:
                        return self.send_message(False, 404, '参数错误', result)
                    # 生成订单 My_Exchange_Info
                    exchange_order_data = {
                        "product_point_id":product_id,
                        "user_id":userid,
                        "goods_no":num,
                        "grade_no":total,
                        "remark":remark,
                        # "express_id":None
                        "express_status":0
                    }
                    t=await My_Exchange_Info.use(transaction).create(**exchange_order_data)

                    # 增加用户历史地址 My_History_Address
                    history_data = {
                        "user_id":userid,
                        # "exchangeorder_id":1,
                        "name":address_obj.name,
                        "mobile":address_obj.mobile,
                        "province":address_res['p_name'],
                        "city": address_res['c_name'],
                        "country": address_res['a_name'],
                        "address": address_obj.address,
                        # "exchangeorder":t

                    }
                    history_address_obj = await My_History_Address.use(transaction).create(**history_data)
                    # 增加用户 积分账单记录 User_PointBill
                    user_bill_data = {
                        "user_id":userid,
                        "bill_type":-2,
                        "bill_status":0,
                        "grade_no":total
                    }
                    await User_PointBill.use(transaction).create(**user_bill_data)
            except Exception as e:
                product_id('下单异常',e)
                return self.send_message(False, 400, '下单异常', result)
            # 再处理 我的兑换 和 历史地址 关联
            await My_History_Address.update({My_History_Address.exchangeorder_id: t.id}).where(My_History_Address.id == history_address_obj.id)
            return self.send_message(True, 0, '下单成功', result)
                # ddd
        except My_Address.DoesNotExist:
            return self.send_message(False, 404, '收货地址不存在', result)
        except Product_Point.DoesNotExist:
            return self.send_message(False, 404, '商品不存在', result)
        except User_Point.DoesNotExist:
            return self.send_message(False, 404, '用户积分不存在', result)



class MyPointCmOrderHandler(BaseHandler):
    ''' 获取兑换订单详情 '''

    @check_login
    async def post(self):
        result = {}
        userid = self.get_session().get('id', 0)
        did = self.verify_arg_legal(self.get_body_argument('did'), '动态ID', False, is_num=True)
        try:
            the_exchange_order = await self.application.objects.get(My_Exchange_Info, user_id=userid, id=did, express_status=1)
            the_exchange_order.express_status = 2
            await self.application.objects.update(the_exchange_order)
            return self.send_message(False, 0, '收货成功', result)
        except My_Exchange_Info.DoesNotExist:
            return self.send_message(False, 404, '订单不存在', result)

class MyPointMyExchangeHandler(BaseHandler):
    ''' 获取积分商品列表 '''

    @check_login
    async def post(self):
        result = []
        userid = self.get_session().get('id', 0)
        sort = self.verify_arg_legal(self.get_body_argument('sort'), '排序类型', False, is_num=True, uchecklist=True,
                                     user_check_list=['0', '1', '2', '3'])
        page = self.verify_arg_legal(self.get_body_argument('page'), '页数', False, is_num=True)
        my_exchange_query = My_Exchange_Info.extend().where(My_Exchange_Info.user_id == userid)
        if sort:
            if sort != '0':
                my_exchange_query = my_exchange_query.where(My_Exchange_Info.express_status == sort)
            else:
                pass
        my_exchange_query = my_exchange_query.order_by(My_Exchange_Info.id.desc()).paginate(int(page), PAGE_SIZE)
        exchanges_warpper = await self.application.objects.execute(my_exchange_query)
        if exchanges_warpper:
            for ex in exchanges_warpper:
                ex_dict = model_to_dict(ex)
                ct = ex_dict.get('createTime', None)
                if ct:
                    ex_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
                ex_dict['product_point'].pop('createTime')
                ex_dict['product_point'].pop('updatetime')
                ex_dict['user'].pop('createTime')
                ex_dict.pop('updatetime')
                express_info_query = My_Express_Info.extend().where(My_Express_Info.id == ex.express_id)
                express_info = await self.application.objects.execute(express_info_query)
                if express_info:
                    for addin in express_info:
                        express_info_dict = model_to_dict(addin)
                        express_info_dict.pop('createTime')
                        express_info_dict.pop('updatetime')
                        ex_dict['express'] = express_info_dict
                result.append(ex_dict)
            success, code, message = True, 0, '获取成功'
            return self.send_message(success, code, message, result)

        else:
            return self.send_message(False, 404, '订单不存在', result)


class MyExchangeDetailHandler(BaseHandler):
    ''' 获取兑换订单详情 '''

    @check_login
    async def post(self):
        result = []
        did = self.verify_arg_legal(self.get_body_argument('did'), '动态ID', False, is_num=True)
        query_ = My_Exchange_Info.extend().where(My_Exchange_Info.id == did)
        exchange_warpper = await self.application.objects.execute(query_)
        if exchange_warpper:
            for p in exchange_warpper:
                p_dict = model_to_dict(p)
                ct = p_dict.get('createTime', None)
                if ct:
                    p_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
                p_dict.pop('updatetime')
                p_dict['product_point'].pop('createTime')
                p_dict['product_point'].pop('updatetime')
                p_dict.pop('user')
                result.append(p_dict)

                # 找出对应历史地址
                exchange_address_query = My_History_Address.select().where(
                    My_History_Address.exchangeorder_id == p_dict['id'])
                address_dict = {}
                p_dict['address'] = {}
                exchange_address_wrapper = await self.application.objects.execute(exchange_address_query)
                if exchange_address_wrapper:
                    for ad in exchange_address_wrapper:
                        address_dict['name'] = ad.name
                        address_dict['mobile'] = ad.mobile
                        address_dict['province'] = ad.province
                        address_dict['city'] = ad.city
                        address_dict['address'] = ad.address
                else:
                    pass
                p_dict['address'] = address_dict

                # 找出快递信息
                express_info_query = My_Express_Info.extend().where(My_Express_Info.id == p.express_id)
                express_info = await self.application.objects.execute(express_info_query)
                if express_info:
                    for addin in express_info:
                        express_info_dict = model_to_dict(addin)
                        express_info_dict.pop('createTime')
                        express_info_dict.pop('updatetime')
                        p_dict['express'] = express_info_dict

            success, code, message, result = True, 0, '获取成功', result
            return self.send_message(success, code, message, result)
        else:
            return self.send_message(False, 404, '订单不存在', result)


class AddressDetailHandler(BaseHandler):
    ''' 获取省市区 '''

    # @check_login
    async def post(self):
        result = []
        pid = self.get_body_argument('pid', None)  # '省id'
        cid = self.get_body_argument('cid', None)  # '市id'
        if pid and cid:
            return self.send_message(False, 404, 'pid 或 cid 参数错误', result)
        query_no = None
        if pid:
            query_no = verify_num(pid)
        elif cid:
            query_no = verify_num(cid)
        area_query = Area.select().where(Area.pid == query_no)
        area_wrappers = await self.application.objects.execute(area_query)
        if area_wrappers:
            for a in area_wrappers:
                area_dict = model_to_dict(a)
                result.append(area_dict)
            success, code, message, result = True, 0, '获取成功', result
            return self.send_message(success, code, message, result)

        else:
            return self.send_message(False, 404, '获取失败', result)


class MyAddressHandler(BaseHandler):
    ''' 创建 修改 删除 地址 '''

    @check_login
    async def get(self):
        result = []
        userid = self.get_session().get('id', 0)
        my_address_query = My_Address.select().order_by(My_Address.id.desc()).where(My_Address.user_id == userid,
                                                                                    My_Address.is_delete == False)
        address_wrappers = await self.application.objects.execute(my_address_query)
        if address_wrappers:
            for ad in address_wrappers:
                sql_ = '''
    SELECT
    t1.name as p_name,
    t2.name as c_name,
    t3.name as a_name
    from
    (select
    name
    from area
    where id=?) as t1
    inner join area as t2
    on t2.id = ?
    inner join area as t3
    on t3.id = ?'''
                address_result = await dbins.select(sql_, (ad.province_id, ad.city_id, ad.area_id))
                if address_result is None:
                    return self.send_message(False, 3003, '获取收货地址失败,请重试', None)
                else:
                    address_detail = address_result[0]
                    detail_dict = {}
                    detail_dict['id'] = ad.id
                    detail_dict['name'] = ad.name
                    detail_dict['mobile'] = ad.mobile
                    address_detail['address'] = ad.address
                    detail_dict['detail'] = address_detail
                    detail_dict['is_default'] = ad.is_default
                    result.append(detail_dict)
            success, code, message, result = True, 0, '获取成功', result
            return self.send_message(success, code, message, result)
        else:
            return self.send_message(False, 404, '地址为空', result)

    @check_login
    async def post(self):
        result = []
        userid = self.get_session().get('id', 0)
        name = self.verify_arg_legal(self.get_body_argument('name'), '收件人', False, )
        mobile = self.verify_arg_legal(self.get_body_argument('mobile'), '手机号', False, )
        pid = self.verify_arg_num(self.get_body_argument('pid'), '省id', is_num=True, )
        cid = self.verify_arg_num(self.get_body_argument('cid'), '市id', is_num=True, )
        aid = self.verify_arg_num(self.get_body_argument('aid'), '县区id', is_num=True, )
        address = self.verify_arg_legal(self.get_body_argument('address'), '详细地址', False, is_len=50, )
        is_default = self.verify_arg_num(self.get_body_argument('is_default'), '是否默认', is_num=True)
        verify_city_ = Area.select().where(Area.id == aid and Area.pid == cid)
        verify_province_ = Area.select().where(Area.id == cid and Area.pid == pid)
        verify_city_wrappers = await self.application.objects.execute(verify_city_)
        verify_province_wrappers = await self.application.objects.execute(verify_province_)

        if not verify_city_wrappers or not verify_province_wrappers:
            return self.send_message(False, 404, '创建失败 省市区参数错误', result)

        # 如果要设置为默认地址，先查询数据库是否有存在默认地址，有改为非默认
        async with await DATABASE.transaction() as transaction:
            if is_default:
                query = (My_Address.use(transaction).update({My_Address.is_default: 0})
                         .where(My_Address.user == userid, My_Address.is_default == 1))
                await query.execute()

            data_dict = {
                "user_id": userid,
                "name": name,
                "mobile": mobile,
                "province": pid,
                "city": cid,
                "area": aid,
                "address": address,
                "is_default": is_default,
            }
            try:
                # await self.application.objects.create(My_Address, **data_dict)
                await My_Address.use(transaction).create(**data_dict)
            except Exception as e:
                # 日志
                log.info('{} 地址创建失败:{}-{}'.format(userid, data_dict, e))
                success, code, message, result = False, 404, '创建失败', ''
                return self.send_message(success, code, message, result)

        success, code, message, result = True, 0, '创建成功', result
        return self.send_message(success, code, message, result)

    @check_login
    async def put(self, *args, **kwargs):
        result = []
        userid = self.get_session().get('id', 0)
        did = self.verify_arg_legal(self.get_body_argument('did'), '地址id', False, is_num=True)
        name = self.verify_arg_legal(self.get_body_argument('name'), '收件人', False, )
        mobile = self.verify_arg_legal(self.get_body_argument('mobile'), '手机号', False, )
        pid = self.verify_arg_num(self.get_body_argument('pid'), '省id', is_num=True, )
        cid = self.verify_arg_num(self.get_body_argument('cid'), '市id', is_num=True, )
        aid = self.verify_arg_num(self.get_body_argument('aid'), '县区id', is_num=True, )
        address = self.verify_arg_legal(self.get_body_argument('address'), '详细地址', False, is_len=50, )
        is_default = self.verify_arg_num(self.get_body_argument('is_default'), '是否默认', is_num=True)

        try:
            address_obj = await self.application.objects.get(My_Address, id=did, user_id=userid)
        except My_Address.DoesNotExist as e:
            return self.send_message(False, 404, 'did参数错误', result)

        verify_city_ = Area.select().where(Area.id == aid and Area.pid == cid)
        verify_province_ = Area.select().where(Area.id == cid and Area.pid == pid)
        verify_city_wrappers = await self.application.objects.execute(verify_city_)
        verify_province_wrappers = await self.application.objects.execute(verify_province_)

        if not verify_city_wrappers or not verify_province_wrappers:
            return self.send_message(False, 404, '创建失败 省市区参数错误', result)

        add_data = {
            "name": name,
            "mobile": mobile,
            "province_id": pid,
            "city_id": cid,
            "area_id": aid,
            "address": address,
            "is_default": is_default,
            "updatetime": curDatetime(),
        }

        # 如果要设置为默认地址，先查询数据库是否有存在默认地址，有改为非默认
        async with await DATABASE.transaction() as transaction:
            try:
                if is_default:
                    query = (My_Address.use(transaction).update({My_Address.is_default: 0})
                             .where(My_Address.user == userid, My_Address.is_default == 1))
                    await query.execute()
                await My_Address.use(transaction).update(**add_data).where(My_Address.id == did)
            except Exception as e:
                # 日志
                log.info('{} 地址修改失败:{}-{}'.format(userid, add_data, e))
                success, code, message, result = False, 404, '修改失败', ''
                return self.send_message(success, code, message, result)
        success, code, message, result = True, 0, '修改成功', result
        return self.send_message(success, code, message, result)

    @check_login
    async def delete(self, *args, **kwargs):
        result = []
        userid = self.get_session().get('id', 0)
        did = self.verify_arg_legal(self.get_body_argument('did'), '地址id', False, is_num=True)
        # self.verify_arg_num(self.get_body_argument('is_delete'), '是否默认', is_num=True)
        try:
            add_obj = await self.application.objects.get(My_Address, id=did, is_delete=False, user_id=userid)
        except My_Address.DoesNotExist:
            return self.send_message(False, 404, '地址不存在', result)
        add_obj.is_delete = True
        await self.application.objects.update(add_obj)
        success, code, message, result = True, 0, '删除成功', result
        return self.send_message(success, code, message, result)


class MyAddressDetailHandler(BaseHandler):
    ''' 创建 修改 删除 地址 '''

    @check_login
    async def get(self):
        result = []
        userid = self.get_session().get('id', 0)
        address_wrappers = await self.application.objects.execute(
            My_Address.select().order_by(My_Address.id.desc()).where(
                My_Address.user_id == userid, My_Address.is_delete == False, My_Address.is_default == True))
        if address_wrappers:
            for ad in address_wrappers:
                sql_ = '''
               SELECT
               t1.name as p_name,
               t2.name as c_name,
               t3.name as a_name
               from
               (select
               name
               from Area
               where id=?) as t1
               inner join Area as t2
               on t2.id = ?
               inner join Area as t3
               on t3.id = ?'''
                # 日志
                address_result = await dbins.select(sql_, (ad.province_id, ad.city_id, ad.area_id))
                log.info('地址:{}-{}-{}-{}'.format(ad.province_id, ad.city_id, ad.area_id,address_result))
                if address_result is None:
                    return self.send_message(False, 3003, '获取收货地址失败,请重试', None)
                else:
                    address_detail = address_result[0]
                    detail_dict = {}
                    detail_dict['id'] = ad.id
                    detail_dict['name'] = ad.name
                    detail_dict['mobile'] = ad.mobile
                    address_detail['address'] = ad.address
                    detail_dict['detail'] = address_detail
                    detail_dict['is_default'] = ad.is_default
                    result.append(detail_dict)
            success, code, message, result = True, 0, '获取成功', result
            return self.send_message(success, code, message, result)
        else:
            return self.send_message(False, 400, '没有默认地址', result)


if __name__ == '__main__':
    async def test_banner_list():
        # res = await banner_list(0)
        print(1)


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_banner_list())
