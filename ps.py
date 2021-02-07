import boto3
from botocore.exceptions import ClientError
import yaml


class ParameterStore:
    def __init__(self, args):
        region = args.region or 'us-east-1'
        self.client = self.create_client(region, args.arn, args.profile)
        self.parameters = {'Parameters': []}

    def create_assumerole_client(self, arn, region):
        try:
            awsClient = boto3.client('sts', region)
            stsresponse = awsClient.assume_role(
                RoleArn=arn,
                RoleSessionName='crossaccountession'
            )

            # Create the client
            client = boto3.client(
                'ssm',
                region,
                aws_access_key_id=stsresponse["Credentials"]["AccessKeyId"],
                aws_secret_access_key=stsresponse["Credentials"]["SecretAccessKey"],
                aws_session_token=stsresponse["Credentials"]["SessionToken"]
            )
        except ClientError as e:
            print(e.response['Error']['Code']+':',
                  e.response['Error']['Message'])
            raise Exception(e)
        return client

    def create_profile_client(self, profile, region):
        try:
            dev = boto3.session.Session(profile_name=profile)
            client = dev.client('ssm', region)
        except ClientError as e:
            print(e.response['Error']['Code']+':',
                  e.response['Error']['Message'])
            raise Exception(e)
        return client

    def create_client(self, region='us-east-1', arn=None, profile=None):
        client = None
        if arn is None and profile is None:
            # Create client using env or . files
            try:
                client = boto3.client('ssm', region)
            except ClientError as e:
                print('printing errorcode and message:')
                print(e.response['Error']['Code']+':',
                      e.response['Error']['Message'])
                raise Exception(e)

        elif arn is not None:
            # Use ARN to switch Role and create the client
            client = self.create_assumerole_client(arn, region)

        elif profile is not None:
            # Use Profile to create a session the client
            client = self.create_profile_client(profile, region)

        return client

    def get_parameters_helper(self, path, recurse, decrypt, nextToken=''):
        if nextToken != '':
            try:
                response = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=recurse,
                    WithDecryption=decrypt,
                    NextToken=nextToken
                )
            except ClientError as error:
                print('Error getting parameters:')
                print(error)
                raise Exception(error)
        else:
            try:
                response = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=recurse,
                    WithDecryption=decrypt,
                )
            except ClientError as error:
                print('Error getting parameters:')
                print(error)
                raise Exception(error)
        return response

    def get_params(self, path='/', recursive=True, decryption=False, nextToken=''):
        parameters = {'Parameters': []}

        resp = self.get_parameters_helper(
            path, recursive, decryption, nextToken)
        # Filter the data to only the keys we care about
        # print(response['Parameters'])
        for i in resp['Parameters']:
            param = [{
                'Name': i['Name'],
                'Type': i['Type'],
                'Value': i['Value']
            }]
            parameters['Parameters'] += param

        if 'NextToken' in resp:
            parameters['Parameters'] += (self.get_params(path, recursive, decryption,
                                                         nextToken=resp['NextToken']))['Parameters']

        self.parameters = parameters

        return self.parameters

    def print_params(self):
        print(yaml.dump(self.parameters))

    def dump_params(self, file_name='parameters.yml'):
        with open(file_name, 'w') as file:
            yaml.dump(self.parameters, file)

    def put_param(self, parameter, overwrite=False):
        print('Putting Parameter: ', parameter)
        try:
            self.client.put_parameter(
                Name=parameter['Name'],
                Value=parameter['Value'],
                Overwrite=overwrite,
                Type=parameter['Type']
            )
        except ClientError as e:
            print('Dumping error code and message')
            print(e.response['Error']['Code']+':',
                  e.response['Error']['Message'])
            raise Exception(e)

    def rm_param(self, parameter):
        print('Removing Parameter: ', parameter)
        try:
            self.client.delete_parameter(Name=parameter['Name'])
        except ClientError as e:
            print('Error deleting parameters:')
            print(e)
            raise Exception(e)


if __name__ == '__main__':
    ps = ParameterStore()

    params = ps.get_params('/MAN-VIPAR/')

    # yaml.dump(params)
    print(yaml.dump(params))
