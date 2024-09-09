from DiscretePlanning.planningProblem import DiscretePlanningProblem
from DiscretePlanning.planningSearch import DiscretePlanningSolver, ForwardSearch
from pathlib import Path
from typing import Dict, Any
from json import loads,dumps, dump
from logging import basicConfig, WARNING, warning

class SearchLogger():
    """
    Logger class intended for saving search state in JSON format as search progresses.
    Log data later to be used for visualization or debugging purposes, with package of user's choosing
    """
    def __init__(self, logFile: Path) -> None:
        """
        Initializes an instance of search logger
        :param logFile: path to Logfile, by default relative to repository root
        """
        self.logFile = logFile
        self.log_entries = []
        basicConfig(level=WARNING)
        return

    def logState(self, event: str, entry: Dict) -> None:
        """
        Adds search state to log entries, later saved to a file through logWrite()

        :param event: Meant to indicate the step in the search algorithm being executed
        :param entry: A dictionary containing any state variables needed to communicate program state, ex. frontier, visited states, etc
        """
        safe_entry  = self._makeSafe(entry)
        try:
            dumps(safe_entry)
            self.log_entries.append({"Event": event, "Entry": safe_entry})
        except(ValueError, TypeError) as err:
            self.log_entries.append({"Event": event, "Entry": "<unstringifiable entry>", "Error": str(err)})
            warning(f'Failed to Stringify Log Entry: {err}')

        return

    def logWrite(self, options=None) -> None:
        """
        Writes current log entirely to log file, does not clear log entries use reset() for this
        Ensures that the directory exists before writing.

        :param options: Write Options Dictionary
            Possible options:
                - 'createParent': determines if the parent directory should be created when missing (default: False)
        """
        if options is None:
            options = {}
        create_parent = options.get("createParent", False)
        if not self.logFile.parent.exists():
            if not create_parent:
                raise ValueError(f'Parent Directory {self.logFile.parent} does not exist')
            try:
                self.logFile.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise IOError(f"Failed to create directory {self.logFile.parent}: {e}")

        with open(self.logFile.resolve(), 'w') as file:
            dump(self.log_entries, file, indent=4)
        return

    def reset(self) -> None:
        """
        Resets log entries to empty list
        """
        self.log_entries=[]
        return

    def changeLogFile(self, logFile: Path)-> None:
        """
        Change log file for logger class
        :param logFile: string corresponding to new log file directory
        """
        self.logFile = logFile
        return

    def _makeSafe(self, entry: Dict) -> Dict:
        """Recursively ensures that the dictionary keys are stringifiable and values are serializable."""
        safe_entry = {}
        if entry is None:
            return safe_entry
        for key, value in entry.items():
            safe_key = str(key)

            try:
                dumps(value)
                safe_value = value
            except (TypeError, ValueError):
                try:
                    safe_value = repr(value)
                except Exception:
                    safe_value = f"<unrepresentable object of type {type(value).__name__}>"

            if isinstance(value, dict):
                safe_value = self._makeSafe(value)

            safe_entry[safe_key] = safe_value

        return safe_entry