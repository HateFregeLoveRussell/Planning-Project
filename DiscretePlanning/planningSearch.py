from typing import Callable, List, Optional, Any
from collections import deque
import heapq
from DiscretePlanning.planningProblem import DiscretePlanningProblem



class DiscretePlanningSolver:
    def __init__(self, problem: DiscretePlanningProblem):
        self.problem = problem
        self.solution = []
        return
        
    def generateSolution(self) -> Optional[List[Any]]:
        """
        Solves the planning problem.
        This method should be overridden by subclasses implementing specific algorithms.
        
        :return: A list of states representing the solution path, or None if no solution exists.
        """
        raise NotImplementedError("The solve method must be implemented by subclasses.")
    
    def validateSolution(self, solution: List[Any]) -> bool:
        """
        Determines if a successful solution provided by the solver is valid given the problem
        
        :param solution: Nonempty List of states representing the solution path.
        :return: A list of states representing the solution path, or None if no solution exists.
        """
        if solution == []:
            raise ValueError("Provided Plan is Empty")
        
        if solution[0] != self.problem.initialState:
            return False
        
        if solution[-1] not in self.problem.goalStates:
            return False
        
        for i in range(len(solution) - 1):
            state = solution[i]

            if not self.problem.belongingFunction(state):
                return False

            possible_succesors = self.problem.get_next_states(state)
            if solution[i+1] not in possible_succesors:
                return False

        return True
    
    def stringifySolution(self, solution: List[Any], options=None):
        """
        Converts the solution path into a formatted string.

        :param solution: List of states representing the solution path.
        :param options: Dictionary of options to customize the output.
            Possible options:
            - 'separator': String to separate states (default: ' -> ').
            - 'state_formatter': Function to format each state (default: str).
            - 'include_indices': Bool, whether to include indices (default: False).
        :return: A formatted string representing the solution path.
        """
        if options is None:
            options = {}
        separator = options.get('separator', ' -> ')
        state_formatter = options.get('state_formatter', str)
        include_indices = options.get('include_indices', False)

        if not solution:
            raise ValueError("Solution not found")
        
        formatted_solution = []
        for i, state in enumerate(solution):
            formatted_state = state_formatter(state)
            if include_indices:
                formatted_solution.append(f"{i+1}. {formatted_state}")
            else:
                formatted_solution.append(formatted_state)

        return separator.join(formatted_solution)

class ForwardSearch(DiscretePlanningSolver):
    def __init__(self, problem: DiscretePlanningProblem, queue_options=None):
        super().__init__(problem)
        if queue_options is None:
            queue_options = {}
        self.queue_type = queue_options.get('type','deque')
        if self.queue_type == 'deque':
                self.frontier = deque()
        elif self.queue_type == 'heapq':
                self.frontier = [] #empty lists are already heapified
        else:
            raise ValueError("Invalid Queue Type Provided")
        return

    def addToFrontier(self, state: Any, priority: float = None):
        """Add a state to the frontier. Overridden by specific algorithms."""
        raise NotImplementedError("addToFrontier must be implemented by subclasses.")

    def expandFrontier(self):
        """Pop a state from the frontier. Overridden by specific algorithms."""
        raise NotImplementedError("expandFrontier must be implemented by subclasses.")

    def resolveDuplicateSuccessor(self, state: Any):
        """Resolve a duplicate successor. Overridden by some specific algorithms."""
        return

    def generateSolution(self) -> Optional[List[Any]]:
        problem = self.problem
        visitedTable = {} # if entry present state visited, value corresponds to preceding value
        self.addToFrontier(problem.initialState, priority=0)
        visitedTable[problem.initialState] = None
        while self.frontier:
            currentState = self.expandFrontier()
            if problem.is_goal_state(currentState):
                self._generateSolutionPath(currentState, visitedTable)
                return self.solution
            for successor in problem.get_next_states(currentState):
                if successor not in visitedTable:
                    visitedTable[successor] = currentState
                    self.frontier.append(successor)
                else:
                    self.resolveDuplicateSuccessor(successor)
        return None

    def _generateSolutionPath(self, currentState: Any, visitedTable: dict):
        self.solution = [currentState]
        while currentState in visitedTable:
            currentState = visitedTable[currentState]
            self.solution.append(visitedTable[currentState])

        self.solution.reverse()
        return
