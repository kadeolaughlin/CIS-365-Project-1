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
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed, first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """

    openingMovesFinished = False

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.overrideAction = False
        self.overrideAct = None
        self.previousPositions = []

    def chooseAction(self, gameState):
        """
        Picks random legal action.
        """
        actions = gameState.getLegalActions(self.index)

        return random.choice(actions)

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

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """

    '''
    A* algorithm found at https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
    '''
    def getPath(self, gameState, endPos, hvalue):

        start_node = Node(None, gameState.getAgentPosition(self.index))
        start_node.g = 0
        start_node.h = 0
        start_node.f = 0
        end_node = Node(None, endPos)
        end_node.g = 0
        end_node.h = 0
        end_node.f = 0

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
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
                new_node = Node(current_node, node_position)
                if gameState.hasWall(node_position[0], node_position[1]):
                    continue
                if Node(current_node, node_position) in closed_list:
                    continue
                children.append(new_node)
            for child in children:
                for closed_child in closed_list:
                    if child == closed_child:
                        continue
                child.g = current_node.g + 1
                if hvalue is None:
                    child.h = self.getMazeDistance((child.position[0], child.position[1]), endPos)
                else:
                    child.h = hvalue
                child.f = child.g + child.h
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue
                open_list.append(child)

