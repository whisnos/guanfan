from peewee_async import transaction, savepoint
from playhouse.shortcuts import JOIN, model_to_dict

from chefserver.config import PAGE_SIZE, DATABASE
from chefserver.models.point import User, User_Point, User_PointBill, BILL_TYPE_DICT, Product_Point_Detail, \
    Product_Point, My_Exchange_Info, My_History_Address, My_Express_Info, Bt_Area, My_Address
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
            success, code, message, result = True, 0, '获取成功', result
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
    async def get(self):
        result = []
        pid = self.get_body_argument('pid', None)  # '省id'
        cid = self.get_body_argument('cid', None)  # '市id'
        if pid and cid:
            return self.send_message(False, 404, 'pid 或 cid 参数错误', result)
        query_no = 0
        if pid:
            query_no = verify_num(pid)
        elif cid:
            query_no = verify_num(cid)
        area_query = Bt_Area.select().where(Bt_Area.parentId == query_no)
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
    async def post(self):
        result = []
        DATABASE.autocommit(False)
        print(1)
        userid = self.get_session().get('id', 0)
        name = self.verify_arg_legal(self.get_body_argument('name'), '收件人', False, )
        mobile = self.verify_arg_legal(self.get_body_argument('mobile'), '手机号', False, )
        pid = self.verify_arg_num(self.get_body_argument('pid'), '省id', is_num=True, )
        cid = self.verify_arg_num(self.get_body_argument('cid'), '市id', is_num=True, )
        aid = self.verify_arg_num(self.get_body_argument('aid'), '县区id', is_num=True, )
        address = self.verify_arg_legal(self.get_body_argument('address'), '详细地址', False, is_len=50, )
        is_default = self.verify_arg_num(self.get_body_argument('is_default'), '是否默认', is_num=True)
        verify_city_ = Bt_Area.select().where(Bt_Area.id == aid and Bt_Area.parentId == cid)
        verify_province_ = Bt_Area.select().where(Bt_Area.id == cid and Bt_Area.parentId == pid)
        verify_city_wrappers = await self.application.objects.execute(verify_city_)
        verify_province_wrappers = await self.application.objects.execute(verify_province_)

        if not verify_city_wrappers or not verify_province_wrappers:
            return self.send_message(False, 404, '创建失败 省市区参数错误', result)

        # 如果要设置为默认地址，先查询数据库是否有存在默认地址，有改为非默认
        if is_default:
            my_address_query = My_Address.select().where(My_Address.user_id == userid, My_Address.is_default == 1)
            my_address_wrappers = await self.application.objects.execute(my_address_query)
            if my_address_wrappers:
                for ad in my_address_wrappers:
                    ad.is_default = 0
                    await self.application.objects.update(ad)
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
            await self.application.objects.create(My_Address, **data_dict)
        except Exception as e:
            # 日志
            log.info('{} 地址创建失败:{}'.format(userid, data_dict))
        success, code, message, result = True, 0, '获取成功', result
        return self.send_message(success, code, message, result)


if __name__ == '__main__':
    async def test_banner_list():
        # res = await banner_list(0)
        print(1)


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_banner_list())
