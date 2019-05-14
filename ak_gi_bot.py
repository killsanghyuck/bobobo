#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
from bot_interface import BotInterface
import json

from importlib import reload



#봇 기본 정보
PARK_HOST_URL = 'https://exapi.myvaletbiz.com/corp/v1/kakaot_webdiscount'
AREA_ID = '12153'

class AKGiBot(BotInterface):

    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']
        self.duration = reservation['duration']
        self.s = requests.Session()

    def login(self):
        return True

    def find_car_number(self):
        flag = False
        ADD_ACTION_PARAMS = {
        	"parkinglot_id" : "Tr-CURvSQn7FBmYhB4dN4w",
        	"car_full" : self.k_car_num,
        	"discounttime_inminute" : self.duration
        }
        headers = {
            'x-api-key': 'ljG1LfZJCt6bak1PFYxS8YnVmQWG6F555yUEnY0c'
        }
        add_req = self.s.post(PARK_HOST_URL, headers=headers, json=ADD_ACTION_PARAMS)
        add_req = json.loads(add_req.content)['message']
        if add_req == u'성공했습니다.':
            flag = True
        elif add_req == u'차량이 없습니다':
            flag = False

        return flag

    def process(self):
        return True

    @staticmethod
    def area_id():
        return AREA_ID
