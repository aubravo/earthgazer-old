import argparse

from earthgazer.constants import ProjectConstants


def show_function(args):
    if 'parameter' in args:
        if args.parameter == 'info':
            print(ProjectConstants.earthgazer_tag)
            print(ProjectConstants.short_license_disclaimer)
        elif args.parameter == 'license':
            print(ProjectConstants.long_license_disclaimer)
        elif args.parameter == 'version':
            print(ProjectConstants.earthgazer_version)
        else:
            print(f'\'{args.parameter}\' function is not supported. Try \'earthgazer show -h\' for more information.')


def config_function(args):
    from earthgazer.setup import GXIBA_CONFIGURATION
    if 'option' in args:
        if args.option == 'get':
            try:
                current_level = GXIBA_CONFIGURATION
                for attribute in args.parameter.split('.'):
                    current_level = getattr(current_level, attribute)
                print(current_level)
            except:
                print(f'Parameter \'{args.parameter}\' not found in Configuration.')
        if args.option == 'set':
            try:
                current_level = GXIBA_CONFIGURATION
                for attribute in args.parameter.split('.'):
                    current_level = getattr(current_level, attribute)
                setattr(GXIBA_CONFIGURATION,args.parameter, 'test')
                print(GXIBA_CONFIGURATION)
            except Exception as e:
                print(e)




main_parser = argparse.ArgumentParser(prog='earthgazer', )
main_parser.add_argument('-v', '--verbose', action='store_true', help='Set logging message level to Debug.')
main_subparsers = main_parser.add_subparsers()

show_subparser = main_subparsers.add_parser('show', help='Show information about the project.')
show_subparser.add_argument('parameter')
show_subparser.set_defaults(func=show_function)

config_subparser = main_subparsers.add_parser('config', help='Get and set project parameters.')
config_subparser.add_argument('option', choices=['get', 'set'])
config_subparser.add_argument('parameter')
config_subparser.set_defaults(func=config_function)

if __name__ == '__main__':
    try:
        parse_results = main_parser.parse_args()
        parse_results.func(parse_results)
    except Exception as e:
        main_parser.print_help()
