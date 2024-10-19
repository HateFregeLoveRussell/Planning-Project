import os
import unittest
import json
from pathlib import Path
from DiscretePlanning.planningSearchVisualization import SearchLogger

class TestSearchLogger(unittest.TestCase):
    def setUp(self):
        self.existing_dir = Path("Tests/TestPath")
        self.existing_dir.mkdir(exist_ok=True)
        self.non_existing_dir = Path("non_existing_logs")
        self.logFile = self.existing_dir / "test_log.json"
        self.non_existing_log_file = self.non_existing_dir / "test_log.json"

    def tearDown(self):
        if self.logFile.exists():
            os.remove(self.logFile)
        if self.non_existing_log_file.exists():
            os.remove(self.non_existing_log_file)
        if self.existing_dir.exists():
            os.rmdir(self.existing_dir)
        if self.non_existing_dir.exists():
            os.rmdir(self.non_existing_dir)
    #init
    def test_logger_init_success(self):
        self.logger = SearchLogger(self.logFile)
        self.assertTrue(self.logger.logFile,self.logFile)
        self.assertEqual(self.logger.log_entries, [])

    #logState
    def test_logger_logState_basic_success(self):
        event = "expand_node"
        entry = {"current_state": "A", "frontier": ["B", "C"], "explored": ["A"]}

        logger = SearchLogger(self.logFile)
        logger.logState(event, entry)

        self.assertEqual(len(logger.log_entries), 1)
        self.assertEqual(logger.log_entries[0]["Event"], event)
        self.assertEqual(logger.log_entries[0]["Entry"], entry)

    def test_logger_logState_invalid_key(self):
        event = "expand_node"
        entry = {(1,2): "A", "another entry": 123}
        logger = SearchLogger(self.logFile)

        logger.logState(event, entry)

        expectedEntry = {"(1, 2)": "A", "another entry": 123}
        self.assertEqual(logger.log_entries[0]["Entry"], expectedEntry)

    def test_logger_logState_invalid_value(self):
        event = "expand_node"
        logger = SearchLogger(self.logFile)

        class MyClass:
            def __repr__(self):
                return "MyClass()"

        entry = {"state": "A", "non_serializable": MyClass()}

        logger.logState(event, entry)

        expectedEntry = {"state": "A", "non_serializable": "MyClass()"}
        self.assertEqual(logger.log_entries[0]["Entry"], expectedEntry)

    def test_logger_logState_invalid_entry(self):
        event = "expand_node"
        logger = SearchLogger(self.logFile)

        class FaultyClass:
            def __repr__(self):
                raise ValueError("Cannot represent")

        entry = {"state": "A", "faulty_value": FaultyClass()}
        logger.logState(event, entry)

        self.assertEqual(logger.log_entries[0]["Entry"]["faulty_value"], "<unrepresentable object of type FaultyClass>")

    def test_logger_logState_nested_entry(self):
        event = "expand_node"
        logger = SearchLogger(self.logFile)

        entry = {
            "state": "A",
            "details": {
                "frontier": ["B", "C"],
                "explored": ["A"],
                (1, 2): {"nested_key": "value"}
            }
        }

        logger.logState(event, entry)

        expectedEntry = {
            "state": "A",
            "details": {
                "frontier": ["B", "C"],
                "explored": ["A"],
                "(1, 2)": {"nested_key": "value"}
            }
        }
        self.assertEqual(logger.log_entries[0]["Entry"], expectedEntry)

    def test_logger_logState_null_entries(self):
        event = "expand_node"
        logger = SearchLogger(self.logFile)
        logger.logState(event, None)

        expectedEntry = {}
        self.assertEqual(logger.log_entries[0]["Entry"], expectedEntry)

        event = None
        logger.logState(event, None)
        expectedEvent = None
        self.assertEqual(logger.log_entries[1]["Event"], expectedEvent)

        event = "expand_node"
        entry = {"nullkey" : None, "nestedNullKey" : ["A" , "B", None]}
        logger.logState(event, entry)

        expectedEntry = {"nullkey" : None, "nestedNullKey" : ["A", "B", None]}
        self.assertEqual(logger.log_entries[2]["Entry"], expectedEntry)

    #reset
    def test_logger_reset_success(self):
        event = "expand_node"
        logger = SearchLogger(self.logFile)

        entry = {
            "state": "A",
            "details": {
                "frontier": ["B", "C"],
                "explored": ["A"],
                (1, 2): {"nested_key": "value"}
            }
        }

        logger.logState(event, entry)
        logger._reset()
        self.assertEqual(logger.log_entries, [])

    #changeLogFile
    def test_logger_changeLogFile_success(self):
        logFile2 = Path("TestPath/TestLogger2.txt")
        logger = SearchLogger(self.logFile)
        logger._changeLogFile(logFile2)
        self.assertEqual(logger.logFile, logFile2)

    #logWrite
    def test_log_write_basic_functionality(self):
        event = "expand_node"
        entry = {"current_state": "A", "frontier": ["B", "C"], "explored": ["A"]}
        logger = SearchLogger(self.logFile)

        logger.logState(event, entry)

        logger.logWrite()

        logger.closeLog()

        with open(self.logFile, 'r') as f:
            logData = json.load(f)

        expected_logData = [{"Event": event, "Entry": entry, "Log Entry Number": 1}]
        self.assertEqual(logData, expected_logData)

    def test_log_write_empty(self):
        logger = SearchLogger(self.logFile)
        logger.logWrite()
        logger.closeLog()

        with open(self.logFile, 'r') as f:
            logData = f.read()

        self.assertEqual(logData, "")


    def test_log_wtire_multiple_entries(self):
        logger = SearchLogger(self.logFile)
        entries = [
            {
                "Event": "expand_node_special",
                "Entry": {"current state special": "Z", "frontier spacial": ["X", "Z"], "explored special": ["Z"]},
            },
            {
                "Event": "expand_node",
                "Entry": {"current state": "B", "frontier": ["A", "C"], "explored": ["B"]},
            }
        ]
        for entry in entries:
            logger.logState(entry["Event"], entry["Entry"])

        logger.logWrite()
        logger.closeLog()

        with open(self.logFile, 'r') as f:
            log_data = json.load(f)
        updated_entries = [{**entry, "Log Entry Number": i +1} for i, entry in enumerate(entries)]
        self.assertEqual(log_data, updated_entries)

    def test_log_write_overwrite(self):
        logger = SearchLogger(self.logFile, 40000)
        entries = [
            {
                "Event": "expand_node_special",
                "Entry": {"current state special": "Z", "frontier spacial": ["X", "Z"], "explored special": ["Z"]},
            },
            {
                "Event": "expand_node",
                "Entry": {"current state": "B", "frontier": ["A", "C"], "explored": ["B"]},
            }
        ]
        for entry in entries:
            logger.logState(entry["Event"], entry["Entry"])

        logger.logWrite()

        newEntries = [
            {
                "Event": "expand_node",
                "Entry": {"current state": "A", "frontier": ["B", "C"], "explored": ["A"]},
            },
            {
                "Event": "expand_node",
                "Entry": {"current state": "B", "frontier": ["A", "C"], "explored": ["B"]},
            }
        ]

        for entry in newEntries:
            logger.logState(entry["Event"], entry["Entry"])

        logger.logWrite()

        logger.closeLog()
        with open(self.logFile, 'r') as f:
            log_data = json.load(f)

        updated_entries = [{**entry, "Log Entry Number": i +1} for i, entry in enumerate(entries)]
        updated_newEntries = [{**entry, "Log Entry Number": j + len(entries) + 1} for j, entry in enumerate(newEntries)]
        self.assertEqual(log_data, updated_entries + updated_newEntries)

    def test_log_write_directory_does_not_exist_no_create_option(self):
        logger = SearchLogger(self.non_existing_log_file)
        entry = {"Event": "Test", "Entry": {"State": "A", "Next": "B"}}
        logger.logState(entry["Event"], entry["Entry"])

        with self.assertRaises(ValueError) as context:
            logger.logWrite()

        logger.closeLog()
        self.assertTrue(f'Parent Directory {self.non_existing_dir} does not exist' in str(context.exception))


    def test_log_write_directory_does_not_exist_create_option(self):
        logger = SearchLogger(self.non_existing_log_file)
        entry = {"Event": "Test", "Entry": {"State": "A", "Next": "B"}}
        logger.logState(entry["Event"], entry["Entry"])

        logger.logWrite(options={"createParent": True})

        logger.closeLog()

        entry.update({"Log Entry Number": 1})

        with open(self.non_existing_log_file, 'r') as file:
            log_data = json.load(file)
            self.assertEqual(log_data, [entry])
if __name__ == '__main__':
    unittest.main()