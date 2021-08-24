# coding=utf-8
from service.PublicFunction import *

filename='pay.ini'


class charge(con):
    """收费标准"""
    flag = '收费标准'

    def _read(self,_name):
        return readIni(filename,self.flag,_name)



    def addCharge(self):
        # 新增收费标准
        time.sleep(1)
        self.menu('收支管理')
        time.sleep(1)
        self.menu('收费标准')
        time.sleep(1)
        self.drc(self._read("新增标准"))
        time.sleep(100)


a=charge()
a.login()
time.sleep(1)
a.addCharge()