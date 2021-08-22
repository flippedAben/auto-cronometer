"""
Logs into Cronometer and provides information necessary in order to make GWT
requests.
"""
from multiprocessing.connection import Listener
from selenium import webdriver
import os
import re
import time

ADDRESS = ('localhost', 6100)


class AutoCronometerServer():
    def __init__(self):
        # Enable headless Firefox
        os.environ['MOZ_HEADLESS'] = '1'

        self.driver = webdriver.Firefox(
            executable_path=str(os.environ.get('geckodriver_path')),
            log_path=os.environ.get('geckodriver_log_path'))

        self._login()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def _login(self):
        print('Logging in to Cronometer')
        self.driver.get('https://cronometer.com/login/')
        user_ele = self.driver.find_element_by_name('username')
        pass_ele = self.driver.find_element_by_name('password')
        user_ele.send_keys(os.environ.get('cronometer_user'))
        pass_ele.send_keys(os.environ.get('cronometer_pass'))
        submit_button = self.driver.find_element_by_id('login-button')
        submit_button.click()

        # Poll for existence the "sesnonce" cookie. We need this to make
        # requests for everything else.
        while self.get_nonce_cookie() is None:
            time.sleep(0.1)
        print('Logged in')

    def listen(self):
        with Listener(ADDRESS) as listener:
            while True:
                with listener.accept() as conn:
                    print('Connection accepted', listener.last_accepted)
                    message = conn.recv()
                    if message == 'gwt_ids':
                        conn.send(self.gwt_ids())
                    if message == 'nonce':
                        conn.send(self.nonce)
                    else:
                        conn.send('Not a valid message.')

    def gwt_ids(self):
        # Assume that IDs are hex strings of size 32.
        gwt_id_re = re.compile(r"'?([A-Z0-9]{32})'?")
        self.driver.get('https://cronometer.com/cronometer/cronometer.nocache.js')
        match = gwt_id_re.search(self.driver.page_source)
        gwt_perm_id = None
        gwt_policy_file_id = None
        if match:
            # Assume there is only one such hex string in this file.
            gwt_perm_id = match.group(1)
            self.driver.get(f'https://cronometer.com/cronometer/{gwt_perm_id}.cache.js')
            match = gwt_id_re.findall(self.driver.page_source)
            if match:
                # Assume there are only 2 IDs, and the second ID is the policy
                # file ID.
                gwt_policy_file_id = match[1]
            else:
                print('Could not get the GWT policy file ID. Qutting...')
                exit(1)
        else:
            print('Could not get the GWT permutation ID. Qutting...')
            exit(1)

        return (gwt_perm_id, gwt_policy_file_id)

    @property
    def nonce(self):
        return self.get_nonce_cookie()['value']

    def get_nonce_cookie(self):
        return self.driver.get_cookie('sesnonce')
