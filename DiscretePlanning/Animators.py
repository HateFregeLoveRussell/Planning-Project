import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Set, Callable, Dict, Optional
from json import loads, JSONDecodeError
from collections import defaultdict
from inspect import signature, Signature
import os


class AbstractAnimator(ABC):
    """Abstract base class for animators that read JSON files to create animations."""

    def __init__(self, json_directory: Path):
        """
        Initializes the animator with the directory containing JSON files.

        Parameters:
        json_directory: The directory containing the JSON files.
        """
        # File management variables
        if not json_directory.exists():
            raise ValueError(f'Directory does not exist, Directory: {json_directory}')

        if json_directory.glob('*.json') == []:
            raise ValueError(f'Directory does not contain any JSON files, Directory: {json_directory}')

        self.dir = json_directory
        self.json_files = sorted(self.dir.glob('*.json'))
        self.current_file_index = 0
        self.current_file = None
        self.memory = []
        self._buff = []

        # Subscription variables
        self._event_to_callbackID = defaultdict(set)
        self._callbackID_to_Callback = {"-" : self._memory_callback}

        pass

    def _get_next(self) -> Optional[Dict]:
        """
        Fetches the next event in order from the series of JSON files.

        Returns:
        dict: The next event dictionary, or None if the next event does not exist.
        """
        if self.current_file_index >= len(self.json_files):
            return None

        # Index incrementation is now meaningful
        if self.current_file is None:
            try:
                self._buff = json.loads(self.json_files[self.current_file_index].read_text())
                self.current_file = self.json_files[self.current_file_index]
            except JSONDecodeError as err:
                raise JSONDecodeError(
                    f"Error decoding JSON in _get_next from {self.json_files[self.current_file_index]}: {err.msg}",
                    doc=err.doc, pos=err.pos)
            except IOError as io_err:
                raise IOError(f"Error reading file {self.json_files[self.current_file_index]} in _get_next: {io_err}")
            except Exception as err:
                raise RuntimeError(
                    f"Unexpected error in _get_next processing file {self.json_files[self.current_file_index]}: {err}")

        while not self._buff:
            self.current_file_index += 1
            if self.current_file_index >= len(self.json_files):
                return None
            self.current_file = self.json_files[self.current_file_index]
            try:
                self._buff = json.loads(self.current_file.read_text())
            except JSONDecodeError as err:
                raise JSONDecodeError(
                    f"Error decoding JSON from {self.current_file}: {err.msg}",
                    doc=err.doc, pos=err.pos)
            except IOError as io_err:
                raise IOError(f"Error reading file {self.current_file} in _get_next: {io_err}")
            except Exception as err:
                raise RuntimeError(f"Unexpected error in _get_next processing file {self.current_file}: {err}")

        # _buff is now populated
        return self._buff.pop(0) if self._buff else None

    def _memory_callback(self, event: Dict):
        self.memory.append(event)

    def _update_JSON_files(self):
        self.json_files = sorted(self.dir.glob('*.json'))

    def _handle_event(self, event: Dict):
        """
        Handles an event by Validating its contents, then calling the subscribed callbacks with appropriate event information.

        Parameters:
        event (dict): The event dictionary containing the event, entry, and Log Entry Number fields.
        """
        #validate event
        self._validate_event(event)
        #event should be safe to use from here
        event_type = event["Event"]
        callback_id_set = self._event_to_callbackID[event_type]
        for callback_id in callback_id_set:
            callback : Callable = self._callbackID_to_Callback.get(callback_id)
            if not callback:
                raise RuntimeError(f"Abstract Animator Internal Memory Coherence lost, should have callback_id {callback_id} "
                                   f"in _CallbackID_to_Callback: {self._callbackID_to_Callback} but key not present")
            callback(event)
        return

    # ~~~ Validation Utilities ~~~
    def _validate_event(self, event: Dict) -> None:
        """
        Determines if Event object provided has valid structure and types, throws Error otherwise

        Parameters:
        event (dict): The event dictionary to be validated
        """
        requirement_dictionary = {
            "Event" : str,
            "Entry" : dict,
            "Log Entry Number": int
        }
        for requirement, required_type in requirement_dictionary.items():
            if requirement not in event:
                raise ValueError(f'Invalid Event encountered, event: {event} does not have "{requirement}" key')
            if not isinstance(event[requirement], required_type):
                raise ValueError(f'Invalid Event encountered, event: {event} does not have value of type '
                                 f'{required_type.__name__} for "{requirement}" key')

        #guaranteed to have event with all 3 proper keys, and appropriate value types
        return

    def _validate_event_types_param(self, event_types: Set[str]) -> None:
        if not isinstance(event_types, set):
            raise TypeError(f'Event Types Parameter Should be of Type Set[Str] is instead "{type(event_types).__name__}"')
        for entry in event_types:
            if not isinstance(entry, str):
                raise TypeError(f'Event Type of Type "{type(entry).__name__}" Not Recognized')
            if entry == "":
                raise ValueError('Empty String Event Types Encountered, this Event Type is Forbidden')
        return

    def _validate_event_callbacks(self, callback: Callable) -> None:
        if not callable(callback):
            raise TypeError(f'Callback Parameter Should be of Type Callable is instead "{type(callback).__name__}"')

        sig = signature(callback)
        sig_params = sig.parameters
        if (len(sig_params) != 1):
            raise ValueError(f'Callback should accept exactly one argument, but it accepts {len(sig_params)}')

        # Check if the function returns None, allowing for missing annotations
        return_annotation = sig.return_annotation
        if return_annotation is not Signature.empty and return_annotation not in [None, 'NoneType']:
            raise ValueError(f'Callback should return None, but it returns "{return_annotation}"')

        return

    def memory_subscribe(self, event_types: Set[str]) -> None:
        """

        Subscribes a callback to a set of events that adds the event information to the classes memory parameter
        This will allow the user to generate event callbacks using subscribe_to_event that can act on event information preceding the event passed to it.

        event_type (Set[str]): The event(s) to subscribe to.
        """
        self._validate_event_types_param(event_types)
        for event_type in event_types:
            self._event_to_callbackID[event_type].update("-")

    def memory_unsubscribe(self, event_types: Set[str]) -> None:
        """
        Dual to memory_subscribe.
        Unsubscribes the callback which adds event information to the classes memory parameter for a Set of events.
        Events for which no memory callbacks are assigned will be ignored.

        :param event_type:
        :return:
        """
        self._validate_event_types_param(event_types)
        for event_type in event_types.intersection(self._event_to_callbackID.keys()):
            if "-" in self._event_to_callbackID[event_type]:
                self._event_to_callbackID[event_type].remove("-")
                if not self._event_to_callbackID[event_type]:
                    del self._event_to_callbackID[event_type]

    def subscribe_to_event(self, event_types: Set[str], callback: Callable, callback_id : str) -> None:
        """
        Subscribes a callback to a particular event type.

        Parameters:
        event_type (Set[str]): The event(s) to subscribe to.
        callback (callable): The callback function to call when the event is encountered.
        callback_id (str): A Unique ID managed by the user, multiple callbacks assigned to the same ID will overwrite each other.
        The Callback_ID "-" is assigned to the memory subscription callback, it is reserved and cannot be used for other user callbacks.
        """
        self._validate_event_types_param(event_types)
        self._validate_event_callbacks(callback)
        if not isinstance(callback_id, str):
            raise TypeError(f'Callback ID Should be of Type String is instead "{type(callback_id).__name__}"')

        #should have valid arguments from here
        for event_type in event_types:
            self._event_to_callbackID[event_type].add(callback_id)
            self._callbackID_to_Callback[callback_id] = callback

        return

    def unsubscribe_from_event(self, event_types: Set[str], callback_id: str,) -> None:
        """
        Unsubscribes a callback from a set of events.
        If all subscribed to events are unsubscribed, the callback_id will be de-registered and can be assigned to a new callback
        in the future by calling subscribe_to_event.

        Parameters:
        event_type (Set[str]): The event(s) to unsubscribe from.
        callback_id (str): The Unique ID managed by the user which correspond to the targeted callback. Non-existent IDs are ignored
        """
        self._validate_event_types_param(event_types)
        if not isinstance(callback_id, str):
            raise TypeError(f'Callback ID Should be of Type String is instead "{type(callback_id).__name__}"')

        #should have valid arguments from here
        for event_type in event_types.intersection(self._event_to_callbackID.keys()):
            #should only include events that have registered callbacks
            if callback_id in self._event_to_callbackID[event_type]:
                self._event_to_callbackID[event_type].remove(callback_id)
                #this branch handles remnant default dict entries
                if not self._event_to_callbackID[event_type]:
                    del self._event_to_callbackID[event_type]

        # if callback ID not registered for any event type
        if all([not callback_id in callbackIDSet for callbackIDSet in self._event_to_callbackID.values()]):
            self._callbackID_to_Callback.pop(callback_id, None)
            #else the callback does not exist in class bookkeeping

        return

    @abstractmethod
    def setup_animation(self):
        """
        Abstract method to set up the animation and initialize necessary components or libraries.
        """
        pass

    @abstractmethod
    def save_animation(self, output_file: str):
        """
        Abstract method to save the generated animation to a file.

        Parameters:
        output_file (str): The path to the file where the animation will be saved.
        """
        pass

    def run(self, output_file: str):
        """
        Method to run the full animation process.

        Parameters:
        output_file (str): The path to the file where the animation will be saved.
        """
        self.setup_animation()
        entry = self._get_next()
        while entry is not None:
            self._handle_event(entry)
            entry = self._get_next()
        self.save_animation(output_file)
        return