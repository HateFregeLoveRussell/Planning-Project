# WIP: This test is a work in progress and should not be run

import unittest
from DiscretePlanning.Animators import AbstractAnimator
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from json import loads, JSONDecodeError

class ConcreteAnimator(AbstractAnimator):
    def save_animation(self, output_file: str):
        pass
    def setup_animation(self):
        pass

mock_read_1 = """[
{
    "Event": "Event 1",
    "Entry": {
        "State": "A1",
        "Items": 12
    },
    "Log Entry Number": 1
}, 
{
    "Event": "Event 3",
    "Entry": {
        "State": "B1",
        "Items": 13
    },
    "Log Entry Number": 2
},
{
    "Event": "Event 2",
    "Entry": {
        "State": "C1",
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
                "State": "A2",
                "Items": 0
            },
            "Log Entry Number": 4
        }, 
        {
            "Event": "Event 1",
            "Entry": {
                "State": "B2",
                "Items": 13
            },
            "Log Entry Number": 5
        },
        {
            "Event": "Event 3",
            "Entry": {
                "State": "C2",
                "Items": 14
            },
            "Log Entry Number": 6
        }
        ]
"""
mock_read_3 = """[
        {
            "Event": "Event 1",
            "Entry": {
                "State": "A3",
                "Items": 0
            },
            "Log Entry Number": 7
        }, 
        {
            "Event": "Event 2",
            "Entry": {
                "State": "B3",
                "Items": 13
            },
            "Log Entry Number": 8
        },
        {
            "Event": "Event 3",
            "Entry": {
                "State": "C3",
                "Items": 14
            },
            "Log Entry Number": 9
        }
        ]
"""
mock_read_combined = """[
{
    "Event": "Event 1",
    "Entry": {
        "State": "A1",
        "Items": 12
    },
    "Log Entry Number": 1
}, 
{
    "Event": "Event 3",
    "Entry": {
        "State": "B1",
        "Items": 13
    },
    "Log Entry Number": 2
},
{
    "Event": "Event 2",
    "Entry": {
        "State": "C1",
        "Items": 14
    },
    "Log Entry Number": 3
},
{
    "Event": "Event 1",
    "Entry": {
        "State": "A2",
        "Items": 0
    },
    "Log Entry Number": 4
}, 
{
    "Event": "Event 1",
    "Entry": {
        "State": "B2",
        "Items": 13
    },
    "Log Entry Number": 5
},
{
    "Event": "Event 3",
    "Entry": {
        "State": "C2",
        "Items": 14
    },
    "Log Entry Number": 6
},
{
    "Event": "Event 1",
    "Entry": {
        "State": "A3",
        "Items": 0
    },
    "Log Entry Number": 7
}, 
{
    "Event": "Event 2",
    "Entry": {
        "State": "B3",
        "Items": 13
    },
    "Log Entry Number": 8
},
{
    "Event": "Event 3",
    "Entry": {
        "State": "C3",
        "Items": 14
    },
    "Log Entry Number": 9
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
        self.assertEqual(animator.memory_callbacks, set())

    def test_AbstractAnimator_init_fail_invalid_directory(self):
        with self.assertRaises(ValueError) as context:
            ConcreteAnimator(self.json_dir)
            self.assertTrue("Directory does not exist" in str(context.exception))

    @patch.object(Path, attribute='exists', return_value=True)
    @patch.object(Path, attribute='glob', return_value=[])
    def test_AbstractAnimator_init_fail_no_json_files(self,mock_glob, mock_exists,):
        with self.assertRaises(ValueError) as context:
            ConcreteAnimator(self.json_dir)
            self.assertTrue("No JSON files found in directory" in str(context.exception))

    # ~~~~ _get_next() ~~~~
    @patch.object(Path, attribute='read_text', return_value=mock_read_1)
    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_get_next_success(self,mock_exists, mock_glob, mock_open):
        animator = ConcreteAnimator(self.json_dir)

        entry1 = animator._get_next()
        self.assertIsInstance(entry1, dict, msg=f'Entry Object not of type dict. Actual type: {type(entry1)}')
        self.assertEqual(entry1['Event'], 'Event 1')
        self.assertEqual(entry1['Log Entry Number'], 1)
        self.assertEqual(entry1['Entry'], {"State": "A1","Items": 12})

        entry2 = animator._get_next()
        self.assertIsInstance(entry2, dict, msg=f'Entry Object not of type dict. Actual type: {type(entry1)}')
        self.assertEqual(entry2['Event'], 'Event 3')
        self.assertEqual(entry2['Log Entry Number'], 2)
        self.assertEqual(entry2['Entry'], {"State": "B1","Items": 13})

        entry3 = animator._get_next()
        self.assertIsInstance(entry3, dict, msg=f'Entry Object not of type dict. Actual type: {type(entry1)}')
        self.assertEqual(entry3['Event'], 'Event 2')
        self.assertEqual(entry3['Log Entry Number'], 3)
        self.assertEqual(entry3['Entry'], {"State": "C1","Items": 14})

        entry4 = animator._get_next()
        self.assertIsNone(entry4)

    @patch.object(Path, attribute='glob', return_value=[Path('test_1.json'), Path('test_2.json'), Path('test_3.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_get_next_success_multiple_files(self,mock_exists, mock_glob):
        def mock_file_read(self):
            if self.name == 'test_1.json':
                content = mock_read_1
            elif self.name == 'test_2.json':
                content = mock_read_2
            else:
                content = mock_read_3
            return content

        with patch.object(Path, 'read_text', new=mock_file_read):
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

    @patch.object(Path, 'glob', return_value=[Path('test_1.json')])
    @patch.object(Path, 'exists', return_value=True)
    def test_AbstractAnimator_get_next_fail_Invalid_JSON(self, mock_exists, mock_glob):
        invalid_json_examples = [
            '{"name": "John"',  # Missing closing brace
            "{'name': 'John'}",  # Single quotes instead of double quotes
            '{"name": "John", "info": "This contains a newline\ncharacter"}',  # Unescaped control characters
            '{"name": "John",}',  # Trailing comma
            '{name: "John"}'  # Non-string key
        ]
        for invalid_json in invalid_json_examples:
            with patch.object(Path, 'read_text', return_value=invalid_json):
                animator = ConcreteAnimator(self.json_dir)
                with self.assertRaises(JSONDecodeError) as context:
                    animator._get_next()
                    self.assertTrue("Error decoding JSON from" in str(context.exception))

    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    @patch.object(Path, 'read_text', side_effect=IOError("File Error"))
    def test_AbstractAnimator_get_next_fail_IO_Error(self, mock_read, mock_exists, mock_glob):
        animator = ConcreteAnimator(self.json_dir)
        with self.assertRaises(IOError) as context:
            animator._get_next()
            self.assertTrue("Error reading file" in str(context.exception))

    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    @patch.object(Path, 'read_text', side_effect=FileNotFoundError)
    def test_AbstractAnimator_get_next_fail_UnknownError(self, mock_read, mock_exists, mock_glob):
        animator = ConcreteAnimator(self.json_dir)
        with self.assertRaises(Exception) as context:
            animator._get_next()
            self.assertTrue("Unexpected error in _get_next processing file" in str(context.exception))

    # ~~~~ _validate_event ~~~~
    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    @patch.object(Path, 'read_text', return_value=mock_read_combined)
    def test_AbstractAnimator_validate_event_success(self, mock_read, mock_exists, mock_glob):
        #initialize Animator
        animator = ConcreteAnimator(self.json_dir)
        entry = animator._get_next()
        #Sanity Check
        self.assertIsNotNone(entry)
        while entry is not None:
            animator._validate_event(entry)
            entry = animator._get_next()

    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_validate_event_fail_invalid_event_type(self, mock_exists, mock_glob):
        test_cases = [
            ({}, r'Invalid Event encountered, event: {} does not have "Event" key'),
            ({"Event": 123}, r'Invalid Event encountered, event: .+ value of type str for "Event" key'),
            ({"Event": "my_event"}, r'Invalid Event encountered, event: .+ does not have "Entry" key'),
            ({"Event": "my_event", "Entry": "not_a_dict"},
             r'Invalid Event encountered, event: .+ value of type dict for "Entry" key'),
            ({"Event": "my_event", "Entry": {}},
             r'Invalid Event encountered, event: .+ does not have "Log Entry Number" key'),
            ({"Event": "my_event", "Entry": {}, "Log Entry Number": "not_an_int"},
             r'Invalid Event encountered, event: .+ value of type int for "Log Entry Number" key')
        ]
        animator = ConcreteAnimator(self.json_dir)
        for event, expected_response in test_cases:
            with self.subTest(event=event):
                with self.assertRaisesRegex(ValueError, expected_response):
                    animator._validate_event(event)


    # ~~~~ memory_subscribe() ~~~~
    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_memory_subscribe_success(self, mock_exists, mock_glob):
        with self.subTest(event="Single Event"):
            animator = ConcreteAnimator(self.json_dir)
            animator.memory_subscribe({"Event 1"})
            self.assertEqual(animator.memory_callbacks, {"Event 1"})

        with self.subTest(event="Multiple Events"):
            animator1 = ConcreteAnimator(self.json_dir)
            animator1.memory_subscribe({"Event 1", "Event 3"})
            self.assertEqual(animator1.memory_callbacks, {"Event 1", "Event 3"})

            animator2 = ConcreteAnimator(self.json_dir)
            animator2.memory_subscribe({"Event 1"})
            animator2.memory_subscribe({"Event 3"})
            self.assertEqual(animator2.memory_callbacks, {"Event 1", "Event 3"})

            self.assertEqual(animator1.memory_callbacks, animator2.memory_callbacks)

        with self.subTest(event="Same Event"):
            animator = ConcreteAnimator(self.json_dir)
            animator.memory_subscribe({"Event 1", "Event 3"})
            animator.memory_subscribe({"Event 1"})
            self.assertEqual(animator.memory_callbacks, {"Event 1", "Event 3"})

    # ~~~~ memory_unsubscribe() ~~~~

    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_memory_unsubscribe_success(self, mock_exists, mock_glob):
        with self.subTest(event="Single Event"):
            animator = ConcreteAnimator(self.json_dir)
            animator.memory_subscribe({"Event 1"})
            animator.memory_unsubscribe({"Event 1"})
            self.assertEqual(animator.memory_callbacks, set())

        with self.subTest(event="Multiple Events"):
            animator1 = ConcreteAnimator(self.json_dir)
            animator1.memory_subscribe({"Event 1", "Event 3"})
            animator1.memory_unsubscribe({"Event 1"})
            self.assertEqual(animator1.memory_callbacks, {"Event 3"})
            animator1.memory_unsubscribe({"Event 3"})
            self.assertEqual(animator1.memory_callbacks, set())

            animator2 = ConcreteAnimator(self.json_dir)
            animator2.memory_subscribe({"Event 1", "Event 3"})
            animator2.memory_unsubscribe({"Event 1", "Event 3"})
            self.assertEqual(animator2.memory_callbacks, set())

            self.assertEqual(animator1.memory_callbacks, animator2.memory_callbacks)

        with self.subTest(event="Non-Existent Event"):
            animator = ConcreteAnimator(self.json_dir)
            animator.memory_subscribe({"Event 1", "Event 3"})
            animator.memory_unsubscribe({"Event Alpha"})
            self.assertEqual(animator.memory_callbacks, {"Event 1", "Event 3"})
            animator.memory_unsubscribe({"Event 1"})
            self.assertEqual(animator.memory_callbacks, {"Event 3"})

    # ~~~~ _validate_event_types_param() ~~~~
    @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    @patch.object(Path, attribute='exists', return_value=True)
    def test_AbstractAnimator_memory_subscribe_fail_invalid_type(self, mock_exists, mock_glob):
        class MyClass:
            def __init__(self):
                pass
        # pass non-string to subscribe_event
        test_cases = [
            ({MyClass()}, r'Event Type of Type ".+" Not Recognized', TypeError),
            ({"Event 1", 12, "Event 3"}, r'Event Type of Type "int" Not Recognized', TypeError),
            ({"Event 1", "Event 3", MyClass()}, r'Event Type of Type ".+" Not Recognized', TypeError),
            ({"Event 1", "", "Event 3"}, r'Empty String Event Types Encountered, this Event Type is Forbidden', ValueError),
            ({"", "Event 2", "Event 3"}, r'Empty String Event Types Encountered, this Event Type is Forbidden', ValueError),
            (MyClass(), r'Event Types Parameter Should be of Type Set\[Str\] is instead ".+"', TypeError)
        ]

        for input, expected_response, error_type in test_cases:
            with self.subTest():
                animator = ConcreteAnimator(self.json_dir)
                with self.assertRaisesRegex(error_type, expected_response):
                    animator._validate_event_types_param(input)

        return



    # # ~~~~ memory_subscriptions ~~~
    # #   ~~~~ memory_subscribe() ~~~~
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_subscribe_success_single_event(self, mock_exists, mock_glob, mock_open):
    #     animator = ConcreteAnimator(self.json_dir)
    #
    #     # subscribe to event 1
    #     animator.memory_subscribe({"Event 1"})
    #     # successively call _get_next()
    #     # build own mirror memory
    #     entry = animator._get_next()
    #     self.assertIsNotNone(entry)
    #     memory = []
    #     while entry is not None:
    #         if entry['Event'] == 'Event 1':
    #             memory.append(entry)
    #         entry = animator._get_next()
    #
    #     #assert equality between mirror and animator memory
    #     self.assertEqual(animator.memory, memory)
    #     return
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_subscribe_success_multiple_events(self):
    #     #create two animators
    #     animator1 = ConcreteAnimator(self.json_dir)
    #     animator2 = ConcreteAnimator(self.json_dir)
    #     # subscribe to 2 events out of 3 on both
    #     animator1.memory_subscribe({"Event 1"})
    #     animator1.memory_subscribe({"Event 3"})
    #
    #     animator2.memory_subscribe({"Event 1", "Event 3"})
    #
    #     # successively call _get_next()
    #     # build own mirror memory
    #     memory1, memory2 = [], []
    #     entry1 = animator1._get_next()
    #     entry2 = animator2._get_next()
    #     while entry1 is not None and entry2 is not None:
    #         if entry1['Event'] == 'Event 1' or entry1['Event'] == 'Event 3':
    #             memory1.append(entry1)
    #         if entry2['Event'] == 'Event 1' or entry2['Event'] == 'Event 3':
    #             memory2.append(entry2)
    #
    #         entry1 = animator1._get_next()
    #         entry2 = animator2._get_next()
    #
    #
    #     self.assertIsNone(animator1._get_next())
    #     self.assertIsNone(animator2._get_next())
    #
    #     #assert equality between mirror memories
    #     self.assertEqual(memory1, memory2)
    #
    #     #assert equality between mirror and animator memories
    #     self.assertEqual(animator1.memory, memory1)
    #     self.assertEqual(animator2.memory, memory2)
    #
    #     #assert (just for safety) equality between animator memories
    #     self.assertEqual(animator1.memory, animator2.memory)
    #
    #     return
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_subscribe_fail_nonexistent_event(self):
    #     animator1 = ConcreteAnimator(self.json_dir)
    #     animator2 = ConcreteAnimator(self.json_dir)
    #
    #     # subscribe to non-existent event
    #     animator1.memory_subscribe({"Event Alpha"})
    #     animator2.memory_subscribe({"Event Alpha"})
    #
    #     # call _get_next() repeatedly until None reached
    #     entry1 = animator1._get_next()
    #     entry2 = animator2._get_next()
    #     mem1,mem2 = [],[]
    #     self.assertIsNotNone(entry1)
    #     self.assertIsNotNone(entry2)
    #
    #     while entry1 is not None and entry2 is not None:
    #         if entry1['Event'] == 'Event 100':
    #             mem1.append(entry1)
    #         if entry2['Event'] == 'Event 100':
    #             mem2.append(entry2)
    #
    #         entry1 = animator1._get_next()
    #         entry2 = animator2._get_next()
    #
    #     self.assertIsNone(animator1._get_next())
    #     self.assertIsNone(animator2._get_next())
    #
    #     # check to see if memory is empty
    #     self.assertEqual(mem1,[])
    #     self.assertEqual(mem2,[])
    #     self.assertEqual(animator1.memory,[])
    #     self.assertEqual(animator2.memory,[])
    #     return
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_subscribe_nonexistent_and_existent_events(self):
    #     # create two instances of ConcreteAnimator
    #     animator1 = ConcreteAnimator(self.json_dir)
    #     animator2 = ConcreteAnimator(self.json_dir)
    #     # one subscribes to an existent event
    #     animator1.memory_subscribe({"Event 1"})
    #     # other subscribes to the existent and a non-existent event
    #     animator2.memory_subscribe({"Event 1", "Event Alpha"})
    #     # call _get_next() on both until None.
    #     mem1,mem2 = [],[]
    #     entry1, entry2 = animator1._get_next(), animator2._get_next()
    #     self.assertIsNotNone(entry1)
    #     self.assertIsNotNone(entry2)
    #     while entry1 is not None and entry2 is not None:
    #         entry1 = animator1._get_next()
    #         entry2 = animator2._get_next()
    #
    #     self.assertIsNone(animator1._get_next())
    #     self.assertIsNone(animator2._get_next())
    #
    #     # compare self.memory on both check for equality
    #     self.assertEqual(animator1.memory, animator2.memory)
    #     return
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_subscribe_successive_subscriptions(self):
    #     animator = ConcreteAnimator(self.json_dir)
    #     # subscribe to 2 events out of 3
    #     animator.memory_subscribe({"Event 1", "Event 3"})
    #     # successively call _get_next()
    #     mem = []
    #     for i in range(9):
    #         entry = animator._get_next()
    #         if entry['Event'] == 'Event 1' or entry['Event'] == 'Event 3':
    #             mem.append(entry)
    #         # in the middle subscribe to third event
    #         if i == 4:
    #             animator.memory_subscribe({"Event 2"})
    #         if i >=4:
    #             if entry['Event'] == 'Event 2':
    #                 mem.append(entry)
    #     # check to see if expected events in self.memory in-between calls
    #     # build own mirror memory while doing this compare at each call
    #     # both content and order should match
    #     pass
    #
    # #   ~~~~ memory_unsubscribe() ~~~~
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_unsubscribe_success_single_event(self):
    #     # create two instances of ConcreteAnimator
    #     animator1 = ConcreteAnimator(self.json_dir)
    #     animator2 = ConcreteAnimator(self.json_dir)
    #     # both subscribed to the same event
    #     animator1.memory_subscribe({"Event 1"})
    #     animator2.memory_subscribe({"Event 1"})
    #     # for one animator, unsubscribe from event half-way through run
    #     for i in range(9):
    #         entry1 = animator1._get_next()
    #         entry2 = animator2._get_next()
    #         if i == 4:
    #             animator1.memory_unsubscribe({"Event 1"})
    #
    #     # assert inequality between the two memories
    #     self.assertNotEqual(animator1.memory, animator2.memory)
    #     difference = [entry for entry in animator2.memory if entry not in animator1.memory]
    #     # assert difference between the two memory arrays is composed only of unsubscribed event
    #     self.assertTrue(all([entry['Event'] == 'Event 1' for entry in difference]))
    #     return
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_unsubscribe_success_multiple_events(self):
    #     # create two instances of ConcreteAnimator
    #     animator1 = ConcreteAnimator(self.json_dir)
    #     animator2 = ConcreteAnimator(self.json_dir)
    #
    #     # both subscribed to the same 2 events
    #     animator1.memory_subscribe({"Event 1", "Event 3"})
    #     animator2.memory_subscribe({"Event 1", "Event 3"})
    #
    #     # for one animator, unsubscribe from both events half-way through run
    #     for i in range(9):
    #         animator1._get_next()
    #         animator2._get_next()
    #         if i == 4:
    #             animator1.memory_unsubscribe({"Event 1", "Event 3"})
    #
    #
    #     self.assertIsNone(animator1._get_next())
    #     self.assertIsNone(animator2._get_next())
    #     # assert inequality between memory arrays
    #     self.assertNotEqual(animator1.memory, animator2.memory)
    #     # assert difference between two memory arrays is composed of both
    #     difference = [entry for entry in animator2.memory if entry not in animator1.memory]
    #     self.assertTrue(all([entry['Event'] == 'Event 1' or entry['Event'] == 'Event 2' for entry in difference]))
    #     return
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=mock_read_combined)
    # @patch.object(Path, attribute='glob', return_value=[Path('test1.json')])
    # @patch.object(Path, attribute='exists', return_value=True)
    # def test_AbstractAnimator_memory_unsubscribe_fail_nonexistent_event(self):
    #     # create two ConcreteAnimator
    #     animator1 = ConcreteAnimator(self.json_dir)
    #     animator2 = ConcreteAnimator(self.json_dir)
    #     # subscribe both to some event
    #     animator1.memory_subscribe({"Event 1"})
    #     animator2.memory_subscribe({"Event 1"})
    #     # unsubscribe one from some non-existent event halfway through
    #     for i in range(9):
    #         entry1 = animator1._get_next()
    #         entry2 = animator2._get_next()
    #         if i == 5:
    #             animator1.memory_unsubscribe({"Event Alpha"})
    #     # assert equality between the two memory arrays
    #     self.assertEqual(animator1.memory, animator2.memory)
    #     return

if __name__ == '__main__':
    unittest.main()