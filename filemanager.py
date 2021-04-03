import json
import yaml
import os.path
# from ruamel.yaml import YAML

# yaml = YAML(typ='safe')


class FileManagerError(Exception):
    """Base class for exceptions in this module."""
    pass


# TODO: Get rid of this trash about testing the file formats and create a
# generic interface, so adding file-type support is easier
class FileManager:

    yamls = ['yaml', 'yml']

    def __init__(self, file_name='parameters.yml'):
        self.fname = file_name
        fformat = file_name.split('.')[-1]
        if fformat in self.yamls:
            self.format = 'yaml'
        elif fformat == 'json':
            self.format = 'json'
        else:
            raise FileManagerError('Invalid File Format!')

        # print("format: ", self.format)
        self.data = {}

    # Reads file into a pyton Dict
    def read(self):
        if not os.path.isfile(self.fname):
            raise FileManagerError('File not found: ', self.fname)
        with open(self.fname, 'r') as file:
            if self.format == 'yaml':
                # print("Reading yaml")
                self.data = yaml.safe_load(file)
            elif self.format == 'json':
                # print("Reading JSON")
                self.data = json.load(file)

        return self.data

    def write(self, data={}):

        if data is not None:
            # print("write: setting data")
            self.data['Parameters'] = data

        with open(self.fname, 'w') as file:
            if self.format == 'yaml':
                # print("write: writing yaml")
                yaml.dump(self.data, file)
            elif self.format == 'json':
                # print("write: writing json")
                json.dump(self.data, file, indent=4)


# Test harness
# This needs serious attention
if __name__ == '__main__':
    fm = FileManager(file_name='parameters.yml')

    fm2 = FileManager(file_name='parameters2.yml')

    data = fm.read()

    print(data)
    fm2.write(data)
