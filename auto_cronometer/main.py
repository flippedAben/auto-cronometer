#!/usr/bin/env python3
"""Usage:
    autocm scrape [--html_dir DIR]
    autocm parse <html_dir> [--json_dir DIR]
    autocm diary
    autocm cloud
    autocm active <data_dir>

Automate food/nutrition bookkeeping tasks.

Commands:
    scrape    Scrape Cronometer's website for recipe HTMLs.
    parse     Parse scraped HTMLs in <html_dir> into JSON files.
    active    Initialize a active.yaml file with all recipes included.
    cloud     Put the grocery list defined by the active.yaml on the cloud.
    diary     Add recipes in active.yaml to today's diary.

Options:
    --html_dir DIR    Store the HTMLs in DIR [default: raw_htmls]
    --json_dir DIR    Store the JSONs in DIR [default: data]

"""
from docopt import docopt
import auto_cronometer.scrape as scrape
import auto_cronometer.parse as parse
import auto_cronometer.update_diary as update_diary
import auto_cronometer.cloudify as cloudify
import auto_cronometer.active_yaml as active_yaml


def main():
    args = docopt(__doc__)
    if args['scrape']:
        scrape.scrape_recipes(args['--html_dir'])
    elif args['parse']:
        parse.parse_recipe_htmls(
            args['<html_dir>'],
            args['--json_dir'],
        )
    elif args['diary']:
        update_diary.add_active_recipes_to_diary()
    elif args['cloud']:
        cloudify.upload_grocery_list()
    elif args['active']:
        active_yaml.create_active_yaml(args['<data_dir>'])


if __name__ == '__main__':
    main()
