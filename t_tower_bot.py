#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime
import json

from bot_interface import BotInterface

reload(sys)
sys.setdefaultencoding('utf-8')

PARK_HOST_URL = 'http://121.128.222.164'
LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/registration/listForDiscount'
ADD_ACTION_URL = '/discount/registration/save'
LIST_FIND = '/state/list'
LOGIN_INFO = {
    'userId': 'parkhere',
    'userPwd': '1234'
}
AREA_ID = '9953'

CORP_NAME = '파킹스퀘어'

class TtowerBot(BotInterface):
    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.duration = reservation['duration']
        self.discount_id = 3
        self.s = requests.Session()

    def login(self):
        login_req = self.s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
        if login_req.status_code == 200:
            return True

    def find_car_number(self):
        flag = False
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNo': self.k_car_num, 'entryDate': self.entry_date})
        if find_req.content[0] == '/r':
            print 'json이 아님'
            return False
        data = json.loads(find_req.content)
        self.returned_car_no = ''
        if len(data) >= 1:
            self.id = data[0]['id']
            self.i_lot_area = data[0]['iLotArea']
            self.returned_car_no = data[0]['carNo']

        if self.returned_car_no == self.k_car_num: flag = True
        return flag

    def process(self):
        flag = False
        def add_action(self):
            ADD_ACTION_PARAMS = {
                'peId': self.id,
                'corp': CORP_NAME,
                'discountType': self.discount_id,
                'carno': self.k_car_num,
                'iLotArea': self.i_lot_area,
                'memo': ''
            }
            add_req = self.s.post(PARK_HOST_URL + ADD_ACTION_URL, data=ADD_ACTION_PARAMS)
            return True

        def list_find(k_car_num):
            flag = False
            LIST_FIND_PARAMS = {
                'startDate': self.entry_date,
                'startTime': '00:00',
                'endDate': self.entry_date,
                'endTime': '23:59',
                'searchField': 'carNo',
                'searchText': self.k_car_num
            }
            list_req = self.s.post(PARK_HOST_URL + LIST_FIND, data=LIST_FIND_PARAMS)
            results = json.loads(list_req.content)
            results = results['data']
            if results[0]['carno'] == self.k_car_num: flag = True
            return flag

        if add_action(self) and list_find(self): flag = True
        return flag

    @staticmethod
    def area_id():
        return AREA_ID
