# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


def genericSearch(problem, fringe, fringeAdd):
    """
    Full-fledged generic search functions to help Pacman plan routes.
    Since each algorithm is very similar. Algorithms for DFS, BFS, UCS, and A*
    differ only in the details of how the fringe is managed.
    Hence I implemented a single generic method which is configured with
    an algorithm-specific queuing strategy called fringeAdd.
    """
    closed = set()      # use set to keep distinct
    start = (problem.getStartState(), 0, [])  # node is a tuple with format like : (state, cost, path)
    fringeAdd(fringe, start, 0)       # fringeAdd(fringe, node, cost)

    while not fringe.isEmpty():
        (state, cost, path) = fringe.pop()

        if problem.isGoalState(state):
            return path

        if not state in closed:
            closed.add(state)

            for childState, childAction, childCost in problem.getSuccessors(state):
                newCost = cost + childCost     # Notice! Can't use cost += childCost
                newPath = path + [childAction]     # Notice! Can't use path.append(childAction)
                newState = (childState, newCost, newPath)
                fringeAdd(fringe, newState, cost)

    return "There is nothing in fringe. Failure!"


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"

    fringe = util.Stack()    # use stack data structure provided in util.py, LIFO
    def fringeAdd(fringe, node, cost):
        if not node in fringe.list:
            fringe.push(node)  # node is a tuple with format like : (state, cost, path)

    return genericSearch(problem, fringe, fringeAdd)
    # util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"

    fringe = util.Queue()    # FIFO
    def fringeAdd(fringe, node, cost):
        if not node in fringe.list:
            fringe.push(node)  # node is a tuple with format like : (state, cost, path)

    return genericSearch(problem, fringe, fringeAdd)
    # util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"

    fringe = util.PriorityQueue()    # Priority Queue ordered by cost
    def fringeAdd(fringe, node, cost):
        fringe.push(node, cost)  # node is a tuple with format like : (state, cost, path)

    return genericSearch(problem, fringe, fringeAdd)
    # util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    A* takes a heuristic function as an argument.
    Heuristics take two arguments: a state in the search problem (the main argument),
    and the problem itself (for reference information).
    """
    "*** YOUR CODE HERE ***"

    fringe = util.PriorityQueue()
    def fringeAdd(fringe, node, cost):  # node is a tuple with format like : (state, cost, path)
        cost += heuristic(node[0], problem)   # f(n) = g(n) + h(n)
        fringe.push(node, cost)

    return genericSearch(problem, fringe, fringeAdd)
    # util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
