import json
import logging
import math
import sys
import threading
import requests
import time
import hashlib
import tkinter as tk
from tkinter import Menu, Toplevel, messagebox


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
    # 请求相关工具参数
    dewuRequestMax = 3  # 请求最大次数
    dewuRequestWaitTime = 5

    # 元素
    tokenEntry = ""  # 文本输入框 Token 值

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
        self.text = text = tk.Text(self.root, width=100)  # 执行日志文本

        text.pack(side="top", expand="yes", fill="both")

        # 菜单
        menu = Menu(self.root)
        menus = Menu(menu, tearoff=0)
        menus.add_command(label="设置自动监测间隔时间(秒)", command=lambda: thread_it(topSetInterval))
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
        # self.getToken()
        self.root.mainloop()

    """
    关于产品
    """

    def about(self):
        messagebox.showinfo("关于", self.appVersions)

    """
    设置顶部信息
    """

    def setInfo(self):
        #                           enterDeposit                            interval
        return "保证金：" + str(self.enterDeposit) + " ；执行间隔 " + str(self.intervalTime) + "秒/次；"

    """
    获取Token
    
    文本无值从当前目录的dewuToken.txt文件获取token
    token 失效则自动打开浏览器获取
    """

    def getToken(self):
        token = self.tokenEntry.get()
        if token == "":  # 文本中token为空值
            try:
                with open('./dewuToken.txt', 'r', encoding='UTF-8') as f:
                    token = f.read()
                    f.close()
                    self.tokenEntry.insert("0", token)  # 回显token到文本
            except:
                messagebox.showerror("消息", "读取本地文件dewuToken.txt失败：" + str(sys.exc_info()[0]))
                return False
        else:
            with open('./dewuToken.txt', 'w', encoding='UTF-8') as f:
                f.write(token)
                f.close()

        self.token = token
        # 请求判断是否有效token
        res = self.get('/home/merchantInfo', '')
        if res['code'] == 200:
            return token
        else:  # 重新自动登录
            # self.textLog("获取token失败,尝试重新获取，3秒后执行","error")
            # time.sleep(3)
            yesNo = messagebox.askyesno("消息", "获取token失败,是否执行重新登录")
            if yesNo:
                return False
            else:
                return '0'

    """
    # ============================ Logging 文本日志 ============================
    """

    # 初始化日志
    def initLogging(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"  # 日期格式
        fp = logging.FileHandler(
            'log/log_' + time.strftime("%Y_%m_%d", time.localtime()) + '.txt', encoding='utf-8')
        fs = logging.StreamHandler()
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])  # 调用

    """
    # ============================ text log 文本日志 ============================
    """
    def textLog(self, log, colorType="def"):
        self.text.tag_add('tag', "end")
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

        self.text.tag_add(tag, "end")
        self.text.tag_config(tag, foreground=color)
        self.text.insert("end", "[" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]=====>" + str(
            log) + '\n',
                         tag)
        self.text.see('end')
        self.root.update()

    """
    # ============================ sign 签名 ============================
    """

    # 生成字符串
    def __arrayToString(self, array):
        strs = ''
        i = 0
        while i < len(array):
            strs += str(array[i][0]) + str(array[i][1])
            i += 1
        return strs

    # 数组排序
    def __arraySort(self, array):
        array = sorted(array.items())
        return array

    # sign 签名
    # 数据按照ASCII码排列
    def __returnSign(self, raw_sign_code_str):
        raw_sign_code_str += '048a9c4943398714b356a696503d2d36'
        # md5原始sign的字符串
        m = hashlib.md5()
        m.update(raw_sign_code_str.encode("utf8"))
        sign = m.hexdigest()
        return sign

    def getSign(self, data=None):
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

    # 请求
    #                     方式     地址  参数
    def dewuRequest(self, method, url, data, requestCount=0):
        if method == "POST" or method == "post":
            response = self.__post(url, data)
        else:
            response = self.__get(url, data)

        resData = json.loads(response.text)
        if response.status_code == 200 and resData["code"] == 200:  #  请求成功
            if requestCount > 0:
                self.textLog("尝试请求成功", "success")
            return resData
        if response.status_code == 401 or resData["code"] == 401:  # 401 重新写获取token
            # TODO token获取操作 只操作一次
            self.getToken()
        else:
            logging.error("接口请求失败：" + response.text)
            # 文本提示写入，重新请求获取
            if requestCount < self.dewuRequestMax:
                self.textLog("查询接口错误，尝试3次重新请求，第 " + str(requestCount + 1) + " 次", "warning")
                time.sleep(self.dewuRequestWaitTime)  # 等待下次请求时间
                requestCount += 1
                self.dewuRequest(method, url, data, requestCount)
            else:
                self.textLog("请求失败", "error")
                return False

    # GET 请求
    def __get(self, url, params):
        params = self.__request(params)
        logging.info(self.api + url, params, self.__headers())  # 日志记录请求
        res = requests.get(self.api + url, params=params,
                           headers=self.__headers())
        return res

    # POST 请求
    def __post(self, url, data):
        data = self.__request(data)
        logging.info(self.api + url, data, self.__headers())  # 日志记录请求
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
