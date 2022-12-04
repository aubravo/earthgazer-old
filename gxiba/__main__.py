#! /usr/bin/env python
# -*- coding: utf-8 -*-

from arbutus import Arbutus
import sys
sys.path.append('.')

if __name__ == "__main__":
    command_line_parser = Arbutus()
    command_line_parser.from_yaml('./config/cli.yaml')
    command_line_parser.parse_args()
