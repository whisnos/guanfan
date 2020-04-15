from datetime import datetime

from peewee import *

from chefserver.config import DATABASE


class BaseModel(Model):
    createTime = DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        database = DATABASE
