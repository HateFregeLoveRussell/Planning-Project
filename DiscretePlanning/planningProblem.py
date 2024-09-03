from typing import Callable
class DiscretePlanningProblem: 
    """
        A class to represent a Discrete Planning Problem based on Formulation 2.1

        ...

        Attributes
        ----------
        stateSpace : dict
            Dictionary representing the state space where keys are states and values are lists of possible actions.
        transitionFunction : str -> list
            A function that takes a state and an action as input and returns the resulting state.
        initialState : str
            The initial state of the problem represented as a string as in stateSpace
        goalStates : list
            A list of goal states for the planning Problem
            
        Methods
        -------
        TODO write methods descriptions
    """

    def __init__(self,stateSpace: dict, transitionFunction: Callable, initialState: str, goalStates: list):
        """
        Initialize the planning problem.
        
        :param stateSpace: Dictionary representing the state space where keys are states and values are lists of possible actions.
        :param transitionFunction: A function that takes a state and an action as input and returns the resulting state.
        :param initialState: The initial state of the problem represented as a string as in stateSpace
        :param goalStates: A list of goal states for the planning Problem
        """
        # dictionary where state x maps to action space U(x)
        self.stateSpace = stateSpace
        # transition function f: X x U(x) -> X
        self.transitionFunction = transitionFunction

        if initialState not in self.stateSpace:
            raise ValueError("Initial State not in State Space")
        self.initialState = initialState
        
        if not all(state in stateSpace for state in goalStates):
            raise ValueError("Some Goal state is not in the State Space")
        self.goalStates = goalStates

