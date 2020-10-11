# py-paramstore
Python tool for manipulating AWS Parameter Store parameters

## Usage
```
usage: main.py [-h] [-p PROFILE | -a ARN] [-r] [-x] [-f FILE] [-g] [-u] [--region REGION] [-q] key

positional arguments:
  key                   Parameter Store Key or 'Tree' to manipulate

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        specify Profile for Source AWS account
  -a ARN, --arn ARN     ARN for source role to assume for migration
  -r, --recurse         Recurse keys, manipulating the tree (DEFAULT IS TRUE)
  -x, --decrypt         Request Decryption of parameters (DEFAULT IS FALSE)
  -f FILE, --file FILE  File for specifying parameters. Defaults to parameters.yml
  -g, --get             Pull Parameters, saving to local file
  -u, --update          Push Parameter updates from local file
  --region REGION       AWS Region for migration (defaults to us-east-1)
  -q, --quiet           Suppress output (better for piping)
  ```

## Usage (details)

This tool can be used for pulling an putting AWS parameter store parameters.  The DEFAULT is to **NOT DECRYPT SECURE STRINGS!**
If you pass the `-x` or `--decrypt` option, your SecureStrings will be displayed or stored in **PLAINTEXT**

A general scenario for migration or updating of many parameters:
1. Pull down parameters with a command like: `python main.py "/parameter/path" -x --region "us-east-2" -g`
2. Open `parameters.yml` with your favorite editor to change parameter values.
3. Push updates with a command like `python main.py "/parameter/path" -u --region "us-east-2"`

## Development

This is a work in progress.  I'm using pipenv, so try `pipenv install --dev` if you want to hack at it.

To have a deterministic build, just `pipenv install --ignore-pipfile`

I've added a .devcontainer folder so if you have VSCode with the Remote Container extension and Docker installed,
you can have a containerized dev environemnt (right version of python + pipenv already installed).  
See https://code.visualstudio.com/docs/remote/containers#_sharing-git-credentials-with-your-container for details

## Distribution (WIP:  HERE THERE BE DRAGONS)

I'm planning on using pyenv, pipenv, and pyinstaller, so `pyinstaller main.py` (or something like it) to make the executable.  
This requires 'framework' so for your pyenv you probably have to `PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.8.2` 
to make pyinstaller work