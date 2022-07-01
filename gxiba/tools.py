import os


def get_env_vars(required_vars):
    try:
        return {var: os.environ[var] for var in required_vars}
    except KeyError:
        raise KeyError('One or more of the required ENVIRONMENT VARIABLES was not found:\n{}'.format(required_vars))
