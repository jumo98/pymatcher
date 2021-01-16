# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 18:22:45 2020

@author: Julian Motz
"""
import logging
import math
import time
import pandas as pd
import numpy as np


class Data():
    """
    Basic class to store ideal functions
    from csv file in memory as DataFrame.

    Parameters
    ----------
    ideal_data : pandas.DataFrame
        Contains the ideal functions stored as a DataFrame.

    Returns
    -------
    None.
    """

    def __init__(self, ideal_data):
        # Create logger first
        self.logger = logging.getLogger(__name__)

        if not isinstance(ideal_data, pd.DataFrame):
            self.logger.error(
                f"Wrong datatype of ideal functions: {type(ideal_data)}")
            raise TypeError(type(ideal_data))

        self._ideal_functions = ideal_data

    def iter_ideal(self):
        return self._ideal_functions.iteritems()

    def _squared_error(self, training_data, ideal_data):
        """
        Calculates Squared Errors for
        two ndarrays with one column or for two values.
        Types of arguments have to match.

        Parameters
        ----------
        training_data : numpy.ndarray or numpy.float64
            Numpy array with one column containing
            the training data or one float value.

        ideal_data : numpy.ndarray or numpy.float64
            Numpy array with one column containing
            the ideal function data or one float value.

        Returns
        -------
        numpy.ndarray or numpy.float64
            Resulting array with deviations
            for each row or single deviation value
        """
        training_type = type(training_data)
        ideal_type = type(ideal_data)

        # Type mismatch
        if training_type != ideal_type:
            msg = "Input objects are of different types"
            self.logger.error(msg, (training_type, ideal_type))
            raise TypesDoNotMatchException(msg, (training_type, ideal_type))

        if isinstance(training_data, np.ndarray) &\
           isinstance(ideal_data, np.ndarray):
            # Raise exception if size does not match
            if training_data.size != ideal_data.size:
                msg = "Datasets contain different amount of points"
                self.logger.error(msg, (training_data.size, ideal_data.size))
                raise IndexCountDoesNotMatchException(msg, (training_data.size,
                                                            ideal_data.size))

            # Calculate all y-deviations squared
            return np.square(np.subtract(training_data, ideal_data))

        elif (isinstance(training_data, np.float64) &
              isinstance(ideal_data, np.float64)):
            # Calculate y-deviation squared
            return math.pow((training_data - ideal_data), 2)

        else:
            # Other types are not supported
            self.logger.error("Types not supported: " +
                              f"{training_type}{ideal_type}")
            raise TypeError(training_type, ideal_type)

    def ideal_column_by_name(self, name):
        """
        Returns column by name.

        Parameters
        ----------
        name : str
            Name of column.

        Returns
        -------
        pandas.DataFrame
            Single column DataFrame
        """
        return self._ideal_functions[name]


class TrainingData(Data):
    """
    Stores training data and ideal functions
    provides function for finding ideal function
    to each training dataset.

    Parameters
    ----------
    training_data : pandas.DataFrame
        Contains the training data stored as a DataFrame.

    ideal_data : pandas.DataFrame
        Contains the ideal functions stored as a DataFrame.

    Returns
    -------
    None.
    """
    def __init__(self, training_data, ideal_data):
        super().__init__(ideal_data=ideal_data)
        if not isinstance(training_data, pd.DataFrame):
            self.logger.error(
                f"Wrong datatype of training data: {type(training_data)}")
            raise TypeError(type(training_data))

        self._training_data = training_data

    def iter_training(self):
        """
        Returns iterator for training data.

        Returns
        -------
        label: object
            The column names for the DataFrame being iterated over.

        content: Series
            The column entries belonging to each label, as a Series.
        """
        return self._training_data.iteritems()

    def training_columns(self):
        """
        Returns columns of training data.

        Returns
        -------
        list
            List of columns, e.g.
            ['y1','y2',..]
        """
        return list(self._training_data)

    def find_ideal_functions(self):
        """
        Finds ideal function for each training data column
        by calculating the sum of squared y-deviations.
        """

        self.logger.info("Finding ideal functions...")
        # Retrieve existing columns in training data
        function_columns = self.training_columns()

        # Create deviations dataframe which saves deviation between
        # function and chosen ideal function for each training function
        deviations = pd.DataFrame(columns=function_columns)

        result_frames = []
        frame_index = ("maximum_deviation", "ideal_function")

        for _, training_set in self.iter_training():
            # Track time per loop
            t0 = time.time()
            self.logger.info(
                f"Finding ideal function for {training_set.name}.")
            # Initialize minimum value to -1 for each
            # training iteration
            min_dev_sum = -1

            # Convert to numpy array for faster calculation
            training_data_np = training_set.to_numpy()

            # Iterate over ideal functions
            for _, ideal_function in self.iter_ideal():
                # Convert to numpy array for faster calculation
                ideal_data_np = ideal_function.to_numpy()

                dev = self._squared_error(training_data=training_data_np,
                                          ideal_data=ideal_data_np)
                dev_sum = dev.sum()

                # If first iteration or sum smaller
                # then previous min set as new min
                if min_dev_sum == -1 or dev_sum < min_dev_sum:
                    min_dev = dev
                    min_dev_sum = dev_sum
                    min_name = ideal_function.name

            # Save ideal function and maximum deviation
            result_frames.append(pd.DataFrame(data={training_set.name:
                                                    [min_dev.max(),
                                                     min_name]},
                                              index=frame_index))

            # Save minimal deviation array for visualizing
            deviations[training_set.name] = min_dev

            t1 = time.time()
            total = (t1-t0)/1000
            self.logger.info(f"Ideal function for {training_set.name} " +
                             f"is {min_name}. Found after {total}ms.")

        # Save deviations for visualization
        self._deviations = deviations
        self.logger.info("Finding ideal functions...Done")

        # Return resulting ideal functions and maxmium deviations
        return pd.concat(result_frames, axis=1, sort=False)

    def deviations(self):
        """
        Returns saved deviations.
        """
        return self._deviations


class TestData(Data):
    """
    Stores ideal functions and
    provides function for mapping test points to
    each found ideal function.
    """
    def map_to_functions(self, result_data, test_filepath):
        """
        Maps test points to previously identified
        ideal functions.

        Parameters
        ----------
        result_data : pandas.DataFrame
            Contains the results data stored as a DataFrame.

        test_filepath : str
            Path where test data is stored.

        Returns
        -------
        mapping_results : pandas.DataFrame
            Contains the mapping results table.
        """
        self.logger.info("Mapping process...")
        t0 = time.time()
        # Create results frame
        result_columns = ['X', 'Y', 'Delta Y', 'No. of ideal func']
        result_df = pd.DataFrame(columns=result_columns)

        # Read test data line by line with chunksize set to 1
        row_reader = pd.read_csv(filepath_or_buffer=test_filepath, chunksize=1)

        # Iterate row by row
        for row in row_reader:
            # Read x and y values from row
            x = row['x'].iloc[0]
            y = row['y'].iloc[0]

            # Set helper variable 'matched' to False
            # Indicates if test point has been matched at least once
            matched = False
            for _, result_column in result_data.iteritems():
                # Extract ideal function name
                ideal_f_name = result_column["ideal_function"]

                # Extract maximum deviation of ideal function
                f_max_deviation = result_column["maximum_deviation"]
                f_values = self.ideal_column_by_name(ideal_f_name)

                # Calculate deviation at position x
                dev = self._squared_error(training_data=y,
                                          ideal_data=f_values[x])

                # Check mapping criterion for calculated deviation
                if self._mapping_criterion(deviation=dev,
                                           max_deviation=f_max_deviation):
                    # Append result row if complies criterion
                    data_row = self._create_result_row(x=x,
                                                       y=y,
                                                       delta_y=math.sqrt(dev),
                                                       no=ideal_f_name)
                    result_df = result_df.append(data_row, ignore_index=True)
                    matched = True

            # If no function complies criterion append row without result
            if not matched:
                data_row = self._create_result_row(x=x, y=y, delta_y="", no="")
                result_df = result_df.append(data_row, ignore_index=True)

        t1 = time.time()
        total = (t1-t0)/1000
        self.logger.info(f"Mapping process done after {total}ms.")
        return result_df

    def _mapping_criterion(self, deviation, max_deviation):
        """
        Checks if complies mapping criterion.

        Parameters
        ----------
        deviation : numpy.float64
            Calculated deviation between test point and
            ideal function.

        max_deviation : numpy.float64
            Previously calculated maximum deviation between
            training data and ideal function.

        Returns
        -------
        result : Boolean
            Complies criterion or not.
        """
        if ((deviation*math.sqrt(2)) <= max_deviation):
            return True
        else:
            return False

    def _create_result_row(self, x, y, delta_y, no):
        """
        Returns row for results table.

        Parameters
        ----------
        x : numpy.float64
            X-value of test point.

        y : numpy.float64
            Y-value of test point.

        delta_y : numpy.float64
            Calculated deviation between test point
            and ideal function.

        no : str
            Name of ideal function.

        Returns
        -------
        row : dict
            Row containing data above to store in DataFrame.
        """
        return {'X': x,
                'Y': y,
                'Delta Y': delta_y,
                'No. of ideal func': no}


class IndexCountDoesNotMatchException(Exception):
    """
    Raised when the count of index entries of multiple
    DataFrames are not equal.

    Attributes:
        message -- explanation of error
        index_counts -- counts for all indices
    """
    def __init__(self, message=None, *index_counts):
        # Calling the base class constructor with the parameter it needs
        super().__init__(message)

        # Save index counts
        self.index_counts = index_counts


class TypesDoNotMatchException(Exception):
    """
    Raised when argument types do not match while
    calculating the squared error.

    Attributes:
        message -- explanation of error
        types -- types of all arguments
    """
    def __init__(self, message=None, *types):
        # Calling the base class constructor with the parameter it needs
        super().__init__(message)

        # Save types
        self.types = types
