# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 16:21:41 2020

@author: Julian Motz
"""
import sqlalchemy
import sqlalchemy.exc
import logging
import pandas as pd

import modules.utils as utils


class Database():
    """
    Class that stores database engine and
    allows creating tables with corresponding data.

    Parameters
    ----------
    cfg : dict
        Configuration dictionary containing JSON properties.

    Returns
    -------
    None.
    """
    def __init__(self, cfg):
        # Create logger first
        self.logger = logging.getLogger(__name__)

        if not isinstance(cfg, dict):
            self.logger.error(f"Wrong datatype for cfg: {type(cfg)}")
            raise TypeError(type(cfg))

        # Read config values
        DB_NAME = utils.read_string_from_config(
            logger=self.logger, cfg=cfg,
            key="dbName")

        self.TRAINING_TABLE = utils.read_string_from_config(
            logger=self.logger, cfg=cfg,
            key="trainingDataTable")

        self.IDEAL_F_TABLE = utils.read_string_from_config(
            logger=self.logger, cfg=cfg,
            key="idealFunctionsTable")

        self.RESULTS_TABLE = utils.read_string_from_config(
            logger=self.logger, cfg=cfg,
            key="resultsTable")

        # Try to create SQLite engine
        connection_string = "sqlite:///" + DB_NAME + ".db"
        self.logger.info('Creating sqlite database engine...')
        try:
            self._engine = sqlalchemy.create_engine(connection_string)
        except sqlalchemy.exc.SQLAlchemyError as err:
            self.logger.error(err)
            raise(err)
        self.logger.info('Creating sqlite database engine...Done')

    def _connect(self):
        """
        Connect to SQLite database.

        Returns
        -------
        sqlalchemy.engine.base.Connection
            Connection to database.
        """
        self.logger.info('Connecting to db...')
        try:
            conn = self._engine.connect()
        except sqlalchemy.exc.SQLAlchemyError as err:
            self.logger.error(err)
            raise(err)

        self.logger.info('Connecting to db...Done')
        return conn

    def _save(self, connection, data, name):
        """
        Save table in SQLite db.

        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
            Connection to database.

        data : DataFrame
            Data which will be saved.

        name : str
            Name of table.

        Returns
        -------
        None.
        """
        self.logger.info(f'Saving data to table {name}.')
        try:
            data.to_sql(name=name, con=connection, if_exists="replace")
        except ValueError as err:
            self.logger.warning(err)
            raise(err)
        finally:
            connection.close()

    def _update_table(self, data, name):
        """
        Updates table.
        Creates table if not already created and
        saves it in db.

        Parameters
        ----------
        data : pandas.DataFrame
            Object where results are stored.

        name : str
            Name of table where to store data.

        Returns
        -------
        None.
        """
        if not isinstance(data, pd.DataFrame):
            self.logger.error(f"Wrong datatype for saving to db: {type(data)}")
            raise TypeError(type(data))

        conn = self._connect()
        self._save(connection=conn,
                   data=data,
                   name=name)

    def _read_table(self, name):
        """
        Reads data from a table with
        specified name.

        Parameters
        ----------
        name : str
            Name of table to read from.

        Returns
        -------
        data - pandas.DataFrame
            Table converted to pandas.DataFrame.
        """
        conn = self._connect()
        return pd.read_sql_table(table_name=name,
                                 con=conn)

    def read_training_table(self):
        """
        Reads data from the
        training table.

        Returns
        -------
        data - pandas.DataFrame
            Table converted to pandas.DataFrame.
        """
        return self._read_table(name=self.TRAINING_TABLE)

    def read_ideal_functions_table(self):
        """
        Reads data from the
        ideal functions table.

        Returns
        -------
        data - pandas.DataFrame
            Table converted to pandas.DataFrame.
        """
        return self._read_table(name=self.IDEAL_F_TABLE)

    def read_results_table(self):
        """
        Reads data from the
        results table.

        Returns
        -------
        data - pandas.DataFrame
            Table converted to pandas.DataFrame.
        """
        return self._read_table(name=self.RESULTS_TABLE)

    def update_training_table(self, data):
        """
        Updates the training data table.
        Creates table if not already created and
        saves it in db.

        Parameters
        ----------
        data : pandas.DataFrame
            Object where results are stored.

        Returns
        -------
        None.
        """
        self._update_table(data=data,
                           name=self.TRAINING_TABLE)

    def update_ideal_functions_table(self, data):
        """
        Updates the ideal functions data table.
        Creates table if not already created and
        saves it in db.

        Parameters
        ----------
        data : pandas.DataFrame
            Object where results are stored.

        Returns
        -------
        None.
        """
        self._update_table(data=data,
                           name=self.IDEAL_F_TABLE)

    def update_result_table(self, data):
        """
        Updates the results table.
        Creates table if not already created and
        saves it in db.

        Parameters
        ----------
        data : pandas.DataFrame
            Object where results are stored.

        Returns
        -------
        None.
        """
        self._update_table(data=data,
                           name=self.RESULTS_TABLE)
