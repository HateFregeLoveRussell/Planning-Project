from typing import Callable, List, Optional, Any
from DiscretePlanning.planningProblem import DiscretePlanningProblem

class DiscretePlanningSolver:
    def __init__(self, problem: DiscretePlanningProblem):
        self.problem = problem
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
    
    def stringifySolution(self, solution: List[Any], options={}):
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
                
        print (f'sol : {solution}')
        print (f'sep : {separator}')
        print (f'formatted_sol : {formatted_solution}')
        print (f'final output : {separator.join(formatted_solution)}')
        return separator.join(formatted_solution)
