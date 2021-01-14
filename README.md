# 得物App商户后台 自动化上架跟单系统

# 文档

 > 必带请求头
channel:pc
clientid:stark
content-type:application/json;charset=UTF-8
passporttoken: {cookie's mchToken}
syscode:DU_USER

> sign加密方式：<br/> 请求参数按ASCII码排序，拼接 字符串 + "048a9c4943398714b356a696503d2d36" <br/>如下

```
pageSize: 20
pageNo: 1

// 排序
pageNo: 1
pageSize: 20

// 拼接字符串
"pageNo1pageSize20" + "048a9c4943398714b356a696503d2d36" = "pageNo1pageSize20048a9c4943398714b356a696503d2d36"
```

### 商家信息
请求方式：get
https://stark.dewu.com/api/v1/h5/biz/home/merchantInfo?sign=fe26befc49444d362c8f17463630bdba
返回参数信息：
```json
{
    "data": {
        "merchantName": "周志发",
        "merchantTypeName": "普通商家-vip",
        "supportSevenDaysNoReasonReturn": false,
        "supportInvoicing": false,
        "returnDepositRed": false,
        "returnDepositExists": false,
        "enterDepositRed": false,
        "enterDeposit": 1000000, // 保证金
        "poundageSale": 10000,
        "performanceSale": 10000,
        "technicalSale": 10000,
        "notEnterprise": true,
        "remainPrepaidFee": 0,
        "remainStorageFee": 0,
        "noticeSignStorageProtocol": false,
        "open": true
    },
    "code": 200,
    "status": 200,
    "msg": "ok",
    "error": false
}
```

---
### 出价列表
请求方式：post
https://stark.dewu.com/api/v1/h5/biz/bidding/biddingList
请求参数：
```
biddingModel: 1
biddingType: "0"
pageNo: 1
pageSize: 20
sellerPriceType: 1 // 出价价格 （>当前渠道最低价）
sign: "897ccf162c15dc2900cc7a513a2b80ce"
```
返回参数信息：
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "spuCount": 9,
        "skuCount": 9,
        "quantityCount": 9,
        "priceCount": 8385100,
        "page": 1,
        "total": 9,
        "pageSize": 20,
        "list": [
            {
                "title": "【送礼推荐】LONGINES 浪琴 康卡斯潜水系列 39mm自动机械男士手表男表 L3.741.4.56.6",
                "brandName": "LONGINES/浪琴",
                "spuId": 30235,
                "logoUrl": "https://cdn.poizon.com/source-img/origin-img/20201204/fc16896e34214bd4a02f8f8f69a5a1da.jpg",
                "articleNumber": "L3.741.4.56.6", // 货号
                "otherNumbers": "",
                "authPrice": 1000000, // 授权价格
                "curMinPrice": 699900, // 最低价
                "globalMinPrice": 699900, // 全渠道最低价
                "myMinPrice": 699900, // 我的最低价
                "myMaxPrice": 699900, // 我的最大价
                "quantity": 1,
                "suitableSkuIdList": [
                    181407808
                ],
                "specStr": "黑色"
            }......
        ]
    },
    "status": 200
}
```
---
### 待发货订单列表
TODO
请求方式：post
https://stark.dewu.com/api/v1/h5/biz/orders/list
请求参数
```
becomingDeliverTimeOut: false
bizType: "0"
endTime: "2021-01-04 23:59:59"
pageNo: 1
pageSize: 20
sign: "61f703c64ecb25eb0dcca204563f55b8"
startTime: "2020-11-30 00:00:00"
status: 1 // 待发货的订单状态
subTypeListString: "0,13"
```
返回参数信息：
```json
{
    "data": {
        "list": [
            {
                "orderNo": "510105506235762096",
                "subOrderNo": "110105506325212096",
                "price": 295900,
                "spuId": 60018,
                "spuTitle": "TISSOT 天梭 力洛克系列钢带 瑞士手表机械表 男款 黑色 T006.407.11.053.00",
                "skuId": 360105808,
                "skuTitle": "TISSOT 天梭 力洛克系列钢带 瑞士手表机械表 男款 黑色 T006.407.11.053.00",
                "productLogo": "https://cdn.poizon.com/source-img/origin-img/20201204/05a284cbc0b04e2f985758abc5bc33ce.jpg",
                "articleNumber": "T006.407.11.053.00",
                "otherNumbers": "",
                "orderTime": "2021-01-04 15:08:05.000",
                "closeType": 0,
                "orderStatus": 2000,
                "statusDesc": "支付成功",
                "specsStr": "黑色",
                "orderType": "0",
                "orderTypeDesc": "普通现货",
                "sellerDeliverTimeLimit": 1609873826000,
                "crossCheck": false,
                "tariff": 0,
                "payTime": "2021-01-04 15:10:26.000",
                "actualAmount": 280264,
                "barCode": "0064071105300",
                "repositoryAddress": "上海上海市杨浦区上海上海市杨浦区茭白园路100号",
                "merchantSubsidyAmount": 0,
                "warehouseCode": "HLBD"
            }
        ],
        "pageNo": 1,
        "pageSize": 20,
        "pages": 1,
        "total": 1
    },
    "code": 200,
    "status": 200,
    "msg": "ok",
    "error": false
}
```
---
### 商品出价查询
TODO
请求方式：post
https://stark.dewu.com/api/v1/h5/biz/search/newProductSearch
请求参数
```
articleNumberStr: "WSRN0012" // 型号搜索内容
productNameStr: "卡地亚" // 商品搜索内容
biddingType: "0"
page: 1
pageSize: 20
sign: "94daf216b5b511d54c43ef980668c563"
```
返回参数信息：
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "pageNum": 0,
        "pageSize": 20,
        "total": 1,
        "pages": 1,
        "contents": [
            {
                "productId": 1204463,
                "logoUrl": "https://cdn.poizon.com/source-img/origin-img/20201204/e2641784dfd2489a98f0db3b06336b0a.jpg",
                "title": "Cartier 卡地亚 Ronde Solo de Cartier系列腕表 银色 WSRN0012",
                "articleNumber": "WSRN0012",
                "spuId": 1204463,
                "categoryId": 505,
                "brandId": 10041,
                "minSalePrice": 1969900
            }
        ]
    },
    "status": 200
}
```
---
### 商品出价规格查询
TODO
请求方式：GET
https://stark.dewu.com/api/v1/h5/biz/newBidding/queryPropsBySpuId
请求参数
```
spuId: 1204463
sign: 0638e9f893a1db3a155c25ec62b63713
```
返回参数信息：
```json
{
    "code": 200,
    "msg": "success",
    "data": [
        {
            "skuId": 601410696,
            "props": [
                {
                    "id": 27381737,
                    "level": 1,
                    "definitionId": 1,
                    "name": "颜色",
                    "value": "银色"
                }
            ]
        }
    ],
    "status": 200
}
```
### 商品详情
请求方式 GET
https://stark.dewu.com/api/v1/h5/biz/bidding/detail
请求参数：
spuId: 1204463
biddingType: 0
sign: b4194769ec14f37dc3f63a72d9a802c8
返回参数信息：
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "detailResponseList": [
            {
                "skuId": 601410696,
                "remainQuantity": 1,
                "price": 6999900,
                "curMinPrice": 1969900,
                "biddingNo": "101220031986400682",
                "priceFollowUpEnabled": false
            }
        ],
        "minPriceList": [
            {
                "skuId": 601410696,
                "price": 1969900,
                "curMinPrice": 1969900
            }
        ],
        "poundageInfoList": [
            {
                "skuId": 601410696,
                "biddingType": 0,
                "poundageDetailInfoList": [
                    {
                        "expenseType": 1,
                        "expenseName": "技术服务费",
                        "originalPercent": 300,
                        "currentPercent": 300,
                        "salePercent": 10000,
                        "expenseLimitMin": 1500,
                        "expenseLimitMax": 24900
                    },
                    {
                        "expenseType": 3,
                        "expenseName": "转账手续费",
                        "originalPercent": 100,
                        "currentPercent": 100
                    },
                    {
                        "expenseType": 5,
                        "expenseName": "查验费",
                        "originalExpense": 1000,
                        "currentExpense": 1000
                    },
                    {
                        "expenseType": 2,
                        "expenseName": "鉴别费",
                        "originalExpense": 1800,
                        "currentExpense": 1800
                    },
                    {
                        "expenseType": 4,
                        "expenseName": "包装服务费",
                        "originalExpense": 1000,
                        "currentExpense": 1000
                    }
                ]
            }
        ]
    },
    "status": 200
}

