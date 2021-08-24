# coding=utf-8
import configparser
import logging
import os
import time
import pymysql
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

cf = configparser.ConfigParser()


def get_root_path():
    """获取当前文件夹路径"""
    return os.path.dirname(os.path.abspath(__file__))


def log():
    """日志输出的函数实例"""
    return Log()


def readIni(filename, flag, _name):
    """读取ini文件"""
    """测试：print(readIni(r"../config.ini", 'config','url'))"""
    cf.read(filename, encoding="utf-8")
    # 获取配置文件中所有section
    secs = cf.sections()
    if flag in secs:
        # 获取某个section名下所对应的键
        options = cf.options(flag)
        if _name in options:
            # 返回配置文件中name所对应的值
            return cf.get(flag, _name)
        else:
            return "未找到对应的键名称(_name):" + str(_name)
    else:
        return "未找到对应的标签(flag):" + str(flag)


def readYaml(filename):
    """读取yaml文件"""
    """测试：print(readYaml("../data/yamlTest"))"""
    with open(filename, 'r', encoding='utf-8') as fp:
        contents = fp.read()
        testCase_dict = yaml.safe_load(contents)
        case_list = []
        for caseName, caseInfo in testCase_dict.items():
            new_dict = {caseName: caseInfo}
            case_list.append(new_dict)
        return case_list


class DB:
    """与数据库连接并执行想要的SQL脚本"""
    """测试：
    with DB() as db:
    sql = "SELECT name,adjustment,actual,frozen,transit,available FROM budget_item WHERE `name` = '" + "养老保险" + "';"
    db.execute(sql)
    bd = list(db)[0]
print("预算项：%s，调整后金额：%s，已发生金额：%s，冻结金额：%s，在途金额：%s，可用预算：%s" %
              (bd['name'], bd['adjustment'], bd['actual'], bd['frozen'], bd['transit'], bd['available']))"""

    def __init__(self, host=readIni(r'../config.ini', 'MysqlSetting', 'ip'), port=3306, db='nky',
                 user=readIni(r'../config.ini', 'MysqlSetting', 'user'),
                 passwd=readIni(r'../config.ini', 'MysqlSetting', 'password'), charset='utf8'):
        # 建立连接
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()


class Log:
    """输出日志"""
    """测试：
    log1 = Log()
    log1.info("test")
    """

    def __init__(self, log_path=os.path.join(get_root_path(), "../logs")):
        # log_path为拼接路径
        # 文件的命名
        self.log_path = log_path
        self.logName = os.path.join(self.log_path, '%s.log' % time.strftime('%Y_%m_%d'))

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 日志输出格式
        self.formatter = logging.Formatter('[%(asctime)s] - %(filename)s] - %(levelname)s: %(message)s')

    def __console(self, level, message):
        # 创建一个FileHandler，用于写到本地
        fh = logging.FileHandler(self.logName, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)

        # 这两行代码是为了避免日志输出重复问题
        self.logger.removeHandler(ch)
        self.logger.removeHandler(fh)

        # 关闭打开的文件
        fh.close()

    def debug(self, message):
        self.__console('debug', message)

    def info(self, message):
        self.__console('info', message)

    def warning(self, message):
        self.__console('warning', message)

    def error(self, message):
        self.__console('error', message)


class con:
    """UI自动化的低层包"""
    configName = "../config.ini"
    configFlag = "config"

    def __init__(self, interface=1):  # 如果不传driver，就默认这个值
        driverPath = os.path.join(get_root_path(), '../data/chromedriver.exe')
        if interface == 1:
            self.driver = webdriver.Chrome(driverPath)
            self.dr = self.driver.find_element_by_xpath
        else:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=driverPath)
            self.dr = self.driver.find_element_by_xpath
        self.driver.implicitly_wait(15)
        self.driver.set_window_size(1366, 1000)

    def quit(self):
        self.driver.quit()

    def getElement(self, _name,_filename, _flag,  _method='xpath'):
        """运用PO模式定位"""
        _location = readIni(_filename, _flag, _name)
        try:
            element = WebDriverWait(self.driver, 5).until(lambda x: x.find_element(_method, _location), message="定位失败")
        except:
            self.quit()
            log().error("文件%s中%s标签%s定位失败，请重试或手动检查" % (str(_filename),str(_flag),str(_name)))
        else:
            return element

    def ele(self,_name):
        """为更加简洁，省略PO模式两个参数"""
        return self.getElement(self.configName, self.configFlag, _name)

    def read(self,_name):
        return readIni(self.configName,self.configFlag,_name)

    def drs(self,location,data):
        try:
            WebDriverWait(self.driver,5).until(lambda x: x.find_element('xpath', location), message="定位失败")
            return self.dr(location).send_keys(data)
        except:
            self.quit()
            log().error("文件%s中%s标签%s定位失败，请重试或手动检查" % (str(self.configName), str(self.configFlag), str(location)))

    def drc(self,location):
        try:
            time.sleep(0.5)
            WebDriverWait(self.driver, 5).until(lambda x: x.find_element('xpath', location), message="定位失败")
            return self.dr(location).click()
        except:
            self.quit()
            log().error("文件%s中%s标签：%s定位失败，请重试或手动检查" % (str(self.configName), str(self.configFlag), str(location)))

    def login(self):
        self.driver.get(self.read('url'))
        self.drs(self.read('用户名'), self.read('account'))
        self.drs(self.read('密码'), self.read('password'))
        self.drc(self.read('登录按钮'))
        time.sleep(1)

    def menu(self,_name):
        # 选择菜单
        self.drc(readIni(self.configName,'菜单',_name))

    def assertInText(self, member):
        """ 断言 Just like self.assertTrue(a not in b), but with a nicer default message."""
        time.sleep(0.5)
        container = self.driver.page_source
        if member not in container:
            standardMsg = '%s 字段没有在页面中找到' % (member)
            log().warning(standardMsg)
        else:
            return '%s 字段断言成功' % member

    def screenShot(self):  # 截图
        # img文件夹路径
        img_path = os.path.join(get_root_path(), r"../img")
        # img文件夹不存在，新建该文件夹
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        # 获取当前日期
        local_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # 日期文件夹路径
        date_file_path = os.path.join(img_path, local_date)
        # 日期文件夹不存在，新建该文件夹
        if not os.path.exists(date_file_path):
            os.makedirs(date_file_path)
        # 截图存放路径
        local_time = time.strftime('%Y-%m-%d %H%M%S', time.localtime(time.time()))
        jt_name = local_time + '.png'
        jt_path = os.path.join(date_file_path, jt_name)
        try:
            self.driver.get_screenshot_as_file(jt_path)
            log().info(str(jt_path) + '截图保存成功')
        except BaseException:
            log().error('截图失败')

    def _cookie(self):
        """获取当前cookie"""
        return self.driver.get_cookies()


c = con()
c.login()
time.sleep(1)
c.quit()

