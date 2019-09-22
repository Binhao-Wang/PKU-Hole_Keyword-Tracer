'''
用户需要设置的参数：
        # 要搜索的关键词
        KEYWORD
        # 输入Email地址和口令
        from_addr = '**your email address**'
        password = '**your email psw**'
        # 输入收件人地址:
        to_addr = '**the receiver you want to send to**'
        # 输入SMTP服务器地址:
'''
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from email.mime.text import MIMEText
import smtplib
import time
from selenium.webdriver.chrome.options import Options
import csv

chrome_options = Options()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(browser, 10)
KEYWORD = '求' # 设置要搜索的关键词
url = 'https://pkuhelper.pku.edu.cn/hole/'


class holeCrawler:

    def __init__(self, url, KEYWORD):
        self.url = url
        self.KEYWORD = KEYWORD
        self.results = []
        self.results_IDs = []
        self.flag = False  # 下一次循环可能会把原来的信息再发一遍，flag用于判断是否有新信息加入，从而是否需要再发一次邮件

    def index_page(self):
        '''抓取页面'''
        browser.get(self.url)
        browser.implicitly_wait(10)
        browser.execute_script('window.scrollBy(0,1000)')
        # print(browser.find_elements_by_css_selector('div.box'))
        html = browser.page_source
        doc = pq(html)
        boxes = doc('div.box').items()
        for box in boxes:
            content = box.find('.box-content').text()
            if KEYWORD in content:
                # 如果找到关键词，那就把这个洞的信息存起来
                hole = {
                    'id': box.find('.box-id').text(),
                    'timestamp': box.find('.box-header span').text()[-13:],
                    'content': box.find('.box-content').text(),
                    'comments': box.find('.flow-reply-row').text(),
                }
                if hole['id'] not in self.results_IDs:  # 检查重复
                    self.results.append(hole)
                    self.results_IDs.append(hole['id'])
                    print('结果存储成功')
                    self.flag = True
                else:
                    print('已有重复结果')
        browser.quit()


    def write_csv(self):
        headers = ['id','timestamp','content','comments']
        with open('results.csv','w',newline='') as f:
            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(self.results)


    def email_notice(self):
        msg = MIMEText(('KEYWORD %s found \n content:\n %s' %
                        (self.KEYWORD, str(self.results))), '', 'utf-8')
        # 输入Email地址和口令
        from_addr = '**your email address**'
        password = '**your email psw**'
        # 输入收件人地址:
        to_addr = '**the receiver you want to send to**'
        # 输入SMTP服务器地址:
        smtp_server = "**the sender's stmp-server --eg. mail.pku.edu.cn"
        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()


holeCrawler = holeCrawler(url, KEYWORD)
loop = 1
while 1:
    print('============Loop %s===========' % loop)
    holeCrawler.index_page()
    if holeCrawler.flag is True:
        holeCrawler.write_csv()
        holeCrawler.email_notice()
        print('\n本次循环后的结果:')
        print(holeCrawler.results)
    else:
        print('\n本次循环没有新信息')
    holeCrawler.flag = False
    loop += 1
    time.sleep(30) # 循环之间的间隔，用户可自行设置
