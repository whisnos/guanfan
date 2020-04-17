from peewee import MySQLDatabase

from chefserver.models.point import Point_Info, Point_Setting, User_Point, User_PointBill, Product_Point, \
    Product_Point_Detail

DATABASE = MySQLDatabase(
    'masterchefmb4', host='127.0.0.1', port=3306,
    user='root', password='root')


def init():
    # 生成表
    DATABASE.create_tables([Point_Info, Point_Setting, User_Point, User_PointBill, Product_Point, Product_Point_Detail])


if __name__ == "__main__":
    init()
