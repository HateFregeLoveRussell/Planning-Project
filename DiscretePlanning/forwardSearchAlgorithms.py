from DiscretePlanning.planningSearchVisualization import VisualizableForwardSearch
from DiscretePlanning.planningProblem import DiscretePlanningProblem
from pathlib import Path
from typing import Any

class ForwardBFS(VisualizableForwardSearch):
    def __init__(self, problem : DiscretePlanningProblem, logFile : Path, createParent: bool = False) -> None:
        queueOptions = {'type' : 'deque'}
        super().__init__(problem, logFile, queueOptions, createParent)

    def addToFrontier(self, state: Any, priority: float = None, from_state: Any = None):
        self.frontier.append(state)

    def expandFrontier(self) -> Any:
        return self.frontier.popleft() #FIFO behaviour enabled

class ForwardDFS(VisualizableForwardSearch):
    def __init__(self, problem : DiscretePlanningProblem, logFile : Path, createParent: bool = False) -> None:
        queueOptions = {'type' : 'deque'}
        super().__init__(problem, logFile, queueOptions, createParent)

    def addToFrontier(self, state: Any, priority: float = None, from_state: Any = None):
        self.frontier.append(state)


    def expandFrontier(self) -> Any:
        return self.frontier.pop() #LIFO behaviour enabled

