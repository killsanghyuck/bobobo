#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime
import json
from bot_interface import BotInterface

from importlib import reload



#웹할인 페이지 계정
LOGIN_INFO = {
    'j_username': 'kakao t',
    'j_password': '123456'
}
#웹할인 페이지
PARK_HOST_URL = 'http://npgsgranparkingroot0.iptime.org'
LOGIN_URL = '/j_spring_security_check'
SEARCH_CAR_NUMBER_URL = '/ezTicket/carSearch'
SEARCH_TICKET_URL = '/ezTicket/carTicket'
GET_PARK_CODE_URL = '/ezTicket/inputDiscountValue'
ADD_COUPON_URL = '/ezTicket/valiDiscountCode.json'
SUBMIT_COUPON_URL = '/ezTicket/inputDiscountValueRegister'

COUPONS = [{ 'id': 60, 'name': '30분쿠폰', 'value': 30 },
           { 'id': 61, 'name': '1시간쿠폰', 'value': 60 },
           { 'id': 62, 'name': '2시간쿠폰', 'value': 120 },
           { 'id': 63, 'name': '3시간쿠폰', 'value': 180 },
           { 'id': 64, 'name': '4시간쿠폰', 'value': 240 }]
AREA_ID = '1804'

class GranSeoulBot(BotInterface):
    def __init__(self, reservation):
        self.real_ti = ''
        self.park_code = ''
        self.click_count = 0
        self.order = { 'discount_value': 0,
                         'discount_name': [],
                         'discount_code': [],
                         'discount_desc': [] }
        self.k_car_num = reservation['k_car_num']
        self.ti = reservation['ti']
        self.entry_date = reservation['entry_date']
        self.duration = reservation['duration']

        self.s = requests.Session()

    def login(self):
        try:
            login_req = self.s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            return True
        except requests.exceptions.ConnectionError:
            print('connection error')
            return False

    def find_car_number(self):
        flag = False
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'car_no': self.k_car_num[-4:]})
        if find_req.status_code == 200:
            soup = BeautifulSoup(find_req.content, 'html.parser')
            for tr in soup.select('table tbody tr'):
                if self.k_car_num != tr.select('a')[0].text: continue
                self.real_ti = tr.select('input')[0].get('value')
                self.real_ti = datetime.datetime.strptime(str(self.real_ti), "%Y%m%d%H%M%S")
                if self.real_ti.strftime("%Y-%m-%d") != self.entry_date: continue
                self.set_duration()
                self.get_park_code()
                flag = True
                break
        return flag

    def process(self):
        flag = True
        self.make_order()
        self.submit_coupon()
        return flag

    def make_order(self):
        coupon_times = list(map(lambda i: i['value'], COUPONS))
        duration = self.duration
        while duration > 0 and not not coupon_times:
            if duration >= coupon_times[-1]:
              coupon = list(filter(lambda i: i['value'] == coupon_times[-1], COUPONS))[0]
              self.add_coupon(coupon)
              duration -= coupon['value']
            else:
              coupon_times.pop()
        if not duration > 0: return True
        coupon = list(filter(lambda i: i['value'] == 30, COUPONS))[0]
        self.add_coupon(coupon)
        return True

    def add_coupon(self, coupon):
        response = self.s.post(PARK_HOST_URL + ADD_COUPON_URL, data={'discount_code': coupon['id'], 'car_no': self.k_car_num, 'clickCount': self.click_count})
        json_body = json.loads(response.content)
        self.order['discount_value'] = self.order['discount_value'] + json_body['dcValue']
        self.order['discount_name'].append(coupon['name'])
        self.order['discount_code'].append(coupon['id'])
        self.order['discount_desc'].append(json_body['dcDesc'])
        self.click_count += 1
        return True

    def set_duration(self):
        to = self.real_ti + datetime.timedelta(minutes = self.duration)
        if to.day == self.real_ti.day: return True
        self.duration -= to.hour * 60
        self.duration -= (to.minute / 30) * 30

    def get_park_code(self):
        get_park_req = self.s.post(PARK_HOST_URL + GET_PARK_CODE_URL, data={'car_no': self.k_car_num, 'car__totaldate': self.real_ti.strftime('%Y%m%d%H%M%S')})
        soup = BeautifulSoup(get_park_req.content, 'html.parser')
        self.park_code = soup.find(id='park_code').get('value')

    def submit_coupon(self):
        params = { 'group_name': '모바일 할인',
                 'department_name': '카카오',
                 'car_no': self.k_car_num,
                 'park_code': self.park_code,
                 'car_in_date': self.real_ti.strftime('%Y-%m-%d') + ' 00:00:00.0',
                 'car_in_time': self.real_ti.strftime('%H:%M'),
                 'car__totaldate': self.real_ti.strftime('%Y%m%d%H%M%S'),
                 'discount_name': ','.join(str(v) for v in self.order['discount_name']),
                 'discount_code': ','.join(str(v) for v in self.order['discount_code']),
                 'discount_value': self.order['discount_value'],
                 'discount_desc': ','.join(str(v) for v in self.order['discount_desc']) }
        self.s.post(PARK_HOST_URL + SUBMIT_COUPON_URL, data=params)

    def submit_coupon_success(self):
        response = self.s.post(PARK_HOST_URL + SEARCH_TICKET_URL)
        if not response.status_code == 200: return False
        soup = BeautifulSoup(response.content, 'html.parser')
        for tr in soup.select('table tbody tr'):
            tr = ','.join(str(v) for v in tr)
            if str(self.duration) in tr and self.k_car_num in tr: return True
        return False

    @staticmethod
    def area_id():
        return AREA_ID
