#-*- coding: utf-8 -*-

from bot_interface import BotInterface
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
import time
import datetime

#bot_list

# 다래
from alpha_bot1 import AlphaBot1
from alpha_bot2 import AlphaBot2
from city_plz_bot import CityPlzBot
from dsme_bot import DsmeBot
from han_no_bot import HanNoBot
from hsbc_bot import HsbcBot
from l7_hong_bot import L7HongBot
from namsan_bot import NamsanBot
from river_tower_bot import RiverTowerBot
from wealtz_bot import WealtzBot
from signature_bot import SignatureBot
from seosomoon_bot import SeoSoMoonBot
from ddmc_bot import DdmcBot
from sahakbusan_bot import SahakBusanBot
from jongro_sc_bot import JongroScBot
from dongil_tower_bot import DongilTowerBot
from camko_yangjae_bot import CamkoYangjaeBot
from jail_op_bot import JailOpBot
from jump_bot import JumpBot
from yzpark_bot import YzparkBot
from mallofk_bot import MallOfKBot
from fast_five_bot import FastFive

#aj
from balsan_park_bot import BalsanParkBot
from gmg_bot import GmgBot

#아마노
from ace_tower_bot import AceTowerBot
from lotte_cityhotel_mapo_bot import LotteCityHotelMapoBot
from podo_mall_bot import PodoMallBot
from sfc_bot import SFCBot
from t_tower_bot import TtowerBot
from noble_bot import NobleBot
from the_k_bot import TheKBot

#넥스파
from gran_seoul import GranSeoulBot
from urban_bot import UrbanBot

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome('/Users/blain1/Documents/chromedriver', options=options)
driver.implicitly_wait(3)

#카카오 어드민 계정
KAKAO_ID = 'san.kill'
KAKAO_PW = '!@dl926516'

HOST_URL = 'https://parking.kakao.com/admin'

all_jobs = []
TODAY = datetime.datetime.today().strftime("%Y-%m-%d")

def admin_login():
    driver.get(HOST_URL + '/login')
    driver.find_element_by_name('manager[login]').send_keys(KAKAO_ID)
    driver.find_element_by_name('manager[password]').send_keys(KAKAO_PW)
    driver.find_element_by_name('commit').click()

def reservation_bot():
    pick_list = []
    for i in range(1, 6):
        driver.get(HOST_URL + '/picks?q[state_eq]=4&page=' + str(i) + '&order=id_desc')
        html = driver.page_source
        if u'로드스터 관리자' in html:
            admin_login()
            return
        soup = BeautifulSoup(html, 'html.parser')
        pick_list += soup.select('table#index_table_picks > tbody > tr > td.col-id')
    if len(pick_list) >= 1:
        for pick in pick_list:
            driver.get(HOST_URL + '/picks/' + pick.text)
            html = driver.page_source
            if u'로드스터 관리자' in html:
                admin_login()
                return
            soup = BeautifulSoup(html, 'html.parser')
            car_number = soup.select('table > tbody > tr.row-license_number > td')
            area_id = soup.select('table > tbody > tr.row-parking_lot > td > a')[0]['href'].split('/')[3]
            k_car_num = car_number[0].encode_contents().strip().replace(' ', '').split("<br/>")[0]
            ti = soup.select('table > tbody > tr.row-created_at > td')[1].text
            ti = datetime.datetime.strptime(str(ti), "%Y/%m/%d %H:%M:%S")
            duration = soup.select('table > tbody > tr.row-ticket_item_code > td')[0].text
            if duration == '종일권':
                duration = 1440
            else:
                duration = int(duration[:-3]) * 60
            for cls in globals()['BotInterface'].__subclasses__():
                if cls.area_id() == area_id:
                    reservation = { 'k_car_num' : k_car_num, 'entry_date' : TODAY, 'ti' : ti, 'duration' : duration}
                    bot = cls(reservation)
                    if bot.login():
                        if bot.find_car_number():
                            if bot.process():
                                try:
                                    driver.get(HOST_URL + '/picks/' + pick.text)
                                    html = driver.page_source
                                    if u'로드스터 관리자' in html:
                                        admin_login()
                                        return
                                    driver.find_element_by_id('select2-pick_state-container').click()
                                except:
                                    return
                                driver.find_element_by_xpath("//li[@aria-selected='false']").click()
                                driver.find_element_by_name('commit').click()
                                print(pick.text + ' : ' + '차량등록 완료 : ' + reservation['k_car_num'])
                            else:
                                print(pick.text + ' : ' + '차량등록 실패 : ' + reservation['k_car_num'])
                        else:
                            print(pick.text + ' : ' + '입차확인불가 : ' + reservation['k_car_num'])
                    else:
                        print('로그인실패 : ' + pick.text)

admin_login()
while True:
    driver.get(HOST_URL)
    html = driver.page_source
    if u'로드스터 관리자' in html:
        admin_login()
    reservation_bot()
    time.sleep(300)
