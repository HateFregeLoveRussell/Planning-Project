# WIP: This test is a work in progress and should not be run

import unittest
import builtins
from DiscretePlanning.Animators import AbstractAnimator
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from json import loads

class ConcreteAnimator(AbstractAnimator):
    def save_animation(self, output_file: str):
        pass
    def setup_animation(self):
        pass

mock_read_1 = """[
{
    "Event": "Event 1",
    "Entry": {
        "State": "A1"
        "Items": 12
    },
    "Log Entry Number": 1
}, 
{
    "Event": "Event 3",
    "Entry": {
        "State": "B1"
        "Items": 13
    },
    "Log Entry Number": 2
},
{
    "Event": "Event 2",
    "Entry": {
        "State": "C1"
        "Items": 14
    },
    "Log Entry Number": 3
}
]
"""
mock_read_2 = """[
        {
            "Event": "Event 1",
            "Entry": {
                "State": "A2"
                "Items": 0
            },
            "Log Entry Number": 1
        }, 
        {
            "Event": "Event 1",
            "Entry": {
                "State": "B2"
                "Items": 13
            },
            "Log Entry Number": 2
        },
        {
            "Event": "Event 3",
            "Entry": {
                "State": "C2"
                "Items": 14
            },
            "Log Entry Number": 3
        }
        ]
"""
mock_read_3 = """[
        {
            "Event": "Event 1",
            "Entry": {
                "State": "A3"
                "Items": 0
            },
            "Log Entry Number": 1
        }, 
        {
            "Event": "Event 2",
            "Entry": {
                "State": "B3"
                "Items": 13
            },
            "Log Entry Number": 2
        },
        {
            "Event": "Event 3",
            "Entry": {
                "State": "C3"
                "Items": 14
            },
            "Log Entry Number": 3
        }
        ]
"""

class test_AbstractAnimator(unittest.TestCase):
    def setUp(self):
        self.json_dir = Path('fake/Directory')

    def tearDown(self):
        pass

    # ~~~~ init() ~~~~
    @patch.object(Path,attribute='exists',return_value=True)
    @patch.object(Path,attribute='glob')
    def test_AbstractAnimator_init_success(self, mock_glob, mock_exists):
        mock_glob.return_value = [Path('test1.json'), Path('test3.json'), Path('test2.json')]
        animator = ConcreteAnimator(self.json_dir)

        self.assertEqual(animator.dir, self.json_dir)
        self.assertEqual(animator.json_files, [Path('test1.json'), Path('test2.json'), Path('test3.json')])
        self.assertEqual(animator.current_file_index , 0)
        self.assertIsNone(animator.current_file)
        self.assertEqual(animator.memory, [])
        self.assertEqual(animator.event_callbacks,{})
        self.assertEqual(animator.memory_callbacks, {})

    def test_AbstractAnimator_init_fail_invalid_directory(self):
        with self.assertRaises(ValueError) as context:
            ConcreteAnimator(self.json_dir)
            self.assertTrue("Directory does not exist" in str(context.exception))

    @patch.object(Path, attribute='exists', return_value=True)
    @patch.object(Path, attribute='glob', return_value=[])
    def test_AbstractAnimator_init_fail_no_json_files(self):
        with self.assertRaises(ValueError) as context:
            ConcreteAnimator(self.json_dir)
            self.assertTrue("No JSON files found in directory" in str(context.exception))

    # ~~~~ _get_next() ~~~~
    @patch("builtins.open", new_callable=mock_open, read_data=mock_read_1)
    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_get_next_success(self,mock_exists, mock_glob, mock_open):
        animator = ConcreteAnimator(self.json_dir)

        entry1 = animator._get_next()
        self.assertIsInstance(entry1, dict)
        self.assertEqual(entry1['Event'], 'Event 1')
        self.assertEqual(entry1['Log Entry Number'], 1)
        self.assertEqual(loads(entry1['Entry']), {"State": "A1","Items": 12})

        entry2 = animator._get_next()
        self.assertIsInstance(entry2, dict)
        self.assertEqual(entry2['Event'], 'Event 2')
        self.assertEqual(entry2['Log Entry Number'], 2)
        self.assertEqual(loads(entry2['Entry']), {"State": "B1","Items": 13})

        entry3 = animator._get_next()
        self.assertIsInstance(entry3, dict)
        self.assertEqual(entry3['Event'], 'Event 3')
        self.assertEqual(entry3['Log Entry Number'], 3)
        self.assertEqual(loads(entry3['Entry']), {"State": "C1","Items": 14})

        entry4 = animator._get_next()
        self.assertIsNone(entry4)

    @patch("builtins.open")
    @patch.object(Path, attribute='glob', return_value=[Path('test_1.json'), Path('test_2.json'), Path('test_3.json')])
    def test_AbstractAnimator_get_next_success_multiple_files(self, mock_glob, mock_open):
        def mock_file_open(file_name, *args, **kwargs):
            if file_name == 'test_1.json':
                content = mock_read_1
            elif file_name == 'test_2.json':
                content = mock_read_2
            else:
                content = mock_read_3

            mock_file = mock_open(content)
            return mock_file()

        mock_open.side_effect = mock_file_open

        animator = ConcreteAnimator(self.json_dir)

        #file1
        file1_event1 = animator._get_next()
        self.assertIsInstance(file1_event1, dict)
        self.assertEqual(file1_event1, loads(mock_read_1)[0])

        file1_event2 = animator._get_next()
        self.assertIsInstance(file1_event2, dict)
        self.assertEqual(file1_event2, loads(mock_read_1)[1])

        file1_event3 = animator._get_next()
        self.assertIsInstance(file1_event3, dict)
        self.assertEqual(file1_event3, loads(mock_read_1)[2])

        #file2
        file2_event1 = animator._get_next()
        self.assertIsInstance(file2_event1, dict)
        self.assertEqual(file2_event1, loads(mock_read_2)[0])

        file2_event2 = animator._get_next()
        self.assertIsInstance(file2_event2, dict)
        self.assertEqual(file2_event2, loads(mock_read_2)[1])

        file2_event3 = animator._get_next()
        self.assertIsInstance(file2_event3, dict)
        self.assertEqual(file2_event3, loads(mock_read_2)[2])

        #file3
        file3_event1 = animator._get_next()
        self.assertIsInstance(file3_event1, dict)
        self.assertEqual(file3_event1, loads(mock_read_3)[0])

        file3_event2 = animator._get_next()
        self.assertIsInstance(file3_event2, dict)
        self.assertEqual(file3_event2, loads(mock_read_3)[1])

        file3_event3 = animator._get_next()
        self.assertIsInstance(file3_event3, dict)
        self.assertEqual(file3_event3, loads(mock_read_3)[2])

        file3_event4 = animator._get_next()
        self.assertIsNone(file3_event4)
        return



if __name__ == '__main__':
    unittest.main()