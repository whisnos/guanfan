from playhouse.shortcuts import model_to_dict

from chefserver.models.point import User, User_Point, User_PointBill, BILL_TYPE_DICT
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
        except Exception as e:
            return self.send_message(False, 400, '获取失败', '')
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
                user_pointbill_query = user_pointbill_query.paginate(int(page),2)
            user_pointbills = await self.application.objects.execute(user_pointbill_query)
            for bill in user_pointbills:
                bill_dict = model_to_dict(bill)
                ct = bill_dict.get('createTime', None)
                bill_dict['bill_type'] = BILL_TYPE_DICT.get(bill_dict.get('bill_type'))
                if ct:
                    bill_dict['createTime'] = ct.strftime('%Y-%m-%d %H:%M:%S')
                result.append(bill_dict)
        except Exception as e:
            return self.send_message(False, 400, '获取失败', '')
        sucess, code, message = True, 0, '获取成功'
        return self.send_message(sucess, code, message, result)


if __name__ == '__main__':
    async def test_banner_list():
        # res = await banner_list(0)
        print(1)


    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_banner_list())
