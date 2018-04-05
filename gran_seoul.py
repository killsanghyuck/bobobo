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
    'j_username': 'kakao t',
    'j_password': '123456'
}
HOST_URL = 'https://parking.kakao.com/admin'
#웹할인 페이지
PARK_HOST_URL = 'http://npgsgranparkingroot1.iptime.org'
LOGIN_URL = '/j_spring_security_check'
SEARCH_CAR_NUMBER_URL = '/ezTicket/carSearch'
SEARCH_TICKET_URL = '/ezTicket/carTicket'
GET_PARK_CODE_URL = '/ezTicket/inputDiscountValue'
ADD_COUPON_URL = '/ezTicket/valiDiscountCode.json'
SUBMIT_COUPON_URL = '/ezTicket/inputDiscountValueRegister'
GRAN_SEOUL_AREA_ID = 58

KAKAO_ID = 'san.kill'
KAKAO_PW = '!@dl926516'

COUPONS = [{ 'id': 60, 'name': '30분쿠폰', 'value': 30 },
           { 'id': 61, 'name': '1시간쿠폰', 'value': 60 },
           { 'id': 62, 'name': '2시간쿠폰', 'value': 120 },
           { 'id': 63, 'name': '3시간쿠폰', 'value': 180 },
           { 'id': 64, 'name': '4시간쿠폰', 'value': 240 }]

#주차장id
AREA_NAME = '그랑서울'
AREA_ID = 1804

driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver', chrome_options=options)
driver.implicitly_wait(3)

def admin_login():
    driver.get(HOST_URL + '/login')
    driver.find_element_by_name('manager[login]').send_keys(KAKAO_ID)
    driver.find_element_by_name('manager[password]').send_keys(KAKAO_PW)
    driver.find_element_by_name('commit').click()

def login():
    login_req = s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
    if login_req.status_code == 200:
        return True

def find_car_number(k_car_num, duration, ti):
    flag = False
    park_code = ''
    real_ti = ''
    find_req = s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'car_no': k_car_num[-4:]})
    if find_req.status_code == 200:
        soup = BeautifulSoup(find_req.content, 'html.parser')
        for tr in soup.select('table tbody tr'):
            if k_car_num != tr.select('a')[0].text: continue
            real_ti = tr.select('input')[0].get('value')
            real_ti = datetime.datetime.strptime(str(real_ti), "%Y%m%d%H%M%S")
            if real_ti.strftime("%Y-%m-%d") != ti.strftime("%Y-%m-%d"): continue
            duration = set_duration(real_ti, duration)
            park_code = get_park_code(k_car_num, real_ti)
            flag = True
            break
    return duration, park_code, real_ti, flag

def make_order(duration, k_car_num):
    order = { 'discount_value': 0,
             'discount_name': [],
             'discount_code': [],
             'discount_desc': [] }
    click_count = 0
    coupon_times = list(map(lambda i: i['value'], COUPONS))
    while duration > 0 and not not coupon_times:
        if duration >= coupon_times[-1]:
          coupon = list(filter(lambda i: i['value'] == coupon_times[-1], COUPONS))[0]
          click_count, order = add_coupon(coupon, click_count, order, k_car_num)
          duration -= coupon['value']
        else:
          coupon_times.pop()
    if not duration > 0: return order
    coupon = list(filter(lambda i: i['value'] == 30, COUPONS))[0]
    click_count, order = add_coupon(coupon, click_count, order, k_car_num)
    return order

def add_coupon(coupon, click_count, order, k_car_num):
    response = s.post(PARK_HOST_URL + ADD_COUPON_URL, data={'discount_code': coupon['id'], 'car_no': k_car_num, 'clickCount': click_count})
    json_body = json.loads(response.content)
    order['discount_value'] = order['discount_value'] + json_body['dcValue']
    order['discount_name'].append(coupon['name'])
    order['discount_code'].append(coupon['id'])
    order['discount_desc'].append(json_body['dcDesc'])
    click_count += 1
    return click_count, order

def set_duration(real_ti, duration):
    to = real_ti + datetime.timedelta(minutes = duration)
    if to.day == real_ti.day: return duration
    duration -= to.hour * 60
    duration -= (to.minute / 30) * 30
    return duration

def get_park_code(k_car_num, real_ti):
    get_park_req = s.post(PARK_HOST_URL + GET_PARK_CODE_URL, data={'car_no': k_car_num, 'car__totaldate': real_ti.strftime('%Y%m%d%H%M%S')})
    soup = BeautifulSoup(get_park_req.content, 'html.parser')
    return soup.find(id='park_code').get('value')

def submit_coupon(k_car_num, park_code, real_ti, order):
    params = { 'group_name': '모바일 할인',
             'department_name': '카카오',
             'car_no': k_car_num,
             'park_code': park_code,
             'car_in_date': real_ti.strftime('%Y-%m-%d') + ' 00:00:00.0',
             'car_in_time': real_ti.strftime('%H:%M'),
             'car__totaldate': real_ti.strftime('%Y%m%d%H%M%S'),
             'discount_name': ','.join(str(v) for v in order['discount_name']),
             'discount_code': ','.join(str(v) for v in order['discount_code']),
             'discount_value': order['discount_value'],
             'discount_desc': ','.join(str(v) for v in order['discount_desc']) }
    add_req = s.post(PARK_HOST_URL + SUBMIT_COUPON_URL, data=params)

def submit_coupon_success(k_car_num, duration):
    response = s.post(PARK_HOST_URL + SEARCH_TICKET_URL)
    if not response.status_code == 200: return False
    soup = BeautifulSoup(response.content, 'html.parser')
    for tr in soup.select('table tbody tr'):
        tr = ','.join(str(v) for v in tr)
        if str(duration) in tr and k_car_num in tr: return True
    return False

def reservation_bot():
    driver.get(HOST_URL + '/picks?q[parking_lot_id_eq]=' + str(AREA_ID) + '&q[state_eq]=4&order=id_desc')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    #픽 id값과 리스트
    pick_list = soup.select('table#index_table_picks > tbody > tr > td.col-id')
    if len(pick_list) >= 1:
        for pick in pick_list:
            driver.get(HOST_URL + '/picks/' + pick.text)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            car_number = soup.select('table > tbody > tr.row-license_number > td')
            ti = soup.select('table > tbody > tr.row-created_at > td')[0].text
            duration = soup.select('table > tbody > tr.row-ticket_item_code > td')[0].text
            k_car_num = car_number[0].encode_contents().strip().replace(' ', '').split("<br/>")[0]
            ti = datetime.datetime.strptime(str(ti), "%Y/%m/%d %H:%M:%S")
            duration = int(duration[:-3]) * 60
            duration, park_code, real_ti, flag = find_car_number(k_car_num, duration, ti)
            if flag:
                order = make_order(duration, k_car_num)
                submit_coupon(k_car_num, park_code, real_ti, order)
                if submit_coupon_success(k_car_num, duration):
                    print(pick.text + ' : ' + '차량등록 완료 : ' + k_car_num)
                    driver.find_element_by_class_name('select2-choice').click()
                    driver.find_element_by_id('select2-result-label-3').click()
                    driver.find_element_by_name('commit').click()
                else:
                    print '차량등록실패'
            else:
                print(pick.text + ' : ' + '입차확인불가 : ' + k_car_num)

admin_login()
while True:
    with requests.Session() as s:
        login()
        reservation_bot()
    time.sleep(300)
