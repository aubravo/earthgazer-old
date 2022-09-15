import argparse
import yaml

__version__ = '0.0.1'


def gxiba_cli():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(help='gxiba commands.', dest='command')

    # GET-IMAGES SUB PARSER
    get_images_parser = sub_parsers.add_parser('get-images',
                                               help='Pull satellite images from sentinel or landsat missions.')
    get_images_parser.add_argument('latitude', type=float)
    get_images_parser.add_argument('longitude', type=float)
    get_images_parser.add_argument('--from', type=str,
                                   help='Lookup for image starting from date in "YYYY-MM-DD" format')
    get_images_parser.add_argument('--to', type=str, help='Lookup for image until date in "YYYY-MM-DD" format')

    # CONFIG SUB PARSER
    config_parser = sub_parsers.add_parser('config', help='Configuration tools.')
    config_subparser = config_parser.add_subparsers(help='gxiba - configuration commands.', dest='subcommand')

    init_config_parser = config_subparser.add_parser('init', help='Init package configuration.')

    with open('./init.yaml', 'r') as startup:
        configuration = yaml.load(startup, Loader=yaml.SafeLoader)
    for parameter in configuration:
        config_subparser.add_parser('get-{}'.format(parameter), help=configuration[parameter]['get-help'])
        set_parameter = config_subparser.add_parser('set-{}'.format(parameter), help=configuration[parameter]['set-help'])
        for argument in configuration[parameter]['set-arguments']:
            for key in argument.keys():
                if argument[key]['kind'] == 'required':
                    prefix = ''
                else:
                    prefix = '--'
                set_parameter.add_argument('{}{}'.format(prefix, key), type=eval(argument[key]['type']),
                                           choices=eval(argument[key]['choices']), help=argument[key]['help'],
                                           default=eval(argument[key]['default']))
    arguments = parser.parse_args()

    if arguments.subcommand:
        try:
            exec('import {}'.format(arguments.command))
        except ModuleNotFoundError:
            exec('import gxiba.{} as {}'.format(arguments.command, arguments.command))
        exec('{}.process_parameters(**vars(arguments))'.format(arguments.command, arguments.subcommand.replace('-', '_')))
    else:
        exec('{}_parser.print_help()'.format(arguments.command))


if __name__ == '__main__':
    gxiba_cli()
