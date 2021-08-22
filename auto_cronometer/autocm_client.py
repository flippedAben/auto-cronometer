import asyncio
import auto_cronometer.gwt_parser as gwt_parser
import httpx # aiohttp hangs for some reason, so we don't use it
from multiprocessing.connection import Client

ADDRESS = ('localhost', 6100)
API_URL = 'https://cronometer.com/cronometer'
SERVICE_NAME = 'com.cronometer.client.CronometerService'


class AutoCronometerClient():
    def __init__(self):
        with Client(ADDRESS) as conn:
            # It's extremely rare for the GWT IDs to change, unless this object
            # lives for many days.
            conn.send('gwt_ids')
            perm_id, policy_file_id = conn.recv()
            self.gwt_perm_id = perm_id
            self.gwt_policy_file_id = policy_file_id
            self.headers = {
                'x-gwt-permutation': self.gwt_perm_id,
                'content-type': 'text/x-gwt-rpc; charset=UTF-8',
            }

    @property
    def nonce(self):
        # The nonce may change frequently, so get it every time.
        with Client(ADDRESS) as conn:
            conn.send('nonce')
            return conn.recv()

    def get_recipe_name_to_id(self):
        print('Getting recipe list')
        data = f'7|0|6|{API_URL}/|{self.gwt_policy_file_id}|{SERVICE_NAME}|findMyFoods|java.lang.String/2004016611|{self.nonce}|1|2|3|4|1|5|6|'
        # TODO Figure out why adding a timeout reduces hang time.
        resp = httpx.post(
            f'{API_URL}/app',
            data=data,
            headers=self.headers,
            timeout=1)
        print('Got recipe list')
        return gwt_parser.parse_recipe_name_to_id(resp.text)

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
        async with httpx.AsyncClient() as session:
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
        resp = await session.post(
                f'{API_URL}/app',
                headers=self.headers,
                data=data)
        return resp.text
