import logging
import yaml
import os

gxiba_path = os.path.expanduser('~') + '/.gxiba/'


def get_parameter(parameter):
    try:
        with open(gxiba_path + 'gxiba_config.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        return configuration[parameter]
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


def set_parameter(parameter, new_value):
    try:
        with open(gxiba_path + 'gxiba_config.yaml', 'r') as config_file:
            configuration = yaml.load(config_file, Loader=yaml.SafeLoader)
        configuration[parameter] = new_value
        with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
            yaml_dump = yaml.dump(configuration, Dumper=yaml.SafeDumper)
            config_file.write(yaml_dump)
    except FileNotFoundError:
        raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')


def init(**kwargs):
    os.makedirs(gxiba_path, exist_ok=True)
    with open('./init.yaml', mode='r') as fp:
        init_parameters = yaml.load(fp, Loader=yaml.SafeLoader)
    parameter_dict = {}
    for parameter in init_parameters:
        for argument in init_parameters[parameter]['set-arguments']:
            parameter_dict.update({parameter: eval(argument[parameter]['default'])})
    with open(gxiba_path + 'gxiba_config.yaml', 'w') as config_file:
        yaml_dump = yaml.dump(parameter_dict, Dumper=yaml.SafeDumper)
        config_file.write(yaml_dump)


def process_parameters(**kwargs):
    command = kwargs['subcommand'].split('-')[0]
    if command == 'set':
        parameter = kwargs['subcommand'][4:]
        new_value = kwargs[parameter]
        set_parameter(parameter, new_value)

    elif command == 'get':
        parameter = kwargs['subcommand'][4:]
        print(get_parameter(parameter))

    else:
        exec('{}(**kwargs)'.format(kwargs['subcommand']))
