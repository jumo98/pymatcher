# -*- coding: utf-8 -*-
"""
Created on Mon Dec  28 16:12:22 2020

@author: Julian Motz
"""
import pandas as pd
import json


def read_data(logger, path):
    """
    Reads data from csv file and converts
    it to a pandas.DataFrame.

    Parameters
    ----------
    path : str
        Path where csv file is stored.

    Returns
    -------
    pandas.DataFrame
        Data from CSV file as table.
    """
    try:
        data = pd.read_csv(index_col='x',
                           filepath_or_buffer=path)
    except FileNotFoundError as err:
        logger.error(f"File not found at {path}")
        raise(err)
    except KeyError as err:
        logger.error("File has no 'x'-column.")
        raise(err)

    return data


def load_config(logger, path):
    """
    Reads data from csv file and converts
    it to a pandas.DataFrame.

    Parameters
    ----------
    path : str
        Path where csv file is stored.

    Returns
    -------
    pandas.DataFrame
        Data from CSV file as table.
    """
    try:
        with open(path) as config_file:
            data = json.load(config_file)
    except FileNotFoundError as err:
        logger.error(f"File not found at {path}")
        raise(err)
    except json.decoder.JSONDecodeError as err:
        logger.error("File is not json file.")
        raise(err)

    return data


def read_string_from_config(logger, cfg, key):
    """
    Reads string from dict.

    Parameters
    ----------
    cfg : dict
        Config file containing data.

    key : str
        Key that should be searched for.

    Returns
    -------
    value : str
        Value of key.
    """
    try:
        entry = cfg[key]
    except KeyError as err:
        logger.error(f"No data found for key {key} in cfg but is required.")
        raise(err)
    if entry == "":
        msg = f"Entry for key {key} is empty."
        logger.error(msg)
        raise EmptyKeyValueException(message=msg,
                                     key=key)

    return entry


class EmptyKeyValueException(Exception):
    """
    Raised when value for key is empty.

    Attributes:
        message -- explanation of error
        key -- key where value was empty
    """
    def __init__(self, message, key):
        super().__init__(message)

        self.key = key
