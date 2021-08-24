# coding=utf-8
"""公共模块的定位"""
from service.PublicFunction import *


class Page(con):
    """Page的基类"""
    def test(self):

        a = self.getElement(r"common.ini",'MysqlSetting','ip')
        print(a)


c = Page()
c.test()


# print(readIni(r"common.ini", 'config','url'))


