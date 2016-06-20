from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import logging
import yaml
import sys
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

display = Display(visible=0, size=(800, 600))
display.start()


class HDFC():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.load_config()

    def load_config(self):
        try:
            f = open("credentials.yml")
        except:
            logger.exception("Error opening config file")
            sys.exit(1)

        config = yaml.load(f.read())
        self.credentials = config['credentials']

    def enter_username(self):
        self.driver.get("https://netbanking.hdfcbank.com/netbanking/")
        assert "Welcome to HDFC Bank" in self.driver.title

        username_wait = WebDriverWait(self.driver, 10)
        frame = username_wait.until(EC.presence_of_element_located((By.NAME, 'login_page')))
        self.driver.switch_to.frame(frame)
        try:
            elem = username_wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'input_password')))
            elem.send_keys(self.credentials['username'])
            elem.send_keys(Keys.RETURN)
            return elem
        except:
            raise

    def enter_password(self):
        password_wait = WebDriverWait(self.driver, 10)
        # As enter_username was executed, we're in the right frame
        elem = password_wait.until(EC.presence_of_element_located((By.NAME, 'fldPassword')))
        elem.send_keys(self.credentials['password'])
        return elem

    def click_secure_image(self):
        image_wait = WebDriverWait(self.driver, 10)
        elem = image_wait.until(EC.presence_of_element_located((By.NAME, 'chkrsastu')))
        elem.click()
        elem.send_keys(Keys.RETURN)

    def do_login(self):
        self.enter_username()
        pass_elem = self.enter_password()
        self.click_secure_image()
        pass_elem.send_keys(Keys.ENTER)

    def parse_amounts(self):
        # Switch iframe and move on
        txn_wait = WebDriverWait(self.driver, 10)
        frame = txn_wait.until(EC.presence_of_element_located((By.NAME, 'main_part')))
        self.driver.switch_to_default_content()
        self.driver.switch_to.frame(frame)

        balance = {}

        # Get Unbilled Amount
        elem = txn_wait.until(EC.presence_of_element_located((By.ID, 'CCActiveMatSummary1')))
        text = elem.text
        balance['HDFC CC'] = float(text[text.find("INR ") + 4:].replace(",", ""))

        # Get Savings Amount
        elem = txn_wait.until(EC.presence_of_element_located((By.ID, 'SavingTotalSummary')))
        text = elem.text
        balance['HDFC Savings'] = float(text[text.find("INR ") + 4:].replace(",", ""))
        return balance

    def do_logout(self):
        # Switch iframe
        self.driver.switch_to_default_content()
        logout_wait = WebDriverWait(self.driver, 10)
        frame = logout_wait.until(EC.presence_of_element_located((By.NAME, 'common_menu1')))
        self.driver.switch_to.frame(frame)

        logout_button = self.driver.find_element_by_xpath('//*[@title="Log Out"]')
        logout_button.click()

        # Wait for the logout message
        logout_wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'msg')))

    def get_unbilled_amount(self):
        self.do_login()
        amount = self.parse_amounts()
        self.do_logout()
        return amount

    def quitdriver(self):
        self.driver.quit()


def main():
    hdfc_interface = HDFC()
    print json.dumps(hdfc_interface.get_unbilled_amount(), indent=2)
    hdfc_interface.quitdriver()

if __name__ == "__main__":
    main()
