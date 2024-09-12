from DiscretePlanning.planningSearchVisualization import VisualizableForwardSearch
from DiscretePlanning.planningProblem import DiscretePlanningProblem
import numpy as np
from typing import Any, Set, Tuple, Callable
from pathlib import Path
import plotly.graph_objs as go
from ast import literal_eval



class HillClimber:
    def __init__(self, height_function: Callable[[int, int], float], size : Tuple[int,int],
                 initialState: str, goalStates: Set[str],) -> None:
        self.height_function = height_function
        self.size = size
        self.problem = DiscretePlanningProblem(belongingFunction = self._belongingFunction,
                                               actionFunction = self._actionFunction,
                                               transitionFunction = self._transitionFunction,
                                               initialState = initialState,
                                               goalStates = goalStates,
                                               costFunction = self._costFunction)


    def _belongingFunction(self, state: str) -> bool:
        coordinates = literal_eval(state)
        x,y = coordinates[0],coordinates[1]
        if type(x) is not int  or type(y) is not int:
            return False
        if x < 0 or x > self.size[0] - 1  or y < 0 or y > self.size[1] - 1:
            return False
        return True

    def _actionFunction(self, state: str) -> Set[str]:
        coordinates = literal_eval(state)
        x, y = coordinates[0], coordinates[1]
        actionSet = set()
        if x == 0:
            actionSet.add('right')
        elif x == self.size[0] - 1:
            actionSet.add('left')
        else:
            actionSet.add('left')
            actionSet.add('right')

        if y == 0:
            actionSet.add('up')
        elif y == self.size[1] - 1:
            actionSet.add('down')
        else:
            actionSet.add('down')
            actionSet.add('up')
        return actionSet

    def _transitionFunction(self, state: str, action: str) -> str:
        coordinates = literal_eval(state)
        x, y = coordinates[0], coordinates[1]
        if action == 'right':
            x +=1
        elif action == 'left':
            x -=1
        elif action == 'up':
            y +=1
        else:
            y -=1
        return repr((x,y))

    def _costFunction(self, state: str, action: str) -> float:
        x,y = literal_eval(state)[0], literal_eval(state)[1]
        coordinates = np.array([x,y,self.height_function(x,y)])
        x_prime, y_prime = literal_eval(self._transitionFunction(state, action))[0],literal_eval(self._transitionFunction(state, action))[1]
        coordinates_prime = np.array([x_prime, y_prime, self.height_function(x_prime, y_prime)])
        return float(np.linalg.norm(coordinates_prime-coordinates))

    def solve(self, solver: VisualizableForwardSearch) -> None:
            solution = solver.generateSolution()
            if (solver.validateSolution(solution)):
                print("Solution valid: " + solver.stringifySolution(solution))
            else:
                print("No Solution Exists")
