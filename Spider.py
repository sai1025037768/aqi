# -*- coding: UTF-8 -*-
import urllib.request, urllib.robotparser, urllib.error, chardet, urllib.parse
from bs4 import BeautifulSoup
import re
import LiveData
import uuid
from sqlserver import MSSQL
import config
import random
import time

USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    ]

def download(url, user_agent='Mozilla/5.0', num_retries=2):
    print('Downloading:', url)
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url, headers=headers)

    try:
        html = urllib.request.urlopen(request).read()
        charset = chardet.detect(html)['encoding']
        html = html.decode(charset)
        # if charset == 'GB2312' or charset == 'gb2312':
        #     html = html.decode('GBK').encode('UTF-8')
        # else:
    except urllib.error.URLError as e:
        print('Download error', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 6:
                return download(url, user_agent, num_retries - 1)
    return html


def parseHtml(seen, user_agent):
    # 使用正则表达式匹配找到的文本内容中的所有s 空格 \n换行 和 <.*?>所有的标签
    pattern = re.compile(r'\s|\n|<br>', re.S)

    liveSeen = set()
    for cityLink in seen:
        user_agent = random.choice(USER_AGENTS)
        print(user_agent)

        delay = random.randint(0, 3)
        time.sleep(delay)

        cityData = download(cityLink, user_agent, 5)
        citySoup = BeautifulSoup(cityData, 'html.parser')
        cityPinyin = cityLink[cityLink.rfind('/') + 1:]
        print(cityPinyin)
        cityName = pattern.sub('', citySoup.find('div', class_='city_name').find('h2').text)
        level = pattern.sub('', citySoup.find('div', class_='level').find('h4').string)
        liveDataTime = citySoup.find('div', class_='live_data_time').find('p').text
        #当前更新时间
        liveDataTime = liveDataTime[liveDataTime.find("：") + 1:]

        #数据更新时间与上次更新时间相同时，不再获取数据
        last_time = config.time_point
        if last_time == liveDataTime:
            return

        liveDataUnit = pattern.sub('', citySoup.find('div', class_='live_data_unit').string)
        liveDataUnit = liveDataUnit[liveDataUnit.find("：") + 1:]
        otherDataTag = citySoup.find('div', class_='span12 data').find_all('div', class_='span1')

        otherDatas = dict()
        for dataTag in otherDataTag:
            if len(dataTag.contents) == 5:
                value = pattern.sub('', dataTag.find('div', class_='value').string)
                caption = pattern.sub('', dataTag.find('div', class_='caption').string)
                otherDatas[caption] = value

        primary_pollutant = pattern.sub('', citySoup.find('div', class_='primary_pollutant').find('p').string)
        affect = pattern.sub('', citySoup.find('div', class_='affect').find('p').string)
        action = pattern.sub('', citySoup.find('div', class_='action').find('p').string)

        id = str(uuid.uuid1())
        liveData = LiveData.LiveData(id, otherDatas['PM2.5/1h'], otherDatas['NO2/1h'], otherDatas['O3/1h'],
                                     otherDatas['SO2/1h'], level, primary_pollutant, otherDatas['PM10/1h'], cityName,
                                     cityPinyin,
                                     action, affect, otherDatas['O3/8h'], liveDataUnit, otherDatas['AQI'],
                                     liveDataTime, otherDatas['CO/1h'])

        liveSeen.add(liveData)

    return liveSeen, liveDataTime


def getLinks(html):
    seen = set()
    soup = BeautifulSoup(html, 'html.parser')
    allcityTag = soup.find('div', class_='all').find_all('a')
    for cityTag in allcityTag:
        link = urllib.parse.urljoin(url, cityTag.attrs['href'])
        seen.add(link)

    return seen


if __name__ == '__main__':



    PROXY_HOSTS = [
        "123.53.86.13:28946",
        "222.182.225.205:28664",
        "49.70.48.126:39025",
        "113.128.31.79:48770",
        "192.168.1.7:81"
    ]

    proxy_host = random.choice(PROXY_HOSTS)
    proxy_support = urllib.request.ProxyHandler({'http': "124.193.201.66:81"})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)

    # rp = urllib.robotparser.RobotFileParser()
    # rp.set_url("http://www.pm25.in/robots.txt")
    # rp.read()
    url = "http://www.pm25.in/"
    user_agent = random.choice(USER_AGENTS)

    # can = rp.can_fetch(user_agent, url)

    # if can:

    html = download(url, user_agent, 5)
    if html:
        seen = getLinks(html)
        # for cityLink in seen:
        liveSeen, time_point = parseHtml(seen, user_agent)

        if liveSeen:
            # 存入数据库
            ms = MSSQL(host=config.host, port=config.port, user=config.user, pwd=config.pwd, db=config.db)
            ms.execute_many(liveSeen)

            #更新配置文件中更新时间
            config.set(time_point)