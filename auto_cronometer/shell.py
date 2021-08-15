import cmd
import yaml
from auto_cronometer.auto_cm import AutoCronometer

# TODO Add autocomplete for file names
class CronometerShell(cmd.Cmd):
    intro = 'Welcome to the Cronometer shell. Type help or ? to list commands.\n'
    prompt = '(auto_cm) '

    def preloop(self):
        self.ac = AutoCronometer()
        self.ac.__enter__()

    def do_lock(self, recipe_list_yaml):
        "Lock ingredients and amounts of the recipe list"
        recipe_id_list = self.ac.get_recipe_list()
        with open(recipe_list_yaml, 'r') as f:
            recipe_list = yaml.load(f, Loader=yaml.FullLoader)
        recipes = []
        # TODO Make this faster by sending parallel recipes and food service
        # calls.
        for recipe_name in recipe_list:
            recipe_id = recipe_id_list[recipe_name]
            recipe = self.ac.get_recipe(recipe_id)
            recipes.append(recipe)
        with open('locked_' + recipe_list_yaml, 'w') as f:
            yaml.dump(recipes, f)

    def do_pull(self, recipe_list_yaml):
        "Pull recipe list from Cronometer into active.yaml"
        recipe_id_list = self.ac.get_recipe_list()
        with open(recipe_list_yaml, 'w') as f:
            yaml.dump(list(recipe_id_list.keys()), f)

    def do_q(self, _):
        "Quit"
        self.ac.__exit__(None, None, None)
        return True

