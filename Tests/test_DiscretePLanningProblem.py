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
        case ('C', 'right'):
            return 'D'
        case ('D', 'left'):
            return 'C'
        case _:
            raise ValueError("state action transition not defined")

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
        
        
class TestDiscretePlanningProblem(unittest.TestCase):
    def setUp(self):
        # A -> B <-> C <-> D . . . Z
        self.belongingFunction = lambda state: state in ['A', 'B', 'C', 'D', 'Z']
        self.transitionFunction = test_transition_function
        self.actionFunction= test_action_function
        self.actionSpace = set(['left','right'])
        self.initialState = 'A'
        self.goalStates = set(['D', 'B'])

    #INIT tests
    def test_init_success(self):
        """Test successful initialization of DiscretePlanningProblem."""
        planningProblem = DiscretePlanningProblem(
            actionFunction=self.actionFunction,
            belongingFunction=self.belongingFunction,
            transitionFunction=self.transitionFunction,
            actionSpace=self.actionSpace,
            initialState=self.initialState,
            goalStates=self.goalStates
        )
        self.assertEqual(planningProblem.initialState, self.initialState)
        self.assertSetEqual(planningProblem.goalStates, self.goalStates)
        self.assertEqual(planningProblem.actionFunction, self.actionFunction)
        self.assertEqual(planningProblem.belongingFunction, self.belongingFunction)
        self.assertEqual(planningProblem.transitionFunction, self.transitionFunction)
        self.assertSetEqual(planningProblem.actionSpace, set(['left','right']))

    def test_init_fail_initial_state(self):
        """Test initialization failure when the initial state is invalid."""
        with self.assertRaises(ValueError) as context:
            planningProblem = DiscretePlanningProblem(
                actionFunction=self.actionFunction,
                belongingFunction=self.belongingFunction,
                transitionFunction=self.transitionFunction,
                actionSpace=self.actionSpace,
                initialState='1',
                goalStates=self.goalStates
            )
            self.assertTrue('Initial State not in State Space' in str(context.exception))

    def test_init_fail_goal_states(self):
        """Test initialization failure when one or more goal states are invalid."""
        with self.assertRaises(ValueError) as context:
            planningProblem = DiscretePlanningProblem(
                actionFunction=self.actionFunction,
                belongingFunction=self.belongingFunction,
                transitionFunction=self.transitionFunction,
                actionSpace=self.actionSpace,
                initialState=self.initialState,
                goalStates = set(['D', 'A', '1', '2'])
            )
            self.assertTrue('One or more Goal States not in State Space' in str(context.exception))

    #get_next_states tests
    def test_get_next_states_success_single(self):
        """Test get_next_states() with single transition per state"""
        planningProblem = DiscretePlanningProblem(
            actionFunction=self.actionFunction,
            belongingFunction=self.belongingFunction,
            transitionFunction=self.transitionFunction,
            actionSpace=self.actionSpace,
            initialState=self.initialState,
            goalStates=self.goalStates
        )
        self.assertEqual(planningProblem.get_next_states('A'), ['B'])
        self.assertEqual(planningProblem.get_next_states('B'), ['C'])
        self.assertEqual(planningProblem.get_next_states('D'), ['C'])
    
    def test_get_next_states_success_multi(self):
        """Test get_next_states() with multiple transition state"""
        planningProblem = DiscretePlanningProblem(
            actionFunction=self.actionFunction,
            belongingFunction=self.belongingFunction,
            transitionFunction=self.transitionFunction,
            actionSpace=self.actionSpace,
            initialState=self.initialState,
            goalStates=self.goalStates
        )
        self.assertCountEqual(planningProblem.get_next_states('C'),['B','D'])
        self.assertEqual(sorted(planningProblem.get_next_states('C')), sorted(['B','D']))

    def test_get_next_states_isolated_state(self):
        """Test get_next_states() with Isolated State"""
        planningProblem = DiscretePlanningProblem(
            actionFunction=self.actionFunction,
            belongingFunction=self.belongingFunction,
            transitionFunction=self.transitionFunction,
            actionSpace=self.actionSpace,
            initialState=self.initialState,
            goalStates=self.goalStates
        )
        self.assertEqual(planningProblem.get_next_states('Z'), [])
    
    def test_get_next_states_failure(self):
        planningProblem = DiscretePlanningProblem(
            actionFunction=self.actionFunction,
            belongingFunction=self.belongingFunction,
            transitionFunction=self.transitionFunction,
            actionSpace=self.actionSpace,
            initialState=self.initialState,
            goalStates=self.goalStates
        )
        with self.assertRaises(ValueError) as context:
            planningProblem.get_next_states('1')
            self.assertTrue("State Not Found in State Space" in str(context.exception))

if __name__ == '__main__':
    unittest.main()