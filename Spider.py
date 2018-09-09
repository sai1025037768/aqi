# -*- coding: UTF-8 -*-
import urllib.request, urllib.robotparser, urllib.error, chardet, urllib.parse
from bs4 import BeautifulSoup
import re
import LiveData
import uuid
from sqlserver import MSSQL


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
        cityData = download(cityLink, user_agent, 5)
        citySoup = BeautifulSoup(cityData, 'html.parser')
        cityPinyin = cityLink[cityLink.rfind('/') + 1:]
        print(cityPinyin)
        cityName = pattern.sub('', citySoup.find('div', class_='city_name').find('h2').text)
        level = pattern.sub('', citySoup.find('div', class_='level').find('h4').string)
        liveDataTime = citySoup.find('div', class_='live_data_time').find('p').text
        liveDataTime = liveDataTime[liveDataTime.find("：") + 1:]
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

    return liveSeen


def getLinks(html):
    seen = set()
    soup = BeautifulSoup(html, 'html.parser')
    allcityTag = soup.find('div', class_='all').find_all('a')
    for cityTag in allcityTag:
        link = urllib.parse.urljoin(url, cityTag.attrs['href'])
        seen.add(link)

    return seen


if __name__ == '__main__':
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("http://www.pm25.in/robots.txt")
    rp.read()
    url = "http://www.pm25.in/"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"

    can = rp.can_fetch(user_agent, url)

    if can:

        html = download(url, user_agent, 5)
        if html:
            seen = getLinks(html)
            # for cityLink in seen:
            liveSeen = parseHtml(seen, user_agent)

            # 存入数据库
            ms = MSSQL(host="202.104.140.36", port="11433", user="sa", pwd="powerdata", db="AQI")
            ms.execute_many(liveSeen)
