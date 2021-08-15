import aiohttp
import asyncio
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

    def get_recipe_name_to_id(self):
        # sesnonce changes sometimes, so make sure to get it before requesting
        data = f'7|0|6|{API_URL}/|{SOME_ID}|{SERVICE_NAME}|findMyFoods|java.lang.String/2004016611|{self.nonce}|1|2|3|4|1|5|6|'
        return gwt_parser.parse_recipe_name_to_id(self.post(data))

    def get_recipes(self, recipe_ids):
        """
        Returns dictionary where each recipe consists
            - a list of ingredients (amounts in grams)
            - a unit conversion mapping (grams per unit) per unique ingredient

        """
        recipes_raw = asyncio.run(self.get_foods_raw(recipe_ids))

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

        ingredients_raw = asyncio.run(self.get_foods_raw(ingredient_ids))

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
        data = f'7|0|7|{API_URL}/|{SOME_ID}|{SERVICE_NAME}|getFood|java.lang.String/2004016611|I|{self.nonce}|1|2|3|4|2|5|6|7|{food_id}|'
        async with session.post(
                f'{API_URL}/app',
                headers=HEADERS,
                data=data) as resp:
            return await resp.text()

