#!/usr/bin/env python3
from ps import ParameterStore
from filemanager import FileManager
import argparse
import yaml
import sys
from pathlib import Path


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
        "key", type=str, help="Parameter Store Key or 'Tree' to manipulate")

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
        val = input('No existing remote Paramters found. Should I get the parent tree?')
        if val.upper() == 'YES' or val.upper == 'Y':
            parent_path = Path(args.key)
            params = param_store.get_params(
                path=str(parent_path.parent), decryption=args.decrypt)['Parameters']
            if not params:
                sys.exit('No Parameters Found!')
        else:
            sys.exit('Aborting')

    return sorted(params, key=lambda i: i['Name'])


def main():

    # TODO:  Make this more modular

    params = []
    args = setup_args()

    # TODO: default to '/' if no key is passed, getting ALL parameters
    if args.key is None:
        print("ERROR:  Must specify a key to manage")
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
        diff_list = {'Parameters': []}
        diffs_found = False

        # Compare local and remote params
        print('Parameters to add:')
        for i in local_params:
            if i not in params:
                diffs_found = True
                print('Found New/Changed Parameter:')
                print(yaml.dump(i))
                diff_list['Parameters'] += [i]
        if diffs_found:
            val = input('APPLY these updates? (only "apply" will apply)')
            if val == 'apply':
                print('APPLYING UPDATE')
                for i in diff_list['Parameters']:
                    param_store.put_param(i, overwrite=True)
                print('PARAMETERS UPDATED')
                exit(0)
            else:
                print('UPDATE ABORTED')
                exit(1)
        else:
            print("No updates found")
            exit(0)

    param_store.print_params()


if __name__ == '__main__':
    main()
