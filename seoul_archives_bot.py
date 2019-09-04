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



PARK_HOST_URL = 'http://211.218.0.250'
LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/registration/listForDiscount'
ADD_ACTION_URL = '/discount/registration/save'
LIST_FIND = '/discount/state/list/doListMst'
LOGIN_INFO = {
    'userId': u'kakaot',
    'userPwd': '123456',
    'referer': ''
}
AREA_ID = '12224'

class SeoularchiveshBot(BotInterface):
    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date'].replace("-","")
        self.duration = reservation['duration']
        self.discount_id = 5
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

        if  self.k_car_num in self.returned_car_no: flag = True
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
