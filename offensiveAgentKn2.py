# baselineTeam.py
# ---------------
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


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)
    self.overrideAction = False
    self.overrideAct = None

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    if self.overrideAction is True:
      return self.overrideAct
      
    if (self.red):
      print(zip(actions,values))

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

 


  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}



class OffensiveReflexAgent(ReflexCaptureAgent):

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    bestAction = random.choice(bestActions)

    foodLeft = len(self.getFood(gameState).asList())

    ghostClose = False  
    hasCapsule = False 
    safeCapsule = False

    features = self.getFeatures(gameState, 'Stop')

    foodList = self.getFood(gameState).asList() 

    

    if not gameState.getAgentState(self.index).isPacman:
      self.home = gameState.getAgentPosition(self.index)
   

    if features['fleeEnemy'] <= 5.0 and gameState.getAgentState(self.index).isPacman:
      ghostClose = True


    if self.red:
      if gameState.getBlueCapsules():
        hasCapsule = True

    if not self.red:
      if gameState.getRedCapsules():
        hasCapsule = True
   
    if ghostClose and hasCapsule and gameState.getAgentState(self.index).numCarrying  >= 1:
        if self.red:  

          capsulePos  = gameState.getBlueCapsules()[0]         
          ghostDistance1 = self.getFeatures(gameState,'Stop')['fleeEnemy']          
          bestDist = self.getMazeDistance(gameState.getAgentPosition(self.index), capsulePos)

          
          if self.getMazeDistance(gameState.getAgentPosition(self.index), self.home) > bestDist:
            
          
            for action in actions:

             ghostDistance2 = self.getFeatures(gameState,action)['fleeEnemy'] 
             successor = self.getSuccessor(gameState, action)
             pos2 = successor.getAgentPosition(self.index)
             dist = self.getMazeDistance(capsulePos, pos2)
          
             if dist < bestDist and (ghostDistance2 - ghostDistance1) >=  0.0:
                bestAction = action
                bestDist = dist      
                safeCapsule = True      
        elif not self.red:         
          capsulePos  = gameState.getRedCapsules()[0]
          ghostDistance1 = features['fleeEnemy']
          bestDist = self.getMazeDistance(gameState.getAgentPosition(self.index), capsulePos)
          
          if self.getMazeDistance(gameState.getAgentPosition(self.index), self.home) > bestDist: 
            
            for action in actions:
              ghostDistance2 = self.getFeatures(gameState,action)['fleeEnemy'] 
              successor = self.getSuccessor(gameState, action)
              pos2 = successor.getAgentPosition(self.index)
              dist = self.getMazeDistance(capsulePos, pos2)

              if dist < bestDist and (ghostDistance2 - ghostDistance1) >= 0.0:
                bestAction = action
                bestDist = dist      
                safeCapsule = True

    if (not safeCapsule and ghostClose and gameState.getAgentState(self.index).numCarrying  > 0) or (len(self.observationHistory) >= 285 and gameState.getAgentState(self.index).numCarrying >= 1) or (gameState.getAgentState(self.index).numCarrying >= 5 and features['distanceToFood'] > 2) or len(foodList) <= 2:
      bestDist = self.getMazeDistance(gameState.getAgentPosition(self.index),self.start)
      ghostDistance1 = features['fleeEnemy']
  
      for action in actions:     
        ghostDistance2 = self.getFeatures(gameState,action)['fleeEnemy'] 
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start, pos2)
        if dist < bestDist and (ghostDistance2 - ghostDistance1) >= 0.0:
          bestAction = action
          bestDist = dist

    if gameState.getAgentState(self.index).numCarrying < 1 and ghostClose:
      if features['distanceToFood'] > 3:
        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          ghostDistance1 = features['fleeEnemy']
          myPos = gameState.getAgentState(self.index).getPosition()
          maxDistance = random.choice([self.getMazeDistance(myPos, food) for food in foodList])
          for action in actions:
            ghostDistance2 = self.getFeatures(gameState,action)['fleeEnemy'] 
            successor = self.getSuccessor(gameState,action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(myPos,pos2)

            if dist < maxDistance and (ghostDistance2 - ghostDistance1) >= 0.0:
              bestAction = action
              bestDist = maxDistance


    

    if gameState.getAgentState(self.index).numCarrying < 3 and gameState.getAgentState(self.index).isPacman:
      
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = gameState.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        for action in actions:
          successor = self.getSuccessor(gameState,action)
          pos2 = successor.getAgentPosition(self.index)
          dist = self.getMazeDistance(self.start,pos2)

        if dist < minDistance:
          bestAction = action
          bestDist = minDistance
    if len(self.observationHistory) > 3:      
      if self.observationHistory[-1].getAgentPosition(self.index) == self.observationHistory[-2].getAgentPosition(self.index) or gameState.getAgentPosition(self.index) == self.observationHistory[-2].getAgentPosition(self.index):
        return random.choice(actions)    


    '''
    else:
      foodList = self.getFood(gameState, action)
      for action in actions:
     '''        
    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      
    return bestAction
    return random.choice(bestActions)
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    
    foodList = self.getFood(successor).asList()    
    
    features['successorScore'] = -len(foodList)#self.getScore(successor)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition

    # Compute distance to the nearest food


    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      maxDistance = max([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
      features['farFood'] = maxDistance

    ghostDistance = 999.0 #Default distance from a Pacman to a ghost
    features['fleeEnemy'] = ghostDistance
    if gameState.getAgentState(self.index).isPacman: #Checks if and agent is currently a pacman
      opponentFutureState = [successor.getAgentState(i) for i in self.getOpponents(successor)] #gets an opponents future state
      ghosts = [p for p in opponentFutureState if p.getPosition() and not p.isPacman and p.scaredTimer == 0] #gets all ghost locations of opponents
      if len(ghosts) > 0:
        ghostDistance = min([float(self.getMazeDistance(myPos, g.getPosition())) for g in ghosts]) #gets closest ghost loaction
        features['fleeEnemy'] = ghostDistance
        #if gameState.getAgentState(self.index).isPacman and gameState.isOnRedTeam(self.index) and ghostDistance != 0:
          #print ghostDistance
        #time.sleep(.25)
    return features
 


  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    #Computes agents noisy distance to the closest enemy agent
    dist = self.getOpponents()
    features['invaderNoisyDistance'] = min(dist)

    #FIND A WAY TO IGNORE ANY EMEMY WHO IS NOT PACMAN

    #REVERSE WEIGHTS IF ISSCARED

    #computes the distance from the start
    distFromStart = self.getMazeDistance(self.start, gameState.getAgentPosition(self.index))
    features['startDist'] = distFromStart

    #computes the number of food left on our side
    currentFood = len(self.getFoodYouAreDefending(gameState).asList())
    successorFood = self.getFoodYouAreDefending(successor)
    if currentFood > successorFood:
      features['foodEaten'] = (currentFood-successorFood)

    #dont go in the spots it has previously visited recently
    if(gameState.getAgentPosition(self.index) in self.previousPositions):
      features['beenBefore'] = 1
    else:
      features['beenBefore'] = 0

    #
    

    #pelletLocationx = self.getCapsulesYouAreDefending(gameState)[0]
    gameState.getAgentPosition(self.index)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -20, 'stop': -100, 'reverse': -5, 'foodEaten': -5,'invaderNoisyDistance': -1,'startDist': 100,'beenBefore':-5}