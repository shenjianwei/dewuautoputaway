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
from selenium.webdriver.chrome.options import Options
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
    # 进程相关参数
    endThread = False  # 进程管理
    endCycleThread = False  # 循环进程管理
    startCycleTasks = False  # 是否开始循环任务
    # 请求相关工具参数
    dewuRequestMax = 3  # 请求最大次数
    dewuRequestWaitTime = 5  # 请求等待间隔时间
    dewuRequestAgainToken = False  # 重新获取token机会
    # 库存相关参数
    saleGoodsList = []  # 库存商品列表
    txtParamNum = 3  # 库存规格字段数

    # 元素
    tokenEntry = ""  # 文本输入框 Token 值
    logTextDom = ""  # 日志 Text 框
    startBtn = ""  # 开始 Button 按钮
    saleGoodsListText = ""  # 库存 Text 框

    # 弹窗
    toplevelSetInterval = ""  # 设置间隔时间弹窗
    topSetIntervalEntry = ""  # 设置间隔时间文本输入框 Token 值

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
        tk.Button(frameBtn, text="结束执行", command=lambda: self.thread_it(App.endTask, self)).pack(padx=15, pady=10, side="right", fill="both", expand="yes")

        # 初始化获得Token
        self.thread_it(App.getToken, self)
        self.root.mainloop()

    def endTask(self):
        """
        结束任务
        :return:
        """
        end = messagebox.askokcancel('提示', '要执行此操作吗')
        if end:
            self.endThread = True

    def startTask(self):
        """
        开始任务
        :return:
        """
        """初始化任务"""
        self.logTextDom.delete('1.0', 'end')  # 清空文本日志
        self.endThread = False
        logging.info("[脚本开始]")

        cookies = self.getToken()
        if cookies:
            # self.textLog("脚本开始", "info")
            # """文本数据读取"""
            # self.textLog("读取数据")
            # self.saleGoodsList = goodsList = self.getSaleGoodsList()
            # if len(goodsList) <= 0:
            #     self.textLog("读取数据失败，请检查上架库存文本信息", "error")
            #     self.setStartBtn()
            #     return False  # 返回结束进程
            #
            # """获取保证金"""
            # self.enterDeposit = self.getMerchantInfo()
            #
            # """下架操作"""
            # self.textLog("======================================全部下架操作======================================","sub")
            # biddingList = self.getGoodsList(True)
            #
            # # 循环获取上架商品列表，下架所有商品操作
            # # TODO 打包时打开
            # for item in biddingList:
            #     # TODO 打包时删除
            #     # if item['articleNumber'] == "L1.611.4.75.2":
            #     self.textLog("下架：" + str(item['articleNumber']))
            #     detailLists = self.getGoodsDetail(item['spuId'])
            #     if self.endThread:
            #         self.endThreadIt()
            #     # 必须全部下架操作
            #     if "detailResponseList" in detailLists:
            #         for detailItem in detailLists["detailResponseList"]:
            #             if "remainQuantity" in detailItem and "price" in detailItem and "biddingNo" in detailItem and "skuId" in detailItem:
            #                 self.deleteGoods(
            #                     detailItem['remainQuantity'], detailItem['price'], detailItem['biddingNo'],
            #                     detailItem['skuId'])
            #     else:
            #         self.textLog("下架参数错误，请重新尝试", "error")
            #         self.endThreadIt()
            #     time.sleep(1)
            #
            #     # 上架商品操作
            #     # TODO 上架添加查询是否有上架操作
            #     self.textLog("======================================上架操作======================================", "sub")
            #     self.textLog("开始上架操作")
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
            #             self.upGoods(spuId, item, no)
            #         else:
            #             self.textLog("未查询到商品，跳过出价\n", "error")
            #         time.sleep(1)
            #
            #     self.firstPutaway = False
            #     self.endUpGoods = True
            #     self.textLog("======================================上架操作结束======================================", "sub")

            self.startCycleTasks = True  # 标记循环任务开启
            self.doWileChangePrice()

        else:
            # 未获取到Token 取消按钮禁用
            self.setStartBtn()

    def doWileChangePrice(self):
        while True:
            self.timeSleep(self.intervalTime)
            # self.changeGoodsPrice()

    def endThreadIt(self):
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

    def getSaleGoodsList(self):
        """
        文本内容读取
        :return: Array
        """
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
        return lists

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

        driver = webdriver.Chrome(executable_path=chromedriver, options=options)
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
            '//*[@placeholder="请输入手机号码"]').send_keys(15355979998)
        driver.find_element_by_xpath(
            '//*[@placeholder="请输入密码"]').send_keys('jeefNO1')
        driver.find_element_by_class_name('el-button').click()
        time.sleep(3)
        cookies = driver.get_cookies()  # Selenium为我们提供了get_cookies来获取登录cookies
        driver.close()  # 获取cookies便可以关闭浏览器
        # 获取cookies中的token
        token = self.getJsonToken(cookies, "mchToken")
        self.openFile(self.dewuTokenFilePath, 'w', token)  # 写入token文件中
        self.tokenEntry.delete("0","end")
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

    def topSetInterval(self):
        """

        :return:
        """
        self.toplevelSetInterval = top = Toplevel()
        top.title("设置执行时间间隔(秒)：")
        top.geometry("400x30")
        tk.Label(top, text="请输入设置执行时间间隔：", width=15).pack(side="left", expand="yes", fill="both")
        self.topSetIntervalEntry = tk.Entry(top, width=10, justify="center")
        self.topSetIntervalEntry.pack(side="left", expand="yes", fill="both")
        tk.Label(top, text="秒", width=1, justify="left").pack(side="left", expand="yes", fill="both")
        tk.Button(top, text="确定", command=lambda: self.thread_it(App.setInterval, self)).pack(side="right", expand="yes", fill="both")

    def setInterval(self):
        """
        设置自动执行间隔时间
        :return:
        """
        self.intervalTime = int(self.topSetIntervalEntry.get())  # 获取输入值
        self.toplevelSetInterval.destroy()  # 关闭弹窗
        self.userInfo.configure(text=self.setInfo())  # 设置信息输出内容
        messagebox.showinfo("消息", "设置成功，将在下一次执行生效")

        if self.startCycleTasks:  # 标记任务在执行时，立马结束上个进程，等待下个进程重新进入
            """主要解决定时30分钟的时候，能够修改为此次等待时间"""
            self.endCycleThread = True
            time.sleep(3)
            self.endCycleThread = False
            self.doWileChangePrice()


    def upGoods(self, spuId, item, no):
        """
        上架操作
        :param spuId: 商品ID
        :param item: 库存信息
        :param no: 型号
        :return:
        """
        counts = item[1]
        if int(counts) <= 0:
            self.textLog("上架失败：库存不足\n", "error")
            return False
        else:
            price = item[2]  # 库存价
            goodsDetail = self.getGoodsDetail(spuId)
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
                    # 上架商品
                    # self.textLog("上架商品：货号：" + no)
                    add = self.addGoods(salePrice[1], 1, size, no)

                    if add:
                        self.textLog("上架成功\n", "success")
                        return True
                    else:
                        self.textLog("上架失败：" + add["msg"] + "\n", "error")
                        return False
                else:
                    if salePrice[2] == 0:
                        self.textLog("取消上架：" + salePrice[3] + "\n", "error")
                        return False
                    else:
                        self.textLog("取消上架：价格过低" + "\n", "error")
                        text = ""
                        if self.firstPutaway == False:
                            self.saleLowGoodsListText.delete('1.0', "end")
                            self.firstPutaway = True
                            text += "型号\t数量\t库存价格\t渠道最低价\t实际到手价\t上架时间\n"
                            # text += "上架时间：" + time.strftime("%Y-%m-%d %H:%M:%S %p", time.localtime()) + "\n"
                        text += no + "\t1\t" + str(price) + "\t" + str(int(minPrice / 100)) + "\t" + str(
                            salePrice[2]) + "\t[" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]\n"
                        self.saleLowGoodsListText.insert("end", text)
                        return False

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
        price = int(price) # 库存价
        salePrice = math.ceil(price * 1.2) # 出售价
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
        timeCount = 0
        while timeCount < times:
            timeCount += 1
            time.sleep(1)
            if self.endThread:  # 有提示 结束进程
                self.endThreadIt()
            if self.endCycleThread:  # 无提示 结束进程
                sys.exit()

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
    # ============================ api ============================
    """

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

    def getOrders(self):
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
        data['pageNo'] = 1
        data['pageSize'] = 20
        data['startTime'] = "2020-11-30 00:00:00"
        data['status'] = 1
        data['subTypeListString'] = "0,13"
        orderList = self.dewuRequest("POST", '/orders/list', data)
        # total = orderList['data']['total']
        orderList = orderList['data']['list']
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
        totalPages = minfo['data']['page']  # 总页数
        if page <= totalPages:
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
        delete = self.dewuRequest("POST",'/newBidding/addOrUpdateSingleBidding', data)
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
        return search['data'][0]['skuId']

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
        if response.status_code == 401 or resData["code"] == 401:  # 401 重新写获取token 只执行一次的Token获取
            if not self.dewuRequestAgainToken:
                self.textLog(resData["msg"], "error")
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
