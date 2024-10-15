from DiscretePlanning.planningProblem import DiscretePlanningProblem
from DiscretePlanning.planningSearch import DiscretePlanningSolver, ForwardSearch
from pathlib import Path
from typing import Dict, Any, Optional, List
from json import dumps, dump
from logging import basicConfig, WARNING, warning

from collections import deque
import heapq
MAX_LINES_PER_FILE = 20000

class SearchLogger():
    """
    Logger class intended for saving search state in JSON format as search progresses.
    Log data later to be used for visualization or debugging purposes, with package of user's choosing
    """

    """
    Logger class intended for saving search state in JSON format as search progresses.
    Log data later to be used for visualization or debugging purposes, with package of user's choosing
    """

    def __init__(self, logFile: Path, maxLines: int = MAX_LINES_PER_FILE) -> None:
        """
        Initializes an instance of search logger
        :param logFile: path to Logfile, by default relative to repository root
        """
        self.logFile = logFile
        self.stem = logFile.stem
        self.log_entries = []
        self.lines = 0
        self.entryNumber = 1
        self.file_index = 0
        self.maxLines = maxLines
        basicConfig(level=WARNING)
        return

    def logState(self, event: str, entry: Dict) -> None:
        """
        Adds search state to log entries, later saved to a file through logWrite()

        :param event: Meant to indicate the step in the search algorithm being executed
        :param entry: A dictionary containing any state variables needed to communicate program state, ex. frontier, visited states, etc
        """
        safe_entry = self._makeSafe(entry)
        try:
            dumps(safe_entry)
            self.log_entries.append({"Event": event, "Entry": safe_entry})
        except (ValueError, TypeError) as err:
            self.log_entries.append({"Event": event, "Entry": "<unstringifiable entry>", "Error": str(err)})
            warning(f'Failed to Stringify Log Entry: {err}')

        return

    def _switchLogFile(self):
        """
        Switches to a new log file when the current one reaches the line limit.
        """
        self.file_index += 1
        self.lines = 0  # Reset line counter
        new_log_file = self.logFile.with_stem(f"{self.stem}_{self.file_index}")
        self.changeLogFile(new_log_file)
        self.reset()

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

        # Ensure the directory exists
        if not self.logFile.parent.exists():
            if not create_parent:
                raise ValueError(f'Parent Directory {self.logFile.parent} does not exist')
            try:
                self.logFile.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise IOError(f"Failed to create directory {self.logFile.parent}: {e}")

        # Check if the file exists to determine how to write (open/close brackets)
        is_new_file = not self.logFile.exists()

        with open(self.logFile.resolve(), 'a') as file:
            if is_new_file:
                file.write("[\n")

            for i, entry in enumerate(self.log_entries):
                entry.update({"Log Entry Number": self.entryNumber})
                self.entryNumber += 1
                json_entry = dumps(entry, indent=4)
                if not is_new_file or i > 0:
                    file.write(",\n")  # Add a comma between entries if not the first one
                file.write(json_entry)

                self.lines += json_entry.count('\n') + 1

        if self.lines >= self.maxLines:
            self._closeLog()
            self._switchLogFile()

        self.reset()
        return


    def _closeLog(self) -> None:
        """
        Closes the JSON array in the log file, ensuring valid JSON formatting.
        """
        with open(self.logFile.resolve(), 'a') as file:
            file.write("\n]")

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

class VisualizableForwardSearch(ForwardSearch):
    def __init__(self, problem: DiscretePlanningProblem, logFile: Path, queue_options: Optional[Dict]=None , createParent: bool = False) -> None:
        """
        initializes search class with logfile
        :param problem: Planning problem to solve, must be an instance of DiscretePlanningProblem
        :param logFile: Path object representing the logFile
        :param queue_options: Dictionary of options dictating what kind of priority queue to initialize
            Possible Options:
                - 'type' : Indicates the type of priority queue to initialize
                    Possible Values:
                        - 'deque' to use deque queue from collections package (used for FIFO/LIFO style implementations)
                        - 'heapq' to use a binary heap using the heapq package
        :param createParent: Boolean indicating if the parent directory should be created when missing (default: False)
        """
        super().__init__(problem, queue_options)
        self.logger = SearchLogger(logFile)
        self.parentOption = createParent
        self.visitedTable = {}

    def generateSolution(self) -> Optional[List[Any]]:
        problem = self.problem
        visitedTable = self.visitedTable # if entry present state visited, value corresponds to preceding value
        self.addToFrontier(problem.initialState)
        visitedTable[problem.initialState] = None
        self.logger.logState("Initialization Event", {"Frontier": str(self.frontier), "Visitation Table": visitedTable})

        while self.frontier:
            currentState = self.expandFrontier()
            self.logger.logState("State Consideration", {"Frontier": str(self.frontier), "Visitation Table": visitedTable, "State": currentState})

            if problem.is_goal_state(currentState):
                self.logger.logState("Goal State Recognized", {"Frontier": str(self.frontier), "Visitation Table": visitedTable, "State": currentState})

                self._generateSolutionPath(currentState, visitedTable)

                self.logger.logState("Solution Generated", {"Frontier": str(self.frontier), "Visitation Table": visitedTable, "State": currentState, "Solution" : self.stringifySolution(self.solution)})
                self.logger.logWrite(options={"createParent": self.parentOption})
                self.logger.reset()
                return self.solution

            self.logger.logWrite(options={"createParent": self.parentOption})
            for action in problem.actionFunction(currentState):
                successor = problem.transitionFunction(currentState, action)
                self.logger.logState("Considering Successor",
                                     {"Frontier": str(self.frontier), "Visitation Table": visitedTable,
                                      "State": currentState, "Successor": successor, "Action": action})
                self.logger.logWrite(options={"createParent": self.parentOption})
                if successor not in visitedTable:
                    visitedTable[successor] = currentState
                    self.addToFrontier(successor, currentState, action)

                    self.logger.logState("Successor Not Previously Visited, Added to Memory",
                                         {"Frontier": str(self.frontier), "Visitation Table": visitedTable,
                                          "State": currentState, "Successor": successor, "Action": action})
                else:
                    self.logger.logState("State Previously Visited, Resolving Duplicate",
                                         {"Frontier": str(self.frontier), "Visitation Table": visitedTable,
                                          "State": currentState, "Successor": successor, "Action": action})

                    self.resolveDuplicateSuccessor(successor, currentState, action)

        self.logger.logState("No Solution Generated", {"Frontier": self.frontier, "Visitation Table": visitedTable, "Solution": None})
        self.logger.logWrite(options={"createParent":self.parentOption})
        self.logger.reset()
        return None
    # TODO: We can get a good speedup if logger acts concurrently, this way search algorithm does not have to block itself for I/O operations
    def _generateSolutionPath(self, currentState: Any, visitedTable: Dict):
        self.solution = []
        while currentState is not None:
            self.solution.append(currentState)
            currentState = visitedTable[currentState]

        self.solution.reverse()
        return

