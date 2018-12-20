#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
from bot_interface import BotInterface

reload(sys)
sys.setdefaultencoding('utf-8')

#봇 기본 정보
PARK_HOST_URL = 'http://125.131.138.11'
LOGIN_URL = '/index.php/login/doLogin'
SEARCH_CAR_NUMBER_URL = '/index.php/main/ajax_CarList'
ADD_ACTION_URL = '/index.php/main/ajax_DisIns'
LIST_FIND = '/discount/state/list/doListMst'
LOGIN_INFO = {
    'login_id': 'kakaot',
    'login_pw': '123456',
    'is_ajax': 1
}
AREA_ID = '11863'

class UrbanBot(BotInterface):

    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.discount_id = 920
        self.s = requests.Session()

    def login(self):
        try:
            login_req = self.s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            return True
        except requests.exceptions.ConnectionError:
            print 'connection error'
            return False

    def find_car_number(self):
        flag = False
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNumber': self.k_car_num[-4:], 'indate1': self.entry_date, 'indate2': self.entry_date, 'is_ajax': 1})
        soup = BeautifulSoup(find_req.content, 'html.parser')
        tr_list = soup.select('tr')
        if len(tr_list) >= 1:
            for tr in tr_list:
                if tr.select('td')[1].text == self.k_car_num:
                    self.serialno = tr.select('td a')[0]['href'].split('&')[3].split('=')[1]
                    flag = True
        return flag

    def process(self):
        flag = False
        if self.add_action() and self.list_find(): flag = True
        return flag

    def add_action(self):
        ADD_ACTION_PARAMS = {
            'InCarNo1': self.k_car_num,
            'chkedVal': self.discount_id,
            'SerialNo': self.serialno,
            'ParkNo': 1,
            'UnitNo': 1,
            'DCReason': '',
            'is_ajax': 1
        }
        add_req = self.s.post(PARK_HOST_URL + ADD_ACTION_URL, data=ADD_ACTION_PARAMS)
        return True

    def list_find(self):
        return True

    @staticmethod
    def area_id():
        return AREA_ID
