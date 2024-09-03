import unittest
from DiscretePlanning.planningProblem import DiscretePlanningProblem
def test_transition_function(state, action):
    match (state,action):
        case ('A','right'):
            return 'B'
        case ('B', 'right'):
            return 'C'
        case ('C', 'left'):
            return 'B'
        case ('D', 'left'):
            return 'C'
        case _:
            raise ValueError("state action transition not defined")
        
class TestDiscretePlanningProblem(unittest.TestCase):
    def setUp(self):
        # A -> B <-> C <- D
        self.stateSpace = {'A' : ['right'], 'B': [ 'right'], 'C': ['left'], 'D': ['left']}
        self.transitionFunction = test_transition_function
        self.initialState = 'A'
        self.goalStates = ['D', 'B']
    
    def test_init_success(self):
        """Test successful initialization of DiscretePlanningProblem."""
        planningProblem = DiscretePlanningProblem(
            self.stateSpace,
            self.transitionFunction,
            self.initialState,
            self.goalStates
        )
        self.assertEqual(planningProblem.initialState, self.initialState)
        self.assertEqual(planningProblem.goalStates, self.goalStates)
        self.assertEqual(planningProblem.stateSpace, self.stateSpace)
        self.assertEqual(planningProblem.transitionFunction, self.transitionFunction)

        

    def test_init_fail_initial_state(self):
        """Test initialization failure when the initial state is invalid."""
        with self.assertRaises(ValueError) as context:
            planningProblem = DiscretePlanningProblem(
                stateSpace = self.stateSpace,
                transitionFunction = self.transitionFunction,
                initialState = 'Z',
                goalStates = self.goalStates
            )
            self.assertTrue('Initial State not in State Space' in str(context.exception))

    def test_init_fail_goal_states(self):
        """Test initialization failure when one or more goal states are invalid."""
        with self.assertRaises(ValueError) as context:
            planningProblem = DiscretePlanningProblem(
                stateSpace = self.stateSpace,
                transitionFunction = self.transitionFunction,
                initialState = self.initialState,
                goalStates = ['D', 'A', 'Z']
            )
            self.assertTrue('One or more Goal States not in State Space' in str(context.exception))

if __name__ == '__main__':
    unittest.main()