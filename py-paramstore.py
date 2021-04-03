#!/usr/bin/env python3
from ps import ParameterStore
from filemanager import FileManager
import argparse
import yaml
import sys
from pathlib import Path
import itertools


def setup_args():
    # Setup Parser and args
    parser = argparse.ArgumentParser()

    # Profile Args
    account_group = parser.add_mutually_exclusive_group(required=False)
    account_group.add_argument("-p", "--profile",
                               help="specify Profile for Source AWS account")
    account_group.add_argument("-a", "--arn",
                               help="ARN for source role to assume for migration")

    # Required Key Arg
    parser.add_argument(
        "key", type=str, nargs='?', help="Parameter Store Key or 'Tree' to manipulate")

    parser.add_argument(
        "-r", "--recurse", help="Recurse keys, manipulating the tree (DEFAULT IS TRUE)",
        action='store_true')

    parser.add_argument(
        "-x", "--decrypt", help="Request Decryption of parameters (DEFAULT IS FALSE)",
        action='store_true')

    parser.add_argument(
        "-f", "--file", help="File for specifying parameters. Defaults to parameters.yml",
        default="parameters.yml")

    parser.add_argument(
        "-g", "--get", help="Pull Parameters, saving to local file",
        action='store_true', default=False)

    parser.add_argument(
        "-u", "--update", help="Push Parameter updates from local file",
        action='store_true', default=False)

    parser.add_argument(
        "--region", help="AWS Region for migration (defaults to us-east-1)")

    parser.add_argument(
        "-q", "--quiet", help="Suppress output (better for piping)", action='store_true', default=False)

    # Parse Args
    return parser.parse_args()


def get_params(param_store, args):
    params = param_store.get_params(
        path=args.key, decryption=args.decrypt)['Parameters']
    if not params:
        val = input(
            'No existing remote Paramters found. Should I get the parent tree?')
        if val.upper() == 'YES' or val.upper == 'Y':
            parent_path = Path(args.key)
            params = param_store.get_params(
                path=str(parent_path.parent), decryption=args.decrypt)['Parameters']
            if not params:
                sys.exit('No Parameters Found!')
        else:
            sys.exit('Aborting')

    return sorted(params, key=lambda i: i['Name'])


def list_compare(list1, list2):
    removed = list(itertools.filterfalse(lambda i: i in list1, list2))
    added = list(itertools.filterfalse(lambda i: i in list2, list1))
    return added, removed


def main():

    # TODO:  Make this more modular

    params = []
    args = setup_args()

    if args.key is None:
        val = input(
            "You didn't specify a parameter key or path to pull.  Do you want to pull ALL parameters?")
        if str.upper(val) == "Y" or str.upper(val) == "YES":
            args.key = "/"
        else:
            exit(-1)

    # Get AWS Session for Parameter Store
    param_store = ParameterStore(args)

    fm = FileManager(args.file)

    params = get_params(param_store, args)

    # Handle pulling params
    if args.get:
        fm.write(params)
        print("Parameters saved to", args.file)
        exit(0)

    if args.update:
        # TODO: Move to helper
        local_params = fm.read()['Parameters']
        if not local_params:
            sys.exit('No local parameters found!')
        local_params = sorted(local_params, key=lambda i: i['Name'])

        added, removed = list_compare(local_params, params)

        # TODO: Move this to a function or module
        if not added == [] or not removed == []:

            print('Parameters to add:')
            print(yaml.dump(added))

            print('Parameters to remove:')
            print(yaml.dump(removed))

            val = input('APPLY these updates? (only "apply" will apply) ')
            if val == 'apply':
                remove_all = False
                for i in removed:
                    if list(filter(lambda x: x['Name'] == i['Name'], added)) == []:
                        if not remove_all:
                            print(
                                'CAUTION!!! YOU ARE ABOUT TO REMOVE A PARAMETER!!!')
                            print(
                                'TYPE "remove" IF YOU ARE SURE YOU WANT TO DO THIS')
                            remval = input(
                                'OR "remove all" IF YOU ARE SURE YOU WANT TO REMOVE ALL PARAMETERS IN THE REMOVE LIST: ')
                            if remval == 'remove all':
                                remove_all = True
                                remval = 'remove'
                            if remval != 'remove':
                                print('Aborting!')
                                exit(0)
                        param_store.rm_param(i)
                for i in added:
                    param_store.put_param(i, overwrite=True)
            else:
                print('UPDATE ABORTED')
                exit(0)
        else:
            print('No updates found')
            exit(0)


if __name__ == '__main__':
    main()
