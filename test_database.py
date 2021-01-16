import unittest
import logging
import pandas as pd

import modules.utils as utils
import modules.database as database


class DatabaseTestCases(unittest.TestCase):

    def test_init_valid_config(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        database.Database(cfg=cfg)

    def test_init_invalid_config(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        cfg.pop("resultsTable")

        with self.assertRaises(KeyError):
            database.Database(cfg=cfg)

    def test_update_table(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        db = database.Database(cfg=cfg)

        df = pd.DataFrame(columns=["A"])
        db._update_table(name="test",
                         data=df)

    def test_update_table_wrong_type(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        db = database.Database(cfg=cfg)

        d = 0.5

        with self.assertRaises(TypeError):
            db._update_table(name="test",
                             data=d)

    def test_read_table(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        db = database.Database(cfg=cfg)

        name = "test"
        df = pd.DataFrame(columns=["A"])
        db._update_table(name=name,
                         data=df)
        db._read_table(name=name)

    def test_read_table_not_found(self):
        logger = logging.getLogger(__name__)
        cfg = utils.load_config(logger, "config/data.json")
        db = database.Database(cfg=cfg)

        name = "not_available"
        with self.assertRaises(ValueError):
            db._read_table(name=name)


unittest.main()
