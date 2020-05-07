from datetime import datetime

from peewee import *

from chefserver.config import DATABASE
from chefserver.models.base import BaseModel

CHANNEL_TYPE = {
    (1, '1级'),
    (2, '2级'),
}


class Tao_Channel_Info(BaseModel):
    name = CharField(verbose_name="频道名称")
    iconImg = CharField(max_length=200, null=True, verbose_name="封面图")
    materialId = CharField(verbose_name="物料id")
    pid = ForeignKeyField('self', null=True, verbose_name="父级id", backref='channels')
    sort = IntegerField(default=0, verbose_name='排序')
    type = IntegerField(choices=CHANNEL_TYPE,verbose_name='分类等级')
    updateTime = DateTimeField(default=datetime.now, verbose_name="更新时间")


class tao_banner_info(BaseModel):
    title = CharField(verbose_name="名称")