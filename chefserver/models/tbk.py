from datetime import datetime

from peewee import *

from chefserver.config import DATABASE
from chefserver.models.base import BaseModel
from chefserver.models.point import User

CHANNEL_LEVEL = {
    (1, '1级'),
    (2, '2级'),
}
CHANNEL_TYPE = {
    (0, '管方提供'),
}
PROMOTE_TYPE = {
    (0, "IOS"),
    (1, "安卓"),
}


class Tao_Promote_Info(BaseModel):
    promoteID = CharField(max_length=50, verbose_name="推广位id")
    type = SmallIntegerField(choices=PROMOTE_TYPE, verbose_name="类型")
    updateTime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class Tao_Channel_Info(BaseModel):
    name = CharField(verbose_name="频道名称")
    iconImg = CharField(max_length=200, null=True, verbose_name="封面图")
    materialId = CharField(verbose_name="物料id")
    pid = ForeignKeyField('self', null=True, verbose_name="父级id", backref='channels')
    sort = IntegerField(default=0, verbose_name='排序')
    level = IntegerField(choices=CHANNEL_LEVEL, verbose_name='分类等级')
    type = IntegerField(choices=CHANNEL_TYPE, default=0, verbose_name='频道类型')
    updateTime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class Tao_Banner_Info(BaseModel):
    title = CharField(verbose_name="名称")
    content = CharField(max_length=200, verbose_name="转链")
    img = CharField(max_length=200, verbose_name="封面图")
    sort = IntegerField(default=0, verbose_name='排序')


class Tao_Recommend_Info(BaseModel):
    name = CharField(verbose_name="名称")
    materialId = CharField(verbose_name="物料id")
    sort = IntegerField(default=0, verbose_name='排序')
    updateTime = DateTimeField(default=datetime.now, verbose_name="更新时间")


COLLECT_TYPE = {
    (0, '足迹'),
    (1, '收藏')
}


class Tao_Collect_Info(BaseModel):
    user = ForeignKeyField(User, verbose_name="所属用户", backref="user_collects")
    itemId = CharField(max_length=50, verbose_name="商品id")
    type = SmallIntegerField(choices=COLLECT_TYPE, verbose_name='类型')
    status = SmallIntegerField(default=0, verbose_name='状态')
    # is_delete = BooleanField(default=False, verbose_name="是否删除")
    updateTime = DateTimeField(default=datetime.now, verbose_name="更新时间")
