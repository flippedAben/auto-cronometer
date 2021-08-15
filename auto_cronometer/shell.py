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

    def do_lock(self, recipe_list_yaml):
        "Lock ingredients and amounts of the YAML's recipe list"
        recipe_id_list = self.ac.get_recipe_list()
        with open(recipe_list_yaml, 'r') as f:
            recipe_list = yaml.load(f, Loader=yaml.FullLoader)

        locked_recipes = {
            'recipes': [],
            'grams_per_unit': {},
        }
        # TODO Make this faster by sending parallel recipes and food service
        # calls.
        for recipe_name in recipe_list:
            recipe_id = recipe_id_list[recipe_name]
            recipe = self.ac.get_recipe(recipe_id)
            unit_conversions = recipe.pop('grams_per_unit')
            locked_recipes['recipes'].append(recipe)
            locked_recipes['grams_per_unit'].update(unit_conversions)

        with open('locked_' + recipe_list_yaml, 'w') as f:
            yaml.dump(locked_recipes, f)

    def do_pull(self, recipe_list_yaml):
        "Pull the recipe list from Cronometer into a YAML file"
        recipe_id_list = self.ac.get_recipe_list()
        with open(recipe_list_yaml, 'w') as f:
            yaml.dump(list(recipe_id_list.keys()), f)

    def completedefault(self, text, line, start_idx, end_idx):
        if os.path.isdir(text):
            return glob.glob(os.path.join(text, '*'))
        else:
            return glob.glob(text + '*')

    def do_q(self, _):
        "Quit"
        self.ac.__exit__(None, None, None)
        return True