{
    "code": 200,
    "msg": "success",
    "data": {
        "detailResponseList": [],
        "minPriceList": [
            {
                "skuId": 601410696,
                "price": 1969900,
                "curMinPrice": 1969900 // 当前现货最低价
            }
        ],
        "poundageInfoList": [
            {
                "skuId": 601410696,
                "biddingType": 0,
                "poundageDetailInfoList": [
                    {
                        "expenseType": 1,
                        "expenseName": "技术服务费",
                        "originalPercent": 300,
                        "currentPercent": 300,
                        "salePercent": 10000,
                        "expenseLimitMin": 1500,
                        "expenseLimitMax": 24900
                    },
                    {
                        "expenseType": 3,
                        "expenseName": "转账手续费",
                        "originalPercent": 100,
                        "currentPercent": 100
                    },
                    {
                        "expenseType": 5,
                        "expenseName": "查验费",
                        "originalExpense": 1000,
                        "currentExpense": 1000
                    },
                    {
                        "expenseType": 2,
                        "expenseName": "鉴别费",
                        "originalExpense": 1800,
                        "currentExpense": 1800
                    },
                    {
                        "expenseType": 4,
                        "expenseName": "包装服务费",
                        "originalExpense": 1000,
                        "currentExpense": 1000
                    }
                ]
            }
        ]
    },
    "status": 200
}
```
---
### 商品下架
TODO
请求方式：post
https://stark.dewu.com/api/v1/h5/biz/newBidding/addOrUpdateSingleBidding
请求参数：
oldQuantity: 1
price: 79999
quantity: 0 // 数量设置 0 （下架）
sellerBiddingNo: "101220031986420892"
sellerBiddingType: 0
sign: "b0f0c4ac58ef329f62790d3d0ba1337a"
skuId: 601410696
type: 1
返回参数信息：
```json
```
---
### 商品上架或修改
TODO
请求方式：post
https://stark.dewu.com/api/v1/h5/biz/newBidding/addOrUpdateSingleBidding
请求参数：
```
// 新增
price: 5999900 // 价格
quantity: 1 // 数量（库存）
sellerBiddingType: 0
sign: "0a82a73de6c418fe4e8f2a95fc5790bb"
skuId: 601410696
type: 1

