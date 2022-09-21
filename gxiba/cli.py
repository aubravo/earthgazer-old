"""
Parameter handling from CLI
"""
import argparse


class CLI:
    REQUIRED = 0
    HIDDEN = 1

    def __init__(self):
        self.main_branch = argparse.ArgumentParser()

    def parse_args(self):
        return vars(self.main_branch.parse_args())

    def add_node(self, node_name: str, branch_name: str = 'main', destination_attr: str = None):
        if destination_attr:
            self.__dict__[node_name + '_node'] = \
                self.__dict__[branch_name + '_branch'].add_subparsers(dest=destination_attr)
        else:
            self.__dict__[node_name + '_node'] = self.__dict__[branch_name + '_branch'].add_subparsers(dest=node_name)

    def get_branch(self, branch_name: str) -> argparse.ArgumentParser:
        return self.__dict__[branch_name + '_branch']

    def add_branch(self, branch_name: str, node_name: str = 'main', help_text: str = None):
        self.__dict__[branch_name + '_branch'] = \
            self.__dict__[node_name + '_node'].add_parser(branch_name, help=help_text)

    def action(self, method):
        class NewAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                method(values)
        return NewAction
