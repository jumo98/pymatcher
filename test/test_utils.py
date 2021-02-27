import unittest
import logging
import json

import modules.utils as utils


class UtilsTestCases(unittest.TestCase):

    def test_read_data(self):
        logger = logging.getLogger(__name__)
        utils.read_data(logger, "data/ideal.csv")

    def test_read_data_not_found(self):
        logger = logging.getLogger(__name__)

        with self.assertRaises(FileNotFoundError):
            utils.read_data(logger, "data/not_available.csv")

    def test_read_data_wrong_fileformat(self):
        logger = logging.getLogger(__name__)

        with self.assertRaises(KeyError):
            utils.read_data(logger, "config/data.json")

    def test_load_config(self):
        logger = logging.getLogger(__name__)
        utils.load_config(logger, "config/data.json")

    def test_load_config_not_found(self):
        logger = logging.getLogger(__name__)

        with self.assertRaises(FileNotFoundError):
            utils.load_config(logger, "config/not_available.json")

    def test_load_config_no_json(self):
        logger = logging.getLogger(__name__)

        with self.assertRaises(json.decoder.JSONDecodeError):
            utils.load_config(logger, "data/test.csv")

    def test_read_string_from_config(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        utils.read_string_from_config(logger=logger,
                                      cfg=cfg,
                                      key="trainFile")

    def test_read_string_from_config_key_not_found(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")

        with self.assertRaises(KeyError):
            utils.read_string_from_config(logger=logger,
                                          cfg=cfg,
                                          key="not_found")

    def test_read_string_from_config_key_empty_key(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        cfg["test"] = ""

        with self.assertRaises(utils.EmptyKeyValueException):
            utils.read_string_from_config(logger=logger,
                                          cfg=cfg,
                                          key="test")


if __name__ == '__main__':
    unittest.main()
