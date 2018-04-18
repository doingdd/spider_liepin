#!/usr/bin/python
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


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
        urls = [
            "https://www.liepin.com/zhaopin/?industries=040&dqs=010&salary=&jobKind=&pubTime=&compkind=&compscale=&industryType=industry_01&searchType=1&clean_condition=&isAnalysis=&init=1&sortFlag=15&flushckid=0&fromSearchBtn=1&headckid=808786ddb45f0c9d&key=%E6%B5%8B%E8%AF%95%E5%BC%80%E5%8F%91"]
        # 10-15万
        # urls = ["https://www.liepin.com/zhaopin/?pubTime=&compkind=&fromSearchBtn=2&ckid=bf3b1b149ff403ec&isAnalysis=&init=-1&searchType=1&flushckid=1&dqs=010&industryType=industry_01&jobKind=&sortFlag=15&industries=030&salary=10$15&compscale=&key=%E6%B5%8B%E8%AF%95&clean_condition=&headckid=4da58c2fba8525a9"]
        # 15-20万
        # urls = ["https://www.liepin.com/zhaopin/?pubTime=&compkind=&fromSearchBtn=2&ckid=7d3f5ec9051ab6c6&isAnalysis=&init=-1&searchType=1&flushckid=1&dqs=010&industryType=industry_01&jobKind=&sortFlag=15&industries=030&salary=15$20&compscale=&clean_condition=&key=%E6%B5%8B%E8%AF%95&headckid=4da58c2fba8525a9"]
        # payload = {'layer_from': 'wwwindex_top_cover_login_userc',
        #               'chk_remember_pwd':'on','user_kind':'0','isMd5':'1'}
        # login_cookies = "grwng_uid=545c9f5a-db35-41ca-961c-315056d4533a"

        r = requests.get(urls[0], headers=self.headers).content
        page_list = BeautifulSoup(r, 'lxml').find("div", class_="pagerbar").find_all("a", string=re.compile('\d+'))
        urls.extend(['https://www.liepin.com' + i['href'] for i in page_list if i['href'] != 'javascript:;'])
        pprint(urls)
        many_jobs = []
        for url in urls:
            r = requests.get(url, headers=self.headers).content
            jobs = BeautifulSoup(r, 'lxml').find('ul', class_='sojob-list').find_all('div',
                                                                                     class_='sojob-item-main clearfix')
            for job in jobs:
                title = job.find('h3')['title'][2:]
                condition = job.find('p', class_='condition clearfix')['title']
                time = job.find('p', class_='time-info').find('time').string
                company_name = job.find('p', class_='company-name').find('a')['title'][2:]
                try:
                    industry = job.find('p', class_='field-financing').find('a', class_='industry-link').string
                except:
                    industry = job.find('p', class_='field-financing').find('span').string
                href = job.find('h3').find('a')['href']
                if not href.startswith('https:'):
                    href = 'https://www.liepin.com' + href
                description = self.spider_description(href)
                if description:
                    a_job = {'company_name': company_name, 'title': title, 'condition': condition,
                             'industry': industry, 'time': time, 'description': description, 'url':href}

                # print href, company_name, title, condition, industry, time, description
                    many_jobs.append(a_job)
        return many_jobs

    def save_jobs(self):
        many_jobs = self.spider()
        with open(r'/root/spider_liepin/data/jobs.csv', 'w') as f:
            f.write(codecs.BOM_UTF8)
            f_csv = csv.writer(f)
            for job in many_jobs:
                print job
                row = [job.get('company_name').encode('utf-8'), job.get('title').encode('utf-8'),
                       job.get('condition').encode('utf-8'), job.get('industry').encode('utf-8'),
                       job.get('time').encode('utf-8'), job.get('description').encode('utf-8')]
                f_csv.writerow(row)

        # print many_jobs

    def spider_description(self, href):
        '''input url of single job, get the description and job requirements.'''
        description = ""
        r = requests.get(href, headers=self.headers).content
        bs = BeautifulSoup(r, 'lxml').find('div', class_='content content-word')
        if bs:
            for string in bs.stripped_strings:
                description += (string + '\n')
            return description

    def word_cloud(self):
        description = ""
        with open(r'/root/spider_liepin/data/jobs.csv') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                description += row[5]

        print type(description)
        r1 = "[(进行)(以上)(以及)]+".decode('utf-8')
        description = re.sub(r1, "".decode('utf-8'), description.decode('utf-8'))
        jieba.load_userdict(r"/root/spider_liepin/data/user_dict.txt")
        seg_list = jieba.cut(description, cut_all=False)
        counter = dict()
        for seg in seg_list:
            if len(seg) > 1:
                counter[seg] = counter.get(seg, 1) + 1
        wordcloud = WordCloud(font_path=r"/root/spider_liepin/font/msyh.ttf",
                              max_words=100, height=600, width=1200).generate_from_frequencies(counter)
        # plt.imshow(wordcloud)
        # plt.axis('off')
        # plt.show()
        wordcloud.to_file(r'/root/spider_liepin/images/wordcloud.jpg')
        counter_sort = sorted(counter.items(), key=lambda value: value[1], reverse=True)
        with open(r'/root/spider_liepin/data/counter.csv', 'wb') as f:
            f.write(codecs.BOM_UTF8)
            f_csv = csv.writer(f)
            for row in counter_sort:
                # print (row[0], row[1])
                f_csv.writerow((row[0].encode('utf-8'), row[1]))

    def make_html(self):
        #prefer_company = ['美团点评','唯品会','Baidu', '腾讯', '阿里巴巴','搜狗','小米','58同城','网易集团','京东金融集团',
                          #'今日头条','去哪儿','携程','360']
        prefer_company = ['美团点评','唯品会','搜狗','小米','58同城','网易集团',
                          '今日头条','去哪儿','携程','360']
        msg_html = '<html><body>'
        many_jobs = self.spider()
        for job in many_jobs:
            if job.get('company_name').encode('utf-8') in prefer_company:
                msg_html += '<a href="{0}">{1}</a>'.format(job.get('url').encode('utf-8'),job.get('title').encode('utf-8'))
                msg_html += '<p>{0}, {1}, {2}, {3}</p>'.format(job.get('company_name').encode('utf-8'),
                                                          job.get('condition').encode('utf-8'),
                                                          job.get('time').encode('utf-8'),
                                                          job.get('industry').encode('utf-8'))
                msg_html += '<p>{0}</p>'.format(job.get('description').encode('utf-8'))
        msg_html += '</body></html>'

        # print msg_html
        return msg_html

    def send_mail(self):
        username = '313449377@qq.com'
        password = 'aeqaapfdmpbcbjga'
        smtp_server = 'smtp.qq.com'
        fro = '313449377@qq.com'
        to = 'doingdd_cool@163.com'
        msg = MIMEMultipart('related')
        msg['Subject'] = 'This is important message'

        msg_html = self.make_html()
        msg = MIMEText(msg_html,'html','utf-8')

        smtp = smtplib.SMTP_SSL(smtp_server, 465)
        # smtp = smtplib.SMTP()
        # smtp.connect('smtp.qq.com')
        smtp.login(username, password)
        smtp.sendmail(fro, to, msg.as_string())
        smtp.quit()


tester = JobSpider()
# tester.spider()
tester.save_jobs()
tester.word_cloud()
# tester.make_html()
tester.send_mail()
