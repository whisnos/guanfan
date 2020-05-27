from datetime import datetime

from peewee import *

from chefserver.config import DATABASE
from chefserver.models.base import BaseModel


class User(BaseModel):
    userName = CharField(max_length=50, verbose_name='名')
    certificationStatus = IntegerField(verbose_name="认证状态")
    status = IntegerField(verbose_name="状态")

POINT_TYPE = {
    (0, '动态'),
    (1, '食谱'),
    (2, '评论'),
    (3, '打赏'),
    (4, '分享'),
}


class Point_Info(BaseModel):
    point_type = IntegerField(choices=POINT_TYPE, verbose_name="积分类型")
    grade_no = IntegerField(verbose_name="积分数")
    status = BooleanField(default=True, verbose_name="状态")

OPTIONS_TYPE = {
    (1, 'every_day 每天N次'),
    (2, 'one_time 一次性'),
    (3, 'no_limit 没有限制'),
}


class Point_Setting(BaseModel):
    pointinfo = ForeignKeyField(Point_Info, verbose_name="积分类型")
    count = IntegerField(default=0, verbose_name="次数")
    options_type = IntegerField(choices=OPTIONS_TYPE, verbose_name="选项类型")
    # status = BooleanField(default=True, verbose_name="状态")
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class User_Point(BaseModel):
    user = ForeignKeyField(User, verbose_name='用户')
    point = IntegerField(default=0, verbose_name='积分数')


BILL_TYPE = {
    (-1, '兑换现金'),
    (-2, '兑换奖品'),
    (-3, '平台扣减'),
    (1, '发布动态'),
    (2, '发布食谱'),
    (3, '发布评论'),
    (4, '发起打赏'),
    (5, '发起分享'),
    (6, '平台赠送'),
    # (6, '兑换现金'),
    # (7, '兑换现金'),
    # (8, '兑换现金'),
    # (9, '兑换现金'),
}

BILL_TYPE_DICT = {
    -1: '兑换现金',
    -2: '兑换奖品',
    -3: '平台扣减',
    1: '发布动态',
    2: '发布食谱',
    3: '发布评论',
    4: '发起打赏',
    5: '发起分享',
    6: '平台赠送',
    # (7, '兑换现金'),
    # (8, '兑换现金'),
    # (9, '兑换现金'),
}

BILL_STATUS = {
    (0, '已完成'),
    (1, '审核中'),
}


class User_PointBill(BaseModel):
    user = ForeignKeyField(User, verbose_name='用户')
    bill_type = IntegerField(choices=BILL_TYPE, verbose_name="账单类型")
    bill_status = IntegerField(choices=BILL_STATUS, verbose_name="账单状态")
    grade_no = IntegerField(verbose_name='单笔积分数')

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.userName).join(User)


class Product_Point(BaseModel):
    '''积分兑换 - 商品表'''
    title = CharField(max_length=100, verbose_name="商品标题")
    grade_no = IntegerField(verbose_name='积分数')
    sku_no = IntegerField(verbose_name="库存数")
    front_image = CharField(max_length=200, verbose_name="封面图")
    status = SmallIntegerField(default=0, verbose_name='状态')
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class Product_Point_Detail(BaseModel):
    '''积分兑换 - 商品 - 详情图表'''
    product_point = ForeignKeyField(Product_Point, verbose_name="所属商品", backref="product_points")
    image = CharField(max_length=200, verbose_name="封面图")
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")

    @classmethod
    def extend(cls):
        return cls.select(cls, Product_Point.id, Product_Point.title).join(Product_Point)


class Express_Info(BaseModel):
    '''快递公司'''
    name = CharField(verbose_name="快递公司名称")


EXPRESS_STATUS = {
    (0, '代发货'),
    (1, '已发货'),
    (2, '已完成'),
}


class My_Express_Info(BaseModel):
    '''我的快递'''
    # user = ForeignKeyField(User, verbose_name="所属用户", backref="user_expresses")
    express_info = ForeignKeyField(Express_Info, verbose_name="快递公司")
    express_no = CharField(max_length=50, verbose_name="快递单号")
    express_status = IntegerField(choices=EXPRESS_STATUS, default=0, verbose_name="快递状态")
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")

    @classmethod
    def extend(cls):
        return cls.select(cls, Express_Info.id, Express_Info.name).join(Express_Info, join_type=JOIN.LEFT_OUTER,
                                                                        on=cls.express_info).switch(cls)


