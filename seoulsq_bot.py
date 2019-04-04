#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bot_interface import BotInterface

from importlib import reload



#봇 기본 정보
PARK_HOST_URL = 'http://seoulsquare.iptime.org:8080/'

AREA_ID = '10508'
driver = webdriver.Chrome('/Users/gilsanghyeog/Documents/chromedriver')
driver.implicitly_wait(3)

class SeoulsqBot(BotInterface):

    def __init__(self, reservation):
        self.k_car_num = reservation['k_car_num']
        self.entry_date = reservation['entry_date']

    def login(self):
        driver.get(PARK_HOST_URL + '/Default.aspx')
        driver.find_element_by_name('TextBox_ID').send_keys('D0082')
        driver.find_element_by_name('TextBox_Pwd').send_keys('1')
        driver.find_element_by_name('Button_Login').click()
        try:
            driver.find_element_by_xpath("//*[text()='차번검색']")
            return True
        except:
            return False

    def find_car_number(self):
        flag = False

        driver.find_element_by_name('TextBox_CarNum').send_keys(self.k_car_num[-4:])
        driver.find_element_by_id('Button_Search').click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        car_list = soup.select('table')[4].select('tbody tr td table tbody tr')

        if len(car_list) >= 2:
            for car in car_list:
                if self.k_car_num == car.select('td')[0].text:
                    driver.find_element_by_xpath('//a[@href="'+car.select('td')[2].select('a')[0]['href']+'"]').click()
                    flag = True
        return flag

    def process(self):
        flag = False
        if self.add_action() and self.list_find(): flag = True
        driver.quit();
        return flag

    def add_action(self):
        driver.find_element_by_id('Button_Discount').click()

        return True

    def list_find(self):
        return True

    @staticmethod
    def area_id():
        return AREA_ID
