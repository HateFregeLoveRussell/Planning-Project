from DiscretePlanning.planningSearchVisualization import VisualizableForwardSearch
from DiscretePlanning.planningProblem import DiscretePlanningProblem
from pathlib import Path
from typing import Any, Callable
import heapq

class ForwardBFS(VisualizableForwardSearch):
    def __init__(self, problem : DiscretePlanningProblem, logFile : Path, createParent: bool = False) -> None:
        queueOptions = {'type' : 'deque'}
        super().__init__(problem, logFile, queueOptions, createParent)

    def addToFrontier(self, state: Any, currentState: Any = None, action: Any = None ):
        self.frontier.append(state)

    def expandFrontier(self) -> Any:
        return self.frontier.popleft() #FIFO behaviour enabled

class ForwardDFS(VisualizableForwardSearch):
    def __init__(self, problem : DiscretePlanningProblem, logFile : Path, createParent: bool = False) -> None:
        queueOptions = {'type' : 'deque'}
        super().__init__(problem, logFile, queueOptions, createParent)

    def addToFrontier(self, state: Any, currentState: Any = None, action: Any = None):
        self.frontier.append(state)

    def expandFrontier(self) -> Any:
        return self.frontier.pop() #LIFO behaviour enabled

class ForwardDijkstraSearch(VisualizableForwardSearch):
    def __init__(self, problem : DiscretePlanningProblem, logFile : Path, createParent: bool = False) -> None:
        queueOptions = {'type': 'heapq'}
        super().__init__(problem, logFile, queueOptions, createParent)
        if self.problem.costFunction is None:
            raise ValueError("No cost function provided for given Problem")
        self.costTable = {self.problem.initialState: 0.0}

    def addToFrontier(self, state: Any, currentState: Any = None, action: Any = None):
        # Compute Cost
        if currentState is not None and action is not None:
            cost = self.costTable[currentState] + self.problem.get_cost(currentState, action)

            self.logger.logState("State being added recognized as a successor, computing cost",
                                 {"Frontier": str(self.frontier), "Visitation Table": self.visitedTable,
                                  "Considered State": state, "Predecessor": currentState, "Action": action,
                                  "Cost Table": self.costTable, "Cost": cost, "Edge Cost": self.problem.get_cost(currentState, action)})

        else:
            cost  = self.costTable[state] #this branch should only execute for initial state
            if cost == 0.0: # this if statement is unnecessary but i included it just to guard against weird errors
                heapq.heappush(self.frontier, (cost, state))
            self.logger.logState("State being added recognized as initial state, deferring to cost table",
                                 {"Frontier": str(self.frontier), "Visitation Table": self.visitedTable
                                     , "Considered State": state, "Cost Table": self.costTable, "Cost" : cost})
        self.logger.logWrite(options={"createParent": self.parentOption})
        # Determine how to modify Frontier
        if state not in self.costTable or cost < self.costTable[state]:
            self.costTable[state] = cost #add or update cost table
            heapq.heappush(self.frontier, (cost, state)) #reorder priority Queue
            self.visitedTable[state] = currentState
            self.logger.logState("State being added either does not have associated cost or a better cost was found, updating memory",
                                 {"Frontier": str(self.frontier), "Visitation Table": self.visitedTable,
                                  "Considered State": state, "Cost Table": self.costTable, "Cost" : cost})
            self.logger.logWrite(options={"createParent": self.parentOption})
        return

    def expandFrontier(self) -> Any:
        return heapq.heappop(self.frontier)[1]  # Pop the state with the lowest cost

    def resolveDuplicateSuccessor(self, state: Any, currentState: Any = None, action: Any = None):
        # We have to potentially reorder based on cost here
        new_cost = self.costTable[currentState] + self.problem.get_cost(currentState, action)
        self.logger.logState("New path to state found, computing new cost",
                             {"Frontier": str(self.frontier), "Visitation Table": self.visitedTable,
                                  "Duplicate State": state, "Predecessor": currentState, "Action": action,
                                  "Cost Table": self.costTable, "New Cost": new_cost,
                              "Edge Cost": self.problem.get_cost(currentState, action)})
        self.logger.logWrite(options={"createParent": self.parentOption})
        # if computed cost is better we have to update cost table & reorder queue
        if new_cost < self.costTable[state]:
            self.costTable[state] = new_cost
            heapq.heappush(self.frontier, (new_cost, state))
            self.visitedTable[state] = currentState  # Update the visited table with the predecessor
            self.logger.logState("New cost better than old cost, updating memory",
                                 {"Frontier": str(self.frontier), "Visitation Table": self.visitedTable,
                                  "Duplicate State": state, "Cost Table": self.costTable, "New Cost" : new_cost,
                                  "Old Cost": self.costTable[state]})
            self.logger.logWrite(options={"createParent": self.parentOption})
        return
