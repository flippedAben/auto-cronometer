import yaml


def get_grocery_list(locked_recipes_yaml):
    with open(locked_recipes_yaml, 'r') as f:
        locked_recipes = yaml.load(f, Loader=yaml.Loader)

    ingredients = consolidate_recipes(locked_recipes)
    convert_units(ingredients, locked_recipes['ingredients'])

    # Exclude items in stock and apply grouping
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    for i, ingredient in ingredients.items():
        ingredient['group'] = config[i]['group']
    ingredients = {
        x: y
        for x, y in ingredients.items()
        if not config[x]['in_stock']}
    return ingredients


def consolidate_recipes(locked_recipes):
    """
    Convert a list of recipes into a list of ingredients. Ingredients of the
    exact same name will be combined additively.

    Returns a list of ingredients with amounts in grams.
    """
    recipes = locked_recipes['recipes']
    ingredient_metadata = locked_recipes['ingredients']

    ingredients = {}
    for recipe in recipes:
        for ingredient in recipe['ingredients']:
            i = ingredient['id']
            name = ingredient_metadata[i]['name']
            grams = ingredient['grams']
            if i in ingredients:
                ingredients[i]['grams'] += grams
            else:
                ingredients[i] = {
                    'name': name,
                    'grams': grams,
                }
    return ingredients


def convert_units(ingredients, ingredient_metadata):
    """
    Convert the amount of each ingredient (in grams) to a friendlier unit.

    Assume that "friendly" means the fewest digits. For example, 3 lb is
    friendlier that 48 oz. Note: 16 oz is 1 lb.
    """

    for i in ingredients:
        ingredient = ingredients[i]
        grams_per_unit = ingredient_metadata[i]['grams_per_unit']
        grams_per_unit['lb'] = grams_per_unit['oz'] * 16

        # Default to grams
        friendliest_unit = 'g'
        amount = float(ingredient['grams'])
        min_digits = len(str(amount))
        for unit, ratio in grams_per_unit.items():
            # Get rid of insane rounding errors
            unit_amount = round(ingredient['grams'] / ratio, 5)
            digits = len(str(unit_amount))
            if 0.1 <= unit_amount and digits < min_digits:
                friendliest_unit = unit
                amount = unit_amount
                min_digits = digits
        ingredient.pop('grams')
        ingredient['unit'] = friendliest_unit
        ingredient['amount'] = amount

