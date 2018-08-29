#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime

def agit():
    url = 'https://agit.in/webhook/60798dfd-9dd7-4246-9969-7728a7bf5a69'
    try:
        res = requests.post(url, {'text':'주간업무 주세요 @group'})
        print res.content
    except requests.exceptions.ConnectionError:
        print '........fff'

agit()
