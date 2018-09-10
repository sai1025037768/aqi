# -*- coding: UTF-8 -*-
import urllib.request, urllib.robotparser, urllib.error, chardet, urllib.parse
import random

PROXY_HOSTS = [
    "123.53.86.13:28946",
    "222.182.225.205:28664",
    "49.70.48.126:39025",
    "113.128.31.79:48770",
    "192.168.1.7:81"
]

proxy_support = urllib.request.ProxyHandler({'http': "49.70.48.126:39025"})
opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)

url = 'https://zh-hans.ipshu.com/my_info'
user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
headers = {'User-agent': user_agent}
request = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(request)
html = response.read().decode('utf-8')
print(html)