"""Extract ODK choice options from a special proprietary JSON format from
another CAPI platform..
"""
import csv
import json
import os

empty_tokens = ('', '""', "''")
choice_options_key1 = 'Properties'
choice_options_key2 = 'ResponseOptionsJson'
nested_val_key = 'SubEntities'
var_name_key = 'Name'
option_name_key = 'NumericValue'
option_label_key = 'ToolTip'


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

    try:
        with open(in_path) as file:
            jsn = json.load(file)
    except json.JSONDecodeError:
        with open(in_path, encoding='utf-8-sig') as file:
            jsn = json.load(file)

    var_choice_lists = find_choice_lists_by_var(jsn)
    var_choice_lists = remove_pairs_w_empty_vals(var_choice_lists)
    for k, v in var_choice_lists.items():
        list_rows = process_choice_list_json_strings(k, v)
        for row in list_rows:
            rows.append(row)

    with open(output_path + 'choice_lists.csv', 'w+') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(rows)


def find_choice_lists_by_var(jsn):
    """Recurse"""
    var_choice_lists = {}

    if isinstance(jsn, dict):
        keys = jsn.keys()
        if choice_options_key1 in keys and \
                choice_options_key2 in jsn[choice_options_key1].keys():
            var_name = jsn[var_name_key]
            choice_list_str = jsn[choice_options_key1][choice_options_key2]
            var_choice_lists[var_name] = choice_list_str
        if nested_val_key in keys and jsn[nested_val_key] is not None:
            var_choice_lists = {
                **var_choice_lists,
                **find_choice_lists_by_var(jsn[nested_val_key])
            }

    elif isinstance(jsn, list):
        for obj in jsn:
            var_choice_lists = {
                **var_choice_lists,
                **find_choice_lists_by_var(obj)
            }

    return var_choice_lists


def remove_pairs_w_empty_vals(obj):
    """Remove keys w/ empty values from obj"""
    new_obj = {}

    for k, v in obj.items():
        if v not in empty_tokens:
            new_obj[k] = v

    return new_obj


def process_choice_list_json_strings(varname: str, choice_list_json: str):
    """Process"""
    rows = []

    # fixes malformed json in source json str: trailing comma
    corrected_json = choice_list_json\
        .replace('}, ]', '} ]')\
        .replace('},]', '}]')\
        .replace('], ]', '] ]')\
        .replace('],]', ']]')
    choices = json.loads(corrected_json)
    for option in choices:
        rows.append([
            str(varname),
            str(option[option_name_key]),
            str(option[option_label_key])
        ])

    return rows
