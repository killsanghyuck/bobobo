#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime

AREA_ID = { u'국내선 제2주차장': 1583345,
             u'국제선주차장': 1582294,
             u'화물청사 주차장': 1583346 ,
             u'국내선 제1주차장': 1583344 }

def gimpo_api():
    seoul_url = 'http://parking.seoul.go.kr/WCFB/ParklandWRT.svc/ParkStatPost'
    gimpo_url = 'http://openapi.airport.co.kr/service/rest/gmpParkingLiveService/getParkingLive?serviceKey=FXX%2Bq5gKaq7ViqUtWQfxTroVz4muyqvFIpIfgAIzL1w36ANMS7i9qt330pFvtli1L1sJrTUxOQDTNsYd8%2FyMEA%3D%3D'
    res = requests.get(gimpo_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    area_list = soup.select('item')
    for k, v in enumerate(area_list):
        data = {'key':'DQIVRNSV4P',
                'infra_id':AREA_ID[v.select('parkingairportcodename')[0].text],
                'current_parking':v.select('parkingistay')[0].text }        
        try:
            response = requests.post(seoul_url, data=data )
            print response.content + " : " + datetime.datetime.today().strftime("%m-%d %H:%M")
        except requests.exceptions.ConnectionError:
            print 'connection error'
while True:
    gimpo_api()
    time.sleep(200)
