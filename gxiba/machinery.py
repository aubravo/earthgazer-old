from cli import CLI


def execute(cli: CLI, parameters: dict = None):
    print(cli.breadcrumbs)
    print(cli.parameters)
    print(parameters['pg-address'])
    if cli.breadcrumbs.startswith('main.config.set-parameter'):
        print('Parameter changed.')
