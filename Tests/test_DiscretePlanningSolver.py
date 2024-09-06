import unittest
from collections import deque
from DiscretePlanning.planningSearch import DiscretePlanningSolver, ForwardSearch
from DiscretePlanning.planningProblem import DiscretePlanningProblem

def test_transition_function(state, action):
    match (state,action):
        case ('A','right'):
            return 'B'
        case ('B', 'right'):
            return 'C'
        case ('C', 'left'):
            return 'B'
        case ('C', 'right'):
            return 'D'
        case ('D', 'left'):
            return 'C'
        case _:
            raise ValueError("state action transition not defined")

def test_predecessor_function(state) -> set:
    match(state):
        case('A'):
            return set(())
        case('B'):
            return set([('A','right'),('C','left')])
        case('C'):
            return set([('B', 'right'),('D','left')])
        case('D'):
            return set([('C','right')])
        case('Z'):
            return set(())
        case _:
            raise ValueError("state actions not defined")

def test_action_function(state) -> set:
    match(state):
        case('A'):
            return set(['right'])
        case('B'):
            return set(['right'])
        case('C'):
            return set(['right', 'left'])
        case('D'):
            return set(['left'])
        case('Z'):
            return set([])
        case _:
            raise ValueError("state actions not defined")

# A -> B <-> C <-> D . . . Z

class TestDiscretePlanningSolver(unittest.TestCase):
    def setUp(self):
        self.belongingFunction = lambda state: state in ['A', 'B', 'C', 'D', 'Z']
        self.transitionFunction = test_transition_function
        self.actionFunction= test_action_function
        self.predecessorFunction = test_predecessor_function
        self.actionSpace = set(['left','right'])
        self.initialState = 'A'
        self.goalStates = set(['D', 'B'])
        self.problem = DiscretePlanningProblem(
            actionFunction=self.actionFunction,
            belongingFunction=self.belongingFunction,
            transitionFunction=self.transitionFunction,
            predecessorFunction=self.predecessorFunction,
            actionSpace=self.actionSpace,
            initialState=self.initialState,
            goalStates=self.goalStates
        )
        
    #init
    def test_solver_init(self):
        solver = DiscretePlanningSolver(self.problem)
        self.assertEqual(solver.problem, self.problem)
        self.assertEqual(solver.solution, [])

    #generateSolution    
    def test_generate_solution_not_implemented(self):
        solver = DiscretePlanningSolver(self.problem)
        with self.assertRaises(NotImplementedError) as context:
            solver.generateSolution()
            self.assertTrue("The solve method must be implemented by subclasses." in str(context.exception))

    #validateSolution
    def test_validate_solution_empty(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = []
        with self.assertRaises(ValueError) as context:
            solver.validateSolution(solution)
            self.assertTrue("Provided Plan is Empty" in str(context.exception))
    
    def test_validate_solution_invalid_initial_state(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['C','D']
        self.assertFalse(solver.validateSolution(solution))
    
    def test_validate_solution_invalid_goal_state(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'B', 'C']
        self.assertFalse(solver.validateSolution(solution))
    
    def test_validate_solution_invalid_state_in_sequence(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'L', 'B']
        self.assertFalse(solver.validateSolution(solution))
    
    def test_validate_solution_invalid_transition(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'C']
        self.assertFalse(solver.validateSolution(solution))
    
    def test_validate_solution_valid(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'B']
        self.assertTrue(solver.validateSolution(solution))
    
    #stringifySolution
    def test_stringify_solution_empty(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = []
        with self.assertRaises(ValueError) as context:
            solver.stringifySolution(solution)
            self.assertTrue("Solution not found" in str(context.exception))
    
    def test_stringify_solution_default_solution(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'B', 'C']
        expected_output = "A -> B -> C"
        self.assertEqual(solver.stringifySolution(solution),expected_output)
    
    def test_stringify_solution_custom_separator(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'B', 'C']
        options = {'separator': ' | '}
        expected_output = "A | B | C"
        self.assertEqual(solver.stringifySolution(solution, options), expected_output)
    
    def test_stringify_solution_custom_state_formatter(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'B', 'C']
        options = {'state_formatter' : str.lower}
        expected_output = "a -> b -> c"
        self.assertEqual(solver.stringifySolution(solution, options), expected_output)
    
    def test_stringify_solution_include_indices(self):
        solver = DiscretePlanningSolver(self.problem)
        solution = ['A', 'B', 'C']
        options = {'include_indices' : True}
        expected_output = "1. A -> 2. B -> 3. C"
        self.assertEqual(solver.stringifySolution(solution, options), expected_output)

class TestForwardSearch(TestDiscretePlanningSolver):
    def setUp(self):
        super().setUp()

    #__init__
    def test_ForwardSearch_init_success(self):
        # deque option
        solver = ForwardSearch(problem=self.problem, queue_options={'type': 'deque'})
        self.assertEqual(solver.problem, self.problem)
        self.assertEqual(solver.solution, [])
        self.assertEqual(solver.queue_type, 'deque')
        self.assertEqual(solver.frontier, deque())

        # heapq option
        solver = ForwardSearch(problem=self.problem, queue_options={'type': 'heapq'})
        self.assertEqual(solver.problem, self.problem)
        self.assertEqual(solver.solution, [])
        self.assertEqual(solver.queue_type, 'heapq')
        self.assertEqual(solver.frontier, [])

    def test_ForwardSearch_init_default(self):
        solver = ForwardSearch(problem=self.problem)
        self.assertEqual(solver.problem, self.problem)
        self.assertEqual(solver.solution, [])
        self.assertEqual(solver.queue_type, 'deque')
        self.assertEqual(solver.frontier, deque())

    def test_ForwardSearch_init_invalid_options(self):
        with self.assertRaises(ValueError) as context:
            solver = ForwardSearch(problem=self.problem, queue_options={'type': 'invalid type'})
            self.assertTrue("Invalid Queue Type Provided" in str(context.exception))

    #addToFrontier
    def test_ForwardSearch_addToFrontier_not_implemented(self):
        solver = ForwardSearch(problem=self.problem, queue_options={'type': 'deque'})
        with self.assertRaises(NotImplementedError) as context:
            solver.addToFrontier('dummyState', 10000)
            self.assertTrue("addToFrontier must be implemented by subclasses." in str(context.exception))
    #expandFrontier
    def test_ForwardSearch_expandFrontier_not_implemented(self):
        solver = ForwardSearch(problem=self.problem, queue_options={'type': 'deque'})
        with self.assertRaises(NotImplementedError) as context:
            solver.expandFrontier()
            self.assertTrue("expandFrontier must be implemented by subclasses." in str(context.exception))

    #generateSolution - Cant really test without mocking a later implementation we would need anyways


if __name__ == '__main__':
    unittest.main()