import time
import logging

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options


class MyNetworkDuoLogin:
    def __init__(self, username, password, environment="production"):
        self.username = username
        self.password = password
        self.cookies = None
        self.driver = self.start_firefox()
        self.environment = environment
        self.login(self.username, self.password)

    def start_firefox(self):
        options = Options()
        options.headless = False

        logging.info("Starting firefox and loading mynetwork")
        binary = FirefoxBinary("/Applications/Firefox.app/Contents/MacOS/firefox-bin")
        return webdriver.Firefox(
            options=options, firefox_binary=binary, executable_path="/Users/shchee/GitHubStuff/ucdnetwork/network_tools/geckodriver"
        )

    def login(self, username, password):
        self.driver.get("https://mynetwork.noc.ucdavis.edu/cgi-bin/netadmin.pl")

        usernameField = self.driver.find_element(By.ID, "username")
        passwordField = self.driver.find_element(By.ID, "password")

        logging.info("Submitting credentials")
        usernameField.send_keys(username)
        passwordField.send_keys(password)

        self.driver.find_element(By.NAME, "submit").click()

        if self.environment == "production":
            time.sleep(5)
            duo_iframe = self.driver.find_element(By.ID, "duo_iframe")
            if duo_iframe:
                self.driver.switch_to.frame(
                    self.driver.find_element(By.ID, "duo_iframe")
                )

                logging.warning("Remember! Don't accept this DUO push")
                logging.info("Waiting for DUO iframe to load")
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn-cancel"))
                )

                logging.info("Cancelling automatic duo push")
                self.driver.find_elements_by_class_name("btn-cancel")[0].click()
                logging.warning("Waiting 60 seconds to prevent Duo's Anomaly Detection")
                time.sleep(60)

                self.driver.find_element_by_name("dampen_choice").click()

                submit_me = self.driver.find_elements(
                    By.CSS_SELECTOR, "button.auth-button.positive"
                )

                for btn in submit_me:
                    if "Push" in btn.text:
                        btn.click()
                        logging.info("Waiting for Duo push acceptance")

                self.driver.switch_to.parent_frame()

        try:
            title = "VLAN SUMMARY"
            WebDriverWait(self.driver, 10).until(EC.title_contains(title))
        except TimeoutException as e:
            self.driver.close()
            raise e

    def get(self, url):
        self.driver.get(url)
        return self.driver.page_source
