# Python爬虫-华为备忘录
华为备忘录官网地址：
https://cloud.huawei.com/home#/notepad/note/allNote/

## 使用方法
使用本工具前，需要自行获取华为备忘录的cookie。

获取cookie的步骤：
1. 登录[https://cloud.huawei.com](https://cloud.huawei.com)，扫码或者帐号登录。
2. 点击【备忘录】应用。
3. 打开浏览器F12开发者工具，点击网络监视器，然后随意点击一条备忘录，找到对应的POST请求，从请求头中找出`Cookie`字段值。

使用cookie：得到cookie后自行替换脚本中的headers中的Cookie内容，方可使用。

## 爬取内容
- 脚本运行后，仅会爬取所有备忘录列表中的内容。
- （未测试，这是原作者实现的功能）备忘录中要是存在图片会自动替换为图片的路径，需要手动根据需要替换为图片的地址。

## 二次开发优化改进内容
（待完善）