// 修改
oldQuantity: 1
price: 6999900
quantity: 1
sellerBiddingNo: "101220031986378182"
sellerBiddingType: 0
sign: "acf4988d88c789759fd705eabf692c3f"
skuId: 601410696
type: 1
```
返回参数信息：
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "sellerBiddingNo": "101220031986378182",
        "uid": 213284781,
        "sellerBiddingType": 0,
        "merchantType": 0,
        "tradeStatus": 2,
        "tradeSubStatus": 0,
        "refundStatus": 0,
        "quantity": 1,
        "spuId": 1204463,
        "skuId": 601410696,
        "skuSaleProp": "[{\"id\":27381737,\"level\":1,\"name\":\"颜色\",\"value\":\"银色\"}]",
        "deposit": 100000,
        "price": 5999900,
        "feeDetail": "{\"detailDto\":[{\"expenseType\":1,\"expenseName\":\"技术服务费\",\"originalExpense\":24900,\"currentExpense\":24900,\"originalPercent\":300,\"currentPercent\":300,\"extendJson\":\"{\\\"currentPercent\\\":300,\\\"currentexpense\\\":24900,\\\"expenseLimit\\\":{\\\"max\\\":24900,\\\"min\\\":1500},\\\"originalTechnicalFeeLimit\\\":{\\\"expenseLimit\\\":{\\\"max\\\":24900,\\\"min\\\":1500},\\\"originalExpense\\\":24900,\\\"originalPercent\\\":300},\\\"salaInfoInnerVo\\\":{\\\"salaPercent\\\":10000,\\\"salaType\\\":5}}\",\"salePercent\":10000},{\"expenseType\":3,\"expenseName\":\"转账手续费\",\"originalExpense\":59999,\"currentExpense\":59999,\"originalPercent\":100,\"currentPercent\":100,\"extendJson\":\"{\\\"currentExpense\\\":59999,\\\"currentPercent\\\":100,\\\"originalExpense\\\":59999,\\\"originalPercent\\\":100}\"},{\"expenseType\":5,\"expenseName\":\"查验费\",\"originalExpense\":1000,\"currentExpense\":1000,\"extendJson\":\"{\\\"currentExpense\\\":1000,\\\"originalExpense\\\":1000}\"},{\"expenseType\":2,\"expenseName\":\"鉴别费\",\"originalExpense\":1800,\"currentExpense\":1800,\"extendJson\":\"{\\\"currentExpense\\\":1800,\\\"originalExpense\\\":1800}\"},{\"expenseType\":4,\"expenseName\":\"包装服务费\",\"originalExpense\":1000,\"currentExpense\":1000,\"extendJson\":\"{\\\"currentExpense\\\":1000,\\\"originalExpense\\\":1000}\"},{\"expenseType\":7,\"expenseName\":\"预计收入\",\"originalExpense\":5911201,\"currentExpense\":5911201},{\"expenseType\":6,\"expenseName\":\"总费用\",\"originalExpense\":88699,\"currentExpense\":88699}],\"version\":\"1.0.0\"}",
        "channel": "商家后台",
        "source": "poizon",
        "oldId": 0,
        "remark": "",
        "isDel": 0,
        "createTime": "2021-01-04 10:17:29.253",
        "modifyTime": "2021-01-04 10:17:29.253",
        "spuTitle": "Cartier 卡地亚 Ronde Solo de Cartier系列腕表 银色 WSRN0012",
        "id": 442700432,
        "extra": "{}"
    },
    "status": 200
}
```

