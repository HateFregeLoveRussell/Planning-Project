from DiscretePlanning.planningProblem import DiscretePlanningProblem
from DiscretePlanning.planningSearch import DiscretePlanningSolver, ForwardSearch
from pathlib import Path
from typing import Dict, Any, Optional, List
from json import dumps, dump
from logging import basicConfig, WARNING, warning

from collections import deque
import heapq

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

    def generateSolution(self) -> Optional[List[Any]]:
        problem = self.problem
        visitedTable = {} # if entry present state visited, value corresponds to preceding value
        self.addToFrontier(problem.initialState, priority=0)
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
            for successor in problem.get_next_states(currentState):
                self.logger.logState("Considering Successor", {"Frontier": str(self.frontier), "Visitation Table": visitedTable, "State": currentState, "Successor": successor})
                self.logger.logWrite(options={"createParent": self.parentOption})
                if successor not in visitedTable:
                    visitedTable[successor] = currentState
                    self.addToFrontier(successor, from_state=currentState)

                    self.logger.logState("Successor Not Previously Visited, Added to Memory", {"Frontier": str(self.frontier), "Visitation Table": visitedTable, "State": currentState, "Successor": successor})
                else:
                    self.logger.logState("State Previously Visited, Resolving Duplicate", {"Frontier": str(self.frontier), "Visitation Table": visitedTable, "State": currentState, "Successor": successor})

                    self.resolveDuplicateSuccessor(successor)

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

