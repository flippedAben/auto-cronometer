"""
Parses GWT response objects into Python lists.
"""

def parse_recipe_name_to_id(response):
    """
    Parse response of the findMyFoods service call.
    Assumptions:
        - The response starts with a 4-char status code (i.e. //OK)
        - The response is a well formatted Python list
        - There is exactly one list in the list which contains strings
            - Within that list, strings with com.cronometer are not recipe
              names, and everything else is
            - The recipes names are in reverse order relative to the IDs
        - Numbers >= 10**7 are recipe IDs, and all other numbers don't matter

    Maps recipe names to ids.
    """
    ids = []
    names = []
    for datum in eval(response[4:]):
        if type(datum) is int:
            if datum >= 10**7:
                ids.append(datum)
        elif type(datum) is list:
            for name in datum:
                if 'com.cronometer' not in name:
                    names.append(name)
    recipe_map = {name: i for (name, i) in zip(names, reversed(ids))}
    return recipe_map


def parse_recipe(response):
    """
    Parse the response of the getFood service call.

    Assumptions:
        - You passed a recipe ID into the getFood service call.
        - There is exactly one list in the list which contains strings
            - A recipe with n ingredients will contain n+1 strings outside of
              the one list. Each of the first n strings is followed by an
              ingredient ID that we can use to make another getFood service
              call, and the amount of it used in the recipe (in grams).
            - The 2nd entry after the string 'English' shows up contains the
              name of the food.
    """
    data = eval(response[4:])
    recipe = {}
    recipe['ingredients'] = []
    for i, datum in enumerate(data):
        if type(datum) is str and data[i+1] > 0:
            ingredient = {
                # ID
                'id': data[i+1],
                'grams': data[i+2],
            }
            recipe['ingredients'].append(ingredient)
        if type(datum) is list:
            recipe['name'] = datum[datum.index('English') + 2]
    return recipe


def parse_food(response):
    """
    Parse the response of the getFood service call.

    Assumptions:
        - You passed a food ID into the getFood service call.
        - There is exactly one list in the list which contains strings
            - The 2nd entry after the string 'English' shows up contains the
              name of the food.
            - Supported measuring units start on an entry containing
              'com.cronometer.client.data.Measure/' and go to 'g'. Any string
              starting with 'com.' is ignored.
        - There is exactly one string outside of the above stated list.
            - The 3rd entry after this string is the food ID.
        - If an entry is the food ID, 3 entries later contains the conversion
          of 'grams per <unit>', except for the last 2.
    """
    data = eval(response[4:])
    food = {}
    for i, datum in enumerate(data):
        if type(datum) is list:
            food['name'] = datum[datum.index('English') + 2]
        elif type(datum) is str:
            food['id'] = data[i + 3]

    # Second pass to get units and conversion ratios
    units = []
    ratios = []
    for i, datum in enumerate(data):
        if type(datum) is list:
            j = datum.index('g') - 1
            units = []
            while not datum[j].startswith('com.cronometer.client.data.Measure/'):
                if not datum[j].startswith('com.'):
                    units.append(datum[j])
                j -= 1
        elif type(datum) is int and datum == food['id']:
            ratios.append(data[i + 3])

    # Drop last two because they are noise
    ratios = ratios[:-2]
    food['grams_per_unit'] = {unit:ratio for (unit, ratio) in zip(units, ratios)}

    return food
