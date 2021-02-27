import unittest
import numpy as np
import logging

import modules.data as data
import modules.utils as utils


def get_ideal_path():
    return "./data/ideal.csv"


def get_train_path():
    return "./data/train.csv"


def _init_test_data_class():
    logger = logging.getLogger(__name__)
    ideal_data = utils.read_data(logger=logger,
                                 path=get_ideal_path())
    training_data = utils.read_data(logger=logger,
                                    path=get_train_path())
    return data.TrainingData(ideal_data=ideal_data,
                             training_data=training_data)


class DataTestCases(unittest.TestCase):

    def test_squared_error_float64_float64(self):
        data_c = _init_test_data_class()
        y1 = np.float64(2)
        y2 = np.float64(4)
        expected_dev = 4
        self.assertEqual(data_c.squared_error(y1, y2), expected_dev,
                         "Expected output to be equal")

    def test_squared_error_ndarray_ndarray(self):
        data_c = _init_test_data_class()
        y1 = np.array((2, 4, 8))
        y2 = np.array((4, 4, 4))
        expected_dev = np.array((4, 0, 16))

        np.testing.assert_allclose(data_c.squared_error(y1, y2), expected_dev)

    def test_squared_error_type_mismatch(self):
        data_c = _init_test_data_class()
        y1_f = np.float64(2)
        y1_a = np.array(2)
        y2_f = np.float64(4)
        y2_a = np.array(2)

        with self.assertRaises(data.TypesDoNotMatchException):
            data_c.squared_error(y1_f, y2_a)

        with self.assertRaises(data.TypesDoNotMatchException):
            data_c.squared_error(y1_a, y2_f)

    def test_squared_error_index_count_mismatch(self):
        data_c = _init_test_data_class()
        y1 = np.array((2, 3, 4))
        y2 = np.array((2, 4))

        with self.assertRaises(data.IndexCountDoesNotMatchException):
            data_c.squared_error(y1, y2)

    def test_squared_error_unsupported_type(self):
        data_c = _init_test_data_class()
        y1 = np.int64(2)
        y2 = np.int64(4)

        with self.assertRaises(TypeError):
            data_c.squared_error(y1, y2)


if __name__ == '__main__':
    unittest.main()
