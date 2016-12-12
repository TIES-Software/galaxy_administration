import anydbm
import os
import unittest
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class GalaxyMonitorLoad(unittest.TestCase):

  def __init__(self, testname):
    super(GalaxyMonitorLoad, self).__init__(testname)

  def setUp(self):
    self.driver = webdriver.Chrome(os.environ['CHROME_DRIVER_DIR'])
    #self.driver = webdriver.PhantomJS()
    self.GALAXY_USER = os.environ['GALAXY_USER']
    self.GALAXY_PASS = os.environ['GALAXY_PASS']
    self.GALAXY_URL = os.environ['GALAXY_URL']
    self.GALAXY_APP_DOMAIN = os.environ['GALAXY_APP_DOMAIN']

  def capture_current_stats(self):
    driver = self.driver
    wait = WebDriverWait(driver, 20)

    driver.get(self.GALAXY_URL)
    wait.until(EC.visibility_of_element_located((By.NAME, "username")))
    email_elem = driver.find_element_by_name("username")
    email_elem.send_keys(self.GALAXY_USER)

    password_elem = driver.find_element_by_name("password")
    password_elem.send_keys(self.GALAXY_PASS)

    login_submit_elem = driver.find_element_by_css_selector("form > button > span.rest")
    login_submit_elem.click()


    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".app-list a")))

    driver.get(self.GALAXY_URL + "app/" + self.GALAXY_APP_DOMAIN)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.cardinal-number.editable > div > input[type=number]")))

    #scrape the stats
    connections = driver.find_element_by_css_selector("#render-target > span > div > div.content-wrapper > span > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td.lower-column.primary > div > div:nth-child(2) > div:nth-child(1) > div > div.cardinal-number > span")
    cpu = driver.find_element_by_css_selector("#render-target > span > div > div.content-wrapper > span > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td.lower-column.primary > div > div:nth-child(2) > div:nth-child(2) > div > div.cardinal-number > span")
    memory = driver.find_element_by_css_selector("#render-target > span > div > div.content-wrapper > span > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td.lower-column.primary > div > div:nth-child(2) > div:nth-child(3) > div > div.cardinal-number > span.cardinal-numeral")
    containers = driver.find_element_by_css_selector("div.cardinal-number.editable > div > input[type=number]")

    #process the stats
    statsdb = anydbm.open('./galaxyStatsDB', 'c')
    try:
        now = time.strftime("%c")
        statsdb[now] = connections.text + ',' + cpu.text  + ',' + memory.text  + ',' + containers.get_attribute("value")
        for key in statsdb.keys():
            print key, statsdb[key]
    finally:
        statsdb.close()


  def tearDown(self):
    self.driver.quit()

if __name__ == "__main__":
  suite = unittest.TestSuite()
  suite.addTest(GalaxyMonitorLoad("capture_current_stats"))

unittest.TextTestRunner().run(suite)
