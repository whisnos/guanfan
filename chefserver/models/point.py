from datetime import datetime

from peewee import *

from chefserver.models.base import BaseModel


class User(BaseModel):
    userName = CharField(max_length=50, verbose_name='名')


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


OPTIONS_TYPE = {
    (1, 'every_day 每天N次'),
    (2, 'one_time 一次性'),
    (3, 'no_limit 没有限制'),
}


class Point_Setting(BaseModel):
    pointinfo = ForeignKeyField(Point_Info, verbose_name="积分类型")
    count = IntegerField(default=0, verbose_name="次数")
    options_type = IntegerField(choices=OPTIONS_TYPE, verbose_name="选项类型")
    status = BooleanField(default=True, verbose_name="状态")
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class User_Point(BaseModel):
    user = ForeignKeyField(User, verbose_name='用户')
    point = IntegerField(default=0, verbose_name='积分数')


BILL_TYPE = {
    (-1, '兑换现金'),
    (-2, '兑换奖品'),
    (1, '发布动态'),
    (2, '发布食谱'),
    (3, '发布评论'),
    (4, '发起打赏'),
    (5, '发起分享'),
    # (6, '兑换现金'),
    # (7, '兑换现金'),
    # (8, '兑换现金'),
    # (9, '兑换现金'),
}

BILL_TYPE_DICT = {
    -1: '兑换现金',
    -2: '兑换奖品',
    1: '发布动态',
    2: '发布食谱',
    3: '发布评论',
    4: '发起打赏',
    5: '发起分享',
    # (6, '兑换现金'),
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
    front_image = CharField(max_length=200, verbose_name="封面图")
    updatetime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class Product_Point_Detail(BaseModel):
    '''积分兑换 - 商品 - 详情图表'''
    product_point = ForeignKeyField(Product_Point, verbose_name="所属商品", backref="product_points")
    image = CharField(max_length=200, verbose_name="封面图")
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
