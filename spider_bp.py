import requests
import re
from lxml import etree
import json
import time
import sys


def get_page(url):
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'})
    html = resp.text
    time.sleep(1.5)
    pat = '共(.*?)頁</td>'
    page = int(re.compile(pat).findall(html)[0])
    # 回傳一個int的數值，表示總頁數
    return page


def start_crawler(url):
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'})
    html = resp.text
    time.sleep(1)
    pat_cat = '<a href="(.*?)"><strong>日本\w{2,4}</strong></a>'
    url_list = re.compile(pat_cat).findall(html)
    for ii in range(len(url_list)):
        url_list[ii] = 'https://www.backpackers.com.tw/forum/' + re.sub(r's=.*?;', '', url_list[ii])
    return url_list


def get_article(url, page):
    myurl = url + '&order=desc&page='
    first = myurl + str(page)
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'})
    html = resp.text
    time.sleep(2)
    pat_url = '<a  href="(.*?)" id=".*">.*?</a>'
    pat_title = '<a  href=".*?" id=".*">(.*?)</a>'
    pat_category = '【(.*?)】'
    url_article = re.compile(pat_url).findall(html)
    category = re.compile(pat_category).findall(html)
    title = re.compile(pat_title).findall(html)
    for ii in range(len(url_article)):
        url_article[ii] = 'https://www.backpackers.com.tw/forum/' + re.sub(r's=.*?;', '', url_article[ii])
        title[ii] = category[ii] + '_' + title[ii]
    return [url_article, title]


def crawl(url):
    content_list = []
    result = []
    dateresult = []
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'})
    time.sleep(0.7)
    html = etree.HTML(resp.text)
    content = html.xpath('//div[@class="vb_postbit"]')
    mydate = html.xpath('//td[starts-with(@id,"td_post_")]/div[@class="smallfont"]/text()')
    for ii in content:
        string = ii.xpath("string(.)")
        content_list.append(string)
    for d in mydate:
        if re.search(r'(\d{4}-\d{2}-\d{2}, \d{2}:\d{2})', d):
            dateresult.append(d.strip())
    result.append(''.join(content_list))
    result.append(dateresult[0])
    return result


if __name__ == '__main__':
    print('we start crawler!')
    target_url = sys.argv[1]
    time.sleep(3)
    pages = get_page(target_url)
    file = sys.argv[2]
    page_start = int(sys.argv[3])
    page_end = int(sys.argv[4])
    print('website:', target_url, 'total pages:', str(pages))
    with open('./' + file + '.txt', 'a', encoding='utf-8') as output:
        for page in range(page_start, page_end+1):
            time.sleep(5)
            print('website:', target_url, 'page:', str(page))
            article = get_article(target_url, page)
            if article == None:
                print('we try next page!')
                continue
            article_url = article[0]
            article_title = article[1]
            print('total items:', str(len(article_url)))
            for item in range(0, len(article_url)):
                mydict = {}
                time.sleep(2)
                mycontent = crawl(article_url[item])
                time.sleep(3)
                mydict['content'] = mycontent[0]
                mydict['date'] = mycontent[1]
                mydict['title'] = article_title[item]
                output.write(json.dumps(mydict, ensure_ascii=False))
                output.write('\n')
                print('page', str(page + 1), 'item', str(item + 1))
        print('finished')