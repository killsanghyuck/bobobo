#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime
import json
from urllib import parse

from bot_interface import BotInterface

from importlib import reload



PARK_HOST_URL = 'http://119.196.121.60'
LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/registration/listForDiscount'
ADD_ACTION_URL = '/discount/registration/save'
LIST_FIND = '/discount/state/list/doListMst'
LOGIN_INFO = {
    'userId': 'kakao5',
    'userPwd': '!234567890',
    'referer': ''
}
AREA_ID = '1454'

class ypBot(BotInterface):
    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date'].replace("-","")
        self.duration = reservation['duration']
        self.ticket_state = reservation['ticket_state']

        if self.ticket_state == 0:
            self.discount_id = 7
        else:
            self.discount_id = 6
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
        # find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNo': self.k_car_num, 'entryDate': self.entry_date})
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL + "?carNo=" + parse.quote(self.k_car_num) + '&entryDate=' + self.entry_date)
        data = json.loads(find_req.content)
        self.returned_car_no = ''
        if len(data) >= 1:
            self.id = data[0]['id']
            self.i_lot_area = data[0]['iLotArea']
            self.returned_car_no = data[0]['carNo']
            self.entry_time = datetime.datetime.strptime(data[0]['entryDateToString'], "%Y-%m-%d %H:%M:%S").strftime("%H")
            if  self.k_car_num in self.returned_car_no: flag = True
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
                'acPlate2': '',
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
