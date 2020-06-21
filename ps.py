import boto3
from botocore.exceptions import ClientError
import yaml


class ParameterStore:
    def __init__(self, region='us-east-1', arn=None, profile=None):
        self.client = self.create_client(region, arn, profile)

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

        elif profile is not None:
            # Use Profile to create a session the client
            try:
                dev = boto3.session.Session(profile_name=profile)
                client = dev.client('ssm', region)
            except ClientError as e:
                print(e.response['Error']['Code']+':',
                      e.response['Error']['Message'])
                raise Exception(e)

        return client

    def get_params(self, path='/', recursive=True, decryption=False, next=''):
        self.parameters = []

        if next != '':
            try:
                response = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=recursive,
                    WithDecryption=decryption,
                    NextToken=next
                )
            except ClientError as error:
                print('Error getting parameters:')
                print(error)
        else:
            response = self.client.get_parameters_by_path(
                Path=path,
                Recursive=recursive,
                WithDecryption=decryption,
            )
        
        # Filter the data to only the keys we care about
        # print(response['Parameters'])
        for i in response['Parameters']:
            param = [{
                'Name': i['Name'],
                'Type': i['Type'],
                'Value': i['Value']
            }]
            self.parameters += param

        if 'NextToken' in response:
            self.parameters += (self.get_params(path, recursive, decryption,
                                                next=response['NextToken']))

        return self.parameters

    def print_params(self):
        print(yaml.dump(self.parameters))

    def dump_params(self, file_name='parameters.yml'):
        with open(file_name, 'w') as file:
            documents = yaml.dump(self.parameters, file)

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
            exit(-2)

    def rm_param(self, parameter):

        self.client.delete_parameter(parameter['Name'])


if __name__ == '__main__':
    ps = ParameterStore()

    # print(json.dumps(ps.get_params('/team-rocket/'), indent=2))
    
    params = ps.get_params('/MAN-VIPAR/')
    # yaml.dump(params)
    print(yaml.dump(params))


    # for i in params:
    #     print("NAME: ", i['Name'])
    #     print("\tType: ", i['Type'])
    #     print("\tValue: ", i['Value'])
    #     print("\tVersion: ", i['Version'])

    # file = open("settlement-kv-export.json", 'r')
    # print(json.dumps(json.load(file), indent=2))

    #  Create Class and test it

    # param_list = get_param_page(
    #     client=pp,
    #     path='/team-rocket/',
    #     recursive=True,
    #     decryption=True
    # )
