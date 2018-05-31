#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
import time
import datetime

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver', options=options)

KAKAO_ID = 'san.kill'
KAKAO_PW = '!@dl926516'

HOST_URL = 'https://parking.kakao.com/admin'

all_jobs = []
TODAY = datetime.datetime.today().strftime("%Y-%m-%d")

def admin_login():
    driver.get(HOST_URL + '/login')
    driver.find_element_by_name('manager[login]').send_keys(KAKAO_ID)
    driver.find_element_by_name('manager[password]').send_keys(KAKAO_PW)
    driver.find_element_by_name('commit').click()


def find_area():
    for page in range(1,8):
        driver.get(HOST_URL + '/gear_companies/parks?page=' + str(page))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        #픽 id값과 리스트
        pick_list = soup.select('table > tbody > tr')
        for area in pick_list:
            if len(area.select('td > span.label-danger')) == 1:
                id = area.select('td')[0].text
                name = area.select('td')[1].text
                print '%s, %s, %s, red' %(id, name, str(page))
            elif len(area.select('td > span.label-warning')) == 1:
                id = area.select('td')[0].text
                name = area.select('td')[1].text
                print '%s, %s, %s, warning' %(id, name, str(page))

while True:
    find_area()
    time.sleep(300)

    find . -type f -exec sed -i 's/cultureground/wannago/g' {} \


# green = []
# red = []
# for page in range(1,8):
#     driver.get(HOST_URL + '/gear_companies/parks?page=' + str(page))
#     html = driver.page_source
#     soup = BeautifulSoup(html, 'html.parser')
#     #픽 id값과 리스트
#     pick_list = soup.select('table > tbody > tr')
#     for area in pick_list:
#         if len(area.select('td > span.label-danger')) == 1:
#
#
#             # driver.get('https://parking-sandbox.kakao.com' + area.select('td > a')[0]['href'])
#             # html = driver.page_source
#             # soup = BeautifulSoup(html, 'html.parser')
#             # if len(soup.select('td')) > 1:
#             #     if soup.select('td')[3].text == '':
#             #         if soup.select('td')[8].text == '0':
#             #             print '%s,%s' % (area.select('td')[0].text, soup.select('td')[13].text)
#             #         else:
#             #             print '%s,%s' % (area.select('td')[0].text, soup.select('td')[8].text)
#             #     else:
#             #         print '%s,%s' % (area.select('td')[0].text, soup.select('td')[3].text)
#         # elif len(area.select('td > span.label-success')) == 1:
#         #     driver.get('https://parking-sandbox.kakao.com' + area.select('td > a')[0]['href'])
#         #     html = driver.page_source
#         #     soup = BeautifulSoup(html, 'html.parser')
#         #     if len(soup.select('td')) > 1:
#         #         if soup.select('td')[3].text == '':
#         #             print '%s,%s' % (area.select('td')[0].text, soup.select('td')[8].text)
#         #         else:
#         #             print '%s,%s' % (area.select('td')[0].text, soup.select('td')[3].text)
#
# for g_area in green:
#     print '%s,%s' % (g_area.select('td')[0].text, g_area.select('td')[1].text)
#
# for r_area in red:
#     print '%s,%s' % (r_area.select('td')[0].text, r_area.select('td')[1].text)
#
# for n_area in no:
#     if 1<len(n_area.select('td')):
#         print '%s,%s' % (n_area.select('td')[0].text, n_area.select('td')[1].text)
