#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bot_interface import BotInterface

from importlib import reload



#봇 기본 정보
PARK_HOST_URL = 'http://1.230.226.2'

AREA_ID = '10558'
driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver')
driver.implicitly_wait(3)

class GvalleyBot(BotInterface):

    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']

    def login(self):
        driver.get(PARK_HOST_URL)
        driver.find_element_by_name('user_email').send_keys(u'파크히어')
        driver.find_element_by_id('password').send_keys('parkhere')
        driver.find_element_by_class_name('button1').click()
        try:
            driver.find_element_by_xpath("//*[text()='등록']")
            return True
        except:
            return False

    def find_car_number(self):
        flag = False

        driver.find_element_by_name('search_car_id').send_keys(self.k_car_num[-4:])
        driver.find_element_by_xpath("//*[text()='검색']").click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        car_list = soup.select('table tbody tr')

        if len(car_list) >= 2:
            for car in car_list:
                if self.k_car_num == car.select('td')[1].text:
                    driver.find_element_by_xpath("//input[@value='"+car.select('td')[0].select('input')[0]['value']+"']").click()
                    flag = True
        return flag

    def process(self):
        flag = False
        if self.add_action() and self.list_find(): flag = True
        driver.quit();​
        return flag

    def add_action(self):
        driver.find_element_by_id('button_discount_4').click()

        return True

    def list_find(self):
        return True

    @staticmethod
    def area_id():
        return AREA_ID
