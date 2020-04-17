from playhouse.shortcuts import JOIN, model_to_dict

from chefserver.config import PAGE_SIZE
from chefserver.models.point import User, User_Point, User_PointBill, BILL_TYPE_DICT, Product_Point_Detail, \
    Product_Point
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
            return self.send_message(False, 404, '商品部存在', result)
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
if __name__ == '__main__':
    async def test_banner_list():
        # res = await banner_list(0)
        print(1)


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_banner_list())
