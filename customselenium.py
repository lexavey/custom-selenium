class CustomSelenium(object):
    """docstring for xxx"""
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.init = config['init']

    def debug(self,text):
        if self.config['init']['debug']:
            print(text)

    def go(self,url):
        d={}
        if self.driver.current_url != url:
            self.debug('debug : load a url : '+url)
            self.driver.get(url)
        d['status'] = True
        return d

    def xpath_exist(self,xpath,driver=None):
        d={}
        d['input']={} # add dict inputted parameters
        d['response']={}
        d['comment']=[] # append object executing comment for debug
        d['status']=False # bool function return
        d['function']=inspect.currentframe().f_code.co_name # current function name

        d['input']['xpath'] = xpath

        if not driver:
            driver=self.driver
        if isinstance(xpath,dict):
            d['comment'].append('input is xpath')
            for k,v in xpath.items():
                out=self.xpath_exist(v)
                if out['status']:
                    d['comment'].append('key [ '+k+' ]')
                    d['comment'].append('xpath [ '+v+' ]')
                    d['status']=True
                    break
            return d
        try:
            out=driver.find_element(By.XPATH, xpath)
            d['response']['element']=out
            d['status']=True
        except NoSuchElementException:
            d['status']=False
        return d

    def xpath_input(self,xpath,value,driver=None):
        d={}
        d['input']={} # add dict inputted parameters
        d['response']={}
        d['comment']=[] # append object executing comment for debug
        d['status']=False # bool function return
        d['function']=inspect.currentframe().f_code.co_name # current function name
        
        d['input']['xpath'] = xpath
        d['input']['value'] = value

        if not driver:
            driver=self.driver
        
        check=self.xpath_exist(xpath)
        if not check['status']:
            d['comment'].append('element not found')
            return d
        elem = check['response']['element']
        if self.init['input']['delay']:
            d['comment'].append('random delay on')
            d['comment'].append('min '+str(self.init['input']['min']))
            d['comment'].append('max '+str(self.init['input']['max']))
            for s in value:
                elem.send_keys(s)
                time.sleep(random.uniform(self.init['input']['min'],self.init['input']['max']))
        else:
            elem.send_keys(value)
        if elem.get_attribute('value') == value:
            d['status']=True
        print(d)
        return d

    def click(self,xpath,driver=None):
        d={}
        d['input']={} # add dict inputted parameters
        d['response']={}
        d['comment']=[] # append object executing comment for debug
        d['status']=False # bool function return
        d['function']=inspect.currentframe().f_code.co_name # current function name
        
        d['input']['xpath'] = xpath

        if not driver:
            driver=self.driver
        
        check=self.xpath_exist(xpath)
        if not check['status']:
            d['comment'].append('element not found')
            return d
        elem = check['response']['element']
        
        if self.init['click']['delay']:
            d['comment'].append('random delay on')
            d['comment'].append('min '+str(self.init['input']['min']))
            d['comment'].append('max '+str(self.init['input']['max']))
        d['comment'].append('try click')
        try:
            driver.execute_script("arguments[0].click()",elem)
            d['status']=True
        except StaleElementReferenceException:
            d['comment'].append('element not ready')
        return d['status']
    
    def force(self, f, *args, succ=[], err=[], skip_blank=True):
        d={}
        d['input']={} # add dict inputted parameters
        d['response']={}
        d['comment']=[] # append object executing comment for debug
        d['status']=False # bool function return
        d['function']=inspect.currentframe().f_code.co_name # current function name

        start = time.time()
        c_retry = 0

        d['input']['f']=f
        d['input']['args']=[*args,]
        d['input']['succ']=succ
        d['input']['err']=err
        d['input']['succ']=succ

        # self.debug('===================================================')
        # self.debug('debug : force start '+str(f))
        # self.debug('debug : force args list ')
        # print(*args)
        # self.debug('debug : force succ list '+str(succ))
        # self.debug('debug : force err list '+str(err))
        self.debug('====================================================================')
        while True:
            self.debug('debug : force in while loops')
            try:
                c = f(*args)
            except ElementNotInteractableException:
                continue
            time.sleep(self.init['while']['delay'])
            end = time.time()
            elapsed = end - start
            if succ:
                self.debug('debug : force succ check is on')
                chk = self.xpath_exist(succ)
                if chk['status']:
                    self.debug('debug : force succ check found success')
                    d['status']=True
                    break
            if err:
                self.debug('debug : force error check is on')
                chk = self.xpath_exist(err)
                if chk['status']:
                    self.debug('debug : force error check found error')
                    # if skip_blank:
                    #     if chk.text == '':
                    #         continue;
                    # return False
                    break
            if not succ and not err:
                self.debug('debug : force function return True')
                d['status']=True
                break
            
            if elapsed > self.init['while']['timeout']:
                self.debug('debug : force timeout')
                break
            c_retry +=1
            if c_retry > self.init['while']['retry']:
                self.debug('debug : force max retry')
                break
        self.debug('debug : force return end False')
        return d