# 得物APP

### 搜索

> 请求地址：https://app.dewu.com/api/v1/h5/search/fire/search/list

```json
{
	"data": {
		"total": 1,
		"totalText": "1件商品",
		"page": 0,
		"productList": [
			{
				"requestId": "9c3f9e5d3b075e24",
				"page": 0,
				"dataType": 0,
				"productId": 1009392,
				"spuId": 1009392,
				"propertyValueId": 20153450,
				"propertyValue": "蓝色",
				"logoUrl": "https: //cdn.poizon.com/source-img/origin-img/20201204/d9ce00e6e741422b83ca98a25bb058d9.jpg",
				"images": [
					"https: //cdn.poizon.com/source-img/origin-img/20201204/d9ce00e6e741422b83ca98a25bb058d9.jpg"
				],
				"title": "【爆款直降】【送礼推荐】LONGINES浪琴康卡斯潜水系列41mm自动机械男士手表男表L3.742.4.96.6",
				"subTitle": "",
				"spuMinSalePrice": 711900,
				"minSalePrice": 711900,
				"maxSalePrice": 0,
				"soldNum": 452,
				"price": 711900,
				"underlineTagVo": [
					
				],
				"recommendReasonTagVo": {
					"title": "要颜有颜，可盐可甜",
					"type": 6,
					"sort": 100,
					"imageUrl": "",
					"startTime": 1599729694000,
					"endTime": 2147454847000
				},
				"brandLogoUrl": "https: //cdn.poizon.com/source-img/brand-img//482cd6c65f6447ff96166fcd4b8b37d4-10022.png",
				"articleNumber": "L3.742.4.96.6",
				"priceType": 1,
				"goodsType": 100,
				"type": 1,
				"isBrandPrice": 0,
				"brandDirectSupply": 0,
				"activityPrice": 0,
				"categoryId": 501,
				"brandId": 10022
			}
		],
		"recList": [
			
		],
		"sizes": [
			
		],
		"showHotProduct": 0,
		"screen": {
			"requestId": "9c3f9e5d3b075e24",
			"category": [
				{
					"categoryId": 501,
					"name": "瑞表",
					"pid": 500,
					"count": 1
				}
			],
			"categoryLevel1": [
				{
					"categoryId": 103,
					"name": "手表",
					"pid": 0,
					"count": 1
				}
			],
			"productFit": [
				{
					"fitId": 2,
					"name": "男",
					"pid": 0,
					"count": 1
				}
			],
			"brand": [
				{
					"brandId": 10022,
					"name": "LONGINES/浪琴",
					"count": 1
				}
			],
			"size": [
				
			],
			"price": [
				
			],
			"series": [
				{
					"id": 273,
					"name": "康卡斯潜水",
					"count": 1
				},
				{
					"id": 488,
					"name": "机械腕表",
					"count": 1
				}
			],
			"cpv": [
				{
					"value": "5845450491771",
					"name": "表壳材质%##%精钢",
					"count": 1
				},
				{
					"value": "5841155523313",
					"name": "机芯类型%##%机械机芯",
					"count": 1
				},
				{
					"value": "5832565590532",
					"name": "镜面材质%##%人工合成蓝宝石表镜",
					"count": 1
				},
				{
					"value": "5849745457895",
					"name": "显示方式%##%指针式",
					"count": 1
				}
			],
			"hasPrice": [
				{
					"value": "1",
					"name": "有货",
					"count": 1
				}
			],
			"sellDate": [
				{
					"value": "2017年",
					"count": 1
				}
			],
			"smartMenus": [
				
			]
		},
		"isShowGeneral": 1,
		"requestId": "9c3f9e5d3b075e24",
		"allowOriginSearch": 0
	},
	"code": 200,
	"status": 200,
	"msg": "ok",
	"error": False
}
```