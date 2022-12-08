#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Integration of all gxiba project related methods.

Project wide tools are centralized here to minimize the risk of cyclic imports.
Some of these tools are dataclasses, handlers, actions and constants, for example:
    from gxiba.DataClasses import SatelliteImage
"""

# standard library requirements
from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os

# Third party libraries
from arbutus import Arbutus
from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
import yaml

GXIBA_PATH = os.path.expanduser('~') + '/.gxiba/'

with open(GXIBA_PATH + 'gxiba_config.yaml') as gxiba_config:
    GXIBA_CONFIG = yaml.load(gxiba_config, Loader=yaml.SafeLoader)

with open('./config/init.yaml', 'r') as config_file:
    GXIBA_INIT = yaml.load(config_file, Loader=yaml.SafeLoader)


@dataclass
class SatelliteImage:
    id: str
    platform: str
    secondary_id: str
    sensing_time: datetime
    north_lat: float
    south_lat: float
    west_lon: float
    east_lon: float
    base_url: str


class Handlers:
    class Handler:
        @staticmethod
        def __get_all_parameters__() -> dict:
            return GXIBA_CONFIG

        @staticmethod
        def __get_parameter__(parameter: str) -> str:
            return Handlers.Handler.__get_all_parameters__()[parameter]

        @staticmethod
        def __set_parameter__(parameter: str, value) -> None:
            params = Handlers.Handler.__get_all_parameters__()
            params[parameter] = value
            with open(GXIBA_PATH + 'gxiba_config.yaml', 'w') as gxiba_config_file:
                yaml_dump = yaml.dump(params, Dumper=yaml.SafeDumper)
                gxiba_config_file.write(yaml_dump)

        @staticmethod
        def __set_parameters_from_dict__(parameters: dict, init: bool = False) -> None:
            if init:
                params = parameters
            else:
                params = Handlers.Handler.__get_all_parameters__()
                for parameter, value in parameters.items():
                    params[parameter] = value
            with open(GXIBA_PATH + 'gxiba_config.yaml', 'w') as gxiba_config_file:
                yaml_dump = yaml.dump(params, Dumper=yaml.SafeDumper)
                gxiba_config_file.write(yaml_dump)

        @staticmethod
        def __get_init__() -> dict:
            return GXIBA_INIT

    class GoogleHandler(Handler):
        @staticmethod
        def __get_credentials__():
            with open(Handlers.GoogleHandler.__get_parameter__('keys-path'), 'r') as keys:
                return service_account.Credentials.from_service_account_info(
                    json.loads(keys.read()), scopes=["https://www.googleapis.com/auth/cloud-platform"])

    class BigQuery(GoogleHandler):
        LANDSAT = 'LANDSAT'
        SENTINEL_2 = 'SENTINEL-2'
        __client__: bigquery.Client = None
        __job_config__: bigquery.QueryJobConfig = None

        class InvalidPlatformError(Exception):
            pass

        def __init__(self):
            logging.debug('Attempting to create BigQuery handler')
            credentials = super().__get_credentials__()
            logging.info('Successfully retrieved credentials file')
            self.__client__ = bigquery.Client(credentials=credentials, project=credentials.project_id)
            self.__job_config__ = bigquery.QueryJobConfig(use_query_cache=False)
            logging.debug('BigQuery handler Created')

        def query(self, query: str):
            logging.debug('Attempting to execute query:\n\t{}'.format(query))
            return self.__client__.query(query, job_config=self.__job_config__)

    class Storage(GoogleHandler):
        __bucket__: str = None
        __client__: storage.Client = None

        def __init__(self):
            logging.debug('Attempting to create Storage handler')
            credentials = super().__get_credentials__()
            logging.info('Successfully retrieved credentials file')
            bucket_path = super().__get_parameter__('gs-bucket')
            logging.info('Using {} bucket'.format(bucket_path))
            self.__client__ = storage.Client(credentials=credentials, project=credentials.project_id)
            self.__bucket__ = self.__client__.get_bucket(bucket_path)
            logging.info('Successfully created storage handler')


class GxibaCLIActions:
    """
    Collection of Actions for the gxiba CLI
    """
    @staticmethod
    @Arbutus.new_action
    def set_parameter(*args, **kwargs):
        try:
            Handlers.Handler.__set_parameter__(kwargs['values'][0], kwargs['values'][1])
        except FileNotFoundError:
            raise FileNotFoundError('No configuration file found. Try running "gxiba config init" first.')

    @staticmethod
    @Arbutus.new_action
    def get_parameter(*args, **kwargs):
        try:
            print(Handlers.Handler.__get_all_parameters__()[kwargs['value']])
        except KeyError:
            print('Parameter {} not recognized. '
                  'Try "gxiba config list-parameters" to see available parameters.'.format(kwargs['values']))

    @staticmethod
    @Arbutus.new_action
    def get_description(*args, **kwargs):
        try:
            print(Handlers.Handler.__get_init__()[kwargs['values']]['help'])
        except KeyError:
            print('Parameter {} not recognized. '
                  'Try "gxiba config list-parameters" to see available parameters.'.format(kwargs['values']))

    @staticmethod
    @Arbutus.new_action
    def list_parameters(*args, **kwargs):
        parameters = Handlers.Handler.__get_all_parameters__()
        for parameter in parameters:
            print(parameter)

    @staticmethod
    @Arbutus.new_action
    def get_all_parameters(*args, **kwargs):
        parameters = Handlers.Handler.__get_all_parameters__()
        for parameter in parameters:
            print(' - {:<30}{}'.format(parameter + ':', parameters[parameter]))

    @staticmethod
    @Arbutus.new_action
    def reset_parameters(*args, **kwargs):
        if os.path.exists(GXIBA_PATH + 'gxiba_config.yaml'):
            print('''This will reset configuration file to it's initial values.''')
            answer = input('Do you want to continue? [Y/n]')
            if answer.upper() == 'Y':
                init_file_parameters = {}
                for parameter, value in Handlers.Handler.__get_init__().items():
                    init_file_parameters[parameter] = value['default']
                Handlers.Handler.__set_parameters_from_dict__(init_file_parameters)
        else:
            print('Configuration file doesnt exist, did you mean: "gxiba config init"?')

    @staticmethod
    @Arbutus.new_action
    def init(*args, **kwargs):
        if os.path.exists(GXIBA_PATH + 'gxiba_config.yaml'):
            print('Configuration file already exists, did you mean: "gxiba config reset"?')
        else:
            os.makedirs(GXIBA_PATH, exist_ok=True)
            init_file_parameters = {}
            for parameter, value in Handlers.Handler.__get_init__().items():
                init_file_parameters[parameter] = value['default']
            Handlers.Handler.__set_parameters_from_dict__(init_file_parameters, True)

    @staticmethod
    @Arbutus.new_action
    def error(*args, **kwargs):
        raise Exception('Test Exception raised from CLI.')
