#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command Line Interface."""
from argparse import ArgumentParser
from sys import stderr

from special_json_to_odk_choices.definitions.error import PackageException
from special_json_to_odk_choices.special_json_to_odk_choices import run


def get_parser():
    """Add required fields to parser.

    Returns:
        ArgumentParser: Argeparse object.
    """
    package_description = 'Extract ODK choice options from a special ' \
                          'proprietary JSON format from another CAPI platform.'
    parser = ArgumentParser(description=package_description)

    input_json_help = 'Input JSON file.'
    parser.add_argument('-i', '--input-json', nargs='+', help=input_json_help)

    out_help = ('Path to save output file. If not present, same directory of'
                'any input files passed will be used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    return parser


def cli():
    """Command line interface for package.

    Side Effects: Executes program.

    Command Syntax:

    Examples:

    """
    parser = get_parser()
    kwargs = parser.parse_args()

    try:
        run(in_paths=kwargs.input_json,
            outpath=kwargs.outpath)
    except PackageException as err:
        err = 'An error occurred.\n\n' + str(err)
        print(err, file=stderr)


if __name__ == '__main__':
    cli()