class My_Exchange_Info(BaseModel):
    '''我的兑换'''
    product_point = ForeignKeyField(Product_Point, verbose_name="所属商品", backref="product_exchanges")
    express = ForeignKeyField(My_Express_Info, null=True, verbose_name="我的快递")
    user = ForeignKeyField(User, verbose_name="所属用户", backref="user_exchanges")
    express_status = IntegerField(choices=EXPRESS_STATUS, default=0, verbose_name="快递状态")
    goods_no = IntegerField(verbose_name="商品数量")
    grade_no = IntegerField(verbose_name='积分数')
    remark = CharField(max_length=50, verbose_name='备注')
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")

    @classmethod
    def extend(cls):
        # 1. 多表join
        # return cls.select(cls.id, cls.express_status, cls.grade_no, cls.goods_no, cls.createTime, cls.remark,
        #                   Product_Point.id, Product_Point.title, My_Express_Info.id, My_Express_Info.express_no, User.id).join(
        #     Product_Point, join_type=JOIN.LEFT_OUTER, on=cls.product_point).switch(cls).join(
        #     My_Express_Info, join_type=JOIN.LEFT_OUTER, on=cls.express).switch(cls).join(
        #     User, join_type=JOIN.LEFT_OUTER, on=cls.user).switch(cls)
        return cls.select(cls,
                          Product_Point, My_Express_Info.id, My_Express_Info.express_no, User).join(
            Product_Point, join_type=JOIN.LEFT_OUTER, on=cls.product_point).switch(cls).join(
            My_Express_Info, join_type=JOIN.LEFT_OUTER, on=cls.express).switch(cls).join(
            User, join_type=JOIN.LEFT_OUTER, on=cls.user).switch(cls)


class My_History_Address(BaseModel):
    '''用户历史地址'''
    user = ForeignKeyField(User, verbose_name="所属用户", backref="user_history_addresses")
    exchangeorder = ForeignKeyField(My_Exchange_Info, verbose_name="用户兑换订单", backref="my_exchanges")
    name = CharField(max_length=50, verbose_name="收件人")
    mobile = CharField(max_length=20, verbose_name="手机号")
    province = CharField(max_length=20, verbose_name="省")
    city = CharField(max_length=20, verbose_name="市")
    area = CharField(max_length=20, verbose_name="区")
    address = CharField(max_length=30, verbose_name="详细地址")


class Area(Model):
    '''省市区'''
    pid = IntegerField(verbose_name="行政区代码",null=True)
    node = CharField(verbose_name="行政区代码",null=True)
    name = CharField(max_length=50, verbose_name="名称")
    level = IntegerField(verbose_name="级别标志 1省 2市 3区")
    lat =DoubleField()
    lng=DoubleField()
    class Meta:
        database = DATABASE

class My_Address(BaseModel):
    '''收货地址'''
    user = ForeignKeyField(User, verbose_name="所属用户", backref="user_addresses")
    name = CharField(max_length=50, verbose_name="收件人")
    mobile = CharField(max_length=20, verbose_name="手机号")
    province = ForeignKeyField(Area, verbose_name="省")
    city = ForeignKeyField(Area, verbose_name="市")
    area = ForeignKeyField(Area, verbose_name="区")
    address = CharField(max_length=30, verbose_name="详细地址")
    is_default = BooleanField(default=False, verbose_name="是否默认地址")
    is_delete = BooleanField(default=False, verbose_name="是否删除")
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")


def just_test():
    # obj = User_Point()
    # obj.user_id = 2
    # obj.point = 10
    # obj.save()
    obj = Point_Info.get(Point_Info.id == 1)
    # delete
    obj.delete_instance()
    Point_Info.delete().where(Point_Info.id == 1).execute()
    # print(obj.grade_no)
    # obj = Point_Info.filter(id=1)[0]
    # print(obj.test_name)
    # points = Point_Info.select().where(Point_Info.id >= 1 & Point_Info.point_type == 1)
    # points = Point_Info.select().order_by(Point_Info.id.desc().asc())
    points = User_Point.select().order_by(User_Point.point.desc()).paginate(2, 3)
    # points = User_Point.update().where(Point_Info.id >= 1 & Point_Info.point_type == 1).execute()
    # points = User_Point.update(point=User_Point+1).where(Point_Info.id >= 1 & Point_Info.point_type == 1).execute()
    # print(points)
    # for p in points:
    #     print(p.grade_no)
    # points = User_Point.select().where(User_Point.user_id == 1)
    print(points, type(points))
    for p in points:
        print(p.user.userName)


if __name__ == '__main__':
    just_test()
