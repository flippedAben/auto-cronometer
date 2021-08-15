#!/usr/bin/env python3
"""Usage:
    autocm shell
    autocm groceries <locked_yaml>

Automate food/nutrition bookkeeping tasks.

Commands:
    shell      Opens a shell to interact with Cronometer.
    groceries  Upload the grocery list defined by <locked_yaml> to the cloud.

"""
from docopt import docopt
import auto_cronometer.cloudify as cloudify
from auto_cronometer.shell import CronometerShell


def main():
    args = docopt(__doc__)
    if args['shell']:
        CronometerShell().cmdloop()
    elif args['groceries']:
        cloudify.upload_grocery_list(args['<locked_yaml>'])


if __name__ == '__main__':
    main()
