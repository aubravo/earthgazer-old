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
        - get-all-parameters
"""

import cli as commandline
import os
import yaml

cli = commandline.CLI()
gxiba_path = os.path.expanduser('~') + '/.gxiba/'


def __get_all_parameters():
    try:
        with open(gxiba_path + 'gxiba_config.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        return configuration
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


@cli.action
def set_parameter(value, *args, **kwargs):
    try:
        with open(gxiba_path + 'gxiba_config.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        configuration[value[0]] = value[1]
        with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
            yaml_dump = yaml.dump(configuration, Dumper=yaml.SafeDumper)
            config_file.write(yaml_dump)
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


@cli.action
def get_parameter(value, *args, **kwargs):
    print(__get_all_parameters()[value])


@cli.action
def error(*args, **kwargs):
    raise Exception('Test Exception caught.\n')


@cli.action
def get_all_parameters(*args, **kwargs):
    parameters = __get_all_parameters()
    for parameter in parameters:
        print('* {:<30}{}'.format(parameter+':', parameters[parameter]))


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
        os.makedirs(gxiba_path)
        with open('./init.yaml', mode='r') as fp:
            init_file_parameters = yaml.load(fp, Loader=yaml.SafeLoader)
        config_file_parameters = {}
        for parameter in init_file_parameters:
            config_file_parameters[parameter] = init_file_parameters[parameter]['default']
        with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
            yaml_dump = yaml.dump(config_file_parameters, Dumper=yaml.SafeDumper)
            config_file.write(yaml_dump)


cli.add_node('main')

""" == GET THE IMAGES == """

cli.add_branch('get-image-metadata')
cli.add_node('get-image-metadata', 'get-image-metadata')

cli.add_branch('landsat', 'get-image-metadata')
cli.add_node('landsat', 'landsat')
cli.add_branch('point', 'landsat')
cli.get_branch('point').add_argument('latitude')
cli.get_branch('point').add_argument('longitude')

cli.add_branch('square', 'landsat')
cli.get_branch('square').add_argument('from-latitude')
cli.get_branch('square').add_argument('to-latitude')
cli.get_branch('square').add_argument('from-longitude')
cli.get_branch('square').add_argument('to-longitude')


cli.add_branch('sentinel', 'get-image-metadata')


""" == CONFIGURATION TOOLS == """

cli.add_branch('config')
cli.add_node('config', 'config')

cli.add_branch('init', 'config', help_text='Start initialization process.')
cli.get_branch('init').add_argument('none', nargs=0, action=init)

cli.add_branch('reset', 'config', help_text='Create or reset configuration file.')
cli.get_branch('reset').add_argument('none', nargs=0, action=reset_parameters)

cli.add_branch('set-parameter', 'config', help_text='Set the value of a parameter by name.')
cli.get_branch('set-parameter').add_argument('variable-name', nargs=2, action=set_parameter,
                                             help='Requires a valid variable-name and new-value')

cli.add_branch('get-parameter', 'config', help_text='Get the value of a parameter by name.')
cli.get_branch('get-parameter').add_argument('variable-name', action=get_parameter,
                                             help='Requires a valid variable-name')

cli.add_branch('get-all-parameters', 'config', help_text='Shows a list of all existing parameters and values.')
cli.get_branch('get-all-parameters').add_argument('none', nargs=0, action=get_all_parameters)

cli.add_branch('error', 'config', help_text='Simulates and exception')
cli.get_branch('error').add_argument('none', nargs=0, action=error)


if __name__ == "__main__":
    try:
        x = cli.parse_args()
        print(x)
    except Exception as e:
        print(e)
        cli.main_branch.print_help()