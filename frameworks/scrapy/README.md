# scrapy爬虫技巧


##一、目标资源分类：
1.动态和静态  
2.图片、文本、音乐、视频


##二、爬取方式：

### 1.解析h5页面
```shell script
xpath
css
requests
beautifulsoup
urllib3
json
```

### 2.Selenium进行动态爬虫：
> Selenium ，自动化测试工具。

1、常见错误： 
`selenium.common.exceptions.NoSuchElementException: Message: Unable to locate element:`  
> 造成原因：  
1、加载慢  
2、没有通过一些交互的方式加载出来，比如要按钮  
3、有些网站需要滚动才会加载新的东西，js来强制滚动 
 
```shell script
js="document.documentElement.scrollTop=10000" #拖动滚动条到屏幕底端  
driver.execute_script(js)
```
			
2、对子元素click无效

3、charles 移动端抓包https  
> 抓取API接口传输的数据  
文本解析， 找规律， 正则表达式的熟练精确使用

4、fiddler 移动端抓包http

## 三、编码问题
unicode和utf-8的关系：  
`unicode`: 统一编码格式,用了 16 位来表示. 但是缺点是需要很大的存储空间和传输带宽,算是牺牲了有效性换取了可靠性。  
`utf-8`: unicode的进化版,变长码,针对英文采用 1 字节,针对汉字采用 3 字节. 缺点是在内存中不好进行处理。

### 1、爬取api数据时返回的是unicode编码,导致不能显示中文.
> 解决方法：  
1、`.json.loads()`  
2、`.encode('utf-8')`  
3、`.encode('latin-1').decode('unicode_escape')`  
4、在scrapy文件中设置 `FEED_EXPORT_ENCODING = 'utf-8'`

### 2、在使用requests, urllib, beautifulsoup等库时候, 不能正常显示中文
> 解决方法：  
使用系统编码解决  
`import os`  
`trans_code = sys.getfilesystemencoding()`
`res.decode(trans_code)`
     
## 四、反爬虫措施

```shell script
111 ****** [scrapy selenium] socket.error: [Errno 111] Connection refused

200  ***** success
202  ***  accept but have not deal

300  * Multiple Choices
301  * Moved Permanently

400 ***** bad requests
401 ***** Unauthorized
403 ***** forbidden
404 ***** not found
405 ***** method not allowed

500 *  Internal Server Error
501 ** Not Implemented
502 ** Bad Gateway
503 ** Service Unavailable
504 *  Gateway Timeout
505 ** HTTP Version Not Supported

headers
proxy{
        ip;
        user_agent
}
```
## 五、部署
sched模块定时 + linux(nohup) + shell  
scrapyd + scrapy.cfg 打包爬虫项目  管理自己的spider


## 六、分布式爬虫
scrapy-redis分布式爬虫






