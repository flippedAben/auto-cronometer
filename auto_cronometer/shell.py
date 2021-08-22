from auto_cronometer.auto_cm import AutoCronometer
import cmd
import glob
import os.path
import readline
import yaml

readline.set_completer_delims(' \t\n')

class CronometerShell(cmd.Cmd):
    intro = 'Welcome to the Cronometer shell. Type help or ? to list commands.\n'
    prompt = '(auto_cm) '

    def preloop(self):
        self.ac = AutoCronometer()
        self.ac.__enter__()
        pass

    def do_pull(self, recipe_list_yaml):
        """
        Pull the recipe list from Cronometer into a YAML file, and lock
        ingredients and amounts of the YAML's recipe list.

        Args: <path to yaml>
        """
        recipe_name_to_id = self.ac.get_recipe_name_to_id()
        with open(recipe_list_yaml, 'r') as f:
            recipe_list = yaml.load(f, Loader=yaml.FullLoader)

        with open(recipe_list_yaml, 'w') as f:
            yaml.dump(list(recipe_name_to_id.keys()), f)

        recipe_ids = [recipe_name_to_id[name] for name in recipe_list]
        recipes = self.ac.get_recipes(recipe_ids)

        with open('locked_' + recipe_list_yaml, 'w') as f:
            yaml.dump(recipes, f)

    def do_init_config(self, _):
        """
        Initialize an config.yaml file. This file will store:
            - whether an ingredient is in stock
            - what group an ingredient belongs in (i.e. dairy, pantry)
        The intent is to manually edit this file.
        """
        recipe_name_to_id = self.ac.get_recipe_name_to_id()
        recipes = self.ac.get_recipes(recipe_name_to_id.values())
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

    def completedefault(self, text, line, start_idx, end_idx):
        if os.path.isdir(text):
            return glob.glob(os.path.join(text, '*'))
        else:
            return glob.glob(text + '*')

    def do_q(self, _):
        "Quit"
        self.ac.__exit__(None, None, None)
        return True

