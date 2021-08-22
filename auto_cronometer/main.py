#!/usr/bin/env python3
"""Usage:
    autocm server
    autocm list <list_yaml>
    autocm lock <list_yaml>
    autocm groceries <locked_yaml>

Automate food/nutrition bookkeeping tasks.

Commands:
    server       Starts a server that gets Cronometer data.
    groceries    Upload the grocery list defined by <locked_yaml> to the cloud.

Commands that require the server to be started first:
    list         Get the list of recipes, and save it to <list_yaml>.
    lock         Get all ingredients required in <list_yaml>.
    init_config  Initialize a config.yaml file. This file will store metadata
                 about ingredients.

"""
from docopt import docopt
import auto_cronometer.cloudify as cloudify
from auto_cronometer.autocm_server import AutoCronometerServer
from auto_cronometer.autocm_client import AutoCronometerClient
import yaml


def main():
    args = docopt(__doc__)
    if args['server']:
        with AutoCronometerServer() as server:
            print('Starting the server...')
            server.listen()
    elif args['list']:
        client = AutoCronometerClient()
        recipe_name_to_id = client.get_recipe_name_to_id()
        with open(args['<list_yaml>'], 'w') as f:
            yaml.dump(list(recipe_name_to_id.keys()), f)
    elif args['lock']:
        client = AutoCronometerClient()
        recipe_list_yaml = args['<list_yaml>']
        with open(recipe_list_yaml, 'r') as f:
            recipe_list = yaml.load(f, Loader=yaml.FullLoader)
        recipe_name_to_id = client.get_recipe_name_to_id()
        recipe_ids = [recipe_name_to_id[name] for name in recipe_list]
        recipes = client.get_recipes(recipe_ids)
        with open('locked_' + recipe_list_yaml, 'w') as f:
            yaml.dump(recipes, f)
    elif args['init_config']:
        """
        Initialize an config.yaml file. This file will store:
            - whether an ingredient is in stock
            - what group an ingredient belongs in (i.e. dairy, pantry)
        The intent is to manually edit this file.
        """
        client = AutoCronometerClient()
        recipe_name_to_id = client.get_recipe_name_to_id()
        recipes = client.get_recipes(recipe_name_to_id.values())
        config = {}
        for i, ingredient in recipes['ingredients'].items():
            config[i] = {
                'name': ingredient['name'],
                'in_stock': False,
                'group': 'TODO',
            }
        # TODO if config.yaml exists, don't overwrite, instead add default
        # values for entries that don't yet exist, and remind the user to update
        # them manually.
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f)
    elif args['groceries']:
        cloudify.upload_grocery_list(args['<locked_yaml>'])


if __name__ == '__main__':
    main()
