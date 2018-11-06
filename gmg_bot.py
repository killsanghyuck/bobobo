#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
from bot_interface import BotInterface

reload(sys)
sys.setdefaultencoding('utf-8')

#봇 기본 정보
PARK_HOST_URL = 'http://ajgmg.ajpark.kr'
LOGIN_URL = '/login'
SEARCH_CAR_NUMBER_URL = '/discount/carSearch.cs?userID=kakaot&contextPath='
LIST_FIND = '/report/reportList.cs'
LOGIN_INFO = {
    'j_username': 'kakaot',
    'j_password': '123456'
}
AREA_ID = '11963'

class GmgBot(BotInterface):

    def __init__(self, reservation):
        #k_car_num = u''
        #entry_date = u'2018-11-06'
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.discount_id = u'dCode=00009'
        self.pKey = ''
        self.s = requests.Session()

    def login(self):
        try:
            #s = requests.Session()
            #login_req = s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            login_req = self.s.post(PARK_HOST_URL + LOGIN_URL, data=LOGIN_INFO)
            return True
        except requests.exceptions.ConnectionError:
            print 'connection error'
            return False

    def find_car_number(self):
        #find_req = s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNumber': k_car_num[-4:], 'from': entry_date, 'fromHH': '00' })
        find_req = self.s.post(PARK_HOST_URL + SEARCH_CAR_NUMBER_URL, data={'carNumber': self.k_car_num[-4:], 'from': self.entry_date, 'fromHH': '00' })
        flag = False
        if find_req.history[0].status_code == 302:
            soup = BeautifulSoup(find_req.content, 'html.parser')
            car_find = soup.select('table')[1].select('tr')[2].select('td')[1].text
            self.pKey = find_req.url.split('?')[1].split('&')[0]
            if self.k_car_num in car_find:
              flag = True            
        else:

        return flag

    def process(self):
        flag = False
        if self.add_action() and self.list_find(): flag = True
        return flag

    def add_action(self):
        #add_req = s.get(PARK_HOST_URL + '/discount/discountApplyProc.cs?' + pKey + '&' + discount_id + '&dKind=%EB%A7%A4%EC%88%98%EC%B0%A8%EA%B0%90&fDays=&remark=')
        add_req = self.s.get(PARK_HOST_URL + '/discount/discountApplyProc.cs?' + self.pKey + '&' + self.discount_id + '&dKind=%EB%A7%A4%EC%88%98%EC%B0%A8%EA%B0%90&fDays=&remark=')
        if add_req.history[0].status_code == 302:
          return True
        return False

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
        response = s.post(PARK_HOST_URL + LIST_FIND, data=LIST_FIND_PARAMS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            if self.k_car_num in soup.text:              
              return True
        return False


    @staticmethod
    def area_id():
        return AREA_ID