class OffensiveReflexAgent(ReflexCaptureAgent):

    def chooseAction(self, gameState):
        """
        A heierachy of decisions to be made for an offence agent
        """
        actions = gameState.getLegalActions(self.index) #A list of all legal actions

        values = [self.evaluate(gameState, a) for a in actions] #evaluates all actoins for whichever makes pacmant closest to food
        maxValue = max(values)
        
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        bestAction = random.choice(bestActions)#A random choice of which best actions, always gets whichever gets pacman nerest to food, this may get overwritten
        

        bestAction = random.choice(bestActions) #Randomly chooses a legal action from actions, this will be the fallthrough action

        foodLeft = len(self.getFood(gameState).asList()) #how much food is left for the agent to get

        ghostClose = False #Boolean for if an enemy ghost is near the pacman
        hasCapsule = False #Boolean for if the power pellet can still be eaten, defaults to no for saftey
        safeCapsule = False #Blooean to keep wheter getting the power pellet is safe
        numCarrying = gameState.getAgentState(self.index).numCarrying #How much food the pacman has eaten without returning to its side
        currentPos = gameState.getAgentPosition(self.index) #Agents position
        turnsLeft =  300 - len(self.observationHistory)#how many turns the agent has left


        features = self.getFeatures(gameState, 'Stop') #the list of features to be used

        foodList = self.getFood(gameState).asList() #The list of food for the pacman to eat

        
        #checks if the agent is a pacman if not sets current location as the home location, where it tries to return to
        if not gameState.getAgentState(self.index).isPacman: 
            self.home = gameState.getAgentPosition(self.index)


        #checks if a ghost is within 5 spaces and sets ghostClose to true
        if features['fleeEnemy'] <= 3.0 and gameState.getAgentState(self.index).isPacman:
            ghostClose = True

        
        #checks if the capsule was eaten if agent is red.
        if self.red:
            if gameState.getBlueCapsules():
                hasCapsule = True

        #checks if the power pellet was eaten if agent is blue
        if not self.red:
            if gameState.getRedCapsules():
                hasCapsule = True


        '''
        If a ghost is close and the capsule is still avalible, checks if home or the capsule is closer
        and if the capsule is safe to eat. If the capsule is closer and safe to eat bestAction is then set
         to whatever action minimizes the distance to it.
        '''              
        if ghostClose and hasCapsule and numCarrying >= 1:
            if self.red:

                capsulePos = gameState.getBlueCapsules()[0]
                ghostDistance1 = features['fleeEnemy']
                bestDist = self.getMazeDistance(currentPos, capsulePos)

                if self.getMazeDistance(currentPos, self.home) > bestDist:

                    for action in actions:

                        ghostDistance2 = self.getFeatures(gameState, action)['fleeEnemy']
                        successor = self.getSuccessor(gameState, action)
                        pos2 = successor.getAgentPosition(self.index)
                        dist = self.getMazeDistance(capsulePos, pos2)

                        if dist < bestDist and (ghostDistance2 - ghostDistance1) >= 0.0:
                            bestAction = action
                            bestDist = dist
                            safeCapsule = True
            elif not self.red:
                capsulePos = gameState.getRedCapsules()[0]
                ghostDistance1 = features['fleeEnemy']
                bestDist = self.getMazeDistance(gameState.getAgentPosition(self.index), capsulePos)

                if self.getMazeDistance(gameState.getAgentPosition(self.index), self.home) > bestDist:

                    for action in actions:
                        ghostDistance2 = self.getFeatures(gameState, action)['fleeEnemy']
                        successor = self.getSuccessor(gameState, action)
                        pos2 = successor.getAgentPosition(self.index)
                        dist = self.getMazeDistance(capsulePos, pos2)

                        if dist < bestDist and (ghostDistance2 - ghostDistance1) >= 0.0:
                            bestAction = action
                            bestDist = dist
                            safeCapsule = True


        '''
        Finds the action that puts pacman closer to home and maintains distance from the ghost or increaces it is called
        if the capsule is not safe to get to and a ghost is near and the pacman has non returned food 
        if the agent has less than 15 moves left and has at leat one food
        if the agent has 5 or more unreturned food and the nearest food is more than two moves away
        or if the agent only has two reamaining food avalibe to eat.
        '''


        if (not safeCapsule and ghostClose and numCarrying > 0) or (turnsLeft <= 15 and numCarrying >= 1) or (numCarrying >= 5 and features['distanceToFood'] > 2) or foodLeft <= 2:
            

            bestDist = self.getMazeDistance(gameState.getAgentPosition(self.index), self.start)
            ghostDistance1 = features['fleeEnemy']

            for action in actions:
                ghostDistance2 = self.getFeatures(gameState, action)['fleeEnemy']
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
                if dist < bestDist and (ghostDistance2 - ghostDistance1) >= 0.0:
                    bestAction = action
                    bestDist = dist

        #if a ghost is close an agent has no food picks a random food to head towards
        if gameState.getAgentState(self.index).numCarrying < 1 and ghostClose: 
            if features['distanceToFood'] > 3:
                if len(foodList) > 0:  # This should always be True,  but better safe than sorry
                    ghostDistance1 = features['fleeEnemy']
                    myPos = gameState.getAgentState(self.index).getPosition()
                    maxDistance = random.choice([self.getMazeDistance(myPos, food) for food in foodList])
                    for action in actions:
                        ghostDistance2 = self.getFeatures(gameState, action)['fleeEnemy']
                        successor = self.getSuccessor(gameState, action)
                        pos2 = successor.getAgentPosition(self.index)
                        dist = self.getMazeDistance(myPos, pos2)

                        if dist < maxDistance and (ghostDistance2 - ghostDistance1) >= 0.0:
                            bestAction = action
                            bestDist = maxDistance
        '''
        An override check so the agent doesn't get stuck in a loop or a single spot.
        '''
        if len(self.observationHistory) > 3:
            if self.observationHistory[-1].getAgentPosition(self.index) == self.observationHistory[-2].getAgentPosition(self.index) or gameState.getAgentPosition(self.index) == self.observationHistory[-2].getAgentPosition(self.index):
                return random.choice(actions)
        

        return bestAction

    """
    Returns a Dictonary of ceratin feature for use in chooseAction

    """

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        foodList = self.getFood(successor).asList()

        features['successorScore'] = -len(foodList)  # self.getScore(successor)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition

        # Compute distance to the nearest food

        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            maxDistance = max([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
            features['farFood'] = maxDistance

        ghostDistance = 999.0  # Default distance from a Pacman to a ghost
        features['fleeEnemy'] = ghostDistance
        if gameState.getAgentState(self.index).isPacman:  # Checks if and agent is currently a pacman
            opponentFutureState = [successor.getAgentState(i) for i in
                                   self.getOpponents(successor)]  # gets an opponents future state
            ghosts = [p for p in opponentFutureState if
                      p.getPosition() and not p.isPacman and p.scaredTimer == 0]  # gets all ghost locations of opponents
            if len(ghosts) > 0:
                ghostDistance = min([float(self.getMazeDistance(myPos, g.getPosition())) for g in
                                     ghosts])  # gets closest ghost loaction
                features['fleeEnemy'] = ghostDistance
                
        return features

    '''
    Returns weights for aspects of features Dictonary. 
    Only used to find way to closest food.
    '''
    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1}

class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """

    def openingMoves(self, gameState):
        """
        This function is called on the defending ghost at the beginning of the game to reach the middle of the board
        as well as anytime the defending ghost is eaten by a pacman. This functions purpose is to get the defending
        ghost into a defensible board position.

        :param gameState:
        :return a legal action:
        """

        # Get legal moves defender ghost can make
        actions = gameState.getLegalActions(self.index)

        # Arbitrary chosen position in middle of board for our defending ghost to get to
        position = (18, 8)

        # The next move our defender needs to make to get to designated position
        path = self.getPath(gameState, position, None)

        # Gets the current defender ghost's position on the board
        x, y = gameState.getAgentPosition(self.index)

        # Checks to see if the defender ghost's current position matches desired position
        if position[0] is x and position[1] is y:
            self.openingMovesFinished = True
            return random.choice(actions)

        # Calculates the x and y coordinates that the defender ghost needs to take in order to make its next move
        # Toward its goal position
        x = path[1][0] - x
        y = path[1][1] - y

        # Checks the calculated coordinates and chooses a legal move accordingly
        if x is 0 and y is 1 and "North" in actions:
            return "North"
        elif x is 0 and y is -1 and "South" in actions:
            return "South"
        elif x is 1 and y is 0 and "East" in actions:
            return "East"
        elif x is -1 and y is 0 and "West" in actions:
            return "West"
        else:
            return random.choice(actions)


    def chooseAction(self, gameState):
        """
        Picks among the legal actions according to features, weights, and gameStates.
        """

        # Checks to see if the defender ghost is in initial position
        if set(self.start) == set(gameState.getAgentPosition(self.index)):
            self.openingMovesFinished = False

        # Checks to see if the opening moves of the defending ghost are complete
        if not self.openingMovesFinished:
            return self.openingMoves(gameState)

        self.previousPositions += gameState.getAgentPosition(self.index)
        if len(self.previousPositions) > 10:
            self.previousPositions.remove(self.previousPositions[0])
            actions = gameState.getLegalActions(self.index)

        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        if self.overrideAction is True:
            return self.overrideAct

        if self.red:
            print(zip(actions, values))

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        return random.choice(bestActions)

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

        # Computes agents noisy distance to the closest enemy agent
        dist = gameState.getAgentDistances()
        features['invaderNoisyDistance'] = min(dist)

        # computes the distance from the start
        distFromStart = self.getMazeDistance(self.start, gameState.getAgentPosition(self.index))
        features['startDist'] = distFromStart

        # computes the number of food left on our side
        currentFood = len(self.getFoodYouAreDefending(gameState).asList())
        successorFood = len(self.getFoodYouAreDefending(successor).asList())
        if currentFood > successorFood:
            features['foodEaten'] = (currentFood - successorFood)

        # dont go in the spots it has previously visited recently
        if (gameState.getAgentPosition(self.index) in self.previousPositions):
            features['beenBefore'] = 1
        else:
            features['beenBefore'] = 0

        # reverse the weights when pacman is scared

        # use noisy distance of closest enemy only

        # pelletLocationx = self.getCapsulesYouAreDefending(gameState)[0]
        gameState.getAgentPosition(self.index)

        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -20, 'stop': -100, 'reverse': -5,
                'foodEaten': -5, 'invaderNoisyDistance': -50, 'startDist': 500, 'beenBefore': -5}

class Node():
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent = None, position = None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
