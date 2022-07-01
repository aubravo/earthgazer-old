import yaml
import os
import logging


class ConfigReader:
    YAML = 'YAML'
    ENV = 'ENV'

    def __init__(self, **kwargs):
        allowed_keys = ['type', 'file', 'envs']
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)
        logging.info('Created a {}')
        if 'type' in self.__dict__:
            if self.type == self.YAML:
                if 'file' in self.__dict__:
                    self.values = yaml_parser(file=self.file)
                else:
                    self.values = yaml_parser()
            elif self.type == self.ENV:
                pass
            else:
                raise KeyError('Type must be one of: YAML, ENV')


def yaml_parser(file="./conf.yaml"):
    with open(file, "r") as yaml_file:
        return yaml.load(yaml_file.read(), Loader=yaml.Loader)
