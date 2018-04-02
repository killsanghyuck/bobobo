#-*- coding: utf-8 -*-

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')

#웹할인 페이지 계정
LOGIN_INFO = {
    'user_id': 'kakaot',
    'password': '123456'
}
HOST_URL = 'https://parking.kakao.com/admin'
#웹할인 페이지
PARK_HOST_URL = 'http://211.218.27.110:8090'

#카카오 어드민 계정
KAKAO_ID = 'san.kill'
KAKAO_PW = '!@dl926516'

LOGIN_URL = '/account/login.asp'
SEARCH_CAR_NUMBER_URL = '/discount/discount_regist.asp'
ADD_ACTION_URL = '/discount/discount_regist.asp'
LIST_FIND = '/discount/discount_list.asp'

#주차장이름
AREA_NAME = '리버타워'
#주차장ID
AREA_ID = 2878

driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver')
driver.implicitly_wait(3)


def login():
    login_req = s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
    if login_req.status_code == 200:
        return True

def find_car_number(k_car_num):
    find_req = s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'license_plate_number': k_car_num[-4:]})
    flag = False
    chk = ''
    if find_req.status_code == 200:
        soup = BeautifulSoup(find_req.content, 'html.parser')
        tr_list = soup.select('table')[3].select('tr')
        if len(tr_list) > 2:
            for i in range(1, len(tr_list)-1):
                try:
                    enter_car = tr_list[i].select('td')[1]
                except IndexError:
                    enter_car = 'null'
                if enter_car == 'null':
                    flag = False
                else:
                    car_num = tr_list[i].select('td')[1].text.strip()
                    parking_time = tr_list[i].select('td')[3].text.strip()
                    if car_num == k_car_num and len(parking_time) == 5:
                        chk = tr_list[i].select('td')[0].select('input')[0]['value']
                        flag = True
                    elif car_num == k_car_num and parking_time > '15':
                        chk = tr_list[i].select('td')[0].select('input')[0]['value']
                        flag = True
    return flag, chk


def add_action(chk, k_car_num):
    ADD_ACTION_PARAMS = {
        'show_car_img': '',
        'show_no_recong': '',
        'request_type_value': 'INSERTDISCOUNT',
        'post_discount_value': 15,
        'license_plate_number': k_car_num[-4:],
        'chk': chk
    }
    add_req = s.post(PARK_HOST_URL + ADD_ACTION_URL, data=ADD_ACTION_PARAMS)
    return True

def list_find(k_car_num):
    flag = True
    # list_req = s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'license_plate_number': k_car_num[-4:]})
    # if list_req.status_code == 200:
    #     soup = BeautifulSoup(list_req.content, 'html.parser')
    #     try:
    #         if soup.select('script')[12]: flag = True
    #     except IndexError:
    #         flag = False
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
            find_car = find_car_number(k_car_num)
            if find_car[0]:
                if add_action(find_car[1], k_car_num):
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
