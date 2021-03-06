#!/usr/bin/env python3
from ps import ParameterStore
from filemanager import FileManager
import argparse
import yaml
import sys


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


if __name__ == '__main__':

    params = []
    args = setup_args()

    if args.key is None:
        print("ERROR:  Must specify a key to manage")
        exit(-1)

    # Get AWS Session for Parameter Store
    if args.profile is not None:
        param_store = ParameterStore(region=args.region, profile=args.profile)
    elif args.arn is not None:
        param_store = ParameterStore(region=args.region, arn=args.arn)
    else:
        # Create source using AWS default profile
        param_store = ParameterStore(region=args.region)

    fm = FileManager(args.file)

    params = param_store.get_params(
        path=args.key, decryption=args.decrypt)['Parameters']
    if not params:
        sys.exit('No remote Paramters found')

    params = sorted(params, key=lambda i: i['Name'])

    # Handle pulling params
    if args.get:
        fm.write(params)
        print("Parameters saved to", args.file)
        exit(0)

    if args.update:
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
