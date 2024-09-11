from DiscretePlanning.forwardSearchAlgorithms import ForwardBFS, ForwardDFS
from DiscretePlanning.planningProblem import DiscretePlanningProblem
import unittest
from typing import Any, Set
from pathlib import Path
from os import remove, rmdir

class testForwardBFS(unittest.TestCase):
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

    def setUp(self):
        #Problem Setup
        belongingFunction = lambda x: x in 'ABCDEFGHI'
        actionFunction = self.actionFunction
        transitionFunction = self.transitionFunction
        initialState = 'A'
        goalStates = {'I'}
        self.problem = DiscretePlanningProblem(belongingFunction, actionFunction, transitionFunction, initialState, goalStates)

        #Logging Set Up
        self.logFile = Path("Tests/TestPath/ForwardBFS.json")
        createParent = True
        self.solver = ForwardBFS(self.problem, self.logFile, createParent)

    def tearDown(self):
        # remove(self.logFile)
        # rmdir(self.logFile.parent)
        return

    def test_BFS(self):
        solution = self.solver.generateSolution()
        self.assertIsNotNone(solution)
        self.assertTrue(self.solver.validateSolution(solution))

class testForwardDFS(unittest.TestCase):
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

    def setUp(self):
        #Problem Setup
        belongingFunction = lambda x: x in 'ABCDEFGHI'
        actionFunction = self.actionFunction
        transitionFunction = self.transitionFunction
        initialState = 'A'
        goalStates = {'I'}
        self.problem = DiscretePlanningProblem(belongingFunction, actionFunction, transitionFunction, initialState, goalStates)

        #Logging Set Up
        self.logFile = Path("Tests/TestPath/ForwardDFS.json")
        createParent = True
        self.solver = ForwardDFS(self.problem, self.logFile, createParent)

    def tearDown(self):
        # remove(self.logFile)
        # rmdir(self.logFile.parent)
        return

    def test_DFS(self):
        solution = self.solver.generateSolution()
        self.assertIsNotNone(solution)
        self.assertTrue(self.solver.validateSolution(solution))


# TODO: Implement a more robust automated test for BFS/DFS behaviour, avoid manual inspection of search log
if __name__ == '__main__':
    unittest.main()