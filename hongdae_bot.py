#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime
import json

from bot_interface import BotInterface

from importlib import reload



PARK_HOST_URL = 'http://hdpark7.awp.co.kr'
LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/registration/listForDiscount'
ADD_ACTION_URL = '/discount/registration/save'
LIST_FIND = '/discount/state/list/doListMst'
LOGIN_INFO = {
    'referer': '',
    'userId': 'kakaot',
    'userPwd': '123456'
}
AREA_ID = '12234'

class HongDaeBot(BotInterface):
    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.duration = reservation['duration']
        self.ticket_state = reservation['ticket_state']

        if self.ticket_state == 0:
            if self.duration == 1440:
                self.discount_id = 17
            elif self.duration == 240:
                self.discount_id = 18
            elif self.duration == 480:
                self.discount_id = 19
        else:
            if self.duration == 1440:
                self.discount_id = 16

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
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNo': self.k_car_num[-4:], 'entryDate': self.entry_date})
        data = json.loads(find_req.content)
        self.returned_car_no = ''
        self.entry_time = '19'
        if len(data) >= 1:
            for car in data:
                if self.k_car_num in car['carNo']:
                    self.id = car['id']
                    self.i_lot_area = car['iLotArea']
                    self.returned_car_no = car['carNo']
                    self.entry_time = datetime.datetime.strptime(car['entryDateToString'], "%Y-%m-%d %H:%M:%S").strftime("%H")
                    flag = True
                    if self.check_time(): flag = False

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
                'peId': self.id,
                'discountType': self.discount_id,
                'carno': self.k_car_num,
                'memo': ''
            }
            add_req = self.s.post(PARK_HOST_URL + ADD_ACTION_URL, data=ADD_ACTION_PARAMS)
            return True

        def list_find(k_car_num):
            flag = True
            # LIST_FIND_PARAMS = {
            #     'startDate': self.entry_date,
            #     'endDate': self.entry_date,
            #     'account_no': 'parkhere81',
            #     'carno': self.k_car_num,
            #     'iLotArea': 81
            # }
            # list_req = self.s.post(PARK_HOST_URL + LIST_FIND, data=LIST_FIND_PARAMS)
            # results = json.loads(list_req.content)
            # results = results['data']
            # if results[0]['carno'] == self.k_car_num: flag = True
            return flag

        if add_action(self) and list_find(self): flag = True
        return flag

    @staticmethod
    def area_id():
        return AREA_ID
