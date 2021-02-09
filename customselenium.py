from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidCookieDomainException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException # not clickable mouse
from selenium.webdriver.common.action_chains import ActionChains # hovermous
from colorama import init
from termcolor import colored
import pyotp
import random
import time
import datetime
import json # go fuck urself if you dont know
import inspect # get current func name
import re # regex module
import calendar # chat unread module
from datetime import date # chat unread module
from dateutil.relativedelta import relativedelta # chat unread module
from pprint import pprint # debug
from configparser import ConfigParser # read ini file

import pickle # cookies module
from pathlib import Path # create dir

"""

Versi : 1.1 beta

"""
class CustomHelper(object):

    def __init__(self, driver):
        self.driver = driver

    def debug(self,text):
        print('DEBUG : '+str(text))

    def go(self,url):
        driver = self.driver
        if driver.current_url != url:
            self.debug('load a url : '+url)
            driver.get(url)
        return True

    def cookies_save(self,name):
        self.debug('save current cookies')
        Path("cookies").mkdir(parents=True, exist_ok=True)
        pickle.dump( self.driver.get_cookies() , open("cookies/"+name+".pkl","wb"))

    def cookies_load(self,name):
        try:
            file=Path("cookies/"+name+".pkl")
            if not file.is_file():
                return False
            self.debug('load saved cookies')
            self.driver.get('https://google.com')
            # tambah validasi url sudah ada atau belum
            cookies = pickle.load(open("cookies/"+name+".pkl", "rb"))
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except InvalidCookieDomainException:
                    self.debug('critical : invalid cookie domain')
                    return False
            return True
        except FileNotFoundError:
            return False

class CustomSelenium(object):
    """docstring for CustomSelenium"""
    def __init__(self, driver, config=None):
        self.driver = driver
        if not config:
            self.config = {
                "timeout" : 10,
                "debug" : True,
                "delay" : 0.009,
                "while":{
                    "timeout" : 10,
                    "delay" : 0.009,
                    "retry" : 50
                }
            }
        else:
            self.config = config

    def debug(self,text):
        if self.config['debug']:
            print('DEBUG : '+str(text))

    def xpath_exist(self,xpath):
        output={}
        output['input']={} # add dictionary inputted parameters
        output['response']={}
        output['comment']=[] # append object executing comment for debug
        output['status']=False # bool function return
        
        output['function']=inspect.currentframe().f_code.co_name # current function name
        output['input']['xpath'] = xpath

        driver=self.driver
        if isinstance(xpath,dict):
            output['comment'].append('input is xpath')
            for k,v in xpath.items():
                out=self.xpath_exist(v)
                output['response'][k]=out
                if out['status']:
                    return out
            return output
        try:
            out=driver.find_element(By.XPATH, xpath)
            output['response']['element']=out
            try:
                output['response']['text']=out.text
            except StaleElementReferenceException:
                output['comment'].append('exception StaleElementReferenceException')
                output['response']['text']=''
            output['status']=True
        except NoSuchElementException:
            output['comment'].append('element not found')
        return output

    def input(self,xpath,value):
        output={}
        output['input']={} # add dict inputted parameters
        output['response']={}
        output['comment']=[] # append object executing comment for debug
        output['status']=False # bool function return
        output['function']=inspect.currentframe().f_code.co_name # current function name
        
        output['input']['xpath'] = xpath
        output['input']['value'] = value

        driver=self.driver
        check=self.xpath_exist(xpath)
        if not check['status']:
            output['comment'].append('element not found')
            return output
        elem = check['response']['element']
        elem.send_keys(value)
        if elem.get_attribute('value') == value:
            output['status']=True
        return output

    def click(self,xpath,mouse=False):
        output={}
        output['input']={} # add dict inputted parameters
        output['response']={}
        output['comment']=[] # append object executing comment for debug
        output['status']=False # bool function return
        output['function']=inspect.currentframe().f_code.co_name # current function name
        
        output['input']['xpath'] = xpath

        driver=self.driver
        check=self.xpath_exist(xpath)
        if not check['status']:
            output['comment'].append('element not found')
            return output
        elem = check['response']['element']
        output['comment'].append('try click')
        try:
            if mouse:
                output['comment'].append('try move mouse')
                action = webdriver.ActionChains(driver)
                action.move_to_element(elem)
                action.perform()
                elem.click()
            else:
                driver.execute_script("arguments[0].click()",elem)
            output['status']=True
        except StaleElementReferenceException:
            output['comment'].append('element not ready')
        except ElementClickInterceptedException:
            output['comment'].append('element not clickable')
        return output
    
    def execute(self, func=None, *args, success=[], error=[], **kwargs):
        if func:
            func_name=func.__name__
        else:
            func_name=None
        output={}
        output['input']={} # add dict inputted parameters
        output['response']={} # each func response
        output['comment']=[] # append object executing comment for debug
        output['status']=False # bool function return
        output['function']=inspect.currentframe().f_code.co_name # current function name

        start = time.time()
        c_retry = 0

        output['input']['func']=func_name
        output['input']['args']=[*args,]
        output['input']['kwargs']=kwargs
        output['input']['success']=success
        output['input']['error']=error

        self.debug('start execute')
        
        while True:
            
            c_retry +=1
            str_retry = str(c_retry)
            time.sleep(self.config['while']['delay'])
            end = time.time()
            elapsed = end - start
            
            if elapsed > self.config['while']['timeout']:
                self.debug('execute while max timeout')
                break
            
            if c_retry > self.config['while']['retry']:
                self.debug('execute while max retry')
                break

            self.debug('debug : force in while loops')
            
            if func:
                arg = ', '.join('\'{0}\''.format(w) for w in args)
                kwarg = ', '.join('{}={}'.format(key, value) for key, value in kwargs.items())
                output['comment'].append('execute run '+func_name+'('+arg+kwarg+')')
                
                run = func(*args,**kwargs)
                print('execute run '+func_name+'('+arg+kwarg+')')
                output['response'][str_retry]={}
                output['response'][str_retry][func_name]=run

            if success:
                self.debug('execute success check is on')
                check = self.xpath_exist(success)
                if check['status']:
                    output['response']['xpath_exist']=check
                    self.debug('execute success check is true')
                    output['status']=True
                    break

            if error:
                self.debug('execute error check is on')
                check = self.xpath_exist(error)
                if check['status']:
                    output['response']['xpath_exist']=check
                    self.debug('execute error check is true')
                    if chk['response']['text'] == '':
                        continue;
                    break

            if not success and not error:
                self.debug('execute has no validation')
                if func:
                    output['status']=run['status']
                else:
                    output['status']=True
                break

        self.debug('end execute')
        print(json.dumps(output,sort_keys=True, indent=4,default=lambda o: '<not serializable>'))
        return output
