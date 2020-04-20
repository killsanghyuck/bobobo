#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime
from bot_interface import BotInterface

from importlib import reload



#봇 기본 정보
PARK_HOST_URL = 'http://116.124.66.81:8090/'
LOGIN_URL = '/account/login.asp'
SEARCH_CAR_NUMBER_URL = '/discount/discount_regist.asp'
ADD_ACTION_URL = '/discount/discount_regist.asp'
LIST_FIND = '/discount/discount_list.asp'
LOGIN_INFO = {
    'user_id': 'kakaot',
    'password': '1111'
}
AREA_ID = '12013'

class centerplaceBot(BotInterface):

    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.ticket_state = reservation['ticket_state']

        if self.ticket_state == 0:
            self.discount_id = 97
        else:
            self.discount_id = 97

        self.s = requests.Session()

    def login(self):
        try:
            login_req = self.s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            return True
        except requests.exceptions.ConnectionError:
            print('connection error')
            return False

    def find_car_number(self):
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'license_plate_number': self.k_car_num[-4:]})
        flag = False
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
                        car_num = tr_list[i].select('td')[1].text.split('[')[0].strip()
                        parking_time = tr_list[i].select('td')[3].text.strip()
                        entry_time = tr_list[i].select('td')[2].text.strip()
                        self.entry_time = datetime.datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S").strftime("%H")
                        if car_num == self.k_car_num and len(parking_time) == 5:
                            self.chk = tr_list[i].select('td')[0].select('input')[0]['value']
                            flag = True
                        elif car_num == self.k_car_num and parking_time > '20':
                            self.chk = tr_list[i].select('td')[0].select('input')[0]['value']
                            flag = True

                        if self.check_time(): flag = False
                        break
        return flag

    def check_time(self):
      flag = False
      entry_time = int(self.entry_time)
      if (entry_time < 18 and entry_time >= 7) and self.ticket_state == 1:
        print(u'이용가능시간 아님(이거 아래 입차확인 불가로 표시함)')
        flag = True

      return flag

    def process(self):
        flag = False
        def add_action(self):
            ADD_ACTION_PARAMS = {
                'show_car_img': '',
                'show_no_recong': '',
                'request_type_value': 'INSERTDISCOUNT',
                'post_discount_value': self.discount_id,
                'license_plate_number': self.k_car_num[-4:],
                'chk': self.chk
            }
            add_req = self.s.post(PARK_HOST_URL + ADD_ACTION_URL, data=ADD_ACTION_PARAMS)
            return True

        def list_find(self):
            return True

        if add_action(self) and list_find(self): flag = True
        return flag

    @staticmethod
    def area_id():
        return AREA_ID
