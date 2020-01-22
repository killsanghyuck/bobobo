#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
from bot_interface import BotInterface

from importlib import reload



#봇 기본 정보
PARK_HOST_URL = 'http://djajwe.ajpark.kr/'
LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/carSearch.cs?userID=kakaot&contextPath='
LIST_FIND = '/report/reportList.cs'
LOGIN_INFO = {
    'j_username': 'kakaot',
    'j_password': '123456'
}
AREA_ID = '16020'

class WooribuildingBot(BotInterface):

    def __init__(self, reservation):
        #k_car_num = u''
        #entry_date = u'2018-11-13'
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.duration = reservation['duration']
        self.ticket_state = reservation['ticket_state']

        if self.ticket_state == 0:
            if self.duration == 1440:
                self.discount_id = u'dCode=00013'
            elif self.duration == 720:
                self.discount_id = u'dCode=00013'
        else:
            if self.duration == 1440:
                self.discount_id = u'dCode=00012'
        self.pKey = ''
        self.s = requests.Session()

    def login(self):
        try:
            #s = requests.Session()
            #login_req = s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            login_req = self.s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            return True
        except requests.exceptions.ConnectionError:
            print('connection error')
            return False

    def find_car_number(self):
        #find_req = s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNumber': k_car_num[-4:], 'from': entry_date, 'fromHH': '00' })
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNumber': self.k_car_num[-4:], 'from': self.entry_date, 'fromHH': '00' })
        flag = False
        if find_req.history == []:
            soup = BeautifulSoup(find_req.content, 'html.parser')
            tr_list = soup.select('table')[1].select('tr')
            for tr in tr_list:
                if self.k_car_num in tr.text:
                    self.pKey = tr['onclick'].split('?')[1][:-1]
                    flag = True
        elif find_req.history[0].status_code == 302:
            soup = BeautifulSoup(find_req.content, 'html.parser')
            car_find = soup.select('table')[1].select('tr')[2].select('td')[1].text
            self.pKey = find_req.url.split('?')[1].split('&')[0]
            if self.k_car_num in car_find:
              flag = True
        return flag

    def process(self):
        flag = False
        if self.add_action(): 
            flag = True
        return flag

    def add_action(self):
        flag = False
        #add_req = s.get(PARK_HOST_URL + '/discount/discountApplyProc.cs?' + pKey + '&' + discount_id + '&dKind=%EB%A7%A4%EC%88%98%EC%B0%A8%EA%B0%90&fDays=&remark=')
        add_req = self.s.get(PARK_HOST_URL + '/discount/discountApplyProc.cs?' + self.pKey + '&' + self.discount_id + '&dKind=%EB%A7%A4%EC%88%98%EC%B0%A8%EA%B0%90&fDays=&remark=')        
        flag = True
        return flag

    def list_find(self):
        LIST_FIND_PARAMS = {
            'from': self.entry_date,
            'fromHH': '00',
            'fromMM': '00',
            'to': self.entry_date,
            'toHH': '23',
            'toMM': '59',
            'dType': u'할인승인',
            'dCriterion': u'입차기준',
            'remark': ''
        }
        flag = False
        response = self.s.post(PARK_HOST_URL + LIST_FIND, data=LIST_FIND_PARAMS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            if self.k_car_num in soup.text:
                flag = True
        return flag


    @staticmethod
    def area_id():
        return AREA_ID