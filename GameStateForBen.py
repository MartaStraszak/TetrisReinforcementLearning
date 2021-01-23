import numpy as np
import pygame, sys, random
from pygame.locals import *
from boardClass import *
from gameControl import *
from drawGame import *

class BenState:
    def __init__(self, board=None, gameState = None, stringEncoding = None):
        self.h, self.w = (24,10)
        self.board = np.zeros((self.h, self.w), dtype = int)
        if board is not None:
            self.board = board
        elif gameState != None:
            for i in range(self.h):
                for j in range(self.w):
                    self.board[i][j] = int(not gameState.gameBoard.grid[i][j].empty)
        elif stringEncoding != None:
            self.board = self.strToState(stringEncoding)
            
        
        
    def __str__(self):
        picture = ''
        for i in range(self.h):
            for j in range(self.w):
                picture += str(self.board[i][j])
            picture += '\n'
        return picture
                    
                    
    def movePiece(self, block, boxLen, position, direction):
        '''direction is (dx,dy) -- returns whether movement is possibe'''
        newX, newY = position[0]+direction[0], position[1]+direction[1]  # pierwsze w pionie drugie w poziomie
        for x in range(boxLen):
            for y in range(boxLen):
                if not block[x][y]:
                    continue
                if (newX+x<0 or newY+y<0 or newX+x>=self.h or newY+y>=self.w) or (self.board[newX+x][newY+y]):
                    return False
        return True
        
    def reduceFullLine(self):
        '''finds a full line and removes it
        the part on top of it drops one unit down
        returns true if line found'''
        for x in range(self.h):
            fullLine=True
            for y in range(self.w):
                if not self.board[x][y]:
                    fullLine=False
            if fullLine:
                for i in range(x):
                    self.board[x-i] = self.board[x-i-1]
                self.board[0] = [0]*self.w
                return True
        return False
        
    def piecePasteToBoard(self, block, boxLen, position):
        '''returns copy of a board with new piece and reward'''
        newBoard = BenState(board = np.copy(self.board))
        for x in range(boxLen):
            for y in range(boxLen):
                if block[x][y]:
                    newBoard.board[position[0]+x][position[1]+y] = 1
        reward = 0
        while newBoard.reduceFullLine():
            reward += 1
        # if 1 in newBoard.board[12]:
            # reward -= 0.1
        # if 1 in newBoard.board[17]:
            # reward -= 0.03
        if self.boardTerminal():
            reward -= 1
        return newBoard , reward
        
    
    def boardAfterAction(self, piece, action):
        '''take state, type of piece and action (move, rotation), return copy of a board and reward
        return False if action not possible'''
        move, rotation = action
        pieceBlock = Tetromino(piece, rotation).block
        boxLen = Tetromino(piece, rotation).boundaryLen
        currX, currY = (0,4)
        reward = 0
        if self.movePiece(pieceBlock, boxLen, (0,4), (0, move)) == False:
            return False 
        currY += move
        while self.movePiece(pieceBlock, boxLen, (currX, currY), (1,0)) != False:
            currX += 1
        return self.piecePasteToBoard(pieceBlock, boxLen, (currX, currY))

    
        
    def stateToStr(self):
        result=''
        for i in range(self.h):
            for j in range(self.w):
                result+=str(int(self.board[i][j]))
        return result
        
    def strToState(self, boardString):
        '''returns numpy array'''
        initBoard = np.zeros((self.h, self.w), dtype = int)
        for i in range(self.h):
            for j in range(self.w):
                initBoard[i][j] = int(boardString[i*self.w+j])
        return initBoard
    
    
    #def '''feature that return number of cleared lines'''
    def validActions(self, pieceType):
        '''returns list of pairs (move, rotation)'''
        actions = []
        for shift in range(-7,8):
            for rot in range(4):
                pieceBlock = Tetromino(pieceType, rot).block
                boxLen = Tetromino(pieceType, rot).boundaryLen
                if self.movePiece(pieceBlock, boxLen, (0,4), (0,shift)):
                    actions.append((shift, rot))
        return actions
    
    def columnsHeight(self):
        heights = [0]*self.w
        for j in range(self.w):
            for i in range(self.h):
                if self.board[i][j]:
                    heights[j] = max(self.h - i, heights[j])
        return heights
        
    def boardTerminal(self):
        for j in range(self.w):
            if self.board[3][j]:
                return True
        return False

    def sumOfHeightDifferences(self):
        heights = self.columnsHeight()
        result = 0
        for j in range(1,self.w):
            result += abs(heights[j-1]-heights[j])
        return result
        
    def holeNum(self):
        heights = self.columnsHeight()
        onesIdx = [self.h - x for x in heights]
        cntHoles = 0
        for j in range(self.w):
            for i in range(onesIdx[j]+1,self.h):
                cntHoles+=(1-self.board[i][j])
        return cntHoles*1.0/(self.w)    
        
    def fillingWrtHighestColumn(self):
        maxColumn = max(self.columnsHeight())
        if maxColumn == 0:
            return 1.0
        onesNum = 0
        for j in range(self.w):
            for i in range(self.h-maxColumn, self.h):
                onesNum += self.board[i][j]
        return onesNum
        
    def holesMass(self):
        mass = 0.0
        for j in range(self.w):
            holeNum = 0
            for i in range(self.h):
                holeNum += 1 - self.board[self.h-1-i][j]
                mass += self.board[self.h-1-i][j] * holeNum    
        return mass
                
    # def sumOfRowy(self):
        
        
    
#    def ''' cos ze dziury nizej sa gorsze, czyli dla dziury patrzysz wysokosc kolumny i sumujemy ile jest kockow nad wszystkimi dziurami lacznie.
#        jeszcze trzeba bedzie wzystko znormalizowac. 1 wersja, gorsze sa dziury na spodzie; 2 wersja, gorsze dziury na gorze'''
        
#        '''suma kwadratow dziur spojnych liczonych w pionie'''
        
        
    
    