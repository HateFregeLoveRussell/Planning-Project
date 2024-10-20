from DiscretePlanning.planningSearchVisualization import VisualizableForwardSearch
from DiscretePlanning.planningProblem import DiscretePlanningProblem
import numpy as np
from typing import Set, Tuple, Callable
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
        #rectilinear transitions
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

        #Diagonal Transitions:
        #boundary Cases
        if x ==0 or x==self.size[0]-1 or y ==0 or y==self.size[1]-1:
            if (x,y) == (0,0):
                actionSet.add('up-right')
            elif (x,y) == (self.size[0]-1,0):
                actionSet.add('up-left')
            elif (x,y) == (self.size[0]-1,self.size[1]-1):
                actionSet.add('down-left')
            elif (x,y) == (0,self.size[1]-1):
                actionSet.add('down-right')
            elif x == 0:
                actionSet.add('down-right')
                actionSet.add('up-right')
            elif y == 0:
                actionSet.add('up-right')
                actionSet.add('up-left')
            elif x == self.size[0]-1:
                actionSet.add('down-left')
                actionSet.add('up-left')
            elif y == self.size[1]-1:
                actionSet.add('down-right')
                actionSet.add('down-left')
        else:
            actionSet.add('up-right')
            actionSet.add('up-left')
            actionSet.add('down-right')
            actionSet.add('down-left')

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
        elif action == 'down':
            y -=1
        elif action == 'down-right':
            x += 1
            y -= 1
        elif action == 'down-left':
            x -= 1
            y -= 1
        elif action == 'up-right':
            y += 1
            x += 1
        elif action == 'up-left':
            y += 1
            x -= 1
        return repr((x,y))

    def _costFunction(self, state: str, action: str) -> float:
        x,y = literal_eval(state)[0], literal_eval(state)[1]
        coordinates = np.array([x,y,self.height_function(x,y)])
        x_prime, y_prime = literal_eval(self._transitionFunction(state, action))[0],literal_eval(self._transitionFunction(state, action))[1]
        coordinates_prime = np.array([x_prime, y_prime, self.height_function(x_prime, y_prime)])
        return float(np.linalg.norm(coordinates_prime-coordinates))

    def solve(self, solver: VisualizableForwardSearch) -> str:
            solution = solver.generateSolution()
            if (solver.validateSolution(solution)):
                return "Solution valid: " + solver.stringifySolution(solution)
            else:
                return "No Solution Exists"
