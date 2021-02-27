# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 18:22:45 2020

@author: Julian Motz
"""

import bokeh
import bokeh.plotting
import bokeh.models
import logging
import math
import sys
import win32api


class Plotter():
    """
    Plotter provides functions to plot the results.

    Parameters
    ----------
    training_data : pandas.DataFrame
        Contains training data.

    ideal_data : pandas.DataFrame
        Contains ideal functions data.

    training_result : pandas.DataFrame
        Contains training results data.

    deviations : pandas.DataFrame
        Contains calculated deviations.

    test_result : pandas.DataFrame
        Contains mapping results data.

    Returns
    -------
    None.
    """

    def __init__(self, training_data, ideal_data,
                 training_result, deviations, test_result):
        # Create logger
        self.logger = logging.getLogger(__name__)

        # Save previously read data
        self._training_data = training_data
        self._ideal_functions = ideal_data

        # Save previous results for visualization
        self._training_result = training_result
        self._deviations = deviations
        self._test_result = test_result

        # Gather system screen resolution
        self._get_screen_resolution()

        # Create empty grid to save plots
        self.grid = []

    def _get_screen_resolution(self):
        """
        Gets system screen resolution
        and sets them as class variables.
        """
        self.os = sys.platform
        if self.os == "win32":
            # Gather system dimension
            self.system_width = win32api.GetSystemMetrics(0)
            self.system_height = win32api.GetSystemMetrics(1)
        else:
            # Assume FHD monitor for other system os
            self.system_width = 1920
            self.system_height = 1080

    def _found_ideal(self, training_function):
        """
        Access found ideal function in results.

        Parameters
        ----------
        training_function : str
            Name of training function.

        Returns
        -------
        ideal_function : str
            Name of paired ideal function.
        """
        if training_function not in list(self._training_result):
            raise(KeyError(training_function))

        return self._training_result[training_function]['ideal_f']

    def _index(self):
        """
        Returns index of ideal functions.

        Returns
        -------
        index : pandas.DataFrame.index
            The index (row labels) of the ideal functions DataFrame.
        """
        return self._ideal_functions.index

    def _ideal_function_by_name(self, name):
        """
        Returns ideal function by given name.

        Parameters
        ----------
        name : str
            Name of ideal function.

        Returns
        -------
        ideal_function : pandas.DataFrame
            Data of specified ideal function.
        """
        if name not in list(self._ideal_functions):
            raise(KeyError(name))

        return self._ideal_functions[name]

    def _training_data_by_name(self, name):
        """
        Returns training data by given name.

        Parameters
        ----------
        name : str
            Name of training set.

        Returns
        -------
        training_data : pandas.DataFrame
            Data of specified training set.
        """
        if name not in list(self._training_data):
            raise(KeyError(name))

        return self._training_data[name]

    def _deviation_by_name(self, name):
        """
        Returns deviation data by given name.

        Parameters
        ----------
        name : str
            Name of training set.

        Returns
        -------
        deviation : pandas.DataFrame
            Deviation data of specified training set.
        """
        if name not in list(self._deviations):
            raise(KeyError(name))

        return self._deviations[name]

    def _training_columns(self):
        """
        Returns columns of training sets.

        Returns
        -------
        columns : list
            Contains iterable column names as strings.
        """
        return list(self._training_data)

    def _points_by_name(self, name, operator):
        """
        Returns mapped or unmapped points for training set with
        specified name and operator.

        Parameters
        ----------
        name : str
            Name of training set.

        operator : str
            Operator to select different points.

        Returns
        -------
        points : pandas.DataFrame
            DataFrame containing specified points.
        """
        if name not in list(self._training_result):
            raise(KeyError(name))

        no = self._test_result['No. of ideal func']
        res = self._training_result[name]['ideal_f']

        if operator == "==":
            return self._test_result.loc[no == res]
        elif operator == "!=":
            return self._test_result.loc[no != res]
        else:
            raise NotImplementedError(f"Operator {operator} not supported.")

    def _mapped_points_by_name(self, name):
        """
        Returns mapped points for training set with
        specified name.

        Parameters
        ----------
        name : str
            Name of training set.

        Returns
        -------
        points : pandas.DataFrame
            DataFrame containing specified points.
        """
        return self._points_by_name(name=name,
                                    operator="==")

    def _unmapped_points_by_name(self, name, m_points):
        """
        Returns unmapped points for training set with
        specified name.

        Parameters
        ----------
        name : str
            Name of training set.

        m_points : pandas.DataFrame
            DataFrame containing the mapped points.

        Returns
        -------
        points : pandas.DataFrame
            DataFrame containing specified points.
        """
        unmapped = self._points_by_name(name=name,
                                        operator="!=")

        # Drop duplicate points
        for _, row in m_points.iterrows():
            drop = (unmapped['X'] == row['X']) & (unmapped['Y'] == row['Y'])
            unmapped = unmapped.drop(unmapped[drop].index)

        return unmapped

    def plot_results(self):
        """
        Plots figures for every training function and
        saves results in class variable "grid".
        """
        # Create empty rows for the plots
        ideal_f_plot = []
        f_point_plot = []

        # Iterate over each training sequence
        for train_f in self._training_columns():
            # Plot ideal function finding
            plot_ideal = self._plot_ideal_function(training_function=train_f)

            # Gather mapped points to specific training function/ideal function
            points = self._mapped_points_by_name(name=train_f)
            unmapped_points = self._unmapped_points_by_name(name=train_f,
                                                            m_points=points)

            # Plot the mapped points
            plot_point = self._plot_mapping(training_function=train_f,
                                            points=points,
                                            unmapped_points=unmapped_points)

            # Append plots to rows
            ideal_f_plot.append(plot_ideal)
            f_point_plot.append(plot_point)

        # Save rows as grid
        self.grid = [ideal_f_plot, f_point_plot]

    def _plot_ideal_function(self, training_function):
        """
        Plots the training data, found ideal function and
        deviation between them.

        Parameters
        ----------
        training_function : str
            Name of training set.

        Returns
        ----------
        plot : bokeh.plotting.figure
        """
        self.logger.info("Plotting ideal function plot for " +
                         training_function)

        # Create figure with title
        ideal_function = self._found_ideal(training_function=training_function)
        title = f"""Training set {training_function} with
