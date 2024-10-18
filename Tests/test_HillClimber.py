from DiscretePlanning.HillClimber import HillClimber
from DiscretePlanning.forwardSearchAlgorithms import ForwardAStar
import unittest
from pathlib import Path
import numpy as np
from ast import literal_eval

# Define the height function
def test_height_function(x: int, y: int) -> float:
    peak1 = 20 * np.exp(-((x - 8)**2 + (y - 8)**2) / 20)
    peak2 = 8 * np.exp(-((x - 15)**2 + (y - 15)**2) / 30)
    peak3 = 2.3 * np.exp(-((x - 10)**2 + (y - 10)**2) / 15)
    return peak1 + peak2 + peak3

class test_HillClimber(unittest.TestCase):
        def setUp(self):
            pass
        def test(self):
            initial_state = repr((1, 19))
            goalStates = {repr((19, 1))}
            size = (20, 20)
            height_function = test_height_function

            def HueristicFunction(state: str) -> float:
                x, y = literal_eval(state)[0], literal_eval(state)[1]
                coordinates = np.array([x, y, height_function(x, y)])
                x_prime, y_prime = literal_eval(next(iter(goalStates)))[0], literal_eval(next(iter(goalStates)))[1]
                coordinates_prime = np.array([x_prime, y_prime, height_function(x_prime, y_prime)])
                return float(np.linalg.norm(coordinates_prime - coordinates))

            logFile = Path("DiscretePlanning/Environment/HillClimberEnvironment/Logs/HillClimberSecondTest.json")
            create_parent = True

            climber = HillClimber(height_function, size, initial_state, goalStates)
            solver = ForwardAStar(problem=climber.problem, logFile=logFile, heuristic=HueristicFunction,
                                  createParent=create_parent)
            climber.solve(solver)

if __name__ == '__main__':
    unittest.main()