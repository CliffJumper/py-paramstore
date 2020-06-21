from ps import ParameterStore
from filemanager import FileManager
import argparse
import yaml
import os.path


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
        "-r", "--recurse", help="Recurse keys, manipulating the tree",
        action='store_true')

    parser.add_argument(
        "-x", "--decrypt", help="Request Decryption of parameters (DEFAULT IS TRUE)",
        action='store_true')

    parser.add_argument(
        "-f", "--file", help="File for specifying parameters. Defaults to parameters.yml",
        default="parameters.yml")

    parser.add_argument(
        "-g", "--get", help="Pull Parameters, saving to local file")

    parser.add_argument("--region", help="AWS Region for migration")

    # Parse Args
    return parser.parse_args()


if __name__ == '__main__':
    use_sps = False
    use_dps = False
    # use_consul = False

    args = setup_args()

    if args.key is None:
        print("ERROR:  Must specify a key to manage")
        exit(-1)

    if args.profile is not None:
        ps_source = ParameterStore(profile=args.profile)
    elif args.arn is not None:
        ps_source = ParameterStore(arn=args.arn)
    else:
        # Create source using AWS defaults
        ps_source = ParameterStore()

    if args.file is None:
        args.file = "parameters.yml"

    fm = FileManager(args.file)
    # Check for config file existence
    if os.path.isfile(args.file):
        # Read in the file
        print('Found', args.file, '.  Checking against current Parameters')
        with open(args.file) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            local_params = yaml.load(file, Loader=yaml.FullLoader)

            # print(local_params)
            # print("PULLED_PARAMS: ")
            remote_params = ps_source.get_params(path=args.key,
                                                 recursive=args.recurse,
                                                 decryption=args.decrypt)
            remote_dict = yaml.load(
                yaml.dump(remote_params), Loader=yaml.FullLoader)
            # print(remote_dict)

            if local_params == remote_dict:
                print('Parameters are identical')
                exit
            else:
                print('The Following Parameters will be added: \n')
                diff_list = []
                for i in local_params:
                    if i not in remote_dict:
                        print('New Entry: ')
                        print(yaml.dump(i))
                        diff_list += [i]

                val = input('Type \'apply\' to perform the update:')
                if val == 'apply':
                    print("APPLYING UPDATE")
                    for i in diff_list:
                        ps_source.put_param(i, overwrite=True)

                    print("Updating local", args.file, " to match AWS order:")
                    keys = ps_source.get_params(path=args.key, recursive=args.recurse,
                                                decryption=args.decrypt)
                    ps_source.dump_params()

                else:
                    print("Aborting update")

    else:
        print('No local parameters found')
        print('Reading parameters and creating', args.file)
        keys = ps_source.get_params(path=args.key, recursive=args.recurse,
                                    decryption=args.decrypt)
        ps_source.dump_params(file_name=args.file)
        # ps_source.print_params()
