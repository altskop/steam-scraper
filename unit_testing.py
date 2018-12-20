import unittest
from parser import game_parser
from parser import tags_parser
from parser import db_handler
from parser import common
import sqlite3
import os

TESTING_FOLDER = "parser/testing/"


class TestPercentage(unittest.TestCase):

    def test_percentage_0(self):
        target = 0
        percent = common.percentage(target, 100)
        self.assertEqual(percent, target, "0% is not calculated properly")

    def test_percentage_50(self):
        target = 50
        percent = common.percentage(target, 100)
        self.assertEqual(percent, target, "50% is not calculated properly")

    def test_percentage_100(self):
        target = 100
        percent = common.percentage(target, 100)
        self.assertEqual(percent, target, "100% is not calculated properly")


class TestYmlReader(unittest.TestCase):

    def setUp(self):
        self.file = TESTING_FOLDER+"testconfig.yml"
        self.config = common.read_config_file(self.file)

    def test_key1(self):
        self.assertEqual(self.config["KEY"],"VALUE","KEY1 value not parsed correctly")

    def test_key2(self):
        self.assertEqual(self.config["KEY_2"],"AlphanumericValue1","KEY2 value not parsed correctly")

    def test_key3(self):
        self.assertEqual(self.config["KEY-3"],"Value With Spaces","KEY3 value not parsed correctly")

    def test_key4(self):
        self.assertEqual(self.config["key-4"],"lowercase key","KEY4 value not parsed correctly")

    def test_key5(self):
        self.assertEqual(self.config["KeY5"],"value with colon : text","KEY5 value not parsed correctly")

    def test_key6(self):
        self.assertEqual(self.config["KEY-6"],"value with comment","KEY6 value not parsed correctly")

    def test_key7(self):
        self.assertEqual(self.config["KEY=7"],"key with equal sign","KEY7 value not parsed correctly")

    def test_key8(self):
        self.assertEqual(self.config["KEY8"],"value with two comments","KEY8 value not parsed correctly")

    def test_key9(self):
        self.assertEqual(self.config["KEY9"],"value/with/slashes","KEY9 value not parsed correctly")

    def test_key_emptyvalue(self):
        with self.assertRaises(KeyError):
            print(self.config["EMPTYVALUE"])

    def test_key10(self):
        self.assertEqual(self.config["KEY10"],"key-value pair after an empty row ^","KEY10 value not parsed correctly")


class TestDbHandler(unittest.TestCase):

    def setUp(self):
        self.test_db = TESTING_FOLDER+"testing_database.db"

    def test1_validate_empty_db(self):
        conn = sqlite3.connect(self.test_db)
        with conn:
            c = conn.cursor()
            with self.assertRaises(sqlite3.OperationalError):
                db_handler.DBHandler.table_verification(c)

    def test2_creating_and_validating_tables(self):
        conn = sqlite3.connect(self.test_db)
        with conn:
            c = conn.cursor()
            db_handler.DBHandler.create_tables(c)
            result = db_handler.DBHandler.table_verification(c)
            self.assertTrue(result, "Validation isn't working properly")

    def tearDown(self):
        os.remove(TESTING_FOLDER+"testing_database.db")


class TestGameParserIsRecorded(unittest.TestCase):

    def setUp(self):
        self.test_db = TESTING_FOLDER+"testing_database.db"
        self.conn = sqlite3.connect(self.test_db)
        with self.conn:
            c = self.conn.cursor()
            c.execute("create table games (id integer primary key not null);")
            c.execute("insert into games values (20);")

    def test_is_recorded_non_existent(self):
        result = game_parser.GameParser.is_not_recorded(self.conn, 10)
        self.assertTrue(result, "Is Recorded in game_parser not working")

    def test_is_recorded_multiple(self):
        result = game_parser.GameParser.is_not_recorded(self.conn, 20)
        self.assertFalse(result, "Is Recorded in game_parser not working")

    def tearDown(self):
        os.remove(TESTING_FOLDER+"testing_database.db")


class TestSecondsToString(unittest.TestCase):

    def test_10_seconds_display(self):
        result = common.seconds_to_string(10)
        self.assertEqual(result, "0:00:10", "Seconds to String not outputting desired result")


if __name__ == '__main__':
    unittest.main()
