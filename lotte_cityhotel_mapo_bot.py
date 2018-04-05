#-*- coding: utf-8 -*-

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
import time
import datetime
import json

reload(sys)
sys.setdefaultencoding('utf-8')

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

#웹할인 페이지 계정
LOGIN_INFO = {
    'userId': 'parkhere81',
    'userPwd': '1234'
}
HOST_URL = 'https://parking.kakao.com/admin'
#웹할인 페이지
PARK_HOST_URL = 'http://www.amanopark.co.kr'

#카카오 어드민 계정
KAKAO_ID = 'san.kill'
KAKAO_PW = '!@dl926516'

LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/registration/listForDiscount'
ADD_ACTION_URL = '/discount/registration/save'
LIST_FIND = '/discount/state/list/doListMst'

TODAY = datetime.datetime.today().strftime("%Y-%m-%d")
#주차장이름
AREA_NAME = '롯데시티호텔'
#주차장ID
AREA_ID = 2018

driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver', chrome_options=options)
driver.implicitly_wait(3)


def login():
    login_req = s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
    if login_req.status_code == 200:
        return True

def find_car_number(k_car_num):
    flag = False
    find_req = s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNo': k_car_num, 'entryDate': TODAY, searchILotArea: 81})
    data = json.loads(find_req.content)
    if len(data) >= 1:
      id = data[0]['id']
      i_lot_area = data[0]['iLotArea']
      returned_car_no = data[0]['carNo']

    return flag, id, i_lot_area, returned_car_no


def add_action(id, i_lot_area, returned_car_no, k_car_num):
    ADD_ACTION_PARAMS = {
        'peId': id,
        'corp': CORP_NAME,
        'discountType': 401,
        'carno': k_car_num,
        'iLotArea': i_lot_area,
        'memo': ''
    }
    add_req = s.post(PARK_HOST_URL + ADD_ACTION_URL, data=ADD_ACTION_PARAMS)
    return True

def list_find(k_car_num):
    flag = False
    LIST_FIND_PARAMS = {
        'startDate': TODAY,
        'endDate': TODAY,
        'account_no': 'parkhere81',
        'carno': k_car_num,
        'iLotArea': 81
    }
    list_req = s.post(PARK_HOST_URL + LIST_FIND, data=LIST_FIND_PARAMS)
    results = json.loads(find_req.content)
    results = results['data']
    if results[0]['carno'] == k_car_num: flag = True
    return flag

def admin_login():
    driver.get(HOST_URL + '/login')
    driver.find_element_by_name('manager[login]').send_keys(KAKAO_ID)
    driver.find_element_by_name('manager[password]').send_keys(KAKAO_PW)
    driver.find_element_by_name('commit').click()

def reservation_bot():
    driver.get(HOST_URL + '/picks?q[parking_lot_id_eq]=' + str(AREA_ID) + '&q[state_eq]=4&order=id_desc')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    #픽 id값과 리스트
    pick_list = soup.select('table#index_table_picks > tbody > tr > td.col-id')
    if len(pick_list) >= 1:
        login()
        for pick in pick_list:
            driver.get(HOST_URL + '/picks/' + pick.text)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            car_number = soup.select('table > tbody > tr.row-license_number > td')
            k_car_num = car_number[0].encode_contents().strip().replace(' ', '').split("<br/>")[0]
            flag, id, i_lot_area, returned_car_no = find_car_number(k_car_num)
            if flag:
                if add_action(id, i_lot_area, returned_car_no, k_car_num):
                    if list_find(k_car_num):
                        print(pick.text + ' : ' + '차량등록 완료 : ' + k_car_num)
                        driver.find_element_by_class_name('select2-choice').click()
                        driver.find_element_by_id('select2-result-label-3').click()
                        driver.find_element_by_name('commit').click()
                    else:
                        print('차량등록실패')
                else:
                    print('차량등록실패')
            else:
                print(pick.text + ' : ' + '입차확인불가 : ' + k_car_num)


admin_login()
while True:
    with requests.Session() as s:
        login()
        reservation_bot()
    time.sleep(300)