ideal function {ideal_function} and deviation"""

        ideal_f_values = self._ideal_function_by_name(ideal_function)
        y_range = (ideal_f_values.min()*1.5, ideal_f_values.max()*1.5)
        plot = self._create_labeled_figure(title=title,
                                           y_range=y_range)

        # Plot training data
        plot.line(x=self._index(),
                  y=self._training_data_by_name(training_function),
                  line_color="red",
                  legend_label="training",
                  line_width=1.25)

        # Plot ideal function
        plot.line(x=self._index(),
                  y=ideal_f_values,
                  line_width=2,
                  legend_label="ideal")

        # Plot deviation
        # plot.vbar(x=self._index(),
        #          top=self._deviation_by_name(training_function),
        #          color="black",
        #          legend_label="deviation")

        # Add legend
        plot.legend.location = "bottom_left"
        plot.legend.click_policy = "hide"

        return plot

    def _plot_mapping(self, points, unmapped_points, training_function):
        """
        Plots a figure containing found ideal function, mapped and
        unmapped points and a band area around ideal function
        illustrating the mapping criterion.

        Parameters
        ----------
        points : pandas.DataFrame
            Contains points mapped to this function.

        unmapped_points : pandas.DataFrame
            Contains points not mapped to this function.

        training_function : str
            Name of training set.

        Returns
        ----------
        plot : bokeh.plotting.figure
        """
        self.logger.info(f"Plotting point mapping for {training_function}")

        # Create figure
        ideal_function = self._found_ideal(training_function=training_function)
        title = f"Points mapped to ideal function {ideal_function}"
        ideal_f_values = self._ideal_function_by_name(ideal_function)
        y_range = (ideal_f_values.min()*1.5, ideal_f_values.max()*1.5)
        plot = self._create_labeled_figure(title=title,
                                           y_range=y_range)
        # Plot ideal function
        plot.line(x=self._index(),
                  y=ideal_f_values,
                  legend_label="ideal")

        # Plot mapped points
        point_source = bokeh.models.ColumnDataSource(points)
        plot.circle(x='X',
                    y='Y',
                    source=point_source,
                    color="red",
                    line_color="red",
                    legend_label="mapped")

        # Plot points not mapped to this function
        unmapped_point_source = bokeh.models.ColumnDataSource(unmapped_points)
        plot.circle(x='X',
                    y='Y',
                    source=unmapped_point_source,
                    color="black",
                    line_color="black",
                    legend_label="unmapped")

        # Create and plot band to visualize mapping range
        ideal_values = self._ideal_function_by_name(ideal_function).to_frame()

        # Calculate lower and upper end with the mapping criterion
        max_deviation = self._deviation_by_name(training_function).max()
        dif = math.sqrt((max_deviation/math.sqrt(2)))
        ideal_function_values = self._ideal_function_by_name(ideal_function)
        ideal_values["lower"] = ideal_function_values - dif
        ideal_values["upper"] = ideal_function_values + dif

        band_source = bokeh.models.ColumnDataSource(ideal_values)
        band = bokeh.models.Band(base='x',
                                 lower='lower',
                                 upper='upper',
                                 source=band_source,
                                 level='underlay',
                                 fill_alpha=1.0,
                                 line_width=1,
                                 line_color='black')
        plot.add_layout(band)

        # Add legend
        plot.legend.location = "bottom_left"
        plot.legend.click_policy = "hide"

        return plot

    def _create_labeled_figure(self, title, y_range):
        """
        Creates a labeled figure and dimensions that
        adjust to screen resolution

        Parameters
        ----------
        title : str
            Title of figure.

        Returns
        ----------
        plot : bokeh.plotting.figure
            Figure with specified title.
        """
        # Calculate dimension for each plot
        width = int((0.95*self.system_width)/len(self._training_columns()))
        height = int((0.8*self.system_height)/2)

        # width and height should be at least 200
        if width < 200:
            width = 200

        if height < 200:
            height = 200

        plot = bokeh.plotting.figure(plot_width=width,
                                     plot_height=height,
                                     title=title,
                                     y_range=y_range)
        plot.xaxis.axis_label = 'X'
        plot.yaxis.axis_label = 'Y'
        return plot

    def show_results(self):
        """
        Presents the results as an HTML page.
        Also saves this page in program directory.
        """
        grid_plot = bokeh.layouts.gridplot(self.grid)
        bokeh.plotting.show(grid_plot)
