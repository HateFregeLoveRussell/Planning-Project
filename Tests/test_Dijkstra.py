import unittest
from typing import Set
from pathlib import Path
from os import rmdir, remove
from DiscretePlanning.forwardSearchAlgorithms import ForwardDijkstraSearch
from DiscretePlanning.planningProblem import DiscretePlanningProblem
class testForwardDijakstra(unittest.TestCase):
    def belongingFunction(self, state: str) -> bool:
        return state in 'ABCDEFGHIZ'
    def actionFunction(self,state: str) -> Set[str]:
        grid = {
            'A': {'right': 'B', 'down': 'D'},
            'B': {'left': 'A', 'right': 'C', 'down': 'E'},
            'C': {'left': 'B', 'down': 'F'},
            'D': {'up': 'A', 'right': 'E', 'down': 'G'},
            'E': {'up': 'B', 'left': 'D', 'right': 'F', 'down': 'H'},
            'F': {'up': 'C', 'left': 'E', 'down': 'I'},
            'G': {'up': 'D', 'right': 'H'},
            'H': {'up': 'E', 'left': 'G', 'right': 'I'},
            'I': {'up': 'F', 'left': 'H'}
        }
        return set(grid[state].keys())

    def transitionFunction(self, state: str, action: str) -> str:
        grid = {
            'A': {'right': 'B', 'down': 'D'},
            'B': {'left': 'A', 'right': 'C', 'down': 'E'},
            'C': {'left': 'B', 'down': 'F'},
            'D': {'up': 'A', 'right': 'E', 'down': 'G'},
            'E': {'up': 'B', 'left': 'D', 'right': 'F', 'down': 'H'},
            'F': {'up': 'C', 'left': 'E', 'down': 'I'},
            'G': {'up': 'D', 'right': 'H'},
            'H': {'up': 'E', 'left': 'G', 'right': 'I'},
            'I': {'up': 'F', 'left': 'H'}
        }
        return grid[state][action]
    def costFunction(self, state: str, action: str) -> float:
        grid = {
            'A': {'right': 2.0, 'down': 1.0},
            'B': {'left': 2.0, 'right': 2.0, 'down': 3.0},
            'C': {'left': 2.0, 'down': 2.0},
            'D': {'up': 1.0, 'right': 4.0, 'down': 2.0},
            'E': {'up': 3.0, 'left': 4.0, 'right': 1.0, 'down': 2.0},
            'F': {'up': 2.0, 'left': 1.0, 'down': 3.0},
            'G': {'up': 2.0, 'right': 3.0},
            'H': {'up': 2.0, 'left': 3.0, 'right': 2.0},
            'I': {'up': 3.0, 'left': 2.0},
        }
        return grid[state][action]

    def setUp(self):
        belongingFunction = self.belongingFunction
        actionFunction = self.actionFunction
        transitionFunction = self.transitionFunction
        costFunction = self.costFunction

        initialState = 'A'
        goalStates = {'I'}
        self.problem = DiscretePlanningProblem(belongingFunction, actionFunction, transitionFunction, initialState,
                                               goalStates, costFunction=costFunction)

        # Logging Set Up
        self.logFile = Path("Tests/TestPath/ForwardDijkstra.json")
        createParent = True
        self.solver = ForwardDijkstraSearch(self.problem, self.logFile, createParent)

    def tearDown(self):
        remove(self.logFile)
        rmdir(self.logFile.parent)
        return

    def test_ForwardDijakstra(self):
        solution = self.solver.generateSolution()
        self.assertIsNotNone(solution)
        self.assertTrue(self.solver.validateSolution(solution))

    def test_ForwardDijakstra_no_solution(self):
        self.problem.goalStates= {'Z'}
        solution = self.solver.generateSolution()
        self.assertIsNone(solution)

if __name__ == '__main__':
    unittest.main()