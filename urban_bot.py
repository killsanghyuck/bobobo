#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bot_interface import BotInterface

reload(sys)
sys.setdefaultencoding('utf-8')

#봇 기본 정보
PARK_HOST_URL = 'http://125.131.138.11'
AREA_ID = '11863'

CORP_NAME = '파킹스퀘어'
driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver')
driver.implicitly_wait(3)

class UrbanBot(BotInterface):

    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']

    def login(self):
        driver.get(PARK_HOST_URL)
        driver.find_element_by_name('login_id').send_keys('kakaot')
        driver.find_element_by_name('login_pw').send_keys('123456')
        driver.find_element_by_xpath("//*[text()='로그인']").click()
        try:
            driver.find_element_by_xpath("//*[text()='주차할인']")
            return True
        except:
            return False

    def find_car_number(self):
        flag = False
        driver.find_element_by_name('carNumber').send_keys(self.k_car_num[-4:])
        driver.find_element_by_xpath("//*[text()='검색']").click()
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        car_list = soup.select('table tbody tr')
        car = car_list[0]
        if len(car_list) >= 1:
            for car in car_list:
                if self.k_car_num == car.select('td')[1].text:
                    driver.find_element_by_xpath("//*[text()='" + self.k_car_num + "']").click()
                    flag = True
        return flag

    def process(self):
        flag = False
        if self.add_action() and self.list_find(): flag = True
        driver.quit();​
        return flag

    def add_action(self):
        driver.find_element_by_name('chk_info').click()
        return True

    def list_find(self):
        return True

    @staticmethod
    def area_id():
        return AREA_ID