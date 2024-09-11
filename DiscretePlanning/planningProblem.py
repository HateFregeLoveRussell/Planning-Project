from typing import Callable, List, Set, Any
class DiscretePlanningProblem: 
    """
        A class to represent a Discrete Planning Problem based on Formulation 2.1

        ...

        Attributes if it belongs to the state space X or not
        actionFunction : X -> U(x)
            A function that takes a state and return a set object corresponding to the actions that can be preformed from this state i.e U(x)
        predecessorFunction: X-> U^{-1}(x)
            A function that takes a state and returns a set of action state pairs that lead to the state i.e U^{-1}(x)
        transitionFunction : X x U(x) -> X
            A function that takes a state and an action as input and returns the resulting state.
        initialState : 
            The initial state of the problem represented as a string as in stateSpace
        goalStates : set
            A list of goal states for the planning Problem
        actionSpace : set
            A set object corresponding to the union of action sets across all sets
            
        Methods
        -------
        get_prev_states : Given a state, return an array of possible predecessor states.

        get_next_states : Given a state, return an array of possible next states.
    """

    def __init__(self,belongingFunction: Callable[[Any], bool], actionFunction: Callable[[Any], Set[Any]], transitionFunction: Callable[[Any, Any], Any], initialState: Any, goalStates: Set[Any], actionSpace: Set[Any] = None, predecessorFunction: Callable[[Any], Set[Any]] = None, costFunction :Callable = None):
        """
        Initialize the planning problem.
        
        :param belongingFunction: A function that takes a state and returns a boolean corresponding to if it belongs to the state space X or not
        :param actionFunction: A function that takes a state and return a set object corresponding to the actions that can be preformed from this state i.e U(x)
        :param predecessorFunction: A function that takes a state and returns a set of actions state pairs that lead to the state i.e U^{-1}(x)
        :param transitionFunction: A function that takes a state and an action as input and returns the resulting state.
        :param initialState: The initial state of the problem represented as a string as in stateSpace
        :param goalStates: A set of goal states for the planning Problem
        :param actionSpace: A set object corresponding to the union of action sets across all sets - optional
        :param costFunction: A function that takes a state and an action as input and gives a non-negative (float) cost associated with the transition as output
        """
        # belonging function f: X -> T/F
        self.belongingFunction = belongingFunction

        # action function f: X -> U(x)
        self.actionFunction = actionFunction

        # transition function f: X x U(x) -> X
        self.transitionFunction = transitionFunction

        # predecessor function f: X -> U^{-1}(x)
        self.predecessorFunction = predecessorFunction

        # cost function f: X x U(x) -> R^+
        self.costFunction = costFunction

        if not belongingFunction(initialState):
            raise ValueError("Initial State not in State Space")
        self.initialState = initialState
        
        if not all(belongingFunction(state) for state in goalStates):
            raise ValueError("Some Goal state is not in the State Space")
        self.goalStates = goalStates
        
        self.actionSpace = actionSpace

    def get_cost(self,state: Any, action: Any) -> float:
        """
        Given a state and an action associated with the state will return cost of transition
        Should be used instead of calling self.costFunction directly
        :param state: The current State belonging to the defined State Space
        :param action:  An action associated with the state, should belong to action space of the state
        :return: a non-negative cost obtained through user provided callback
        """
        #gaurd against malformed inputs
        if not self.belongingFunction(state):
            raise ValueError("State not in State Space")
        if action not in self.actionFunction(state):
            raise ValueError("Action not in action set associated with State")

        cost = self.costFunction(state, action)
        if type(cost) != float:
            raise ValueError("Returned cost is not a float")
        if cost < 0:
            raise ValueError("Returned cost is negative")

        return cost

    def get_next_states(self, state) -> list: 
        """
        Given a state, return an array of possible next states.
        
        :param state: The current state.
        :return: List of possible next states.
        """
        if not self.belongingFunction(state):
            raise ValueError("State Not Found in State Space")
        
        actions = self.actionFunction(state)

        return [self.transitionFunction(state,action) for action in actions]

    def get_prev_states(self, state) -> list:
        """
        Given a state, return an array of possible predecessor states.
        
        :param state: The current state.
        :return: List of possible predecessor states.
        """
        if not self.belongingFunction(state):
            raise ValueError("State Not Found in State Space")
        if self.predecessorFunction is None:
            raise RuntimeError("Predecessor Function Not Defined")
        
        actionStatePairs = self.predecessorFunction(state)
        return [actionStatePair[0] for actionStatePair in actionStatePairs]

    def is_goal_state(self, state: Any) -> bool:
        """
        Given a state, return true if state belongs to goal states return false otherwise

        :param state: the potential goal state
        """
        #TODO: we can achieve this functionality for countable Goal Sets using a callback made by the user
        return state in self.goalStates
