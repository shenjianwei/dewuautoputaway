import json
import logging
import math
import os
import re
import sys
import threading
import requests
import time
import wx
import wx.adv
import hashlib
import tkinter as tk
from tkinter import Menu, Toplevel, messagebox
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput.mouse import Button, Controller as c1


# from pynput.keyboard import Key, Controller as c2

# ----------------------------------------------------
# | 编译语句 -- --onefile... 用于影藏的调用鼠标键盘工具
# | pyinstaller auto_putaway.py --onefile --hidden-import=pynput.keyboard._xorg --hidden-import=pynput.mouse._xorg --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32
# ----------------------------------------------------
import winapi


class App(wx.adv.TaskBarIcon):
    """
    config

    默认的初始化配置参数
    """
    DEBUGER = True
    # 参数
    appVersions = "得物APP自动化脚本 V0.5.1"  # 项目信息
    enterDeposit = 0  # 保证金
    enterDepositPlenty = True  # 保证金是否充足
    intervalTime = (10 if DEBUGER else 60)  # 执行间隔时间（秒）
    token = ""  # Token值
    url = 'https://stark.dewu.com'  # 请求域名
    api = url + '/api/v1/h5/biz'  # 请求地址
    dewuTokenFilePath = "./dewuToken.txt"
    root = ""
    # 进程相关参数
    endThread = False  # 进程管理
    endCycleThread = False  # 循环进程管理
    startCycleTasks = False  # 是否开始循环任务
    startCycle = False  # 是否开始循环任务2
    autoNum = 0  # 自动循环次数
    firstPutaway = False  # 是否第一次执行 用于修改价格过低的输入框清除重置操作
    firstGetSubNum = True  # 是否第一次进订单 第一次，则默认使用最大订单号，作为之后的比较用
    orderSubNum = ""  # 比对订单号
    autoStart = False  # 自动开始状态
    # 请求相关工具参数
    dewuRequestMax = 3  # 请求最大次数
    dewuRequestWaitTime = 5  # 请求等待间隔时间
    dewuRequestAgainToken = False  # 重新获取token机会
    # 库存相关参数
    saleGoodsList = []  # 库存商品列表
    txtParamNum = 3  # 库存规格字段数
    # 订单相关
    orderList = []
    haveUpdate = False  # 是否有新订单
    everyHaveUpdate = False  # 每次是否有新订单
    newOrderCount = 0  # 新订单数量
    newUpGoodsInfo = ""  # 新上架商品信息
    firstOrder = False


    # 元素
    intervalTimeEntry = ""  # 间隔时间输入框
    intervalTimeSetBtn = ""  # 间隔时间 设置按钮

    cycleTimes = (5 if DEBUGER else 10)  # 循环次数
    cycleTimesEntry = ""  # 循环次数输入框
    cycleTimesSetBtn = ""  # 循环次数 设置按钮

    tokenEntry = ""  # 文本输入框 Token 值
    logListBoxDom = ""  # 日志 List 列表框
    logTextDom = ""  # 日志 Text 框
    startBtn = ""  # 开始 Button 按钮
    saleGoodsListText = ""  # 库存 Text 框
    orderListText = "" # 销售日志 Text 框

    # 弹窗
    toplevelSetInterval = ""  # 设置间隔时间弹窗
    topSetIntervalEntry = ""  # 设置间隔时间文本输入框 Token 值

    # 查看渠道价弹窗
    topWatchCurMinPrice = ""  # 弹窗

    # 浏览器参数
    driverSelf = ""

    # 托盘参数
    ICON = './lib/favicon.ico'
    TITLE = '得物App自动上架系统托盘图标'
    HAVE_NEW_MSG = False
    STOP_FLASH = True

    MENU_ID1, MENU_ID2 = wx.NewIdRef(count=2)

    def __init__(self):
        super().__init__()

        # 设置图标和提示
        self.SetIcon(wx.Icon(self.ICON), self.TITLE)

        # 绑定菜单项事件
        self.Bind(wx.EVT_MENU, self.onShow, id=self.MENU_ID1)
        self.Bind(wx.EVT_MENU, self.onExit, id=self.MENU_ID2)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.onShow)

        self.initLogging()  # 初始化日志

        self.root = tk.Tk()
        self.root.title(self.appVersions)

        frame0 = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frame0.pack(fill="x", ipady=2)
        self.userInfo = tk.Label(frame0, text=self.setInfo())
        self.userInfo.pack(padx=2, pady=0, side="left", fill="x", expand="no")
        # times.pack_forget()
        self.intervalTimeEntry = tk.Entry(frame0, width=10, justify='center')
        self.intervalTimeEntry.pack(padx=2, pady=0, side="left", fill="x", expand="no")
        self.intervalTimeEntry.insert("0", self.intervalTime)
        tk.Label(frame0, text="秒/次", anchor="w").pack(padx=2, pady=0, side="left", fill="x", expand="no")
        self.intervalTimeSetBtn = tk.Button(frame0, text="设置", height=1,
                                            command=lambda: self.thread_it(App.setInterval, self))
        self.intervalTimeSetBtn.pack(padx=2, pady=0, side="left", fill="x", expand="no")
        # self.intervalTimeConfirmBtn = tk.Button(frame0, text="确定")

        tk.Label(frame0, text="循环次数：", anchor="w").pack(padx=2, pady=0, side="left", fill="x", expand="no")
        self.cycleTimesEntry = tk.Entry(frame0, width=10, justify='center')
        self.cycleTimesEntry.insert("0", self.cycleTimes)
        self.cycleTimesEntry.pack(padx=2, pady=0, side="left", fill="x", expand="no")
        tk.Label(frame0, text="次", anchor="w").pack(padx=2, pady=0, side="left", fill="x", expand="no")
        self.cycleTimesSetBtn = tk.Button(frame0, text="设置", height=1,
                                          command=lambda: self.thread_it(App.setCycleTimes, self))
        self.cycleTimesSetBtn.pack(padx=2, pady=0, side="left", fill="x", expand="no")
        # self.cycleTimesConfirmBtn = tk.Button(frame0, text="确定")

        # self.userInfo = tk.Label(self.root, text=self.setInfo(), justify="left")
        # self.userInfo.pack()

        # tk.Label(self.root, text="Passport Token：", anchor="w").pack(side="top", fill="x")
        tk.Label(self.root, text="Token说明：用于请求接口时所用到的验证参数。Token获取方式：在登录得物商家后台，请求接口中passporttoken字段的值。", anchor="w",
                 fg="red").pack(side="top", fill="x")
        self.tokenEntry = tk.Entry(self.root)
        self.tokenEntry.pack(side="top", fill="x")

        frame1 = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frame1.pack(fill="x", ipady=2)
        tk.Label(frame1, text="上架库存：", anchor="w", height=1, width=40).pack(padx=2, pady=0, side="left", fill="x", expand="yes")
        tk.Label(frame1, text="价格过低商品日志：", anchor="w", height=1, width=40).pack(padx=2, pady=0, side="left", fill="x", expand="yes")
        tk.Label(frame1, text="待发货销售日志：", anchor="w", height=1, width=40).pack(padx=2, pady=0, side="right", fill="x", expand="yes")

        frame2 = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frame2.pack(fill="x", ipady=3)
        self.saleGoodsListText = tk.Text(frame2, width=40, height=12)  # 43
        self.saleGoodsListText.pack(padx=2, pady=0, side="left", fill="x", expand="yes")
        self.saleLowGoodsListText = tk.Text(frame2, width=40, height=12)  # 47
        self.saleLowGoodsListText.pack(padx=2, pady=0, side="left", fill="x", expand="yes")
        self.orderListText = tk.Text(frame2, width=40, height=12)
        self.orderListText.pack(padx=2, pady=0, side="right", fill="x", expand="yes")

        tk.Label(self.root, text="执行日志：", anchor="w").pack(side="top", fill="x")
        # self.logListBoxDom = tk.Listbox(self.root)
        # self.logListBoxDom.pack(side="top", expand="yes", fill="both")
        self.logTextDom = tk.Text(self.root, width=100)  # 执行日志文本
        self.logTextDom.pack(side="top", expand="yes", fill="both")

        # 菜单
        menu = Menu(self.root)
        menus = Menu(menu, tearoff=0)
        menus.add_command(label="设置自动监测间隔时间(秒)", command=lambda: self.thread_it(App.topSetInterval, self))
        menu.add_cascade(label="设置", menu=menus)
        menu.add_command(label='关于', command=self.about)
        self.root.config(menu=menu)

        frameBtn = tk.Frame(self.root, relief="ridge")
        # 设置填充和布局
        frameBtn.pack(fill="x", ipady=10)

        self.startBtn = tk.Button(frameBtn, text="开始执行", command=lambda: self.thread_it(App.startTask, self))
        self.startBtn.pack(padx=15, pady=10, side="left", fill="both", expand="yes")
        # button1.grid(row=0, column=1)
        tk.Button(frameBtn, text="结束执行", fg="red", command=lambda: self.thread_it(App.endTask, self)).pack(padx=15, pady=10, side="left", fill="both", expand="yes")
        tk.Button(frameBtn, text="获取价格", fg="#2db7f5", command=lambda: self.thread_it(App.watchCurMinPrice, self)).pack(padx=15, pady=10, side="right", fill="both", expand="yes")

        if self.DEBUGER:
            tk.Button(self.root, text="读取文本数据", command=lambda: self.thread_it(App.test, self, "read")).pack(
                side="left")
            tk.Button(self.root, text="测试下架", command=lambda: self.thread_it(App.test, self, "down")).pack(side="left")
            tk.Button(self.root, text="测试上架和修改价格", command=lambda: self.thread_it(App.test, self, "up")).pack(
                side="left")
            # tk.Button(self.root, text="测试修改价格", command=lambda: self.thread_it(App.test, self, "update")).pack(side="left")
            tk.Button(self.root, text="测试订单", command=lambda: self.thread_it(App.test, self, "order")).pack(side="left")
            tk.Button(self.root, text="测试消息提示闪烁", command=lambda: self.thread_it(App.test, self, "test_msg")).pack(side="left")
            tk.Button(self.root, text="测试", command=lambda: self.thread_it(App.test, self, "test")).pack(side="left")

        # 初始化获得Token
        self.thread_it(App.getToken, self)
        self.root.protocol("WM_DELETE_WINDOW", self.callbackClose)
        self.root.mainloop()

    def callbackClose(self):
        if self.driverSelf != "":
            self.driverSelf.close()
        wx.Exit()


    def endTask(self):
        """
        结束任务
        :return:
        """
        end = messagebox.askokcancel('提示', '要执行此操作吗')
        if end:
            if self.driverSelf != "":
                time.sleep(1)
                self.driverSelf.close()
            self.autoStart = False  # 关闭自动开始标记
            self.endThread = True

    def startTask(self):
        """
        开始任务
        :return:
        """
        """初始化任务"""
        self.logTextDom.delete('1.0', 'end')  # 清空文本日志
        self.endThread = False
        self.firstOrder = False
        self.autoNum = 0
        logging.info("[脚本开始]")

        cookies = self.getToken()
        if cookies:
            self.textLog("脚本开始", "info")
            self.setStartBtn(False)

            # 手动重新开始，订单操作重新获取最大订单号，否则继续沿用之前的订单号（手动可能包含操了库存）
            if not self.autoStart:  # 手动执行才操作的内容
                self.firstGetSubNum = True

                """文本数据读取"""
                self.getSaleGoodsList()  # 在第一次手动中获取防止再次重新获取文本数据

            """获取保证金"""
            self.enterDeposit = self.getMerchantInfo()

            """订单同步操作"""
            self.syncOrder()

            """下架操作"""
            self.downGoods()

            """上架操作"""
            # self.upTask()

            """下架加修改操作(合并上架与下架操作)"""
            self.upAndChangeTask()

            self.startCycleTasks = True  # 标记循环任务开启
            self.doWileChangePrice()

        else:
            # 未获取到Token 取消按钮禁用
            self.setStartBtn()

    def autoStartTask(self):
        self.autoStart = True
        self.startTask()

    def doWileChangePrice(self):
        if not self.startCycle:
            while True:
                timeSleepStop = self.timeSleep(self.intervalTime)
                if timeSleepStop:
                    break
                else:
                    # 循环重置
                    if self.autoNum >= self.cycleTimes:
                        self.autoStartTask()
                    else:
                        """下架加修改操作(合并上架与下架操作)"""
                        self.upAndChangeTask()

    def endThreadIt(self):
        self.autoNum = 0
        self.setStartBtn()
        self.textLog("进程结束", "info")
        sys.exit()

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
        return "保证金：" + str(self.enterDeposit) + "；执行间隔："  # "保证金：" + str(self.enterDeposit) + " ；执行间隔 " + str(self.intervalTime) + "秒/次；"

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

    def getSaleGoodsList(self):
        """
        文本内容读取
        :return: Array
        """
        self.textLog("读取数据")
        f = self.saleGoodsListText.get("1.0", "end")
        f = f.split("\n")
        lists = []
        for item in f:
            if self.endThread:
                self.endThreadIt()
            items = item.split("\t")
            if len(items) == self.txtParamNum:
                haveGoods = False
                for listsItem in lists:
                    if listsItem[0] == items[0]:
                        haveGoods = True
                        self.textLog("存在相同型号商品：" + listsItem[0], "warning")
                if haveGoods == False:
                    self.textLog(str(items))
                    lists.append(items)

        if len(lists) <= 0:
            self.textLog("读取数据失败，请检查上架库存文本信息", "error")
            self.setStartBtn()
            self.endThreadIt()  # 返回结束进程

        self.saleGoodsList = lists

    def authLogin(self):
        """
        打开浏览器登录获取token
        :return: token|""
        """
        mouse = c1()
        url = self.url + '/business/login.html'
        options = Options()
        options.binary_location = "./lib/brower/chrome.exe"  # 指定浏览器位置
        if not os.path.isfile(options.binary_location):
            messagebox.showerror("警告", "浏览器获取失败，请将浏览器放入当前目录 lib/brower 目录中")
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
        chromedriver = "./lib/chromedriver.exe"
        if not os.path.isfile(chromedriver):
            messagebox.showerror("警告", "缺少浏览器 chromedriver.exe 驱动，请将驱动放置在 lib 目录中")

        self.driverSelf = driver = webdriver.Chrome(executable_path=chromedriver, options=options)
        # 通过浏览器的dev_tool在get页面钱将.webdriver属性改为"undefined"
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",
        })
        driver.maximize_window()
        WebDriverWait(driver, 10)
        driver.get(url)
        while True:
            if self.endThread:
                driver.close()
                self.endThreadIt()
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
            '//*[@placeholder="请输入手机号码"]').send_keys(15355979998)
        driver.find_element_by_xpath(
            '//*[@placeholder="请输入密码"]').send_keys('jeefNO1')
        driver.find_element_by_class_name('el-button').click()
        getCount = 0
        getCookies = False
        token = ""
        while getCount < 10:
            time.sleep(1)
            getCount += 1
            cookies = driver.get_cookies()
            token = self.getJsonToken(cookies, "mchToken")
            if token != "":
                getCount = 10
                getCookies = True

        if not getCookies:
            self.textLog("Token获取失败请重新尝试", "error")
            time.sleep(1)
            driver.close()
            self.endThreadIt()

        time.sleep(1)
        driver.close()  # 获取cookies便可以关闭浏览器
        self.driverSelf = ""
        # 获取cookies中的token
        self.openFile(self.dewuTokenFilePath, 'w', token)  # 写入token文件中
        self.tokenEntry.delete("0", "end")
        self.tokenEntry.insert("0", token)  # 写入输入框展示
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

    def watchCurMinPrice(self):
        """
        查询渠道最低价格弹窗
        :return:
        """
        def getPriceText():
            """
            查询渠道价格，并输出至页面
            :return:
            """
            model = priceText.get("1.0", "end")
            model = model.split("\n")
            print(model)
            priceText.delete("1.0", "end")
            priceText.insert("end", "获取中，请稍等...")
            first = False
            for item in model:
                print(item)
                time.sleep(1)
                item = item.split("\t")
                itemModel = item[0]
                if "型号" in itemModel or "获取完成。" in itemModel:
                    continue
                if len(item[0]) > 1:
                    if not first:
                        priceText.delete("1.0", "end")
                        priceText.insert("end", "型号\t渠道最低价\t销量\t标题\n")
                        first = True

                    # 最低价查询
                    searchGoods = self.searchGoods(itemModel)
                    if len(searchGoods) > 0:

                        # 商品信息查询
                        goodsInfo = self.appSearchGoods(searchGoods[0]["articleNumber"], 0)
                        goodsText = ""
                        if goodsInfo:
                            goodsText = str(goodsInfo["soldNum"]) + "\t" + goodsInfo["title"]

                        spuId = searchGoods[0]["spuId"]
                        goodsDetail = self.getGoodsDetail(spuId)
                        if "minPriceList" in goodsDetail:
                            minPrice = goodsDetail["minPriceList"][0]  # 接口获取列表，可能会存在多个最低价
                            priceText.insert("end", itemModel + "\t" + str(int(minPrice["curMinPrice"] / 100)) + "\t" + goodsText + "\n")
                        else:
                            priceText.insert("end", itemModel + "\t" + "暂无人上架\t" + goodsText + "\n")
                    else:
                        priceText.insert("end", itemModel + "\t" + "未查询到商品\n")



                priceText.see("end")
            priceText.insert("end", "获取完成。")

        self.topWatchCurMinPrice = top = Toplevel()
        top.title("查看渠道最低价格")
        self.endThread = True
        tk.Label(top, text="价格获取框", anchor="w", justify="left").pack(fill="both", expand="no")
        priceText = tk.Text(top)
        priceText.pack(fill="both", expand="yes")
        tk.Button(top, text="获取价格", width=30, height=2, command=lambda: self.thread_it(getPriceText)).pack()

    def topSetInterval(self):
        """
        时间设置弹窗
        :return:
        """
        self.toplevelSetInterval = top = Toplevel()
        top.title("设置执行时间间隔(秒)：")
        top.geometry("400x30")
        tk.Label(top, text="请输入设置执行时间间隔：", width=15).pack(side="left", expand="yes", fill="both")
        self.topSetIntervalEntry = tk.Entry(top, width=10, justify="center")
        self.topSetIntervalEntry.pack(side="left", expand="yes", fill="both")
        tk.Label(top, text="秒", width=1, justify="left").pack(side="left", expand="yes", fill="both")
        tk.Button(top, text="确定", command=lambda: self.thread_it(App.setInterval, self)).pack(side="right",
                                                                                              expand="yes", fill="both")

    def setInterval(self):
        """
        设置自动执行间隔时间
        :return:
        """

        def setInl(intervalTime):
            self.intervalTime = int(intervalTime)  # 获取输入值
            # self.userInfo.configure(text=self.setInfo())  # 设置信息输出内容
            messagebox.showinfo("消息", "设置成功，将在下一次执行生效")

            if self.startCycleTasks:  # 标记任务在执行时，立马结束上个进程，等待下个进程重新进入
                """ 间隔时间操作 """
                """主要解决定时30分钟的时候，能够修改为此次等待时间"""
                self.endCycleThread = True  # 结束上一个循环
                time.sleep(3)
                self.endCycleThread = False
                self.doWileChangePrice()

        if self.topSetIntervalEntry != "":
            self.toplevelSetInterval.destroy()  # 关闭弹窗
            setInl(self.topSetIntervalEntry.get())
        elif self.intervalTimeEntry != "":
            setInl(self.intervalTimeEntry.get())

    def setCycleTimes(self):
        self.cycleTimes = int(self.cycleTimesEntry.get())
        messagebox.showinfo("消息", "设置成功")

    def calculateFollowPrice(self, price, goodsDetail):
        price = int(price)
        curMinPrice = 0
        addPrice = price
        while curMinPrice < price:
            addPrice += 1
            poundagePrice = self.poundagePrice(addPrice, goodsDetail["poundageInfoList"][0]["poundageDetailInfoList"])
            curMinPrice = addPrice - poundagePrice

        print(addPrice, curMinPrice)
        return [addPrice, curMinPrice]

    # def upTask(self):
    #     """
    #     上架任务
    #     :return:
    #     """
    #     # 上架商品操作
    #     # TODO 上架添加查询是否有上架操作
    #     self.textLog("======================================上架操作======================================", "sub")
    #     self.textLog("开始上架操作\n")
    #     for item in self.saleGoodsList:
    #         if self.endThread:
    #             self.endThreadIt()
    #         no = str(item[0])
    #         # 搜索货号，判断有无相关商品
    #         self.textLog("查询商品：货号：" + no)
    #         goods = self.searchGoods(item[0])
    #         if len(goods) > 0:
    #             spuId = goods[0]["spuId"]
    #             # 查询商品详情
    #             if not self.enterDepositPlenty:  # 保证金不足跳出循环
    #                 break
    #             self.upGoods(spuId, item, no)
    #         else:
    #             self.textLog("未查询到商品，跳过出价\n", "error")
    #         time.sleep(1)
    #
    #     self.firstPutaway = False
    #     self.textLog("======================================上架操作结束======================================", "sub")

    def upAndChangeTask(self):
        """
        上架&更新任务

        逻辑：
            下架完后操作该方法 -> 读取文本库存 -> 查询商品是否有上架 -有-> 修改操作 -> 先下架当前商品，再重新上架商品（保证金问题）
                                                            -无-> 上架操作
        :return:
        """
        # 初始化
        self.startCycle = True
        if self.autoNum > 0:
            self.logTextDom.delete("1.0", "end")  # 每次循环清空文本
        self.firstPutaway = False

        self.autoNum += 1
        self.textLog("======================================第 " + str(
            self.autoNum) + " 次循环======================================", "sub")
        self.textLog("======================================出价和改价操作======================================", "sub")

        notUpdateCount = 0  # 未更新数量
        updateCount = 0  # 更新数量
        successCount = 0  # 更新成功数量
        errorCount = 0  # 更新失败数量
        upCount = 0  # 更新失败数量
        for item in self.saleGoodsList:  # 循环库存
            if self.endThread:
                self.endThreadIt()
            goodsNo = str(item[0])  # 库存商品型号
            # goodsCount = int(item[1])  # 库存商品数量
            goodsPrice = int(item[2])  # 库存商品价格
            binddingGoods = []  # 上架商品信息

            biddingList = self.getGoodsList()  # 查询上架商品

            for listItem in biddingList:  # 循环筛选出已上架商品
                if listItem['articleNumber'] == goodsNo:
                    binddingGoods = listItem

            # 改价前检查订单
            # TODO 不做修改 提示专用 ！！！！！！
            self.updateOrder()

            if binddingGoods:
                # 商品详情
                spuId = binddingGoods["spuId"]
                goodsDetail = self.getGoodsDetail(spuId)

                if not ("poundageInfoList" in goodsDetail):
                    self.textLog("查询接口失败：取消商品[" + goodsNo + "]价格更新\n", "error")
                else:
                    self.textLog("开始更新价格：货号：" + goodsNo)

                    # 价格计算
                    updateSalePrice = self.updateSalePrice(goodsPrice, binddingGoods['curMinPrice'],
                                                           binddingGoods['myMaxPrice'], goodsDetail)
                    uspStatus = updateSalePrice[0]  # 价格计算状态
                    uspSalePrice = updateSalePrice[1]  # 出价
                    uspPrice = updateSalePrice[2]  # 库存价 0：接口欧问题

                    if uspStatus:  # 计算价格返回true 或 与当前你最低价不同
                        if int(uspSalePrice) == int(binddingGoods['curMinPrice']):  # 出价 与 当前最低价
                            notUpdateCount += 1
                            self.textLog("价格相同，不作更新\n", "warning")
                        else:
                            # 修改价格
                            # # TODO 打包时打开
                            # 下架再重新上架
                            # 下架
                            detailItem = goodsDetail["detailResponseList"][0]
                            self.deleteGoods(
                                detailItem['remainQuantity'], detailItem['price'], detailItem['biddingNo'],
                                detailItem['skuId'])

                            # 上架 下架后最低价变动，需重新获取最低价
                            upGoods = self.upGoods(spuId, item, goodsNo, True)
                            # update = self.addGoods(uspSalePrice, 1, size, goodsNo)

                            if upGoods == True:  # 必须 == True，数组[...]判断也是True
                                successCount += 1
                                self.textLog("更新价格成功", "success")
                                                              # biddingNo, minPrice
                                followPrice = self.calculateFollowPrice(goodsPrice, goodsDetail)
                                self.textLog("计算跟价价格：" + str(followPrice[0]))
                                setFollow = self.setFollowPrice(detailItem["biddingNo"], int(followPrice[0] * 100))
                                if setFollow:
                                    self.textLog("设置自动跟价成功，跟价价格：" + str(followPrice[0]) + "除去手续费到手价：" + str(followPrice[1]) + "\n", "success")
                                else:
                                    self.textLog("设置自动跟价失败\n", "error")
                    else:
                        notUpdateCount += 1
                        if uspPrice == 0:
                            self.textLog("不作更新\n", "warning")
                        else:
                            self.textLog("取消更新：价格过低" + "\n", "error")

                            text = ""
                            if not self.firstPutaway:
                                self.saleLowGoodsListText.delete('1.0', "end")
                                self.firstPutaway = True
                                text += "型号\t数量\t库存价格\t渠道最低价\t实际到手价\t上架时间\n"

                            text += goodsNo + "\t1\t" + str(goodsPrice) + "\t" + str(
                                int(int(binddingGoods["curMinPrice"]) / 100)) + "\t" + str(uspPrice) + "\t[" + str(
                                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]\n"

                            self.saleLowGoodsListText.insert("end", text)
                    updateCount += 1
            else:
                """与仓库商品未查询到，操作上架"""
                # 搜索货号，判断有无相关商品
                if self.enterDepositPlenty:  # 保证金不足跳出循环
                    self.textLog("查询商品：货号：" + goodsNo)
                    goods = self.searchGoods(goodsNo)
                    if len(goods) > 0:
                        spuId = goods[0]["spuId"]
                        # 查询商品详情
                        upGoods = self.upGoods(spuId, item, goodsNo)
                        if upGoods:
                            upCount += 1
                    else:
                        self.textLog("未查询到商品，跳过出价\n", "error")

        # 统计订单操作，由于每次改价查询都要操作检查订单
        if not self.haveUpdate:
            self.textLog("无新增库存相关商品订单")
        else:
            self.textLog("新增订单：" + str(self.newOrderCount) + " 单")
            self.textLog(self.newUpGoodsInfo)
            self.textLog("")

        # 每1分钟执行一次
        self.textLog("======================================第 " + str(
            self.autoNum) + " 次循环结束======================================\n", "sub")
        self.startCycle = False

    def orderTask(self):
        """
        订单任务

        逻辑：
            查询订单，设置最大订单号（用于比较） -> 循环进入新订单 -> 比对订单号 -大于-> 修改文本库存中对应的商品库存 -> 还有库存则再上架一个
        :return:
        """
        self.updateOrder()

    def downGoods(self):
        """
        下架操作
        :return:
        """
        """下架操作"""
        self.textLog("======================================全部下架操作======================================", "sub")
        biddingList = self.getGoodsList(True)

        def down(item):
            self.textLog("下架：" + str(item['articleNumber']))
            detailLists = self.getGoodsDetail(item['spuId'])
            if self.endThread:
                self.endThreadIt()
            # 必须全部下架操作
            if "detailResponseList" in detailLists:
                for detailItem in detailLists["detailResponseList"]:
                    if "remainQuantity" in detailItem and "price" in detailItem and "biddingNo" in detailItem and "skuId" in detailItem:
                        self.deleteGoods(
                            detailItem['remainQuantity'], detailItem['price'], detailItem['biddingNo'],
                            detailItem['skuId'])
            else:
                self.textLog("下架参数错误，请重新尝试", "error")
                self.endThreadIt()

        # 循环获取上架商品列表，下架所有商品操作
        for item in biddingList:
            # TODO 打包时删除
            if self.DEBUGER:
                for saleItem in self.saleGoodsList:
                    if item['articleNumber'] == saleItem[0]:
                        print(item['articleNumber'])
                        down(item)
            else:
                down(item)

            if not self.DEBUGER:
                time.sleep(1)
        self.textLog("======================================全部下架操作结束======================================\n", "sub")

    def upGoods(self, spuId, item, no, update=False):
        """
        上架操作
        :param spuId: 商品ID
        :param item: 库存信息
        :param no: 型号
        :param update:
        :return:
        """
        counts = item[1]
        if int(counts) <= 0:
            self.textLog("上架失败：库存不足\n", "error")
            return False
        else:
            price = item[2]  # 库存价
            goodsDetail = self.getGoodsDetail(spuId)
            if "detailResponseList" in goodsDetail:  # 判断商品是否已经有货出价中
                if len(goodsDetail["detailResponseList"]) > 0:
                    self.textLog("已在出价\n", "warning")
                    return True

            if not ("poundageInfoList" in goodsDetail):
                self.textLog("查询接口失败：取消商品[" + no + "]上架\n", "error")
            else:
                minPrice = 0  # 最低出价
                if "minPriceList" in goodsDetail:  # 检测是否有同款商品在售
                    minPrice = goodsDetail["minPriceList"][0]['curMinPrice']
                    salePrice = self.updateSalePrice(price, minPrice, 0, goodsDetail)  # 上架价格计算
                else:
                    # 上架 计算其他商户为上价的价格
                    salePrice = self.addSalePrice(price, goodsDetail)

                self.textLog(
                    "最低价：" + str(int(minPrice / 100)) + "元；出价：" + str(int(salePrice[1] / 100)) + "元(实际到手价:" + str(
                        salePrice[2]) + "元)；库存价：" + str(price) + "元")

                if salePrice[0]:
                    # # TODO 打包时打开
                    # 查询规格
                    size = self.sizeGoods(spuId)
                    if len(size) > 0:
                        # TODO 多规格需要做弹窗选择，记录第一次的选择，后续自动记录
                        skuId = size[0]["skuId"]
                    else:
                        skuId = size[0]["skuId"]
                    # 上架商品
                    # self.textLog("上架商品：货号：" + no)
                    add = self.addGoods(salePrice[1], 1, skuId, no)

                    if add == True:
                        self.textLog(("改价成功" if update else "上架成功"), "success")

                        goodsDetail = self.getGoodsDetail(spuId)
                        if "detailResponseList" in goodsDetail:  # 判断商品是否已经有货出价中
                            # 设置自动跟价
                            #                               biddingNo, minPrice
                            followPrice = self.calculateFollowPrice(price, goodsDetail)
                            self.textLog("计算跟价价格：" + str(followPrice[0]))
                            setFollow = self.setFollowPrice(goodsDetail["detailResponseList"][0]["biddingNo"], int(followPrice[0] * 100))
                            if setFollow:
                                self.textLog("设置自动跟价成功，跟价价格：" + str(followPrice[0]) + "除去手续费到手价：" + str(followPrice[1]) + "\n", "success")
                                return True
                            else:
                                self.textLog("设置自动跟价失败\n", "error")
                                return False
                        else:
                            self.textLog("未查询到相关上架商品可供设置自动跟价\n", "error")
                            return False

                    else:
                        self.textLog(("改价失败：" if update else "上架失败：") + add["msg"] + "\n", "error")
                        return False
                else:
                    if salePrice[2] == 0:
                        self.textLog(("取消改价：" if update else "取消上架：") + salePrice[3] + "\n", "error")
                        return False
                    else:
                        self.textLog(("取消改价：价格过低" if update else "取消上架：价格过低") + "\n", "error")
                        text = ""
                        if not self.firstPutaway:
                            self.saleLowGoodsListText.delete('1.0', "end")
                            self.firstPutaway = True
                            text += "型号\t数量\t库存价格\t渠道最低价\t实际到手价\t上架时间\n"
                            # text += "上架时间：" + time.strftime("%Y-%m-%d %H:%M:%S %p", time.localtime()) + "\n"
                        text += no + "\t1\t" + str(price) + "\t" + str(int(minPrice / 100)) + "\t" + str(
                            salePrice[2]) + "\t[" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]\n"
                        self.saleLowGoodsListText.insert("end", text)
                        return False

    def syncOrder(self):
        """
        同步订单
        :return:
        """
        self.textLog("初始化订单")
        biddingList = self.getOrders()
        if len(biddingList) > 0:
            # self.orderListText.delete("1.0", "end")
            # self.orderListText.insert("end", "货号\t数量\t库存价格\t到手价格\t睡时间\n")
            for item in biddingList:
                if not item["subOrderNo"] in self.orderList:
                    # if not "110105689535684777" == item["subOrderNo"]:
                    self.orderList.append(item["subOrderNo"])  # 存入订单数组
            #     self.orderListText.insert("end", "articleNumber\t1\t\tactualAmount")

    def updateOrder(self):
        """
        订单操作
        他能买，有订单，说明某件商品他上架过
        仓库商品是否有库存
        从最新的一笔订单，开始等待下一笔订单
        :return:
        """
        print(self.orderList)
        # self.textLog("======================================订单操作======================================", "sub")
        orderList = self.getOrders()  # 获取订单列表，倒序排列
        self.everyHaveUpdate = False
        if len(orderList) > 0:  # 有订单

            for orderItem in orderList:
                if not orderItem["subOrderNo"] in self.orderList:
                    self.newOrderCount += 1

            for orderItem in orderList:
                if not orderItem["subOrderNo"] in self.orderList:  # 在订单中不执行，说明已经执行过了
                    self.orderList.append(orderItem["subOrderNo"])  # 记录到库存中
                    for saleItem in self.saleGoodsList:  # 查找匹配的库存商品
                        if saleItem[0] == orderItem['articleNumber']:
                            count = int(saleItem[1])
                            if count > 0:  # 有库存
                                count -= 1

                                self.everyHaveUpdate = True
                                self.newUpGoodsInfo += "新上架：[货号：" + saleItem[0] + "；库存(余)：" + str(count) + " (" + saleItem[1] + "-1)]\n"

                                if not self.firstOrder:
                                    self.firstOrder = True
                                    self.orderListText.insert("end", "货号\t数量\t库存价格\t到手价格\t下单时间\n")
                                self.orderListText.insert("end", str(saleItem[0]) + "\t1\t" + str(saleItem[2]) + "\t" + str(orderItem["actualAmount"] / 100) + "\t[" + str(orderItem["payTime"]) + "]\n")

                                saleItem[1] = str(count)  # 修改库存

                                # 修改文本库存显示
                                txt = ""
                                # 重新拼接文本
                                for txtItem in self.saleGoodsList:
                                    txt += txtItem[0] + "\t" + txtItem[1] + "\t" + txtItem[2] + "\n"

                                self.saleGoodsListText.delete('1.0', 'end')
                                self.saleGoodsListText.insert('end', txt)  # 文本写入

                                self.startFlash()  # 打开闪烁提示

                                self.haveUpdate = True
                            # else:
                                # self.textLog("库存不足：货号：" + saleItem[0])

    """
    # ============================ 价格计算 ============================
    """

    def addSalePrice(self, price, goodsDetail):
        """
        计算上架价格
        在上架的商品中，无相同商品在线上出价时的计算
        :param price: 仓库价格
        :param goodsDetail: 商品详情
        :return: Array 数组返回[计算状态，出价价格，到手价格，错误信息（到手价为0的情况才写入）]
        """
        price = int(price)  # 库存价
        salePrice = math.ceil(price * 1.2)  # 出售价
        finalPrice = int(str(salePrice)[-1])  # 7 + 2 = 9
        # 整理出售价
        addPrice = 0
        if finalPrice != 9:
            addPrice = 9 - int(finalPrice)
        salePrice += addPrice

        if "poundageInfoList" in goodsDetail:
            proundage = self.poundagePrice(salePrice, goodsDetail['poundageInfoList'][0]['poundageDetailInfoList'])
            proundagePrice = salePrice - proundage
            if proundagePrice < price:  # 减去手续费，小于库存价格，不上架
                return [False, salePrice * 100, proundagePrice]
            else:
                salePrice = salePrice * 100  # * 100 => 分
                return [True, salePrice, proundagePrice]
        else:
            return [False, salePrice * 100, 0, "未查询到接口手续费[PoundageInfoList]相关信息"]

    def poundagePrice(self, price, poundageDetailInfoList):
        """
        手续费费用计算
        :param price: 出价价格
        :param poundageDetailInfoList: 手续费信息
        :return: 手续费
        """
        poundage = 0
        for item in poundageDetailInfoList:
            if 'currentExpense' in item:  # 直接手续费
                poundage += (item['currentExpense'] / 100)
            else:
                if 'currentPercent' in item:  # 手续费比例
                    currentExpense = (price * (item['currentPercent'] / 10000))  # 计算手续费
                    if 'expenseLimitMax' in item and 'expenseLimitMin' in item:  # 最高或最低手续费
                        expenseLimitMax = item['expenseLimitMax'] / 100
                        expenseLimitMin = item['expenseLimitMin'] / 100
                        if currentExpense > expenseLimitMax:
                            currentExpense = expenseLimitMax
                        if currentExpense < expenseLimitMin:
                            currentExpense = expenseLimitMin
                    poundage += currentExpense

        return poundage

    def updateSalePrice(self, price, curMinPrice, myMaxPrice, goodsDetail):
        """
        计算上架后金额修改计算 或 有别的卖家在卖时的金额计算
        价格不得低于库存价格！！！
        :param price: 库存价
        :param curMinPrice: 最低价
        :param myMaxPrice: 我的出价
        :param goodsDetail: 商品详情
        :return:  Array 数组返回[计算状态，出价价格，到手价格，错误信息（到手价为0的情况才写入）]
        """
        myMaxPrice = myMaxPrice / 100  # 元
        curMinPrice = curMinPrice / 100  # 元
        salePrice = 0
        price = int(price)

        if myMaxPrice == curMinPrice:  # 我的出价 等于 渠道最低价 => 不操作
            salePrice = curMinPrice
        elif price == curMinPrice:  # 库存价格 等于 渠道最低价 => 不操作
            salePrice = curMinPrice
        elif price > curMinPrice:  # 库存价格 大于 渠道最低价 => 计算渠道最低价 - 10 且 不得低于库存价
            # salePrice = price  # 按库存价格，之后进行数据操作
            salePrice = curMinPrice - 10  # 按渠道最低价格
        elif price < curMinPrice:  # 库存价格 小于 渠道最低价 => 计算渠道最低价 - 10 且 不得低于库存价
            salePrice = curMinPrice - 10

        if "poundageInfoList" in goodsDetail:
            proundage = self.poundagePrice(salePrice,
                                           goodsDetail['poundageInfoList'][0]['poundageDetailInfoList'])  # 手续费
            proundagePrice = salePrice - proundage  # 到手价
            if proundagePrice < price:  # 减去手续费，小于库存价格，不上架
                return [False, salePrice * 100, proundagePrice]
            else:
                # 1.取整 2.转str取末尾数 3.转int 4.计算9进制要加的数 5.加原价格 * 100 转 分
                finalPrice = int(str(int(salePrice))[-1])  # 例：7 + 2 = 9
                addPrice = 0
                if finalPrice != 9:
                    addPrice = 9 - int(finalPrice)
                salePrice += addPrice
                salePrice = salePrice * 100  # * 100 => 分
                return [True, salePrice, proundagePrice]
        else:
            return [False, salePrice * 100, 0, "未查询到接口手续费[PoundageInfoList]相关信息"]

    """
    # ============================ Helprs 帮助函数 ============================
    """

    def timeSleep(self, times):
        """
        自定义睡眠时间
        :param times:
        :return:
        """
        stopTimeSleep = False
        timeCount = 0
        while timeCount < times:
            timeCount += 1
            time.sleep(1)
            if self.endThread:  # 有提示 结束进程
                self.endThreadIt()
            if self.endCycleThread:  # 无提示 结束进程
                stopTimeSleep = True
                break

        return stopTimeSleep

    def setStartBtn(self, status=True):
        """
        按钮状态操作
        :param status:
        :return:
        """
        if status:
            self.startBtn.configure(state='normal', text="开始执行")
        else:
            self.startBtn.configure(state='disable', text="正在执行中")

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

    def array_get(self, array, key="", defVal=None):
        """
        获取数组的值
        :param array: 数组
        :param key: 键
        :param defVal: 默认值
        :return: Value(String|int|float...)|""
        """
        if key == "":
            return ""
        else:
            if key in array:
                return array[key]
            else:
                if defVal is None:
                    return ""
                else:
                    return defVal



    """
    # ============================ app api ============================
    """

    def appSearchGoods(self, keywords, page, sortMode=1, sortType=1):
        """
        APP的搜索接口
        :param keywords: 关键词
        :param page: 页数 0 开始
        :param sortMode: 排序状态
        :param sortType: 排序类型
        :return:
        """
        # 关键词搜索商品接口
        url = "https://app.dewu.com/api/v1/h5/search/fire/search/list"
        param = dict()
        param["title"] = keywords
        param["page"] = page
        param["sortType"] = sortType
        param["sortMode"] = sortMode
        param["limit"] = 20
        param["showHot"] = -1
        param["isAggr"] = 1
        param["unionId"] = ""

        res = self.dewuRequest("GET", url, param)
        if res["data"]["total"] > 0:
            goods = res["data"]["productList"][0]
            if keywords in goods["articleNumber"]:  # 关键词必须匹配
                return goods
            else:
                return False
        else:
            return False

    """
    # ============================ api ============================
    """

    def setFollowPrice(self, biddingNo, minPrice):
        """
        设置跟价
        :return:
        """
        logging.info("[设置跟价]")
        data = dict()
        data['autoSwitch'] = "true"
        data['biddingNo'] = biddingNo
        data['minPrice'] = minPrice
        data['type'] = 2
        setFollow = self.dewuRequest("POST", '/bidding/autoBiddingSetting', data)
        if not setFollow:
            return False
        if setFollow['code'] == 200:
            return True
        else:
            return False

    def getMerchantInfo(self):
        """
        获取保证金
        :return:
        """
        logging.info("[获取保证金]")
        minfo = self.dewuRequest("GET", '/home/merchantInfo?sign=fe26befc49444d362c8f17463630bdba', '')
        enterDeposit = self.array_get(minfo['data'], "enterDeposit", 0)
        self.enterDeposit = str(int(int(enterDeposit) / 100))
        self.textLog("获取保证金：" + self.enterDeposit)
        self.userInfo.configure(text=self.setInfo())
        return minfo['data']['enterDeposit']

    def getOrders(self, page=1):
        """
        获取订单
        :return:
        """
        logging.info("[获取订单列表]")
        data = dict()
        data['becomingDeliverTimeOut'] = "false"
        data['bizType'] = "0"
        data['endTime'] = time.strftime(
            "%Y-%m-%d", time.localtime()) + " 23:59:59"
        data['pageNo'] = page
        data['pageSize'] = 20
        data['startTime'] = "2020-11-30 00:00:00"
        data['status'] = 1
        data['subTypeListString'] = "0,13"
        orderList = self.dewuRequest("POST", '/orders/list', data)
        # total = orderList['data']['total']
        orderList = orderList['data']['list']
        if len(orderList):
            page += 1
            orderList = orderList + self.getOrders(page)
        return orderList

    def getGoodsList(self, shelf=False, page=1, statistics=True):
        """
        获取出价列表
        :param shelf: 下架提示 必须要全部下架，避免未下架完导致上架2个的意外
        :param page: 分页
        :param statistics: 是否输出提示信息，配合 shelf
        :return: ArrayList
        """
        logging.info("[获取出价列表]")
        data = dict()
        data['pageNo'] = page
        data['pageSize'] = 20
        data['biddingType'] = '0'
        data['biddingModel'] = 1
        minfo = self.dewuRequest("POST", '/bidding/biddingList', data)

        total = minfo['data']['total']  # 数量
        goodsList = minfo['data']['list']  # 数据列表
        if len(goodsList) > 0:
            time.sleep(1)
            page += 1
            goodsList = goodsList + self.getGoodsList(shelf, page, False)

        if shelf and statistics:
            goodsCount = len(goodsList)
            self.textLog("总数量：" + str(total) + "；下架数量：" + str(goodsCount))
            if total != goodsCount:
                self.textLog("下架数量错误，请重新尝试", "error")
                self.endThreadIt()

        return goodsList

    def getGoodsDetail(self, spuId):
        """
        TODO 暂时不改重新获取信息的逻辑
        获取商品详情
        :param spuId: 商品ID
        :return:
        """
        logging.info("[获取出价商品详情]")
        param = dict()
        param['spuId'] = spuId
        param['biddingType'] = 0
        detail = self.dewuRequest("GET", '/bidding/detail', param)
        if not ("poundageInfoList" in detail["data"]):
            tryCount = 0
            while tryCount < 3:  # 尝试3次请求
                self.textLog("查询接口错误，尝试3次重新请求，第 " + str(tryCount + 1) + " 次", "warning")
                tryCount += 1
                if "poundageInfoList" in detail["data"]:
                    # 请求成功跳出循环操作
                    break
                else:
                    param = dict()
                    param['spuId'] = spuId
                    param['biddingType'] = 0
                    detail = self.dewuRequest("GET", '/bidding/detail', param)
                if tryCount < 3:
                    time.sleep(5)  # 等待5秒

        return detail['data']

    def deleteGoods(self, oldQuantity, price, sellerBiddingNo, skuId):
        """
        下架商品
        :param oldQuantity: 旧的数量
        :param price: 价格
        :param sellerBiddingNo:
        :param skuId:
        :return:
        """
        logging.info("[下架商品]")
        data = dict()
        data['oldQuantity'] = oldQuantity
        data['price'] = price
        data['quantity'] = 0
        data['sellerBiddingNo'] = sellerBiddingNo
        data['sellerBiddingType'] = 0
        data['skuId'] = skuId
        data['type'] = 1
        delete = self.dewuRequest("POST", '/newBidding/addOrUpdateSingleBidding', data)
        if delete['code'] == 200:
            return True
        else:
            return False

    def searchGoods(self, articleNumberStr):
        """
        查询商品
        :param articleNumberStr: 查询关键字（货号）
        :return: Array
        """
        logging.info("[搜索查询商品]")
        data = dict()
        data['articleNumberStr'] = articleNumberStr  # 型号搜索内容
        data['biddingType'] = "0"
        data['page'] = 1
        data['pageSize'] = 20
        search = self.dewuRequest("post", '/search/newProductSearch', data)
        return search['data']['contents']

    def sizeGoods(self, spuId):
        """
        出价规格查询
        :param spuId: 商品ID
        :return:
        """
        logging.info("[查询商品规格]")
        param = dict()
        param['spuId'] = spuId
        search = self.dewuRequest("GET", '/newBidding/queryPropsBySpuId', param)
        return search['data']

    def addGoods(self, price, quantity, skuId, no):
        """
        上架商品
        :param price:
        :param quantity:
        :param skuId:
        :param no:
        :return:
        """
        logging.info("[上架商品]" + no)
        data = dict()
        data['price'] = price  # 价格
        data['quantity'] = quantity  # 数量（库存）
        data['sellerBiddingType'] = 0
        data['skuId'] = skuId
        data['type'] = 1
        add = self.dewuRequest("POST", '/newBidding/addOrUpdateSingleBidding', data)
        if add['code'] == 200:
            logging.info("[上架成功]", "success")
            return True
        else:
            logging.warning("[上架失败]", "error")
            return add

    def updateGoods(self, oldQuantity, price, quantity, skuId, biddingNo):
        """
        修改上架商品价格
        :param oldQuantity: 旧数量
        :param price: 价格
        :param quantity: 新数量
        :param skuId:
        :param biddingNo:
        :return:
        """
        logging.info("[修改商品]")

        data = dict()
        data['oldQuantity'] = oldQuantity  # 旧库存
        data['price'] = price  # 价格
        data['quantity'] = quantity  # 数量（库存）
        data['sellerBiddingNo'] = biddingNo
        data['sellerBiddingType'] = 0
        data['skuId'] = skuId
        data['type'] = 1
        update = self.dewuRequest("POST", '/newBidding/addOrUpdateSingleBidding', data)
        return update

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
        if response.status_code == 200 and resData["code"] == 10002001:  # TODO 分页未读取到数据报错信息：{"domain":"duapp-stark-service","code":10002001,"msg":"出价编号不能为空","status":10002001}
            resData["data"] = {}
            resData["data"]["total"] = 0
            resData["data"]["list"] = []
            return resData
        if response.status_code == 401 or resData["code"] == 401:  # 401 重新写获取token 只执行一次的Token获取
            if not self.dewuRequestAgainToken:
                self.textLog(resData["msg"], "error")
                # TODO 打开解决死循环获取
                # self.dewuRequestAgainToken = True
                self.textLog("Token失效尝试重新获取", "warning")
                self.token = self.authLogin()
                return self.dewuRequest(method, url, data, requestCount)
            else:
                logging.error("[接口][请求失败][Token重新获取失效]" + response.text)
                self.textLog("请求失败：" + resData["msg"], "error")
                return False
        if resData["code"] == 20900021:
            self.enterDepositPlenty = False
            return resData
        else:
            logging.error("[接口][请求失败]" + response.text)
            self.textLog(resData["msg"], "error")
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
        url = url if bool(re.search("https://", url)) else self.api + url
        res = requests.get(url, params=params, headers=self.__headers())
        return res

    # POST 请求
    def __post(self, url, data):
        data = self.__request(data)
        logging.info(
            "[接口][请求][请求地址]" + self.api + url + "[请求参数]" + str(data) + "[请求头]" + str(self.__headers()))  # 日志记录请求
        url = url if bool(re.search("https://", url)) else self.api + url
        res = requests.post(url, data=json.dumps(data), headers=self.__headers())
        return res

    # 请求参数处理
    def __request(self, params):
        if "sign" in params:
            del params["sign"]
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

    """
    # ================================ 托盘 ==========================
    """
    def CreatePopupMenu(self):
        '''生成菜单'''

        menu = wx.Menu()
        # 添加两个菜单项
        menu.Append(self.MENU_ID1, '显示')
        menu.Append(self.MENU_ID2, '退出')
        return menu

    def onShow(self, event):
        self.root.wm_attributes('-topmost', 1)
        self.root.wm_attributes('-topmost', 0)
        self.stopFlash()
        # wx.MessageBox('111')

    def onExit(self, event):
        wx.Exit()
        sys.exit()

    def newMessage(self):
        if self.HAVE_NEW_MSG == False:
            self.STOP_FLASH = True
            self.startFlash()
        else:
            self.stopFlash()

    # 开始闪烁
    def startFlash(self):
        while self.STOP_FLASH:
            time.sleep(0.5)
            self.changeIcon()

    def stopFlash(self):
        self.STOP_FLASH = False
        time.sleep(1)
        self.SetIcon(wx.Icon("./lib/favicon.ico"), self.TITLE)
        self.ICON = "./lib/favicon.ico"

    def changeIcon(self):
        if self.ICON == "./lib/favicon.ico":
            self.SetIcon(wx.Icon("favicon-hide.ico"), self.TITLE)
            self.ICON = "./lib/favicon-hide.ico"
        else:
            self.SetIcon(wx.Icon("favicon.ico"), self.TITLE)
            self.ICON = "./lib/favicon.ico"

    """
    # ================================ 测试 ==========================
    """

    def test(self, type=""):
        self.endThread = False
        if type == "read":
            print("{读取文本数据}")
            self.getSaleGoodsList()
        if type == "down":  # 下架
            print("{下架}")
            self.downGoods()
        if type == "up":  # 上架
            print("{上架+修改}")
            self.upAndChangeTask()
        if type == "update":  # 更新
            print("{更新}")
        if type == "order":  # 订单
            print("{订单}")
            self.updateOrder()
        if type == "test_msg":  # 测试消息闪烁提示
            self.newMessage()
        if type == "test":  # 测试
            print("{测试}")
            # toast = ToastNotifier()
            # toast.show_toast(title="新订单", msg="您有一条新的订单请注意查看",
            #                  icon_path="/favicon.ico", duration=5)
            # winapi.flash(self.SetIcon)
            # self.stopFlash()
            # self.search_by_keywords_load_more_data("L3.742.4.96.6", 0)

            # self.logListBoxDom.insert("end", "123", )

        print("结束操作")

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__()
        App()


class MyApp(wx.App):
    def OnInit(self):
        MyFrame()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
