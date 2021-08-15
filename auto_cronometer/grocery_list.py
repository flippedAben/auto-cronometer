import yaml
from pprint import pprint


def get_grocery_list(locked_recipes_yaml):
    with open(locked_recipes_yaml, 'r') as f:
        recipes = yaml.load(f, Loader=yaml.Loader)

    ingredients = consolidate_recipes(recipes)
    pprint(ingredients)

    return []


def consolidate_recipes(recipes):
    """
    Convert a list of recipes into a list of ingredients. Ingredients of the
    exact same name will be combined additively.

    Returns a list of ingredients with amounts in grams.
    """
    ingredients = {}
    for recipe in recipes:
        for ingredient in recipe['ingredients']:
            name = ingredient['name']
            grams = ingredient['grams']
            if name in ingredients:
                ingredients[name] += grams
            else:
                ingredients[name] = grams
    return ingredients
