# coding: utf-8
import cProfile
from pprint import pprint
import csv
from collections import Counter
import re
import requests
from bs4 import BeautifulSoup
import jieba
import codecs
import matplotlib.pyplot as plt
from wordcloud import WordCloud


class JobSpider():
    def __init__(self):
        self.company = []
        self.text = ""
        self.headers = {'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
                        'Referer': 'https://passport.liepin.com/ajaxproxy.html'}
        # 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

    def spider(self):
        # 20-30万
        urls = ["https://www.liepin.com/zhaopin/?pubTime=&compkind=&fromSearchBtn=2&ckid=9ebc3054fd98e3c3&isAnalysis=&init=-1&searchType=1&flushckid=1&dqs=010&industryType=industry_01&jobKind=&sortFlag=15&industries=030&salary=20$30&compscale=&key=%E6%B5%8B%E8%AF%95&clean_condition=&headckid=4da58c2fba8525a9"]
        #10-15万
        # urls = ["https://www.liepin.com/zhaopin/?pubTime=&compkind=&fromSearchBtn=2&ckid=bf3b1b149ff403ec&isAnalysis=&init=-1&searchType=1&flushckid=1&dqs=010&industryType=industry_01&jobKind=&sortFlag=15&industries=030&salary=10$15&compscale=&key=%E6%B5%8B%E8%AF%95&clean_condition=&headckid=4da58c2fba8525a9"]
        #15-20万
        # urls = ["https://www.liepin.com/zhaopin/?pubTime=&compkind=&fromSearchBtn=2&ckid=7d3f5ec9051ab6c6&isAnalysis=&init=-1&searchType=1&flushckid=1&dqs=010&industryType=industry_01&jobKind=&sortFlag=15&industries=030&salary=15$20&compscale=&clean_condition=&key=%E6%B5%8B%E8%AF%95&headckid=4da58c2fba8525a9"]
        # payload = {'layer_from': 'wwwindex_top_cover_login_userc',
        #               'chk_remember_pwd':'on','user_kind':'0','isMd5':'1'}
        # login_cookies = "grwng_uid=545c9f5a-db35-41ca-961c-315056d4533a"

        r = requests.get(urls[0], headers=self.headers).content
        page_list = BeautifulSoup(r, 'lxml').find("div", class_="pagerbar").find_all("a", string = re.compile('\d+'))
        urls.extend([i['href'] for i in page_list if i['href'] != 'javascript:;'])
        pprint(urls)
        many_jobs = []
        for url in urls:
            r = requests.get(url, headers=self.headers).content
            jobs = BeautifulSoup(r, 'lxml').find('ul', class_='sojob-list').find_all('div', class_='sojob-item-main clearfix')
            for job in jobs:
                title = job.find('h3')['title'][2:]
                condition = job.find('p', class_='condition clearfix')['title']
                time = job.find('p',class_='time-info').find('time').string
                company_name = job.find('p',class_='company-name').find('a')['title'][2:]
                industry = job.find('a',class_='industry-link').string
                href = job.find('h3').find('a')['href']
                description = self.spider_description(href)
                a_job = {'company_name':company_name, 'title':title, 'condition':condition,
                         'industry':industry, 'time':time, 'description':description}

                # print href, company_name, title, condition, industry, time, description
                many_jobs.append(a_job)
        with open(r'.\data\jobs.csv', 'w') as f:
            f.write(codecs.BOM_UTF8)
            f_csv = csv.writer(f)
            for job in many_jobs:
                row = [job.get('company_name').encode('utf-8'),job.get('title').encode('utf-8'),
                       job.get('condition').encode('utf-8'),job.get('industry').encode('utf-8'),
                       job.get('time').encode('utf-8'),job.get('description').encode('utf-8')]
                f_csv.writerow(row)

        print many_jobs

    def spider_description(self, href):
        '''input url of single job, get the description and job requirements.'''
        description = ""
        r = requests.get(href, headers=self.headers).content
        bs = BeautifulSoup(r, 'lxml').find('div', class_='content content-word')
        for string in bs.stripped_strings:
            description += (string + '\n')
        return description

    def word_cloud(self):
        description = ""
        with open(r'.\data\jobs.csv') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                description += row[5]

        print type(description)
        r1 = "[(进行)(以上)(以及)]+".decode('utf-8')
        description = re.sub(r1, "".decode('utf-8'), description.decode('utf-8'))
        jieba.load_userdict(r".\data\user_dict.txt")
        seg_list = jieba.cut(description, cut_all=False)
        counter = dict()
        for seg in seg_list:
            if len(seg) > 1:
                counter[seg] = counter.get(seg, 1) + 1
        wordcloud = WordCloud(font_path=r".\font\msyh.ttf",
                              max_words=100, height=600, width=1200).generate_from_frequencies(counter)
        #plt.imshow(wordcloud)
        #plt.axis('off')
        #plt.show()
        wordcloud.to_file(r'.\images\worldcloud.jpg')
        counter_sort = sorted(counter.items(), key=lambda value: value[1], reverse=True)
        with open(r'.\data\counter.csv', 'wb') as f:
            f.write(codecs.BOM_UTF8)
            f_csv = csv.writer(f)
            for row in counter_sort:
                # print (row[0], row[1])
                f_csv.writerow((row[0].encode('utf-8'), row[1]))



tester = JobSpider()
tester.spider()
tester.word_cloud()