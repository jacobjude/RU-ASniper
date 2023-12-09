import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import config

NETID = config.NETID
PASSWORD = config.PASSWORD
SEMESTER_SELECTION = config.QUERY_PARAMS_WEBREG["semesterSelection"]
SEMESTER_SELECTION_URL = f"https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection={SEMESTER_SELECTION}&indexList="

class Browser:
   def __init__(self, show_browser=True, log_level=3, netid=NETID, password=PASSWORD):
        self.netid = netid
        self.password = password
        self.chrome_options = Options()
        if not show_browser:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument(f"--log-level={log_level}")
        self.driver = None
        self.refreshing = False
        self.upkeeping = False
        self.registering = False

   def open_browser(self):
       self.driver = webdriver.Chrome(options=self.chrome_options)
       return self.driver

   def visit_url(self, url=SEMESTER_SELECTION_URL):
       self.driver.get(url)
       
   def open_webreg(self):
       self.open_browser()
       self.visit_url(f"https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection={SEMESTER_SELECTION}&indexList=")
       
   def is_on_login_page(self):
       return "cas.rutgers.edu/login?" in self.driver.current_url
   
   def is_waiting_for_duo(self):
       return "duosecurity" in self.driver.current_url
   
   def handle_duo(self):
       continue_button = None
       retry_button = None
       
       while self.is_waiting_for_duo():
           try:
               continue_button = self.driver.find_element(By.ID, "trust-browser-button")
               break
           except NoSuchElementException:
               pass
           
           try:
               retry_button = self.driver.find_element(By.XPATH, '//button[normalize-space()="Try again"]')
               break
           except NoSuchElementException:
               pass
           
       if continue_button:
           continue_button.click()
       elif retry_button:
           retry_button.click()
           self.handle_duo()
           
   def handle_login(self):
       netid_box = self.driver.find_element(By.NAME, "username")
       password_box = self.driver.find_element(By.NAME, "password")
       netid_box.send_keys(self.netid)
       password_box.send_keys(self.password)
       login_button = self.driver.find_element(By.NAME, "submit")
       login_button.click()
       
       if self.is_waiting_for_duo():
           print("\nPlease accept the Duo push notification on your phone.")
           self.handle_duo()
           
   def is_on_registration_page(self):
       try:
           self.driver.find_element(By.ID, "i1") # if this element exists, then we are on the registration page
           return True
       except:
           return False
       
   def refresh_page(self, url=None):
       if url:
           self.driver.get(url)
       else:
           self.driver.refresh()
           
   def is_on_registration_page_alternate(self):
        return "webreg/editSchedule.htm" in self.driver.current_url or "webreg/refresh.htm" in self.driver.current_url       
           
   def register_course(self, course_index):
        # stop the while loop after 0.5 seconds to prevent it from getting hung
        start_wait = time.perf_counter() 
        while (not self.is_on_registration_page_alternate()) and time.perf_counter() - start_wait < 0.3:
            time.sleep(0)
        if not self.is_on_registration_page_alternate():
            self.restore()
        add_courses_button = self.driver.find_element(By.ID, "submit")
        index1_box = self.driver.find_element(By.ID, "i1")
        index1_box.send_keys(str(course_index))
        add_courses_button.click()
        end = time.perf_counter()
        start_wait = time.perf_counter() 
        while not self.is_on_registration_page_alternate() and time.perf_counter() - start_wait < 5:
            time.sleep(0)
        self.restore()
        return end

   def restore(self, url=f"https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection={SEMESTER_SELECTION}&indexList=", should_wait=True):
        self.visit_url(url)
        if self.is_on_login_page():
            self.handle_login()

        if should_wait==True:
            start_wait = time.perf_counter()
            while not self.is_on_registration_page() and time.perf_counter() - start_wait < 5:
                time.sleep(0)
           
   def is_driver_running(self):
       if self.driver is None:
           return False
   
       try:
           # Ensuring that self.driver.window_handles is not empty
           return bool(self.driver.window_handles)
       except:
           return False
       
   def refresh_page_and_restore(self, url=SEMESTER_SELECTION_URL):
        if self.registering:
            return False
        self.refreshing = True
        
        self.refresh_page(url="https://sims.rutgers.edu/webreg/refresh.htm")
        
        if not self.is_on_registration_page():
            self.restore(url, should_wait=False)
        self.refresh_page(url)  
       
        self.refreshing = False
        return True
       
   def keep_driver_running(self):
       if self.registering:
           return
       self.upkeeping = True
       if not self.is_driver_running():
           self.driver = self.open_browser()
           self.restore()
       self.upkeeping = False


def main():
    browser = Browser()
    browser.open_browser()
    browser.open_webreg()
    browser.handle_login()


if __name__ == "__main__":
    main()