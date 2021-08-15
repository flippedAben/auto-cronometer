import yaml


def get_grocery_list(locked_recipes_yaml):
    # TODO Complete this function. Find out what we need to return.
    # Consolidate ingredients into one.
    with open(locked_recipes_yaml, 'r') as f:
        recipes = yaml.load(f, Loader=yaml.Loader)
    return []

