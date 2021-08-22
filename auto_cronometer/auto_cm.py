import aiohttp
import asyncio
from selenium import webdriver
import os
import time
import re
import requests
import auto_cronometer.gwt_parser as gwt_parser

API_URL = 'https://cronometer.com/cronometer'
SERVICE_NAME = 'com.cronometer.client.CronometerService'


class AutoCronometer():
    def __init__(self):
        # Enable headless Firefox
        os.environ['MOZ_HEADLESS'] = '1'

        self.driver = webdriver.Firefox(
            executable_path=os.environ.get('geckodriver_path'),
            log_path=os.environ.get('geckodriver_log_path'))

        self._get_gwt_metadata()
        self._login()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def _get_gwt_metadata(self):
        # Assume that IDs are hex strings of size 32.
        gwt_id_re = re.compile(r"'?([A-Z0-9]{32})'?")
        self.driver.get('https://cronometer.com/cronometer/cronometer.nocache.js')
        match = gwt_id_re.search(self.driver.page_source)
        if match:
            # Assume there is only one such hex string in this file.
            gwt_perm_id = match.group(1)
            print(gwt_perm_id)
            self.headers = {
                'x-gwt-permutation': gwt_perm_id,
                'content-type': 'text/x-gwt-rpc; charset=UTF-8',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
            }
            self.driver.get(f'https://cronometer.com/cronometer/{gwt_perm_id}.cache.js')
            match = gwt_id_re.findall(self.driver.page_source)
            if match:
                # Assume there are only 2 IDs, and the second ID is the policy
                # file ID.
                self.gwt_policy_file_id = match[1]
                print(self.gwt_policy_file_id)
            else:
                print('Could not get the GWT policy file ID. Qutting...')
                exit(1)
        else:
            print('Could not get the GWT permutation ID. Qutting...')
            exit(1)

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

    @property
    def nonce(self):
        # The actual nonce is a hex string contained in the value of the
        # sesnonce cookie.
        return self.get_nonce_cookie()['value']

    def get_nonce_cookie(self):
        return self.driver.get_cookie('sesnonce')

    def post(self, data):
        with requests.Session() as session:
            resp = session.post(
                f'{API_URL}/app',
                data=data,
                headers=self.headers,
                timeout=1)
            print(f'{resp.status_code}: Got recipes list')
            return resp.content

    def get_recipe_name_to_id(self):
        # sesnonce changes sometimes, so make sure to get it before requesting
        data = f'7|0|6|{API_URL}/|{self.gwt_policy_file_id}|{SERVICE_NAME}|findMyFoods|java.lang.String/2004016611|{self.nonce}|1|2|3|4|1|5|6|'
        print(data)
        return gwt_parser.parse_recipe_name_to_id(self.post(data))

    def get_recipes(self, recipe_ids):
        """
        Returns dictionary where each recipe consists
            - a list of ingredients (amounts in grams)
            - a unit conversion mapping (grams per unit) per unique ingredient

        """
        print('Getting recipes')
        recipes_raw = asyncio.run(self.get_foods_raw(recipe_ids))
        print('Got recipes')

        recipes = {
            'recipes': [],
            'ingredients': {},
        }
        ingredient_ids = []
        for recipe_id, recipe_raw in zip(recipe_ids, recipes_raw):
            recipe = gwt_parser.parse_recipe(recipe_raw)
            recipe['id'] = recipe_id
            recipes['recipes'].append(recipe)

            ingredient_ids.extend(i['id'] for i in recipe['ingredients'])
        ingredient_ids = list(set(ingredient_ids))

        print('Getting ingredients')
        ingredients_raw = asyncio.run(self.get_foods_raw(ingredient_ids))
        print('Got ingredients')

        for food_raw in ingredients_raw:
            food = gwt_parser.parse_food(food_raw)
            food_id = food.pop('id')
            recipes['ingredients'][food_id] = food

        return recipes

    async def get_foods_raw(self, food_ids):
        """
        Get many foods concurrently.

        For recipes, the food_id is the recipe ID.
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for food_id in food_ids:
                tasks.append(asyncio.create_task(
                    self.get_food_raw(session, food_id))
                )
            return await asyncio.gather(*tasks)

    async def get_food_raw(self, session, food_id):
        """
        Gets the raw response (i.e. no parsing) of a getFood service call.

        Note: the food itself may or may not be actually raw.
        """
        data = f'7|0|7|{API_URL}/|{self.gwt_policy_file_id}|{SERVICE_NAME}|getFood|java.lang.String/2004016611|I|{self.nonce}|1|2|3|4|2|5|6|7|{food_id}|'
        print(f'Requesting food {food_id}')
        # TODO: sometimes this hangs. Is it because Cronometer is blocking me
        # due to too many requests?
        async with session.post(
                f'{API_URL}/app',
                headers=self.headers,
                data=data,
                timeout=5) as resp:
            print(f'{resp.status}: Got food {food_id}')
            return await resp.text()

