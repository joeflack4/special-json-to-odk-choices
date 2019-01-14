"""Extract ODK choice options from a special proprietary JSON format from
another CAPI platform..
"""
import csv
import json
import os

choice_options_key1 = 'Properties'
choice_options_key2 = 'ResponseOptionsJson'
nested_val_key = 'SubEntities'


# noinspection PyUnusedLocal
def run(in_paths, outpath: str = ''):
    """Process input files.

    Args:
        in_paths (str | list): Input JSON file paths.
        outpath (str): Path to save output file. If not present, same directory
            of any input files passed will be used.
    """
    if isinstance(in_paths, list):
        for jsn in in_paths:
            process_json(jsn, outpath)
    elif isinstance(in_paths, str):
        process_json(in_paths, outpath)


# noinspection PyUnusedLocal
def process_json(in_path, outpath: str = ''):
    """Process input file.

    Args:
        in_path (str): Input JSON file path.
        outpath (str): Path to save output file. If not present, same directory
            of any input files passed will be used.
    """
    if outpath:
        output_path = outpath
    else:
        output_path = os.path.dirname(in_path)

    header = ['list_name', 'name', 'label']
    rows = [header]

    with open(in_path) as file:
        jsn = json.load(file)
        choice_list_json_strings = find_choice_lists(jsn)
        for i, choice_list in enumerate(choice_list_json_strings):
            list_name = 'list' + str(i+1)
            list_rows = process_choice_list_json_strings(choice_list)
            for row in list_rows:
                rows.append([list_name] + row)

    with open(output_path + 'choice_lists.csv', 'w+') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(rows)


def find_choice_lists(jsn):
    """Recurse"""
    choice_lists = []

    if isinstance(jsn, dict):
        keys = jsn.keys()
        if choice_options_key1 in keys:
            props = jsn[choice_options_key1]
            prop_keys = props.keys()
            if choice_options_key2 in prop_keys:
                choice_list_str = jsn[choice_options_key1][choice_options_key2]
                choice_lists.append(choice_list_str)
        if nested_val_key in keys and jsn[nested_val_key] is not None:
            found = find_choice_lists(jsn[nested_val_key])
            if isinstance(found, str):  # duplicate code
                choice_lists.append(found)
            elif isinstance(found, list):
                choice_lists += found

    elif isinstance(jsn, list):
        for obj in jsn:
            found = find_choice_lists(obj)
            if isinstance(found, str):  # duplicate code
                choice_lists.append(found)
            elif isinstance(found, list):
                choice_lists += found

    return choice_lists


def process_choice_list_json_strings(choice_list_jsn_str):
    """Process"""
    rows = []

    choices = json.loads(choice_list_jsn_str)
    for option in choices:
        rows.append(
            [str(option['NumericValue']), str(option['ToolTip'])])

    return rows
