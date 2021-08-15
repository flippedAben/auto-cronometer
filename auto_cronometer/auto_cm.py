from selenium import webdriver
import os
import time
import requests
import auto_cronometer.gwt_parser as gwt_parser

# TODO: These constants may change. If they do, figure out why.
# I don't know what this is, but it's necessary.
SOME_ID = os.environ.get('cronometer_hex')
# I don't know what this is either, but it's necessary. Something to do with how
# GWT does its generation?
GWT_PERM = 'E0EAD93C6F95D5F986CFD7611F67840C'

API_URL = 'https://cronometer.com/cronometer'
SERVICE_NAME = 'com.cronometer.client.CronometerService'
HEADERS = {
    'x-gwt-permutation': GWT_PERM,
    'content-type': 'text/x-gwt-rpc; charset=UTF-8',
}


class AutoCronometer():
    def __init__(self):
        # Enable headless Firefox
        os.environ['MOZ_HEADLESS'] = '1'

        self.driver = webdriver.Firefox(
            executable_path=os.environ.get('geckodriver_path'),
            log_path=os.environ.get('geckodriver_log_path'))
        self._login()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def _login(self):
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

    @property
    def nonce(self):
        # The actual nonce is a hex string contained in the value of the
        # sesnonce cookie.
        return self.get_nonce_cookie()['value']

    def get_nonce_cookie(self):
        return self.driver.get_cookie('sesnonce')

    def post(self, data):
        session = requests.Session()
        resp = session.post(
            f'{API_URL}/app',
            headers=HEADERS,
            data=data)
        return resp.content

    def get_recipe_list(self):
        # sesnonce changes sometimes, so make sure to get it before requesting
        data = f'7|0|6|{API_URL}/|{SOME_ID}|{SERVICE_NAME}|findMyFoods|java.lang.String/2004016611|{self.nonce}|1|2|3|4|1|5|6|'
        return gwt_parser.parse_recipe_list(self.post(data))

    def get_recipe(self, recipe_id):
        # For recipes, the food_id is the recipe ID.
        # The responses of custom recipes and Cronometer default foods are
        # different, so be aware. Cronometer calls it getFood for both.
        print('Get recipe')
        recipe_data = gwt_parser.parse_recipe(self.get_food_raw(recipe_id))
        recipe = {
            'id': recipe_id,
            'name': recipe_data['name'],
            'ingredients': [],
        }
        print('Loop through ingredients')
        for ingredient in recipe_data['ingredients']:
            food = gwt_parser.parse_food(self.get_food_raw(ingredient['id']))
            ingredient.update(food)
            recipe['ingredients'].append(ingredient)
        print('Finish loop')
        return recipe

    def get_food_raw(self, food_id):
        """
        Gets the raw response (i.e. no parsing) of a getFood service call.

        Note: the food itself may or may not be actually raw.
        """
        data = f'7|0|7|{API_URL}/|{SOME_ID}|{SERVICE_NAME}|getFood|java.lang.String/2004016611|I|{self.nonce}|1|2|3|4|2|5|6|7|{food_id}|'
        return self.post(data)
