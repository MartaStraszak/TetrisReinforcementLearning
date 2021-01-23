import numpy as np
import pygame, sys, random
from pygame.locals import *
from boardClass import *
from gameControl import *
from drawGame import *
from scipy import stats
from GameStateForBen import BenState
import matplotlib.pyplot as plt

class AgentBen:

    def __init__(self,weights=None):
        if weights is not None:
        #if type(weights) == np.ndarray:
            self.weights = weights
        else:
            self.weights = np.zeros(self.numOfFeatures())
        self.mean = np.zeros(self.numOfFeatures())
        self.range = np.ones(self.numOfFeatures())
        self.computeNormalization('HumanTraining.txt')
        self.gamma = 0.9
        self.alpha = 0.05
        self.savedMoves = []
        self.movesMemory = 2
        
            
    def numOfFeatures(self):
        vector = self.featureVector(BenState(), 'J', (0,0),normalize=False)
        return len(vector)
        
    def computeNormalization(self,dataFile):
        data = self.fetchSamplesFromFile(dataFile)
        numFeatures = self.numOfFeatures()
        if numFeatures == 0:
            print('Problem with normalization: no data available')
            exit()
        minValues = (10**6)*np.ones(numFeatures)
        maxValues = -(10**6)*np.ones(numFeatures)
        sum = np.zeros(numFeatures)
        for board, piece, shift, rot in data:
            featureV = self.featureVector(board, piece, (shift,rot), normalize=False)
            sum+=featureV
            minValues = np.minimum(minValues, featureV)
            maxValues = np.maximum(maxValues, featureV)
        self.range = maxValues - minValues
        self.mean = sum/len(data)
        self.range[numFeatures-1] = 1.0
        self.mean[numFeatures-1] = 0.0
    
    def featureVector(self,boardState, pieceType, action, normalize = True):
        '''outputs numpy vector of features'''
        nextBoard, reward = boardState.boardAfterAction(pieceType, action)
        vector = []
        #vector+=nextBoard.columnsHeight()
        vector.append(nextBoard.sumOfHeightDifferences())
        heights = np.array(nextBoard.columnsHeight())
        vector += list(heights)
        vector.append(heights.max())
        vector.append(heights.mean())
        vector.append(nextBoard.holeNum())
        vector.append(nextBoard.fillingWrtHighestColumn())
        vector.append(reward)
        vector.append(nextBoard.holesMass())
        vector.append(1.0)
        vector = np.array(vector)
        if normalize:
            vector = (np.array(vector) - self.mean)/self.range
            #print(vector)
        return vector
        
    def printWeights(self):
        for w in self.weights:
            sys.stdout.write("%.2f " % w)
        sys.stdout.write('\n')
        
    def updateWeights(self, boardState, pieceType, action):
        newBoardState, reward = boardState.boardAfterAction(pieceType, action)
        newPieceType = random.choice(['I','J','L','O','S','Z','T'])
        bestQvalue, bestAction = self.proposeAction(newBoardState,newPieceType)
        featureV = self.featureVector(boardState, pieceType, action)
        sample = reward + self.gamma * bestQvalue
        difference = np.dot(self.weights, featureV) - sample
        #print(difference)
        # self.printWeights()
        self.weights = self.weights - self.alpha * difference * featureV
        
    
    def Qvalue(self, boardState, pieceType, action):
        featureV = self.featureVector(boardState, pieceType, action)
        return np.dot(self.weights, featureV)
    
    def proposeAction(self,boardState,pieceType,epsGreedy=0.0,noise=0.001):
        '''given grid and piece type -- char, propose action (shift,rot)
        returns (Q-value, action)'''
        bestAction = None
        bestQvalue = None
        actions = boardState.validActions(pieceType)
        if random.random()<epsGreedy:
            return 0.0, random.choice(actions)
        for action in actions:
            Q = self.Qvalue(boardState, pieceType, action)+random.random()*noise
            if bestQvalue is None or bestQvalue < Q:
                bestQvalue = Q
                bestAction = action
        if bestQvalue == None:
            bestQvalue = 0
        return bestQvalue, bestAction
        
    def proposeAction2(self,boardState,pieceType):
        '''given grid and piece type -- char, propose action (shift,rot)
        returns (Q-value, action)'''
        bestAction = None
        bestQvalue = None
        actions = boardState.validActions(pieceType)
        for action in actions:
            Q = self.Qvalue(boardState, pieceType, action)
            if bestQvalue < Q:
                bestQvalue = Q
                bestAction = action
            print(pieceType+' '+str(action)+' '+("%.2f " % Q))
        if bestQvalue == None:
            bestQvalue = 0
        print(bestQvalue, bestAction)
        return bestQvalue, bestAction
    
    def fetchSamplesFromFile(self, dataFile):
        with open(dataFile) as f:
            lines = f.readlines()
        data = []
        for line in lines:
            line=line.strip()
            currBoard,currPieceType,currShift,currRot = line.split()
            currBoard = BenState(stringEncoding = currBoard)
            currShift = int(currShift)
            currRot = int(currRot)
            data.append((currBoard,currPieceType,currShift,currRot))
        return data
        
    def trainUsingData(self, dataFile, numIter):
        data = self.fetchSamplesFromFile(dataFile)
        for it in range(numIter):
            random.shuffle(data)
            for board, piece, shift, rot in data:
                self.updateWeights(board, piece, (shift,rot))
                
    def addToMemory(self, board, pieceType, action):
        if len(self.savedMoves) == self.movesMemory:
            self.savedMoves = self.savedMoves[self.movesMemory//2 : ]
        self.savedMoves.append((board, pieceType, action))
        
    def getFromMemory(self):
        # return self.savedMoves[-1]
        return random.choice(self.savedMoves)
        
    def savePlot(self,scores):
        numEpisodes=len(scores)
        maxScore=np.max(scores)
        
        xi=range(numEpisodes)
        y=scores
        #slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
        #line = slope*xi+intercept
        averages = []
        numAverage = 10
        for i in range(numEpisodes):
            sum=0.0
            for j in range(numAverage):
                sum+=scores[max(0,i-j)]
            averages.append(sum/numAverage)
            
        plt.plot(xi, y, 'ro', xi, averages, linewidth=3.0)
        plt.axis([0, numEpisodes, 0, maxScore])
        try:
            plt.savefig('plot.png', bbox_inches='tight')
            plt.gcf().clear()
        except Exception as inst:
            print("Exception when saving figure")
            print(inst)

                
                
    def trainRL(self, episodes):
        # self.trainUsingData(dataFile,1)
        # for noEpisode in range(episodes):
            # score=0
            # currBoard = BenState()
            # while not currBoard.boardTerminal():
                # currPieceType = random.choice(['I','J','L','O','S','Z','T'])
                # qval,action = self.proposeAction(currBoard,currPieceType,epsGreedy=0.00)
                # self.updateWeights(currBoard, currPieceType, action)
                # currBoard, reward=currBoard.boardAfterAction(currPieceType, action)
                # score += reward
            # print('Episode '+str(noEpisode)+': '+str(score)+'\n\n\n')
            # self.printWeights()
            
        self.trainUsingData('HumanTraining.txt',1)
        scoreList=[]
        for noEpisode in range(episodes):
            score=0
            currBoard = BenState()
            epsG=max(0.0,random.random()-0.5)*0.0
            print("epsGreedy: %.3f " % epsG)
            oldWeights = self.weights
            while not currBoard.boardTerminal():
                currPieceType = random.choice(['I','J','L','O','S','Z','T'])
                qval,action = self.proposeAction(currBoard,currPieceType,epsGreedy=epsG)
                self.addToMemory(currBoard, currPieceType, action)
                randomBoard, randomPiece, randomAction = self.getFromMemory()
                self.updateWeights(randomBoard, randomPiece, randomAction)
                currBoard, reward=currBoard.boardAfterAction(currPieceType, action)
                score += reward
            scoreList.append(score)
            print('Episode: '+str(noEpisode))
            print('Score: '+str(score))
            print("L2 Change in weights: %.3f"%np.linalg.norm(oldWeights -self.weights))
            self.printWeights()
            print('\n')
            self.savePlot(scoreList)

            
        
        
            
        
        