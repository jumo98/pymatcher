# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 18:18:51 2020

@author: Julian Motz
"""
import os
import os.path
import logging
import logging.config

import modules.data as data
import modules.database as db
import modules.plot as plot
import modules.utils as utils


def main():
    # Set maximal threads to eight to avoid computation problems
    os.environ['NUMEXPR_MAX_THREADS'] = '8'

    # Load logger configuration
    logging.config.fileConfig(fname='config/logger.conf')

    # Get the logger specified in the file
    logger = logging.getLogger(__name__)
    logger.info("Starting program.")

    # Read config data
    cfg = utils.load_config(logger, "config/data.json")

    # Set constant paths to where data is stored
    # Information is retrieved from config file
    logger.info("Reading config file.")
    DATA_DIR = utils.read_string_from_config(logger=logger,
                                             cfg=cfg,
                                             key="dataDir")

    TRAIN_FILE = utils.read_string_from_config(logger=logger,
                                               cfg=cfg,
                                               key="trainFile")

    IDEAL_FILE = utils.read_string_from_config(logger=logger,
                                               cfg=cfg,
                                               key="idealFile")

    TEST_FILE = utils.read_string_from_config(logger=logger,
                                              cfg=cfg,
                                              key="testFile")

    TRAIN_PATH = os.path.join(os.path.dirname(__file__),
                              DATA_DIR,
                              TRAIN_FILE)

    IDEAL_PATH = os.path.join(os.path.dirname(__file__),
                              DATA_DIR,
                              IDEAL_FILE)

    TEST_PATH = os.path.join(os.path.dirname(__file__),
                             DATA_DIR,
                             TEST_FILE)

    # Create database instance
    database = db.Database(cfg=cfg)

    # Save training data and ideal functions in db
    training_data = utils.read_data(logger=logger,
                                    path=TRAIN_PATH)
    ideal_data = utils.read_data(logger=logger,
                                 path=IDEAL_PATH)
    database.update_training_table(data=training_data)
    database.update_ideal_functions_table(data=ideal_data)

    # Initiate training process
    trainingData = data.TrainingData(training_data=training_data,
                                     ideal_data=ideal_data)
    training_result = trainingData.find_ideal_functions()

    # Initiate mapping process
    testData = data.TestData(ideal_data=ideal_data)
    test_result = testData.map_to_functions(result_data=training_result,
                                            test_filepath=TEST_PATH)

    # Save mapping results in db
    database.update_result_table(data=test_result)

    # Create plotter instance with results
    Plotter = plot.Plotter(ideal_data=ideal_data,
                           training_data=training_data,
                           training_result=training_result,
                           deviations=trainingData.deviations(),
                           test_result=test_result)

    # Plot results
    Plotter.plot_results()

    # Show results
    Plotter.show_results()

    logger.info("Program has finished.")


if __name__ == '__main__':
    main()
