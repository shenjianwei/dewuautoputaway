import json
import logging
import math
import os
import sys
import threading
import requests
import time
import hashlib
import tkinter as tk
from tkinter import Menu, Toplevel, messagebox
from selenium import webdriver
from selenium.webdriver import common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput.mouse import Button, Controller as c1
# from pynput.keyboard import Key, Controller as c2


class App:
    """
    config

    默认的初始化配置参数
    """
    # 参数
    appVersions = "得物APP自动化脚本 V0.3.1"  # 项目信息
    enterDeposit = 0  # 保证金
    intervalTime = 10  # 执行间隔时间（秒）
    token = ""  # Token值
    url = 'https://stark.dewu.com'  # 请求域名
    api = url + '/api/v1/h5/biz'  # 请求地址
    dewuTokenFilePath = "./dewuToken.txt"
    # 请求相关工具参数
    dewuRequestMax = 3  # 请求最大次数
    dewuRequestWaitTime = 5  # 请求等待间隔时间
    dewuRequestAgainToken = False  # 重新获取token机会

    # 元素
    tokenEntry = ""  # 文本输入框 Token 值
    logTextDom = ""  # 日志 text 框

    def __init__(self):
        self.initLogging()  # 初始化日志

        self.root = tk.Tk()
        self.root.title(self.appVersions)

        self.userInfo = tk.Label(self.root, text=self.setInfo(), justify="left")
        self.userInfo.pack()

        tk.Label(self.root, text="Passport Token：", anchor="w").pack(side="top", fill="x")
        tk.Label(self.root, text="Token说明：用于请求接口时所用到的验证参数。Token获取方式：在登录得物商家后台，请求接口中passporttoken字段的值。", anchor="w",
                 fg="red").pack(side="top", fill="x")
        self.tokenEntry = tk.Entry(self.root)
        self.tokenEntry.pack(side="top", fill="x")
        tk.Label(self.root, text="上架库存：", anchor="w").pack(side="top", fill="x")
        tk.Label(self.root, text="价格过低商品日志：", anchor="w").pack(side="top", fill="x")

        frame1 = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frame1.pack(fill="x", ipady=2)
        tk.Label(frame1, text="上架库存：", anchor="w").pack(padx=2, pady=0, side="left", fill="x", expand="yes")
        tk.Label(frame1, text="价格过低商品日志：", anchor="w").pack(padx=2, pady=0, side="right", fill="x", expand="yes")

        frame2 = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frame2.pack(fill="x", ipady=3)
        self.saleGoodsListText = tk.Text(frame2, width=72, height=12)
        self.saleGoodsListText.pack(padx=3, pady=0, side="left", fill="both", expand="yes")
        self.saleLowGoodsListText = tk.Text(frame2, height=12)
        self.saleLowGoodsListText.pack(padx=3, pady=0, side="right", fill="both", expand="yes")

        tk.Label(self.root, text="执行日志：", anchor="w").pack(side="top", fill="x")
        self.logTextDom = tk.Text(self.root, width=100)  # 执行日志文本
        self.logTextDom.pack(side="top", expand="yes", fill="both")

        # 菜单
        menu = Menu(self.root)
        menus = Menu(menu, tearoff=0)
        menus.add_command(label="设置自动监测间隔时间(秒)")
        menu.add_cascade(label="设置", menu=menus)
        menu.add_command(label='关于', command=self.about)
        self.root.config(menu=menu)

        frameBtn = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frameBtn.pack(fill="x", ipady=10)

        self.startBtn = tk.Button(frameBtn, text="开始执行")
        self.startBtn.pack(padx=15, pady=10, side="left", fill="both", expand="yes")
        # button1.grid(row=0, column=1)
        tk.Button(frameBtn, text="结束执行", ).pack(padx=15, pady=10, side="right", fill="both", expand="yes")

        # 初始化获得Token
        self.thread_it(App.getToken, self)
        self.root.mainloop()

    # self.getToken()
    def thread_it(self, func, *args):
        """
        将函数打包进线程
        :param func: 方法（Class.func）
        :param args: 参数 (self|*args)
        :return:
        """
        # 创建
        t = threading.Thread(target=func, args=args)
        # 守护 !!!
        t.setDaemon(True)
        # 启动
        t.start()
        # 阻塞--卡死界面！
        # t.join()

    def about(self):
        """
        关于产品 - 弹窗提示
        """
        messagebox.showinfo("关于", self.appVersions)

    def setInfo(self):
        """
        设置顶部信息
        :return: String
        """
        #                           enterDeposit                            interval
        return "保证金：" + str(self.enterDeposit) + " ；执行间隔 " + str(self.intervalTime) + "秒/次；"

    def getToken(self):
        """
        获取Token

        文本无值从当前目录的dewuToken.txt文件获取token
        token 失效则自动打开浏览器获取
        :return: token|False
        """
        token = self.tokenEntry.get()
        if token == "":  # 文本中token为空值
            try:
                with open(self.dewuTokenFilePath, 'r', encoding='UTF-8') as f:
                    token = f.read()
                    f.close()
                    self.tokenEntry.insert("0", token)  # 回显token到文本
            except:
                messagebox.showerror("消息", "读取本地文件" + self.dewuTokenFilePath + "失败：" + str(sys.exc_info()[0]))
                return False
        else:
            with open(self.dewuTokenFilePath, 'w', encoding='UTF-8') as f:
                f.write(token)
                f.close()

        self.token = token
        # 请求判断是否有效token
        res = self.dewuRequest('get', '/home/merchantInfo', '')
        if res:
            if res['code'] == 200:
                return token

        return False

    def authLogin(self):
        """
        打开浏览器登录获取token
        :return: token|""
        """
        mouse = c1()
        url = self.url + '/business/login.html'
        options = webdriver.ChromeOptions()
        # 设置浏览器初始 位置x,y & 宽高x,y
        # 不加载图片,加快访问速度
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2})
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        # 关闭自动测试状态显示
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options.add_experimental_option(
            'excludeSwitches', ['enable-automation'])
        # 关闭开发者模式
        options.add_experimental_option("useAutomationExtension", False)
        # 添加本地代理
        # options.add_argument("--proxy--server=127.0.0.1:8080")
        # 添加UA
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        options.add_argument('user-agent=' + ua)

        driver = webdriver.Chrome(
            executable_path="./lib/chromedriver.exe", options=options)
        # 通过浏览器的dev_tool在get页面钱将.webdriver属性改为"undefined"
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",
        })
        driver.maximize_window()
        WebDriverWait(driver, 10)
        driver.get(url)
        while True:
            time.sleep(2)
            mouse.position = (1450, 370)
            mouse.press(Button.left)
            mouse.move(1450, 373)
            time.sleep(2)
            mouse.release(Button.left)
            WebDriverWait(driver, 5, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'nc-lang-cnt')))
            if driver.find_element_by_class_name('nc-lang-cnt').text == '验证通过':
                break
            else:
                driver.refresh()

        time.sleep(1)
        driver.find_element_by_xpath(
            '//*[@placeholder="请输入手机号码"]').send_keys(15757395822)  # 15355979998
        driver.find_element_by_xpath(
            '//*[@placeholder="请输入密码"]').send_keys('Dyf131452')  # jeefNO1
        driver.find_element_by_class_name('el-button').click()
        time.sleep(3)
        cookies = driver.get_cookies()  # Selenium为我们提供了get_cookies来获取登录cookies
        driver.close()  # 获取cookies便可以关闭浏览器
        # 获取cookies中的token
        token = self.getJsonToken(cookies, "mchToken")
        self.openFile(self.dewuTokenFilePath, 'w', token)  # 写入token文件中
        return token

    def getJsonToken(self, tokenJson, tokenKey):
        """
        获取json中的token值
        :param tokenJson: Json参数
        :param tokenKey: 键
        :return: token|""
        """
        # tokenJson = json.loads(tokenJson)
        tokenValue = ""
        for jsonItem in tokenJson:
            if jsonItem['name'] == tokenKey:
                tokenValue = jsonItem['value']
        return tokenValue

    """
    # ============================ Helprs 帮助函数 ============================
    """

    def initLogging(self):
        """
        初始化日志
        :return: 无
        """
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"  # 日期格式
        self.openPath("./log")
        fp = logging.FileHandler(
            './log/log_' + time.strftime("%Y_%m_%d", time.localtime()) + '.txt', encoding='utf-8')
        fs = logging.StreamHandler()
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])  # 调用

    def openFile(self, path, action, content=""):
        """
        打开文件操作，包括写入读取
        :param path: 请求路径
        :param action: 文件操作动作
        :param content: 写入内容内容
        :return: String - 返回文件读取内容或写入内容
        """
        text = str(content)
        global f
        try:
            def wFile():
                f = open(path, "w", encoding='UTF-8')
                f.write(text)

            if action == "w":
                wFile()
            # if action == "r":
            else:
                # 没有文件，则新建空白文件
                if not os.path.isfile(path):
                    wFile()

                f = open(path, "r", encoding='UTF-8')
                text = f.read()

        finally:
            if f:
                f.close()
        return text

    def openPath(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    """
    # ============================ text log 文本日志 ============================
    """

    def textLog(self, log, colorType="def"):
        """
        文本日志输出显示
        :param log: 日志内容
        :param colorType: 日志类型：error、success、info、sub、warning
        :return:
        """
        self.logTextDom.tag_add('tag', "end")
        if colorType == "error":
            tag = 'tag_error'
            color = '#ed4014'
        elif colorType == "success":
            tag = 'tag_success'
            color = '#19be6b'
        elif colorType == "info":
            tag = 'tag_info'
            color = '#2db7f5'
        elif colorType == "sub":
            tag = 'tag_sub'
            color = '#515a6e'
        elif colorType == "warning":
            tag = 'tag_warning'
            color = '#ff9900'
        else:
            tag = 'tag_def'
            color = '#000000'

        self.logTextDom.tag_add(tag, "end")
        self.logTextDom.tag_config(tag, foreground=color)
        self.logTextDom.insert("end", "[" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]=====>" + str(
            log) + '\n',
                               tag)
        self.logTextDom.see('end')
        self.root.update()

    """
    # ============================ sign 签名 ============================
    """

    def __arrayToString(self, array):
        """
        生成字符串
        :param array: 数组
        :return: String 返回数组的键值拼接
        """
        strs = ''
        i = 0
        while i < len(array):
            strs += str(array[i][0]) + str(array[i][1])
            i += 1
        return strs

    def __arraySort(self, array):
        """
        数组排序
        :param array:
        :return:
        """
        array = sorted(array.items())
        return array

    def __returnSign(self, raw_sign_code_str):
        """
        加密sign签名
        数据按照ASCII码排列
        :param raw_sign_code_str:
        :return:
        """
        raw_sign_code_str += '048a9c4943398714b356a696503d2d36'
        # md5原始sign的字符串
        m = hashlib.md5()
        m.update(raw_sign_code_str.encode("utf8"))
        sign = m.hexdigest()
        return sign

    def getSign(self, data=None):
        """
        获取签名
        :param data:
        :return:
        """
        if data is None:
            data = dict()
        if (len(data) > 0):
            data = self.__arraySort(data)
            data = self.__arrayToString(data)
        else:
            data = ''
        sign = self.__returnSign(data)
        return sign

    """
    # ============================ request 请求 ============================
    """

    def dewuRequest(self, method, url, data, requestCount=0):
        """
        请求方法
        :param method: 请求方式
        :param url: 请求地址
        :param data: 请求参数
        :param requestCount: 重新尝试请求次数
        :return:
        """
        if method == "POST" or method == "post":
            response = self.__post(url, data)
        else:
            response = self.__get(url, data)

        logging.info("[接口][返回]" + response.text)

        resData = json.loads(response.text)
        if response.status_code == 200 and resData["code"] == 200:  # 请求成功
            if requestCount > 0:
                self.textLog("尝试请求成功", "success")
            return resData
        if response.status_code == 401 or resData["code"] == 401:  # 401 重新写获取token 只执行一次的Token获取
            if not self.dewuRequestAgainToken:
                self.dewuRequestAgainToken = True
                self.textLog("Token失效尝试重新获取", "warning")
                self.token = self.authLogin()
                return self.dewuRequest(method, url, data, requestCount)
            else:
                logging.error("[接口][请求失败][Token重新获取失效]" + response.text)
                self.textLog("请求失败：" + resData["msg"], "error")
                return False
        else:
            logging.error("[接口][请求失败]" + response.text)
            # 文本提示写入，重新请求获取
            if requestCount < self.dewuRequestMax:
                self.textLog("查询接口错误，尝试3次重新请求，第 " + str(requestCount + 1) + " 次", "warning")
                time.sleep(self.dewuRequestWaitTime)  # 等待下次请求时间
                requestCount += 1
                return self.dewuRequest(method, url, data, requestCount)
            else:
                logging.error("[接口][请求失败]" + "多次请求失败")
                self.textLog("请求失败：" + resData["msg"], "error")
                return False

    # GET 请求
    def __get(self, url, params):
        params = self.__request(params)
        logging.info(
            "[接口][请求][请求地址]" + self.api + url + "[请求参数]" + str(params) + "[请求头]" + str(self.__headers()))  # 日志记录请求
        res = requests.get(self.api + url, params=params, headers=self.__headers())
        return res

    # POST 请求
    def __post(self, url, data):
        data = self.__request(data)
        logging.info(
            "[接口][请求][请求地址]" + self.api + url + "[请求参数]" + str(data) + "[请求头]" + str(self.__headers()))  # 日志记录请求
        res = requests.post(
            self.api + url, data=json.dumps(data), headers=self.__headers())
        return res

    # 请求参数处理
    def __request(self, params):
        if len(params) > 0:
            params['sign'] = self.getSign(params)
        else:
            params = dict()
            params['sign'] = self.getSign()
        return params

    # 请求头处理
    def __headers(self):
        return {
            'channel': 'pc',
            'clientid': 'stark',
            'content-type': 'application/json;charset=UTF-8',
            'passporttoken': self.token,
            'syscode': 'DU_USER'
        }


app = App()