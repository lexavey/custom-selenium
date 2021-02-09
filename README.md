# custom-selenium
Just my experience

class Test(object):
   def __init__(self, driver):
      self.driver = driver
      self.custom = CustomSelenium(driver)
      self.helper = CustomHelper(driver)
   def load(self):
     self.helper.go('https://google.com')
