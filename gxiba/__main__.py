"""
== Gxiba CLI structure ==

- gxiba
    - get-image-metadata
        -landsat
            - point
            - square
        -sentinel
            - point
            - square
    - config
        - init
        - reset
        - set-parameter
        - get-parameter
        - get-description
        - list-parameters
        - get-all-parameters
"""

import cli as commandline
import os
import yaml
import machinery

cli = commandline.CLI()
gxiba_path = os.path.expanduser('~') + '/.gxiba/'


def __get_all_parameters():
    try:
        with open(gxiba_path + 'gxiba_config.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        return configuration
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


def __get_init():
    try:
        with open('./init.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        return configuration
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


@cli.action
def set_parameter(*args, **kwargs):
    try:
        with open(gxiba_path + 'gxiba_config.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        configuration[kwargs['values'][0]] = kwargs['values'][1]
        with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
            yaml_dump = yaml.dump(configuration, Dumper=yaml.SafeDumper)
            config_file.write(yaml_dump)
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


@cli.action
def get_parameter(*args, **kwargs):
    try:
        print(__get_all_parameters()[kwargs['values']])
    except KeyError:
        print('Parameter {} not recognized. '
              'Try "gxiba config list-parameters" to see available parameters.'.format(kwargs['values']))


@cli.action
def get_description(*args, **kwargs):
    try:
        print(__get_init()[kwargs['values']]['help'])
    except KeyError:
        print('Parameter {} not recognized. '
              'Try "gxiba config list-parameters" to see available parameters.'.format(kwargs['values']))


@cli.action
def list_parameters(*args, **kwargs):
    parameters = __get_all_parameters()
    for parameter in parameters:
        print(parameter)


@cli.action
def get_all_parameters(*args, **kwargs):
    parameters = __get_all_parameters()
    for parameter in parameters:
        print('* {:<30}{}'.format(parameter + ':', parameters[parameter]))


@cli.action
def reset_parameters(*args, **kwargs):
    if os.path.exists(gxiba_path + 'gxiba_config.yaml'):
        print('''This will reset configuration file to it's initial values.''')
        answer = input('Do you want to continue? [Y/n]')
        if answer.upper() == 'Y':
            with open('./init.yaml', mode='r') as fp:
                init_file_parameters = yaml.load(fp, Loader=yaml.SafeLoader)
            config_file_parameters = {}
            for parameter in init_file_parameters:
                config_file_parameters[parameter] = init_file_parameters[parameter]['default']
            with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
                yaml_dump = yaml.dump(config_file_parameters, Dumper=yaml.SafeDumper)
                config_file.write(yaml_dump)
    else:
        print('Configuration file doesnt exist, did you mean: "gxiba config init"?')


@cli.action
def init(*args, **kwargs):
    if os.path.exists(gxiba_path + 'gxiba_config.yaml'):
        print('Configuration file already exists, did you mean: "gxiba config reset"?')
    else:
        os.makedirs(gxiba_path, exist_ok=True)
        with open('./init.yaml', mode='r') as fp:
            init_file_parameters = yaml.load(fp, Loader=yaml.SafeLoader)
        config_file_parameters = {}
        for parameter in init_file_parameters:
            config_file_parameters[parameter] = init_file_parameters[parameter]['default']
        with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
            yaml_dump = yaml.dump(config_file_parameters, Dumper=yaml.SafeDumper)
            config_file.write(yaml_dump)


@cli.action
def error(*args, **kwargs):
    raise Exception('Test Exception caught.\n')


""" == GET THE IMAGES == """
cli.add_branch('get-image-metadata')
cli.add_branch('landsat', 'get-image-metadata')
cli.add_branch('point', 'landsat')
cli.get_branch('point').add_argument('latitude')
cli.get_branch('point').add_argument('longitude')

cli.add_branch('square', 'landsat')
cli.get_branch('square').add_argument('from-latitude')
cli.get_branch('square').add_argument('to-latitude')
cli.get_branch('square').add_argument('from-longitude')
cli.get_branch('square').add_argument('to-longitude')

cli.add_branch('sentinel', 'get-image-metadata')
cli.add_branch('point', 'sentinel')
cli.get_branch('point').add_argument('latitude')
cli.get_branch('point').add_argument('longitude')

cli.add_branch('square', 'sentinel')
cli.get_branch('square').add_argument('from-latitude')
cli.get_branch('square').add_argument('to-latitude')
cli.get_branch('square').add_argument('from-longitude')
cli.get_branch('square').add_argument('to-longitude')

""" == CONFIGURATION TOOLS == """

cli.add_branch('config')
cli.add_branch('init', 'config', help_text='Start initialization process.').add_argument('none', nargs=0, action=init)
cli.add_branch('reset', 'config', help_text='Create or reset configuration file.'
               ).add_argument('none', nargs=0, action=reset_parameters)
cli.add_branch('set-parameter', 'config', help_text='Set the value of a parameter by name.'
               ).add_argument('parameter-name', nargs=2, action=set_parameter,
                              help='Requires a valid parameter-name and new-value')
cli.add_branch('get-parameter', 'config', help_text='Get the value of a parameter by name.'
               ).add_argument('parameter-name', action=get_parameter, help='Requires a valid parameter-name')
cli.add_branch('get-description', 'config', help_text='Get the description of a parameter by name.'
               ).add_argument('parameter-name', action=get_description, help='Requires a valid parameter-name')
cli.add_branch('list-parameters', 'config', help_text='Get a list of all available parameters.'
               ).add_argument('none', nargs=0, action=list_parameters, help='Requires a valid parameter-name')
cli.add_branch('get-all-parameters', 'config', help_text='Shows a list of all existing parameters and values.'
               ).add_argument('none', nargs=0, action=get_all_parameters)
cli.add_branch('error', 'config', help_text='Simulates and exception'
               ).add_argument('none', action='store_true')

if __name__ == "__main__":
    try:
        cli.parse_args()
        machinery.execute(cli, __get_all_parameters())
    except Exception as e:
        cli.main_branch.print_help()
        raise Exception(e)
