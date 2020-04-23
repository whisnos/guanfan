from datetime import datetime

from peewee import *
from torpeewee import Model as torpeewee_model

from chefserver.config import DATABASE


class PeeModel(Model):
    createTime = DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        database = DATABASE


class BaseModel(PeeModel, torpeewee_model):
    pass
