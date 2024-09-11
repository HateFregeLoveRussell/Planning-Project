from DiscretePlanning.planningProblem import DiscretePlanningProblem
from DiscretePlanning.forwardSearchAlgorithms import ForwardAStar
from pathlib import Path
from typing import Callable, Any, Tuple, Set
from os import remove, rmdir
from math import sqrt
import unittest
import re
class test_AStar(unittest.TestCase):
    def special_costFunction(self, state: str, action: str) -> float:
        #set up high-cost barrier at a diagonal. Lowest cost path should go under and move vertically to goal
        specialSet = [(1,5), (2,4), (3,3), (4,2)]
        coordinates = tuple(map(int, re.findall(r'\d+', state)))
        x = coordinates[0]
        y = coordinates[1]
        if (x,y) in specialSet:
            return 11.0
        successor = self.transitionFunction(state, action)
        coordinates_prime = tuple(map(int, re.findall(r'\d+', successor)))
        x_prime = coordinates[0]
        y_prime = coordinates[1]
        if (x_prime,y_prime) in specialSet:
            return 11.0
        return 1.0

    def belongingFunction(self, state: str) -> bool:
        # 6x6 grid of unicost nodes
        coordinates = tuple(map(int, re.findall(r'\d+', state)))
        x = coordinates[0]
        y = coordinates[1]
        if type(x) is not int or type(y) is not int:
            return False
        if x > 5 or x < 0:
            return False
        if y > 5 or y < 0:
            return False
        return True
    def actionFunction(self,state: str) -> Set[str]:
        coordinates = tuple(map(int, re.findall(r'\d+', state)))
        x = coordinates[0]
        y = coordinates[1]
        actionSet = set()
        if x == 0:
            actionSet.add("right")
        elif x == 5:
            actionSet.add("left")
        else:
            actionSet.add("right")
            actionSet.add("left")

        if y == 0:
            actionSet.add("up")
        elif y == 5:
            actionSet.add("down")
        else:
            actionSet.add("up")
            actionSet.add("down")

        return actionSet

    def transitionFunction(self, state: str, action: str) -> str:
        coordinates = tuple(map(int, re.findall(r'\d+', state)))
        x = coordinates[0]
        y = coordinates[1]
        if action == "right":
            x = x +1
        elif action == "left":
            x = x -1
        elif action == "up":
            y = y +1
        elif action == "down":
            y = y -1
        else:
            raise ValueError("Invalid action")
        return f'({x}, {y})'

    def costFunction(self, state: Tuple, action: str) -> float:
        return 1.0

    def hueristicFunction(self, state: str) -> float:
        coordinates = tuple(map(int, re.findall(r'\d+', state)))
        x = coordinates[0]
        y = coordinates[1]
        return sqrt((x-5)**2 + (y-5)**2) #Use L-2 Norm as Heuristic

    def setUp(self):
        belongingFunction = self.belongingFunction
        actionFunction = self.actionFunction
        transitionFunction = self.transitionFunction
        costFunction = self.costFunction

        initialState = '(0, 0)'
        goalStates = {'(5, 5)'}
        self.problem = DiscretePlanningProblem(belongingFunction, actionFunction, transitionFunction, initialState,
                                               goalStates, costFunction=costFunction)

        # Logging Set Up
        self.logFile = Path("Tests/TestPath/ForwardAStar.json")
        createParent = True
        self.solver = ForwardAStar(problem = self.problem, logFile = self.logFile,heuristic=self.hueristicFunction,createParent= createParent)

    def tearDown(self):
        remove(self.logFile)
        rmdir(self.logFile.parent)
        return

    def test_AStar_success(self):
        solution = self.solver.generateSolution()
        self.assertIsNotNone(solution)
        self.assertTrue(self.solver.validateSolution(solution))

    def test_AStar_special(self):
        self.problem.costFunction = self.special_costFunction
        solution = self.solver.generateSolution()
        self.assertIsNotNone(solution)
        self.assertTrue(self.solver.validateSolution(solution))
if __name__ == '__main__':
    unittest.main()
    #TODO: weird bug where initial cost calculations appear before initialization event