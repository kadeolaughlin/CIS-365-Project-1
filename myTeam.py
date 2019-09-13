# myTeam.py
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from node import *

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'BaseAgent', second = 'BaseAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class BaseAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

  '''
  A* algorithm found at https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
  '''
  def getPath(self,gameState,endPos):
    start_node = Node(None, gameState.getAgentPosition(self.index))
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, endPos)
    end_node.g = end_node.h = end_node.f = 0
    open_list = []
    closed_list = []
    open_list.append(start_node)
    while len(open_list) > 0:
      current_node = open_list[0]
      current_index = 0
      for index, item in enumerate(open_list):
        if item.f < current_node.f:
          current_node = item
          current_index = index
      open_list.pop(current_index)
      closed_list.append(current_node)
      if current_node == end_node:
        path = []
        current = current_node
        while current is not None:
          path.append(current.position)
          current = current.parent
        return path[::-1]
      children = []
      for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Adjacent squares
        node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
        new_node = Node(current_node, node_position)
        if gameState.hasWall(node_position[0],node_position[1]):
            continue
        if Node(current_node,node_position) in closed_list:
            continue
        children.append(new_node)
      for child in children:
        for closed_child in closed_list:
          if child == closed_child:
            continue
        child.g = current_node.g + 1
        child.h = self.getMazeDistance((child.position[0],child.position[1]),endPos)
        child.f = child.g + child.h
        for open_node in open_list:
          if child == open_node and child.g > open_node.g:
            continue
        open_list.append(child)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    #gets the agents position and stores in x and y
    x, y = gameState.getAgentPosition(self.index)
    #finds the path from the current position to (5,1)
    path = self.getPath(gameState,(5,1))
    #get the agents position minus the next step in the path
    x = path[1][0] - x
    y = path[1][1] - y
    print(self.getMazeDistance(gameState.getAgentPosition(self.index),(5,1)))
    print('Current: ', gameState.getAgentPosition(self.index),'Next: ', path[1], 'Action: ',x,y)
    if x is 0 and y is 1:
      return 'North'
    elif x is 0 and y is -1:
      return 'South'
    elif x is 1 and y is 0:
      return 'East'
    elif x is -1 and y is 0:
      return 'West'
    elif x is -1 and y is -1:
      act = gameState.getLegalActions(self.index)
      if 'North' in act:
        act.remove('North')
      if 'East' in act:
        act.remove('East')
      return random.choice(act)
    else:
      return random.choice(actions)
